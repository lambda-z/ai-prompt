from __future__ import annotations

"""可选：当你不想调用 LLM 时，提供一个确定性的模板输出。

你可以在 planner_node 中检测 OPENAI_API_KEY 是否存在，若不存在则返回这个模板。
"""


def deterministic_file_map(package_name: str) -> dict[str, str]:
    pkg = package_name
    return {
        "README.md": f"# {pkg}\n\nA tiny package that provides greet(name) -> str.\n\n## Install\n\n```bash\npip install .\n```\n\n## Usage\n\n```python\nfrom {pkg} import greet\nprint(greet('World'))\n```\n",
        "LICENSE": "MIT License\n\nCopyright (c) 2026\n\nPermission is hereby granted, free of charge, to any person obtaining a copy...\n",
        "MANIFEST.in": "include README.md\ninclude LICENSE\ninclude MANIFEST.in\nrecursive-include src *.py\nrecursive-include tests *.py\n",
        "setup.py": (
            "from setuptools import setup, find_packages\n\n"
            "setup(\n"
            f"    name='{pkg}',\n"
            "    version='0.1.0',\n"
            "    package_dir={'': 'src'},\n"
            "    packages=find_packages(where='src'),\n"
            "    include_package_data=True,\n"
            "    python_requires='>=3.10',\n"
            ")\n"
        ),
        f"src/{pkg}/__init__.py": (
            "def greet(name: str) -> str:\n"
            "    return f'Hello, {name}!'\n"
        ),
        "tests/test_greet.py": (
            f"from {pkg} import greet\n\n"
            "def test_greet():\n"
            "    assert greet('World') == 'Hello, World!'\n"
        ),
    }
