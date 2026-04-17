#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


def collect_files(input_dir: Path, recursive: bool) -> list[Path]:
    pattern = "**/*" if recursive else "*"
    return sorted(path for path in input_dir.glob(pattern) if path.is_file())


def read_text_with_fallback(path: Path) -> str | None:
    """Read text files safely; return None for likely binary files."""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            return path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            return None


def merge_folder_files(
    input_dir: Path,
    output_file: Path,
    recursive: bool = False,
) -> tuple[int, int]:
    files = collect_files(input_dir, recursive)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    merged_count = 0
    skipped_count = 0

    with output_file.open("w", encoding="utf-8", newline="\n") as out:
        for file_path in files:
            text = read_text_with_fallback(file_path)
            if text is None:
                skipped_count += 1
                continue

            rel_name = file_path.relative_to(input_dir).as_posix()
            out.write(f"{rel_name}\n")
            out.write("<content>\n")
            out.write(text)
            if text and not text.endswith("\n"):
                out.write("\n")
            out.write("\n")
            merged_count += 1

    return merged_count, skipped_count


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Read all files in a folder and merge them into one output file.\n"
            "Each section starts with file name and a <content> marker."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python tool/common/merge_folder_files.py input_folder output.md\n"
            "  python tool/common/merge_folder_files.py input_folder output.md --recursive"
        ),
    )
    parser.add_argument("input_dir", type=Path, help="Folder containing files to merge")
    parser.add_argument("output_file", type=Path, help="Output merged file path")
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Include files from subfolders recursively",
    )
    return parser


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()

    if not args.input_dir.exists():
        raise FileNotFoundError(f"Input folder not found: {args.input_dir}")
    if not args.input_dir.is_dir():
        raise ValueError(f"Input path is not a folder: {args.input_dir}")

    merged_count, skipped_count = merge_folder_files(
        args.input_dir,
        args.output_file,
        recursive=args.recursive,
    )

    print(f"Merged {merged_count} file(s) into: {args.output_file}")
    if skipped_count:
        print(f"Skipped {skipped_count} file(s) (likely binary/non-UTF text)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())