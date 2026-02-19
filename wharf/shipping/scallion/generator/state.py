from __future__ import annotations

from typing import TypedDict, Optional


class GraphState(TypedDict, total=False):
    # inputs
    user_input: str
    output_root: str
    package_name: str

    # planner
    prompt_text: str
    raw_json_text: str

    # validator
    files: dict[str, str]
    last_error: str
    revision_count: int

    # executor
    generated_dir: str
    written_files: list[str]

    # final
    response: str
