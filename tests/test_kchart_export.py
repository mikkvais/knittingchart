import base64
import json
import re

import pytest

from knittingchart.convert import convert_pdf
from knittingchart.export_html import render_chart_json, simple_cell_px


@pytest.fixture(scope="module")
def kchart_result(sample_pdf_path):
    return convert_pdf(sample_pdf_path, output_format="kchart")


@pytest.fixture(scope="module")
def simple_html(sample_pdf_path):
    return convert_pdf(sample_pdf_path, simplified=True)


def test_kchart_filename(kchart_result):
    assert kchart_result.filename.endswith(".kchart")


def test_kchart_schema_and_dimensions(kchart_result, sample_chart_dims):
    cols, rows, seg_count = sample_chart_dims
    doc = json.loads(kchart_result.html)
    assert doc["format"] == "knittingchart"
    assert doc["version"] == 1
    assert doc["cols"] == cols
    assert doc["rowCount"] == rows
    assert doc["rowNumbers"][0] == 1
    assert doc["rowNumbers"][-1] == rows
    assert doc["cellPx"] == simple_cell_px(cols)
    assert len(doc["segments"]) == seg_count
    assert doc["chartId"] == kchart_result.chart.chart_id
    assert doc["title"]


def test_kchart_bits_length(kchart_result):
    doc = json.loads(kchart_result.html)
    raw = base64.b64decode(doc["bits"])
    bit_count = len(raw) * 8
    assert bit_count >= doc["rowCount"] * doc["cols"]
    assert bit_count < doc["rowCount"] * doc["cols"] + 8


def test_kchart_bits_match_simple_html(simple_html, kchart_result):
    html_bits = re.search(r'"bits":"([^"]+)"', simple_html.html)
    assert html_bits
    doc = json.loads(kchart_result.html)
    assert doc["bits"] == html_bits.group(1)


def test_simple_cell_px_52_columns():
    assert simple_cell_px(52) == 21


def test_render_chart_json_roundtrip(kchart_result, sample_chart_dims):
    _cols, rows, _ = sample_chart_dims
    doc = json.loads(render_chart_json(kchart_result.chart))
    assert doc["rowCount"] == rows
