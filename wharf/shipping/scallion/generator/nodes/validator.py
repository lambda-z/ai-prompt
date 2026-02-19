from __future__ import annotations

import json
from typing import Any

from generator.state import GraphState
from generator.runtime.sanitize import validate_file_map


def _strip_fences(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        # 简易处理：去掉开头/结尾 fence
        t = t.strip("`")
        # 可能是 json\n...
        if t.startswith("json\n"):
            t = t[5:]
        t = t.strip()
    return t


def validator_node(state: GraphState) -> GraphState:
    raw = state.get("raw_json_text", "")

    try:
        raw = _strip_fences(raw)
        parsed: Any = json.loads(raw)
        if not isinstance(parsed, dict):
            raise ValueError("Top-level JSON must be an object mapping file paths to string contents")

        # 强约束：所有 value 必须是字符串
        files: dict[str, str] = {}
        for k, v in parsed.items():
            if not isinstance(k, str):
                raise ValueError("All keys must be strings (file paths)")
            if not isinstance(v, str):
                raise ValueError(f"File content for {k} must be a string")
            files[k] = v

        # 基本安全检查 + 必要文件检查
        validate_file_map(files, package_name=state.get("package_name", "greet_package"))

        return {**state, "files": files, "last_error": ""}

    except Exception as e:
        return {**state, "last_error": f"{type(e).__name__}: {e}"}
