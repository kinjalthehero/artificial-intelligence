import json
from pathlib import Path

import pandas as pd
import yaml
from PyPDF2 import PdfReader

from app.utils.text_cleaner import clean_text


def extract_text(file_path: str) -> list[dict]:
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
    return [{"text": clean_text(p["text"]), "page": p["page"]} for p in pages if p["text"].strip()]


def _extract_pdf(path: Path) -> list[dict]:
    pages = []
    reader = PdfReader(str(path))
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if text.strip():
            pages.append({"text": text, "page": i + 1})
    return pages


def _extract_text_file(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8", errors="replace").strip()
    if not text:
        return []
    return [{"text": text, "page": 1}]


def _extract_csv(path: Path) -> list[dict]:
    df = pd.read_csv(str(path))
    return _dataframe_to_pages(df)


def _extract_excel(path: Path) -> list[dict]:
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
    try:
        return df.to_markdown(index=False)
    except Exception:
        return df.to_string(index=False)
