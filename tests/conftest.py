"""Shared pytest fixtures (synthetic chart PDF — no copyrighted patterns)."""

from __future__ import annotations

from pathlib import Path

import pymupdf
import pytest

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"

# Must match chart_page_indices(): >= 1000 grid rects and "Chart N" label.
_SAMPLE_COLS = 52
_SAMPLE_ROWS = 20


def write_sample_chart_pdf(path: Path) -> None:
    """Write a minimal vector grid PDF for integration tests."""
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open()
    page = doc.new_page(width=500, height=400)
    page.insert_text((16, 22), "Chart 1", fontsize=12)
    cell = 8.0
    x0, y0 = 16.0, 32.0
    for ri in range(_SAMPLE_ROWS):
        for ci in range(_SAMPLE_COLS):
            x = x0 + ci * cell
            y = y0 + ri * cell
            dark = (ri + ci) % 2 == 0
            fill = (0.15, 0.15, 0.15) if dark else (1.0, 1.0, 1.0)
            rect = pymupdf.Rect(x, y, x + cell, y + cell)
            page.draw_rect(rect, color=fill, fill=fill, width=0)
    doc.save(str(path))
    doc.close()


@pytest.fixture(scope="session")
def sample_pdf_path(tmp_path_factory: pytest.TempPathFactory) -> Path:
    cached = FIXTURES_DIR / "sample_chart.pdf"
    if cached.is_file():
        return cached
    path = tmp_path_factory.mktemp("pdf") / "sample_chart.pdf"
    write_sample_chart_pdf(path)
    return path


@pytest.fixture(scope="session")
def sample_chart_dims() -> tuple[int, int, int]:
    """cols, row_count, segment_count for sample_chart.pdf."""
    return _SAMPLE_COLS, _SAMPLE_ROWS, 1
