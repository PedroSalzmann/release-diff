import json
from pathlib import Path

import pytest

from src.schemas import Quote, ReleaseExtraction
from src.validate import (
    load_pages,
    normalize,
    numbers_in,
    parse_br_number,
    quote_found,
    useful_keywords,
    validate_extraction,
)

ROOT = Path(__file__).resolve().parent.parent
PAGES_JSON = ROOT / "output" / "EMBJ3" / "2026Q1_pages.json"
FIXTURE = ROOT / "tests" / "fixtures" / "embraer_2026Q1_extraction.json"

if not PAGES_JSON.exists():
    pytest.skip("2026Q1_pages.json not available", allow_module_level=True)


@pytest.fixture(scope="module")
def pages():
    return load_pages(PAGES_JSON)


@pytest.fixture(scope="module")
def extraction():
    return ReleaseExtraction.model_validate(json.loads(FIXTURE.read_text(encoding="utf-8")))


def all_quotes(ex):
    quotes = [g.quote for g in ex.guidance]
    quotes += [t.quote for t in ex.tone_signals]
    quotes += [c.quote for c in ex.capital_allocation]
    quotes += [q for th in ex.themes for q in th.quotes]
    return quotes


def margin_item(ex):
    return next(g for g in ex.guidance if g.metric == "Margem EBIT ajustada")


def test_fixture_quotes_all_valid(extraction, pages):
    quotes = all_quotes(extraction)
    assert len(quotes) == 30
    bad = [q for q in quotes if not quote_found(q, pages)]
    assert not bad, bad


def test_fixture_guidance_verified(extraction, pages):
    out = validate_extraction(extraction, pages)
    assert len(out.guidance) == 5
    for g in out.guidance:
        assert g.verified is True and g.issues == []


def test_validate_does_not_mutate_input(extraction, pages):
    validate_extraction(extraction, pages)
    assert extraction.guidance[0].verified is None


def test_tampered_quote(extraction, pages):
    ex = extraction.model_copy(deep=True)
    item = margin_item(ex)
    item.quote.text = item.quote.text.replace("8,7%", "8,8%")
    out = margin_item(validate_extraction(ex, pages))
    assert "quote_not_found" in out.issues
    assert out.verified is False


def test_number_not_in_quote(extraction, pages):
    ex = extraction.model_copy(deep=True)
    margin_item(ex).low = 8.8
    out = margin_item(validate_extraction(ex, pages))
    assert out.issues == ["number_not_in_quote: 8.8"]


def test_soft_hyphen_quote_found(pages):
    assert quote_found(Quote(page=4, text="exceto quando indicado de outra maneira"), pages)


def test_line_break_hyphen_quote_found(pages):
    assert quote_found(Quote(page=11, text="norte-americanos"), pages)


def test_unknown_page_not_found(pages):
    assert not quote_found(Quote(page=999, text="Embraer"), pages)


@pytest.mark.parametrize(
    "token, expected",
    [
        ("1.248,7", 1248.7),
        ("8,7", 8.7),
        ("5.6", 5.6),
        ("(2,4)", -2.4),
        ("1.000", 1000.0),
        ("200", 200.0),
        ("+3,5%", 3.5),
        ("-3,5", -3.5),
        ("US$8,2", 8.2),
        ("R$(957,5)", -957.5),
    ],
)
def test_parse_br_number(token, expected):
    assert parse_br_number(token) == pytest.approx(expected)


def test_numbers_in_parentheses_negative():
    assert numbers_in("caixa de (2,4) e 1.248,7") == [-2.4, 1248.7]


def test_numbers_in_page_4_has_dot_decimal(pages):
    assert 5.6 in numbers_in(pages[3].text)


def test_useful_keywords(pages):
    assert useful_keywords(["Eve", "Praetor"], pages) == ["Praetor"]


def test_normalize_quotes_and_dash():
    assert normalize("“ola” ‘x’ a–b c") == "\"ola\" 'x' a-b c"
