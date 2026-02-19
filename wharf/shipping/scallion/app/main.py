import argparse
import os
from dotenv import load_dotenv

from generator.graph import build_graph


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate a pip-installable Python package using LangGraph.")
    p.add_argument("--out", default="./out", help="Output root directory")
    p.add_argument("--name", default="greet_package", help="Package name")
    p.add_argument(
        "--request",
        default="请生成一个最小可安装的 python 包，提供 greet(name: str) -> str，返回 'Hello, {name}!'，并包含测试、README、LICENSE、MANIFEST.in、setup.py。",
        help="User request to inject into prompt",
    )
    return p.parse_args()


def main() -> None:
    load_dotenv()

    args = parse_args()
    os.makedirs(args.out, exist_ok=True)

    graph = build_graph()

    result = graph.invoke(
        {
            "user_input": args.request,
            "output_root": os.path.abspath(args.out),
            "package_name": args.name,
            "revision_count": 0,
            "last_error": "",
        }
    )

    print(result.get("response", "(no response)"))


if __name__ == "__main__":
    main()
