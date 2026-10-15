"""Validate an LLM extraction against the release's page text.

Every finding must be traceable to a verbatim quote on a given page, and every
number is checked by code against that quote, never by the LLM. Items that fail
are flagged (verified=False + issues), never deleted.
"""

import json
import re
from pathlib import Path

from src.extract import Page
from src.schemas import GuidanceItem, Quote, ReleaseExtraction

_SOFT_HYPHEN_RE = re.compile("­\\s*")
# Real hyphen broken at line end: "norte-\namericanos" -> "norte-americanos".
_LINE_HYPHEN_RE = re.compile(r"(?<=[^\W\d_])-\n(?=[a-zà-ÿ])")
_QUOTES = str.maketrans({"“": '"', "”": '"', "‘": "'", "’": "'", "–": "-", "—": "-", " ": " "})
# Either a parenthesized number "(2,4)" or a number with optional sign, which
# only counts as a sign when not glued to a preceding word character.
_NUMBER_RE = re.compile(r"\(\s*\d+(?:[.,]\d+)*\s*\)|(?:(?<!\w)[-+])?\d+(?:[.,]\d+)*")


def load_pages(json_path) -> list[Page]:
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))
    return [Page(d["page"], d["text"]) for d in data]


def normalize(text: str) -> str:
    text = _SOFT_HYPHEN_RE.sub("", text)
    text = _LINE_HYPHEN_RE.sub("-", text)
    text = text.translate(_QUOTES)
    return re.sub(r"\s+", " ", text).strip()


def _page_text(page: int, pages: list[Page]) -> str | None:
    for p in pages:
        if p.page == page:
            return normalize(p.text)
    return None


def quote_found(quote: Quote, pages: list[Page]) -> bool:
    text = _page_text(quote.page, pages)
    return text is not None and normalize(quote.text) in text


def parse_br_number(token: str) -> float:
    negative = "(" in token or "-" in token
    s = re.sub(r"[^\d.,]", "", token)
    # A dot followed by exactly 3 digits is a thousands separator; any other dot
    # is decimal (the PDF itself mixes "5.6%" with "6,4%"). Comma is always decimal.
    s = re.sub(r"\.(?=\d{3}(?!\d))", "", s).replace(",", ".")
    value = float(s)
    return -value if negative else value


def numbers_in(text: str) -> list[float]:
    return [parse_br_number(m.group()) for m in _NUMBER_RE.finditer(text)]


def check_guidance(item: GuidanceItem, pages: list[Page]) -> list[str]:
    issues = []
    if not quote_found(item.quote, pages):
        issues.append("quote_not_found")
    quote_numbers = numbers_in(item.quote.text)
    for value in (item.low, item.high):
        if value is not None and not any(abs(value - n) <= 1e-9 for n in quote_numbers):
            issues.append(f"number_not_in_quote: {value:g}")
    if item.perimeter is not None:
        page_text = _page_text(item.quote.page, pages) or ""
        if normalize(item.perimeter).lower() not in page_text.lower():
            issues.append(f"perimeter_not_on_page: {item.perimeter}")
    return issues


def _share_of_pages(keyword: str, pages: list[Page]) -> float:
    kw = normalize(keyword).lower()
    hits = sum(kw in normalize(p.text).lower() for p in pages)
    return hits / len(pages) if pages else 0.0


def useful_keywords(keywords: list[str], pages: list[Page], max_share: float = 0.5) -> list[str]:
    """Keywords that occur in the release but are not so common they say nothing."""
    return [k for k in keywords if normalize(k) and 0 < _share_of_pages(k, pages) <= max_share]


def keywords_present(keywords: list[str], pages: list[Page]) -> bool:
    return any(normalize(k) and _share_of_pages(k, pages) > 0 for k in keywords)


def validate_extraction(extraction: ReleaseExtraction, pages: list[Page]) -> ReleaseExtraction:
    result = extraction.model_copy(deep=True)
    for item in result.guidance:
        item.issues = check_guidance(item, pages)
        item.verified = not item.issues
    for item in [*result.tone_signals, *result.capital_allocation]:
        item.issues = [] if quote_found(item.quote, pages) else ["quote_not_found"]
        item.verified = not item.issues
    for theme in result.themes:
        theme.issues = [f"quote_not_found: p{q.page}" for q in theme.quotes if not quote_found(q, pages)]
        if not useful_keywords(theme.keywords, pages):
            theme.issues.append("no_useful_keyword")
        theme.verified = not theme.issues
    return result
