from __future__ import annotations

import pymupdf

from knittingchart.models import ChartSegment, MergedChart
from knittingchart.pdf_pages import chart_page_indices
from knittingchart.vector_grid import assign_row_numbers, extract_grid_from_page


def merge_segments(
    segments: list[ChartSegment],
    *,
    title: str,
    source_name: str,
    chart_id: str,
) -> MergedChart:
    assign_row_numbers(segments)
    rows: list[list[int]] = []
    row_numbers: list[int] = []
    cols = segments[0].col_count if segments else 0

    for seg in segments:
        if seg.col_count != cols:
            raise ValueError(
                f"{seg.name}: expected {cols} columns, got {seg.col_count}"
            )
        for offset, row in enumerate(seg.rows):
            rows.append(row)
            row_numbers.append(seg.first_row + offset)

    return MergedChart(
        title=title,
        source_name=source_name,
        chart_id=chart_id,
        cols=cols,
        segments=segments,
        rows=rows,
        row_numbers=row_numbers,
    )


def extract_from_document(doc: pymupdf.Document) -> list[ChartSegment]:
    indices = chart_page_indices(doc)
    if not indices:
        raise ValueError("No chart pages found in PDF")
    segments: list[ChartSegment] = []
    for idx in indices:
        segments.append(extract_grid_from_page(doc[idx], idx))
    return segments
