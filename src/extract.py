"""Extract per-page text from an earnings-release PDF, in reading order."""

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import pymupdf

# Blocks whose left edge falls in the same 150 pt bucket are treated as one column.
COLUMN_BUCKET = 150

# Running page header, e.g. "3 | DIVULGAÇÃO DE RESULTADOS | 1º TRIMESTRE DE 2026".
HEADER_RE = re.compile(r"^\s*\d+\s*\|\s*DIVULGAÇÃO DE RESULTADOS\s*\|")


@dataclass
class Page:
    page: int  # 1-based
    text: str


def _clean(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.splitlines()).strip()


def extract_pages(pdf_path) -> list[Page]:
    pages = []
    with pymupdf.open(pdf_path) as doc:
        for i, pg in enumerate(doc, start=1):
            blocks = [b for b in pg.get_text("blocks") if b[6] == 0]
            # Reading order: column (bucketed left edge), then top to bottom.
            blocks.sort(key=lambda b: (round(b[0] / COLUMN_BUCKET), b[1]))
            texts = [b[4] for b in blocks if not HEADER_RE.match(b[4])]
            pages.append(Page(i, "\n\n".join(_clean(t) for t in texts)))
    return pages


def save_pages(pages: list[Page], out_path) -> None:
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    data = [{"page": p.page, "text": p.text} for p in pages]
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: python -m src.extract <pdf_path> <out_json>")
    save_pages(extract_pages(sys.argv[1]), sys.argv[2])
