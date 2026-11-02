from __future__ import annotations

from pathlib import Path
from typing import BinaryIO

import pymupdf

from knittingchart.export_html import (
    make_chart_id,
    render_chart_json,
    render_viewer_html,
    suggest_html_filename,
    suggest_kchart_filename,
)
from knittingchart.merge import extract_from_document, merge_segments
from knittingchart.models import HtmlResult


def convert_pdf(
    source: str | Path | bytes | BinaryIO,
    *,
    source_name: str | None = None,
    simplified: bool = False,
    output_format: str = "html",
) -> HtmlResult:
    warnings: list[str] = []

    if isinstance(source, (str, Path)):
        path = Path(source)
        pdf_bytes = path.read_bytes()
        name = source_name or path.name
    elif isinstance(source, bytes):
        pdf_bytes = source
        name = source_name or "pattern.pdf"
    else:
        pdf_bytes = source.read()
        name = source_name or "pattern.pdf"

    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    try:
        segments = extract_from_document(doc)
        title = _title_from_doc(doc, name)
        chart = merge_segments(
            segments,
            title=title,
            source_name=name,
            chart_id="pending",
        )
        chart.chart_id = make_chart_id(name, chart)
    finally:
        doc.close()

    if chart.row_count < 1:
        raise ValueError("Extracted chart has no rows")

    if output_format == "kchart":
        html = render_chart_json(chart, simplified=simplified)
        filename = suggest_kchart_filename(name)
    elif output_format == "html":
        html = render_viewer_html(chart, simplified=simplified)
        filename = suggest_html_filename(name, simplified=simplified)
    else:
        raise ValueError(f"Unknown output format: {output_format}")

    return HtmlResult(html=html, filename=filename, chart=chart, warnings=warnings)


def _title_from_doc(doc: pymupdf.Document, fallback: str) -> str:
    meta = doc.metadata.get("title") or ""
    meta = meta.strip()
    if meta:
        return meta
    stem = Path(fallback).stem.replace("_", " ").replace(".", " ")
    return stem or "Knitting chart"
