"""Extract text from PDF, TXT, and Markdown files."""

from pathlib import Path

import fitz  # PyMuPDF


def extract_text(file_path: str) -> list[dict]:
    """Return a list of {'text': ..., 'page': ...} dicts from the file.

    For PDFs each page is a separate entry; for text/markdown the whole
    file is one entry with page=1.
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return _extract_pdf(path)
    elif suffix in (".txt", ".md", ".markdown"):
        return _extract_text_file(path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")


def _extract_pdf(path: Path) -> list[dict]:
    pages = []
    with fitz.open(str(path)) as doc:
        for i, page in enumerate(doc):
            text = page.get_text().strip()
            if text:
                pages.append({"text": text, "page": i + 1})
    return pages


def _extract_text_file(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8", errors="replace").strip()
    if not text:
        return []
    return [{"text": text, "page": 1}]
