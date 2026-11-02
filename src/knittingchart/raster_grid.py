"""Raster fallback for scanned chart PDFs (not used for vector-first patterns)."""

from __future__ import annotations

import pymupdf

from knittingchart.models import ChartSegment


def extract_grid_raster(page: pymupdf.Page, page_index: int) -> ChartSegment:
    raise NotImplementedError(
        "Raster chart extraction is not implemented; use a vector PDF export"
    )
