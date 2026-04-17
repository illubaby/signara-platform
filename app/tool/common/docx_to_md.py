#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import zipfile
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree as ET


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
XML_NS = {"w": W_NS}


def qn(tag: str) -> str:
    return f"{{{W_NS}}}{tag}"


def load_xml_from_docx(docx_path: Path, inner_path: str) -> ET.Element:
    with zipfile.ZipFile(docx_path, "r") as archive:
        xml_bytes = archive.read(inner_path)
    return ET.fromstring(xml_bytes)


def load_style_map(docx_path: Path) -> dict[str, str]:
    """Map style IDs to human-readable style names from styles.xml."""
    try:
        styles_root = load_xml_from_docx(docx_path, "word/styles.xml")
    except KeyError:
        return {}

    style_map: dict[str, str] = {}
    for style in styles_root.findall("w:style", XML_NS):
        style_id = style.get(qn("styleId"))
        name_node = style.find("w:name", XML_NS)
        style_name = name_node.get(qn("val")) if name_node is not None else None
        if style_id and style_name:
            style_map[style_id] = style_name
    return style_map


def collapse_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def iter_run_texts(paragraph: ET.Element) -> Iterable[str]:
    for run in paragraph.findall("w:r", XML_NS):
        text_nodes = run.findall("w:t", XML_NS)
        text = "".join(node.text or "" for node in text_nodes)

        if not text:
            if run.find("w:tab", XML_NS) is not None:
                yield "\t"
            elif run.find("w:br", XML_NS) is not None:
                yield "\n"
            continue

        rpr = run.find("w:rPr", XML_NS)
        is_bold = rpr is not None and rpr.find("w:b", XML_NS) is not None
        is_italic = rpr is not None and rpr.find("w:i", XML_NS) is not None

        if is_bold and is_italic:
            yield f"***{text}***"
        elif is_bold:
            yield f"**{text}**"
        elif is_italic:
            yield f"*{text}*"
        else:
            yield text


def paragraph_style_name(paragraph: ET.Element, style_map: dict[str, str]) -> str:
    ppr = paragraph.find("w:pPr", XML_NS)
    if ppr is None:
        return ""

    pstyle = ppr.find("w:pStyle", XML_NS)
    if pstyle is None:
        return ""

    style_id = pstyle.get(qn("val"), "")
    return style_map.get(style_id, style_id)


def paragraph_is_list(paragraph: ET.Element) -> bool:
    ppr = paragraph.find("w:pPr", XML_NS)
    if ppr is None:
        return False
    return ppr.find("w:numPr", XML_NS) is not None


def heading_level(style_name: str) -> int | None:
    match = re.match(r"Heading\s*(\d+)$", style_name, flags=re.IGNORECASE)
    if not match:
        return None
    level = int(match.group(1))
    return max(1, min(level, 6))


def convert_table(tbl: ET.Element) -> list[str]:
    rows: list[list[str]] = []
    for tr in tbl.findall("w:tr", XML_NS):
        cells: list[str] = []
        for tc in tr.findall("w:tc", XML_NS):
            p_texts: list[str] = []
            for p in tc.findall("w:p", XML_NS):
                text = collapse_ws("".join(iter_run_texts(p)))
                if text:
                    p_texts.append(text)
            cells.append(" ".join(p_texts))
        rows.append(cells)

    if not rows:
        return []

    max_cols = max(len(r) for r in rows)
    normalized = [r + [""] * (max_cols - len(r)) for r in rows]

    lines: list[str] = []
    header = normalized[0]
    lines.append("| " + " | ".join(header) + " |")
    lines.append("| " + " | ".join(["---"] * max_cols) + " |")
    for row in normalized[1:]:
        lines.append("| " + " | ".join(row) + " |")
    return lines


def convert_docx_to_markdown(docx_path: Path) -> str:
    style_map = load_style_map(docx_path)
    document_root = load_xml_from_docx(docx_path, "word/document.xml")
    body = document_root.find("w:body", XML_NS)
    if body is None:
        return ""

    md_lines: list[str] = []

    for node in body:
        if node.tag == qn("p"):
            style_name = paragraph_style_name(node, style_map)
            text = collapse_ws("".join(iter_run_texts(node)))
            if not text:
                continue

            h_level = heading_level(style_name)
            if h_level is not None:
                md_lines.append(f"{'#' * h_level} {text}")
                md_lines.append("")
                continue

            if paragraph_is_list(node):
                md_lines.append(f"- {text}")
                continue

            md_lines.append(text)
            md_lines.append("")

        elif node.tag == qn("tbl"):
            table_lines = convert_table(node)
            if table_lines:
                md_lines.extend(table_lines)
                md_lines.append("")

    # Trim trailing blank lines.
    while md_lines and md_lines[-1] == "":
        md_lines.pop()

    return "\n".join(md_lines) + ("\n" if md_lines else "")


def convert_one_file(docx_path: Path, output_path: Path) -> Path:
    markdown = convert_docx_to_markdown(docx_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")
    return output_path


def collect_docx_files(input_dir: Path, recursive: bool = False) -> list[Path]:
    pattern = "**/*.docx" if recursive else "*.docx"
    return sorted(path for path in input_dir.glob(pattern) if path.is_file())


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Convert .docx to Markdown (.md).\n"
            "Supports single-file conversion and batch folder conversion."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python tool/common/docx_to_md.py input.docx\n"
            "  python tool/common/docx_to_md.py input.docx -o out.md\n"
            "  python tool/common/docx_to_md.py input_folder output_folder\n"
            "  python tool/common/docx_to_md.py input_folder output_folder --recursive"
        ),
    )
    parser.add_argument(
        "input_path",
        type=Path,
        help="Path to input .docx file or input folder containing .docx files",
    )
    parser.add_argument(
        "output_path",
        nargs="?",
        type=Path,
        default=None,
        help="Output .md file path (file mode) or output folder path (folder mode)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Optional output path override (same meaning as output_path positional)",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="When input_path is a folder, include .docx files recursively",
    )
    return parser


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()

    input_path: Path = args.input_path
    output_override: Path | None = args.output
    output_path_arg: Path | None = args.output_path

    if not input_path.exists():
        raise FileNotFoundError(f"Input path not found: {input_path}")

    # Use --output if given, otherwise fallback to positional output_path.
    chosen_output = output_override if output_override is not None else output_path_arg

    if input_path.is_file():
        if input_path.suffix.lower() != ".docx":
            raise ValueError(f"Expected a .docx file, got: {input_path}")

        output_file = chosen_output or input_path.with_suffix(".md")
        converted = convert_one_file(input_path, output_file)
        print(f"Converted: {input_path}")
        print(f"Output   : {converted}")
        return 0

    if not input_path.is_dir():
        raise ValueError(f"Input path is neither a file nor directory: {input_path}")

    if chosen_output is None:
        raise ValueError(
            "For folder input, provide an output folder as the 2nd positional argument "
            "or with -o/--output"
        )

    output_dir = chosen_output
    output_dir.mkdir(parents=True, exist_ok=True)

    docx_files = collect_docx_files(input_path, recursive=args.recursive)
    if not docx_files:
        print(f"No .docx files found in: {input_path}")
        return 0

    print(f"Found {len(docx_files)} .docx file(s)")
    for docx_file in docx_files:
        out_file = output_dir / f"{docx_file.stem}.md"
        convert_one_file(docx_file, out_file)
        print(f"Converted: {docx_file} -> {out_file}")

    print(f"Done. Wrote {len(docx_files)} Markdown file(s) to: {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())