from __future__ import annotations

import argparse
import sys
import webbrowser
from pathlib import Path

import uvicorn


def main(argv: list[str] | None = None) -> None:
    argv = argv if argv is not None else sys.argv[1:]
    parser = argparse.ArgumentParser(prog="knittingchart")
    sub = parser.add_subparsers(dest="command")

    serve = sub.add_parser("serve", help="Start local converter UI (default)")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8765)
    serve.add_argument(
        "--no-open-browser",
        action="store_true",
        help="Do not open the browser automatically",
    )

    convert = sub.add_parser("convert", help="Convert a PDF to standalone HTML")
    convert.add_argument("pdf", type=Path)
    convert.add_argument("-o", "--output", type=Path, required=True)
    convert.add_argument(
        "--simple",
        action="store_true",
        help="E-reader friendly HTML (canvas viewer sized for Kobo; use with HTML output)",
    )
    convert.add_argument(
        "--format",
        choices=("html", "kchart"),
        default="html",
        help="Output format (default: html)",
    )
    convert.add_argument(
        "--json",
        action="store_const",
        const="kchart",
        dest="format",
        help="Alias for --format kchart",
    )

    args = parser.parse_args(argv)
    command = args.command or "serve"

    if command == "serve":
        host = getattr(args, "host", "127.0.0.1")
        port = getattr(args, "port", 8765)
        no_open = getattr(args, "no_open_browser", False)
        url = f"http://{host}:{port}/"
        if not no_open:
            webbrowser.open(url)
        uvicorn.run(
            "knittingchart.server:app",
            host=host,
            port=port,
            reload=False,
        )
    elif command == "convert":
        from knittingchart.convert import convert_pdf

        result = convert_pdf(
            args.pdf,
            simplified=getattr(args, "simple", False),
            output_format=args.format,
        )
        args.output.write_text(result.html, encoding="utf-8")
        print(
            f"Wrote {args.output} ({result.chart.row_count} rows × {result.chart.cols} sts, "
            f"{args.format})"
        )
    else:
        parser.error(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
