import pytest

from knittingchart.convert import convert_pdf


@pytest.fixture(scope="module")
def converted(sample_pdf_path):
    return convert_pdf(sample_pdf_path)


def test_finds_chart_segment(converted, sample_chart_dims):
    _cols, _rows, seg_count = sample_chart_dims
    assert len(converted.chart.segments) == seg_count


def test_chart_one_dimensions(converted, sample_chart_dims):
    cols, rows, _ = sample_chart_dims
    seg = converted.chart.segments[0]
    assert seg.name == "Chart 1"
    assert seg.row_count == rows
    assert seg.col_count == cols
    assert seg.first_row == 1


def test_merged_row_count(converted, sample_chart_dims):
    cols, rows, _ = sample_chart_dims
    assert converted.chart.cols == cols
    assert converted.chart.row_count == rows
    assert converted.chart.row_numbers[0] == 1
    assert converted.chart.row_numbers[-1] == rows


def test_html_contains_viewer_markers(converted):
    assert "knittingchart:" in converted.html
    assert "%%CHART_DATA%%" not in converted.html
    assert '"rowCount"' in converted.html
