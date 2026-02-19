import json
import zipfile
from pathlib import Path

import pytest

from util.project_file_packer import ProjectFilePacker, FilePackError, StorageError


@pytest.fixture()
def packer():
    if ProjectFilePacker is None:
        pytest.skip("Please set correct import: from your_module import ProjectFilePacker, FilePackError, StorageError")
    return ProjectFilePacker()


def _read_zip_text(zip_path: Path, member: str) -> str:
    with zipfile.ZipFile(zip_path, "r") as zf:
        with zf.open(member, "r") as f:
            return f.read().decode("utf-8")


def _zip_namelist(zip_path: Path) -> list[str]:
    with zipfile.ZipFile(zip_path, "r") as zf:
        return sorted(zf.namelist())


def test_json2file_with_dict_creates_zip_and_cleans_tmp(tmp_path: Path, packer):
    file_path = tmp_path / "work"
    out_path = tmp_path / "out"
    project_name = "demo"

    file_map = {
        "src/main.py": "print('hello')\n",
        "README.md": "# Demo\n",
        "config/app.json": '{"env":"dev"}\n',
    }

    result = packer.json2file(
        file_map=file_map,
        file_path=str(file_path),
        output_path=str(out_path),
        project_name=project_name,
    )

    zip_path = Path(result["zip_path"])
    assert zip_path.exists()
    assert zip_path.is_file()
    assert zip_path.parent.resolve() == out_path.resolve()

    # 临时目录应当被清理：file_path/project_name 不存在
    assert not (file_path / project_name).exists()

    # zip 内部路径应从 project_name 开始
    names = _zip_namelist(zip_path)
    assert f"{project_name}/README.md" in names
    assert f"{project_name}/src/main.py" in names
    assert f"{project_name}/config/app.json" in names

    # 文件内容校验
    assert _read_zip_text(zip_path, f"{project_name}/src/main.py") == "print('hello')\n"
    assert _read_zip_text(zip_path, f"{project_name}/README.md") == "# Demo\n"


def test_json2file_with_json_string(tmp_path: Path, packer):
    file_path = tmp_path / "work"
    out_path = tmp_path / "out"
    project_name = "p1"

    file_map_dict = {
        "a.txt": "A\n",
        "dir/b.txt": "B\n",
    }
    file_map_json = json.dumps(file_map_dict, ensure_ascii=False)

    result = packer.json2file(
        file_map=file_map_json,
        file_path=str(file_path),
        output_path=str(out_path),
        project_name=project_name,
    )
    zip_path = Path(result["zip_path"])
    assert zip_path.exists()

    names = _zip_namelist(zip_path)
    assert f"{project_name}/a.txt" in names
    assert f"{project_name}/dir/b.txt" in names
    assert _read_zip_text(zip_path, f"{project_name}/dir/b.txt") == "B\n"


def test_json2file_overwrites_existing_zip(tmp_path: Path, packer):
    file_path = tmp_path / "work"
    out_path = tmp_path / "out"
    project_name = "demo"

    out_path.mkdir(parents=True, exist_ok=True)
    existing_zip = out_path / f"{project_name}.zip"
    existing_zip.write_bytes(b"old zip placeholder")

    result = packer.json2file(
        file_map={"x.txt": "new\n"},
        file_path=str(file_path),
        output_path=str(out_path),
        project_name=project_name,
    )
    zip_path = Path(result["zip_path"])
    assert zip_path.exists()
    assert zip_path.read_bytes() != b"old zip placeholder"
    assert f"{project_name}/x.txt" in _zip_namelist(zip_path)


@pytest.mark.parametrize(
    "bad_project_name",
    ["", "a/b", r"a\b", "..", "demo..", "de..mo"],
)
def test_json2file_rejects_bad_project_name(tmp_path: Path, packer, bad_project_name: str):
    file_path = tmp_path / "work"
    out_path = tmp_path / "out"

    with pytest.raises(FilePackError):
        packer.json2file(
            file_map={"a.txt": "x"},
            file_path=str(file_path),
            output_path=str(out_path),
            project_name=bad_project_name,
        )


@pytest.mark.parametrize(
    "bad_key",
    [
        "../evil.txt",
        "..\\evil.txt",
        "/abs/path.txt",
        r"C:\abs\path.txt",
        "dir/../../evil.txt",
    ],
)
def test_json2file_rejects_path_traversal_in_keys(tmp_path: Path, packer, bad_key: str):
    file_path = tmp_path / "work"
    out_path = tmp_path / "out"

    with pytest.raises(FilePackError):
        packer.json2file(
            file_map={bad_key: "boom"},
            file_path=str(file_path),
            output_path=str(out_path),
            project_name="safe",
        )


def test_json2file_rejects_non_string_values(tmp_path: Path, packer):
    file_path = tmp_path / "work"
    out_path = tmp_path / "out"

    with pytest.raises(FilePackError):
        packer.json2file(
            file_map={"a.txt": 123},  # type: ignore
            file_path=str(file_path),
            output_path=str(out_path),
            project_name="p",
        )


def test_json2file_rejects_invalid_json(tmp_path: Path, packer):
    file_path = tmp_path / "work"
    out_path = tmp_path / "out"

    with pytest.raises(FilePackError):
        packer.json2file(
            file_map="{not valid json}",
            file_path=str(file_path),
            output_path=str(out_path),
            project_name="p",
        )


def test_file2storage_returns_file_url(tmp_path: Path, packer):
    f = tmp_path / "a.zip"
    f.write_bytes(b"abc")

    result = packer.file2storage(str(f))
    assert "url" in result
    assert result["url"].startswith("file://")


def test_file2storage_raises_when_missing(tmp_path: Path, packer):
    missing = tmp_path / "missing.zip"
    with pytest.raises(StorageError):
        packer.file2storage(str(missing))
