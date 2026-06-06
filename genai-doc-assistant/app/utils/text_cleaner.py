"""
Text Cleaner — Normalize Extracted Text
=========================================
Cleans up text extracted from documents before chunking and embedding.

Why clean text?
- PDFs often have weird Unicode characters, control characters, and inconsistent whitespace
- CSV/Excel exports may have encoding issues
- Consistent, clean text produces better embeddings (garbage in = garbage out)
"""

import re
import unicodedata


def clean_text(text: str) -> str:
    """Normalize text: fix Unicode, remove control chars, collapse whitespace."""
    # Normalize Unicode (e.g., convert fullwidth chars to ASCII equivalents)
    text = unicodedata.normalize("NFKC", text)
    # Remove control characters (except newlines and tabs)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    # Normalize line endings (Windows CRLF → Unix LF)
    text = re.sub(r"\r\n", "\n", text)
    # Collapse multiple spaces/tabs into a single space
    text = re.sub(r"[ \t]+", " ", text)
    # Collapse 3+ consecutive newlines into 2 (max one blank line)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
