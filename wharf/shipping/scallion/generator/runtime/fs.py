from __future__ import annotations

import os

from generator.runtime.sanitize import safe_join


def write_files(base_dir: str, files: dict[str, str]) -> list[str]:
    """Write file map to disk under base_dir. Returns list of written paths."""
    os.makedirs(base_dir, exist_ok=True)
    written: list[str] = []

    for rel_path, content in files.items():
        abs_path = safe_join(base_dir, rel_path)
        parent = os.path.dirname(abs_path)
        os.makedirs(parent, exist_ok=True)
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(content)
        written.append(abs_path)

    return written
