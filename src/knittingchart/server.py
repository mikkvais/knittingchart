from __future__ import annotations

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, Response

from knittingchart.convert import convert_pdf
from knittingchart.export_html import render_converter_page

app = FastAPI(title="Knitting Chart Converter", version="0.1.0")


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    return HTMLResponse(render_converter_page())


@app.post("/api/convert")
async def api_convert(
    file: UploadFile = File(...),
    simplified: str = Form(default="false"),
    output_format: str = Form(default="html"),
) -> Response:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF file.")

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    use_simple = simplified.lower() in ("1", "true", "yes", "on")
    fmt = output_format.lower()
    if fmt not in ("html", "kchart"):
        raise HTTPException(status_code=400, detail="output_format must be html or kchart")
    try:
        result = convert_pdf(
            data,
            source_name=file.filename,
            simplified=use_simple,
            output_format=fmt,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Conversion failed: {exc}",
        ) from exc

    media_type = (
        "application/json; charset=utf-8"
        if fmt == "kchart"
        else "text/html; charset=utf-8"
    )
    return Response(
        content=result.html.encode("utf-8"),
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{result.filename}"',
        },
    )
