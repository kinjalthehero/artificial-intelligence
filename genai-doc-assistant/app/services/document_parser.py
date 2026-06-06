"""
Multi-Format Document Parser (6 formats)
==========================================
Extracts text from uploaded documents in 6 different formats.

Each parser returns a list of {"text": str, "page": int} dicts, where "page" represents
a logical section (actual page for PDFs, sheet for Excel, row group for CSV, etc.).

Library choices:
- PDF:   PyPDF2 — pure Python, no C dependencies (easier Docker builds than PyMuPDF)
- CSV:   pandas — industry standard for tabular data, converts to readable markdown tables
- Excel: pandas + openpyxl — handles .xlsx/.xls, supports multiple sheets
- JSON:  stdlib json — built-in, no extra dependency needed
- YAML:  PyYAML — the standard Python YAML parser, uses safe_load to prevent code execution
- TXT:   stdlib open() — plain text, simplest case
"""

import json
from pathlib import Path

import pandas as pd
import yaml
from PyPDF2 import PdfReader

from app.utils.text_cleaner import clean_text


def extract_text(file_path: str) -> list[dict]:
    """Route to the correct parser based on file extension.

    Returns cleaned text pages. Each page has {"text": str, "page": int}.
    Empty pages are filtered out after cleaning.
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    parsers = {
        ".pdf": _extract_pdf,
        ".txt": _extract_text_file,
        ".csv": _extract_csv,
        ".xlsx": _extract_excel,
        ".xls": _extract_excel,
        ".json": _extract_json,
        ".yaml": _extract_yaml,
        ".yml": _extract_yaml,
    }

    parser = parsers.get(suffix)
    if not parser:
        raise ValueError(f"Unsupported file type: {suffix}")

    pages = parser(path)
    # Clean each page's text (normalize whitespace, strip control chars) and filter empties
    return [{"text": clean_text(p["text"]), "page": p["page"]} for p in pages if p["text"].strip()]


def _extract_pdf(path: Path) -> list[dict]:
    """Extract text from PDF page by page using PyPDF2."""
    pages = []
    reader = PdfReader(str(path))
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if text.strip():
            pages.append({"text": text, "page": i + 1})
    return pages


def _extract_text_file(path: Path) -> list[dict]:
    """Read plain text file as a single page. Uses 'replace' for encoding errors."""
    text = path.read_text(encoding="utf-8", errors="replace").strip()
    if not text:
        return []
    return [{"text": text, "page": 1}]


def _extract_csv(path: Path) -> list[dict]:
    """Convert CSV to readable markdown tables using pandas.

    Large CSVs are split into groups of 50 rows (via _dataframe_to_pages)
    so each chunk is a manageable size for the LLM to process.
    """
    df = pd.read_csv(str(path))
    return _dataframe_to_pages(df)


def _extract_excel(path: Path) -> list[dict]:
    """Extract text from Excel files. Each worksheet becomes a separate "page"
    with a sheet name header, so the LLM knows which sheet data came from.
    """
    pages = []
    xls = pd.ExcelFile(str(path))
    for page_num, sheet_name in enumerate(xls.sheet_names, 1):
        df = pd.read_excel(xls, sheet_name=sheet_name)
        header = f"## Sheet: {sheet_name}\n\n"
        table_text = header + _dataframe_to_text(df)
        if table_text.strip():
            pages.append({"text": table_text, "page": page_num})
    return pages


def _extract_json(path: Path) -> list[dict]:
    """Convert JSON to readable text. Arrays become one page per element;
    objects become a single pretty-printed page.
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        pages = []
        for i, item in enumerate(data):
            text = json.dumps(item, indent=2, ensure_ascii=False)
            pages.append({"text": text, "page": i + 1})
        return pages if pages else []

    text = json.dumps(data, indent=2, ensure_ascii=False)
    return [{"text": text, "page": 1}]


def _extract_yaml(path: Path) -> list[dict]:
    """Convert YAML to readable text. Uses safe_load to prevent arbitrary code execution."""
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if data is None:
        return []

    if isinstance(data, list):
        pages = []
        for i, item in enumerate(data):
            text = yaml.dump(item, default_flow_style=False, allow_unicode=True)
            pages.append({"text": text, "page": i + 1})
        return pages if pages else []

    text = yaml.dump(data, default_flow_style=False, allow_unicode=True)
    return [{"text": text, "page": 1}]


def _dataframe_to_pages(df: pd.DataFrame, rows_per_page: int = 50) -> list[dict]:
    """Split a DataFrame into pages of 50 rows each.

    Each page includes the column names header so the LLM always knows
    what columns exist, even when reading a single chunk.
    50 rows per page keeps chunk sizes manageable for embedding and retrieval.
    """
    pages = []
    columns_header = "Columns: " + ", ".join(df.columns.tolist()) + "\n\n"

    for i in range(0, len(df), rows_per_page):
        chunk = df.iloc[i : i + rows_per_page]
        text = columns_header + _dataframe_to_text(chunk)
        pages.append({"text": text, "page": (i // rows_per_page) + 1})

    if not pages:
        pages.append({"text": columns_header + "(empty dataset)", "page": 1})

    return pages


def _dataframe_to_text(df: pd.DataFrame) -> str:
    """Convert DataFrame to markdown table for readability. Falls back to plain text."""
    try:
        return df.to_markdown(index=False)
    except Exception:
        return df.to_string(index=False)
