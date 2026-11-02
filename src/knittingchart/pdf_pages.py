from __future__ import annotations

import re

import pymupdf


def chart_page_indices(doc: pymupdf.Document) -> list[int]:
    """Return 0-based page indices that contain a knitting grid."""
    indices: list[int] = []
    for i in range(doc.page_count):
        page = doc[i]
        if len(page.get_drawings()) < 1000:
            continue
        text = page.get_text()
        if re.search(r"Chart\s+\d+", text, re.I):
            indices.append(i)
    return indices


def chart_name_from_page(page: pymupdf.Page) -> str:
    text = page.get_text()
    match = re.search(r"Chart\s+(\d+)", text, re.I)
    if match:
        return f"Chart {match.group(1)}"
    return "Chart"
