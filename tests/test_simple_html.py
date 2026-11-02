import pytest

from knittingchart.convert import convert_pdf
from knittingchart.export_html import simple_cell_px


@pytest.fixture(scope="module")
def simple(sample_pdf_path):
    return convert_pdf(sample_pdf_path, simplified=True)


def test_simple_filename(simple):
    assert simple.filename.endswith("-simple.html")


def test_simple_uses_compact_canvas_not_dom_grid(simple):
    assert "<canvas" in simple.html
    assert '"bits"' in simple.html
    assert '<table class="chart"' not in simple.html
    assert len(simple.html.encode("utf-8")) < 200_000


def test_simple_cell_size_for_kobo(simple, sample_chart_dims):
    cols, rows, _ = sample_chart_dims
    assert f"var CELL = {simple_cell_px(cols)}" in simple.html
    assert simple.chart.row_count == rows


def test_simple_html_row_done_markers(simple):
    assert "doneRows" in simple.html
    assert "DONE_COL" in simple.html
    assert "toggleRowDone" in simple.html
