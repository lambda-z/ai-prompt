from generator.runtime.sanitize import validate_file_map


def test_validate_file_map_ok():
    files = {
        "setup.py": "print('x')\n",
        "MANIFEST.in": "include README.md\n",
        "README.md": "# hi\n",
        "LICENSE": "MIT\n",
        "src/greet_package/__init__.py": "def greet(name: str) -> str:\n    return f'Hello, {name}!'\n",
    }
    validate_file_map(files, package_name="greet_package")
