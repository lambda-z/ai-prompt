from __future__ import annotations

import json
import os
import shutil
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Union, Optional
from urllib.parse import quote


FileMapInput = Union[str, Dict[str, str]]


class FilePackError(Exception):
    """打包/落盘相关错误。"""


class StorageError(Exception):
    """存储相关错误。"""


@dataclass(frozen=True)
class PackResult:
    """json2file 的返回结构。"""
    zip_path: str  # 生成的zip完整路径


@dataclass(frozen=True)
class StorageResult:
    """file2storage 的返回结构。"""
    url: str  # 存储对象的访问地址


class ProjectFilePacker:
    """
    将 file_map (json字符串/dict) 写入到项目目录中，并打包为 zip。
    """

    # ---------------------------
    # Public APIs
    # ---------------------------

    def json2file(
        self,
        file_map: FileMapInput,
        file_path: str,
        output_path: str,
        project_name: str,
    ) -> Dict[str, str]:
        """
        根据 file_map 在 file_path/project_name 下创建文件结构并写入内容；
        最终打包到 output_path 下的 zip 文件，并清理临时目录。
        返回：{"zip_path": "..."}  (完整路径)
        """
        file_map_dict = self._parse_file_map(file_map)
        self._validate_project_name(project_name)

        base_dir = Path(file_path).expanduser().resolve()
        out_dir = Path(output_path).expanduser().resolve()
        tmp_project_dir = base_dir / project_name

        self._ensure_dir(base_dir)
        self._ensure_dir(out_dir)

        zip_full_path: Optional[Path] = None
        try:
            # 1) 创建/清空临时项目目录
            self._recreate_dir(tmp_project_dir)

            # 2) 写入文件结构
            self._write_files(tmp_project_dir, file_map_dict)

            # 3) 打包为 zip
            zip_full_path = self._make_zip(
                src_dir=tmp_project_dir,
                out_dir=out_dir,
                zip_name=f"{project_name}.zip",
            )

            return PackResult(zip_path=str(zip_full_path)).__dict__
        finally:
            # 4) 清理临时目录（不影响 zip）
            # 若需要保留调试，可在此处加开关
            self._safe_remove_dir(tmp_project_dir)

    def file2storage(self, file_path: str) -> Dict[str, str]:
        """
        将 file_path 指向的文件上传/保存至存储系统，并返回可访问 URL。
        这里给出一个“本地存储”的默认实现：返回 file:// URL。
        你可以继承此类并覆盖该方法，实现 S3/OSS/COS 等上传。
        """
        p = Path(file_path).expanduser().resolve()
        if not p.exists() or not p.is_file():
            raise StorageError(f"File not found or not a file: {p}")

        url = self._to_file_url(p)
        return StorageResult(url=url).__dict__

    # ---------------------------
    # Parsing & Validation
    # ---------------------------

    def _parse_file_map(self, file_map: FileMapInput) -> Dict[str, str]:
        """将 json 字符串或 dict 解析成 dict[str, str]。"""
        if isinstance(file_map, dict):
            return self._ensure_str_str_dict(file_map)

        if isinstance(file_map, str):
            try:
                obj = json.loads(file_map)
            except json.JSONDecodeError as e:
                raise FilePackError(f"Invalid json string: {e}") from e
            if not isinstance(obj, dict):
                raise FilePackError("file_map json must be an object (dict).")
            return self._ensure_str_str_dict(obj)

        raise FilePackError("file_map must be a json string or dict.")

    def _ensure_str_str_dict(self, d: dict) -> Dict[str, str]:
        """确保 dict 的 key/value 都是 str。"""
        out: Dict[str, str] = {}
        for k, v in d.items():
            if not isinstance(k, str):
                raise FilePackError(f"file_map key must be str, got {type(k)}: {k}")
            if not isinstance(v, str):
                # 内容也可以改成支持 bytes/None 等，这里按需求严格 str
                raise FilePackError(f"file_map value must be str, got {type(v)}: {k}")
            out[k] = v
        return out

    def _validate_project_name(self, project_name: str) -> None:
        """避免路径穿越/非法目录名。"""
        if not project_name or not isinstance(project_name, str):
            raise FilePackError("project_name must be a non-empty string.")

        # 禁止路径分隔符，避免 project_name 变成多级路径
        if "/" in project_name or "\\" in project_name:
            raise FilePackError("project_name must not contain path separators (/ or \\).")

        # 简单禁止 '..'
        if ".." in project_name:
            raise FilePackError("project_name must not contain '..'.")

    def _sanitize_relpath(self, rel_path: str) -> Path:
        """
        将用户提供的相对路径转为安全的相对 Path：
        - 禁止绝对路径
        - 禁止 '..' 路径穿越
        """
        p = Path(rel_path)

        if p.is_absolute():
            raise FilePackError(f"Absolute path not allowed in key: {rel_path}")

        # 统一处理：分段检查
        for part in p.parts:
            if part in ("..", ""):
                raise FilePackError(f"Unsafe path segment in key: {rel_path}")

        return p

    # ---------------------------
    # Filesystem Helpers
    # ---------------------------

    def _ensure_dir(self, path: Path) -> None:
        """确保目录存在。"""
        path.mkdir(parents=True, exist_ok=True)

    def _recreate_dir(self, path: Path) -> None:
        """若目录存在则删除重建，保证干净。"""
        if path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True, exist_ok=True)

    def _safe_remove_dir(self, path: Path) -> None:
        """安全删除目录（存在才删）。"""
        try:
            if path.exists():
                shutil.rmtree(path)
        except Exception:
            # 清理失败不应影响主流程（zip 已经生成）
            pass

    def _write_files(self, root: Path, file_map: Dict[str, str]) -> None:
        """
        遍历 file_map 写入文件。
        key: 相对路径/文件名
        value: 文件内容（str）
        """
        for rel, content in file_map.items():
            safe_rel = self._sanitize_relpath(rel)
            target = (root / safe_rel).resolve()

            # 防止 resolve 后跳出 root（双保险）
            if not str(target).startswith(str(root.resolve()) + os.sep) and target != root.resolve():
                raise FilePackError(f"Path escapes project root: {rel}")

            # 创建父目录并写文件
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")

    # ---------------------------
    # Zip Helpers
    # ---------------------------

    def _make_zip(self, src_dir: Path, out_dir: Path, zip_name: str) -> Path:
        """将 src_dir 打包为 out_dir/zip_name，并返回 zip 路径。"""
        zip_path = (out_dir / zip_name).resolve()

        # 若同名 zip 已存在，覆盖
        if zip_path.exists():
            zip_path.unlink()

        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for file in src_dir.rglob("*"):
                if file.is_file():
                    # arcname 让 zip 内部路径从 project_name 开始
                    arcname = file.relative_to(src_dir.parent)
                    zf.write(file, arcname=str(arcname))

        return zip_path

    # ---------------------------
    # Storage Helpers (local demo)
    # ---------------------------

    def _to_file_url(self, path: Path) -> str:
        """将本地路径转为 file:// URL（示例用）。"""
        # Windows/Posix 都尽量兼容
        p = path.as_posix()
        return "file://" + quote(p)


# ---------------------------
# Example
# ---------------------------
if __name__ == "__main__":
    packer = ProjectFilePacker()

    # file_map = {
    #     "src/main.py": "print('hello')\n",
    #     "README.md": "# Demo\n",
    #     "config/app.json": '{"env":"dev"}\n',
    # }

    with open("../wharf/receiving/lang-graph.json", "r", encoding="utf-8") as f:
        file_map = f.read()

    result = packer.json2file(
        file_map=file_map,
        file_path="",
        output_path="../wharf/shipping",
        project_name="scallion",
    )
    print("zip:", result["zip_path"])

    storage = packer.file2storage(result["zip_path"])
    print("url:", storage["url"])
