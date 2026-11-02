from __future__ import annotations

from collections import Counter

import pymupdf

from knittingchart.models import ChartSegment
from knittingchart.pdf_pages import chart_name_from_page


def _cell_size(drawings: list) -> tuple[float, float]:
    sizes = Counter(
        (round(d["rect"].width, 2), round(d["rect"].height, 2)) for d in drawings
    )
    (cw, ch), count = sizes.most_common(1)[0]
    if count < 100:
        raise ValueError("Could not detect grid cell size on page")
    return cw, ch


def extract_grid_from_page(page: pymupdf.Page, page_index: int) -> ChartSegment:
    drawings = page.get_drawings()
    if not drawings:
        raise ValueError(f"Page {page_index + 1} has no vector drawings")

    cw, ch = _cell_size(drawings)
    by_y: dict[float, list[tuple[float, int]]] = {}
    for d in drawings:
        rect = d["rect"]
        if abs(rect.width - cw) > 0.5 or abs(rect.height - ch) > 0.5:
            continue
        fill = d.get("fill")
        dark = 1 if fill and fill[0] < 0.9 else 0
        y = round(rect.y0, 1)
        by_y.setdefault(y, []).append((rect.x0, dark))

    if not by_y:
        raise ValueError(f"Page {page_index + 1}: no grid cells found")

    row_keys = sorted(by_y.keys(), reverse=True)
    rows: list[list[int]] = []
    for y in row_keys:
        # Same order as printed PDF: stitch 52 on the left, stitch 1 on the right.
        cells = sorted(by_y[y], key=lambda t: t[0])
        rows.append([dark for _, dark in cells])

    if not rows:
        raise ValueError(f"Page {page_index + 1}: no grid rows found")

    col_counts = {len(r) for r in rows}
    if len(col_counts) != 1:
        raise ValueError(
            f"Page {page_index + 1}: inconsistent column counts {col_counts}"
        )

    name = chart_name_from_page(page)
    return ChartSegment(name=name, page_index=page_index, first_row=0, rows=rows)


def assign_row_numbers(segments: list[ChartSegment]) -> None:
    next_row = 1
    for seg in segments:
        seg.first_row = next_row
        next_row += seg.row_count
