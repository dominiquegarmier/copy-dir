from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Callable
from typing import Generator
from typing import Sequence

import pyperclip
from gitignore_parser import parse_gitignore
from gitignore_parser import parse_gitignore_str

BASE_IGNORE = [
    ".git/",
    ".DS_Store",
]


def crawl_directory(
    dir: Path,
    matchers: Sequence[Callable[[str], bool]],
) -> Generator[Path, None, None]:
    if not dir.is_dir():
        raise ValueError(f"The provided root path '{dir}' is not a directory.")

    matcher_lst = list(matchers)
    ignore_file = dir / ".gitignore"

    if ignore_file.exists():
        matcher_lst.append(parse_gitignore(ignore_file))

    for p in dir.iterdir():
        if p.is_file():
            if not any(m(str(p.absolute())) for m in matcher_lst):
                yield p
        if p.is_dir():
            yield from crawl_directory(p, matcher_lst)


def git_aware_tree(dir: Path) -> Generator[Path, None, None]:
    base_matchers = [parse_gitignore_str("\n".join(BASE_IGNORE), os.getcwd())]
    for p in crawl_directory(dir, base_matchers):
        yield p.absolute()


def jank_file(path: Path) -> list[str]:
    ret = []
    ret.append(f"file: {path.absolute()}")
    with path.open("r", errors="ignore") as f:
        for l in f:
            ret.append(l.rstrip("\n"))
    ret.append("-" * 24)
    return ret


def main() -> int:

    parser = argparse.ArgumentParser(description="Display directory tree structure.")
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to copy (default: current directory)",
    )

    args = parser.parse_args()
    directory = Path(args.directory).resolve()

    lines = []
    for path in git_aware_tree(directory):
        lines.extend(jank_file(path))

    pyperclip.copy("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
