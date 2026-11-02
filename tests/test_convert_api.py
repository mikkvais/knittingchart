import pytest
from fastapi.testclient import TestClient

from knittingchart.server import app


@pytest.fixture
def client():
    return TestClient(app)


def test_index(client):
    res = client.get("/")
    assert res.status_code == 200
    assert "Knitting chart converter" in res.text


def test_convert_api(client, sample_pdf_path):
    with sample_pdf_path.open("rb") as f:
        res = client.post(
            "/api/convert",
            files={"file": ("sample_chart.pdf", f, "application/pdf")},
        )
    assert res.status_code == 200
    assert "text/html" in res.headers.get("content-type", "")
    assert "attachment" in res.headers.get("content-disposition", "").lower()
    assert "rowCount" in res.text


def test_convert_api_simple(client, sample_pdf_path):
    with sample_pdf_path.open("rb") as f:
        res = client.post(
            "/api/convert",
            data={"simplified": "true"},
            files={"file": ("sample_chart.pdf", f, "application/pdf")},
        )
    assert res.status_code == 200
    assert "simple.html" in res.headers.get("content-disposition", "").lower()
    assert "<canvas" in res.text
    assert len(res.content) < 200_000


def test_convert_rejects_non_pdf(client):
    res = client.post(
        "/api/convert",
        files={"file": ("x.txt", b"hello", "text/plain")},
    )
    assert res.status_code == 400
