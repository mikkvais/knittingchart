# Knitting chart converter

Convert knitting chart PDFs into **standalone HTML** or **`.kchart` JSON** with row-by-row reading aids (highlighted row, muted other rows, odd/even color invert for double knitting).

Licensed under the [MIT License](LICENSE).

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Run the converter UI

```bash
python -m knittingchart serve
```

Open http://127.0.0.1:8765/, choose your PDF, click **Convert**, then download or open the output.

## CLI

```bash
python -m knittingchart convert your-pattern.pdf -o chart.html
```

### E-readers (Kobo + KOReader)

Nickel’s browser is unreliable for chart HTML. Prefer **`.kchart` JSON** and a KOReader plugin (see your plugin repo’s README):

```bash
python -m knittingchart convert your-pattern.pdf -o chart.kchart --format kchart
```

**Simplified HTML** remains for desktop browsers or KOReader’s “Open with → Knitting chart” when available:

```bash
python -m knittingchart convert your-pattern.pdf -o chart-simple.html --simple
```

The web UI can export `.kchart` or simplified HTML. Simplified HTML uses bit-packed data and a canvas grid sized for typical Kobo Elipsa width.

## Tests

Tests use a **synthetic vector grid PDF** generated in `tests/conftest.py` (no bundled commercial patterns). To refresh the optional on-disk copy:

```bash
python -c "from tests.conftest import write_sample_chart_pdf; from pathlib import Path; write_sample_chart_pdf(Path('tests/fixtures/sample_chart.pdf'))"
pytest
```

## Contributing
