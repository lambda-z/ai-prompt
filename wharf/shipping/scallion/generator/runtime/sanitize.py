from __future__ import annotations

import os


_REQUIRED_FILES = {
    "setup.py",
    "MANIFEST.in",
    "README.md",
    "LICENSE",
}


def safe_join(base_dir: str, rel_path: str) -> str:
    """Prevent path traversal; return absolute safe path."""
    base_abs = os.path.abspath(base_dir)
    target_abs = os.path.abspath(os.path.join(base_abs, rel_path))

    if target_abs == base_abs:
        raise ValueError("Invalid path: points to base directory")

    # Must stay inside base_dir
    if not (target_abs.startswith(base_abs + os.sep)):
        raise ValueError(f"Path traversal detected: {rel_path}")

    return target_abs


def validate_file_map(files: dict[str, str], package_name: str) -> None:
    """Basic structural checks for a pip-installable package."""
    missing = [f for f in _REQUIRED_FILES if f not in files]
    if missing:
        raise ValueError(f"Missing required top-level files: {missing}")

    # Must include package module init
    init_candidates = [
        f"{package_name}/__init__.py",
        f"src/{package_name}/__init__.py",
    ]
    if not any(p in files for p in init_candidates):
        raise ValueError(
            "Missing __init__.py. Expected one of: " + ", ".join(init_candidates)
        )

    # Minimal greet function presence check (soft)
    init_path = next((p for p in init_candidates if p in files), None)
    if init_path and "greet" not in files[init_path]:
        raise ValueError("__init__.py does not appear to define or export greet")

    # Prevent absolute paths
    for path in files.keys():
        if os.path.isabs(path):
            raise ValueError(f"Absolute paths are not allowed: {path}")
        if "\x00" in path:
            raise ValueError("NUL byte in path")
