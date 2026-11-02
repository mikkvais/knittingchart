from __future__ import annotations

import base64
import hashlib
import json
import re
from pathlib import Path

from knittingchart.models import MergedChart

_TEMPLATES = Path(__file__).resolve().parent / "templates"


def _pack_rows(chart: MergedChart) -> str:
    """Bit-pack rows (1=dark) into base64 for compact embedding."""
    bits: list[int] = []
    for row in chart.rows:
        for cell in row:
            bits.append(cell)
    if not bits:
        return ""
    pad = (-len(bits)) % 8
    bits.extend([0] * pad)
    out = bytearray()
    for i in range(0, len(bits), 8):
        byte = 0
        for b in bits[i : i + 8]:
            byte = (byte << 1) | b
        out.append(byte)
    return base64.b64encode(bytes(out)).decode("ascii")


def simple_cell_px(cols: int) -> int:
    """Cell size for simplified / Kobo-oriented viewers (exported for tests)."""
    return _simple_cell_px(cols)


def chart_payload(chart: MergedChart) -> dict:
    segments = [
        {
            "name": s.name,
            "firstRow": s.first_row,
            "lastRow": s.last_row,
            "page": s.page_index + 1,
        }
        for s in chart.segments
    ]
    return {
        "cols": chart.cols,
        "rowNumbers": chart.row_numbers,
        "rowCount": chart.row_count,
        "bits": _pack_rows(chart),
        "segments": segments,
    }


# Kobo Elipsa 2E and similar: 1440×1920; leave room for side controls.
_SIMPLE_VIEWPORT_WIDTH = 1440
_SIMPLE_RAIL_PX = 260
_SIMPLE_MARGIN_PX = 16
_SIMPLE_DONE_COL_PX = 28


def _simple_cell_px(cols: int) -> int:
    usable = (
        _SIMPLE_VIEWPORT_WIDTH
        - _SIMPLE_RAIL_PX
        - _SIMPLE_MARGIN_PX
        - _SIMPLE_DONE_COL_PX
    )
    return max(10, min(32, usable // max(cols, 1)))


def kchart_document(chart: MergedChart, *, simplified: bool = True) -> dict:
    """Build the versioned .kchart JSON object."""
    return {
        "format": "knittingchart",
        "version": 1,
        "title": chart.title,
        "chartId": chart.chart_id,
        "cellPx": _simple_cell_px(chart.cols),
        **chart_payload(chart),
    }


def render_chart_json(chart: MergedChart, *, simplified: bool = True) -> str:
    """Serialize a chart as standalone .kchart JSON (UTF-8, trailing newline)."""
    _ = simplified  # cell sizing is always Kobo-oriented for .kchart v1
    return json.dumps(kchart_document(chart), ensure_ascii=False, separators=(",", ":")) + "\n"


def render_viewer_html(chart: MergedChart, *, simplified: bool = False) -> str:
    title = chart.title
    if simplified:
        cell_px = _simple_cell_px(chart.cols)
        template = (_TEMPLATES / "viewer-simple.html").read_text(encoding="utf-8")
        payload = json.dumps(chart_payload(chart), separators=(",", ":"))
        return (
            template.replace("%%TITLE%%", _escape_html(title))
            .replace("%%CHART_ID%%", _escape_js(chart.chart_id))
            .replace("%%CHART_DATA%%", payload)
            .replace("%%CELL_PX%%", str(cell_px))
            .replace("%%RAIL_PX%%", str(_SIMPLE_RAIL_PX))
        )
    template = (_TEMPLATES / "viewer.html").read_text(encoding="utf-8")
    payload = json.dumps(chart_payload(chart), separators=(",", ":"))
    return (
        template.replace("%%TITLE%%", _escape_html(title))
        .replace("%%CHART_ID%%", _escape_js(chart.chart_id))
        .replace("%%CHART_DATA%%", payload)
    )


def render_converter_page() -> str:
    return (_TEMPLATES / "converter.html").read_text(encoding="utf-8")


def _escape_html(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _escape_js(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')


def suggest_kchart_filename(source_name: str) -> str:
    stem = Path(source_name).stem or "knitting-chart"
    safe = re.sub(r"[^\w\-]+", "-", stem).strip("-").lower()
    base = safe or "knitting-chart"
    return f"{base}.kchart"


def suggest_html_filename(source_name: str, *, simplified: bool = False) -> str:
    stem = Path(source_name).stem or "knitting-chart"
    safe = re.sub(r"[^\w\-]+", "-", stem).strip("-").lower()
    base = safe or "knitting-chart"
    if simplified:
        return f"{base}-simple.html"
    return f"{base}.html"


def make_chart_id(source_name: str, chart: MergedChart) -> str:
    raw = f"{source_name}|{chart.cols}|{chart.row_count}|{chart.row_numbers[0]}|{chart.row_numbers[-1]}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]
