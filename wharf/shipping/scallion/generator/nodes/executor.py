from __future__ import annotations

import os

from generator.state import GraphState
from generator.runtime.fs import write_files


def executor_node(state: GraphState) -> GraphState:
    files = state.get("files", {})
    output_root = state["output_root"]
    package_name = state.get("package_name", "greet_package")

    target_dir = os.path.join(output_root, package_name)
    written = write_files(target_dir, files)

    return {
        **state,
        "generated_dir": target_dir,
        "written_files": written,
    }
