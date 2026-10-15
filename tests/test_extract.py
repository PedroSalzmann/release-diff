import re
from pathlib import Path

import pytest

from src.extract import HEADER_RE, extract_pages

RAW = Path(__file__).resolve().parent.parent / "raw" / "EMBJ3"


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def load(name: str):
    path = RAW / name
    if not path.exists():
        pytest.skip(f"{name} not available")
    return extract_pages(path)


@pytest.fixture(scope="module")
def q1():
    return load("2026Q1_release.pdf")


@pytest.fixture(scope="module")
def q2():
    return load("2026Q2_release.pdf")


def test_q1_page_count(q1):
    assert len(q1) == 26


def test_q1_guidance_margin_on_page_4(q1):
    assert "margem EBIT ajustada entre 8,7% e 9,3%" in norm(q1[3].text)


def test_q1_business_jets_sentence_contiguous_on_page_5(q1):
    assert "29 jatos executivos (16 pequenos e 13 médios)" in norm(q1[4].text)


def test_q1_no_page_starts_with_running_header(q1):
    for p in q1:
        assert not HEADER_RE.match(p.text), f"header left on page {p.page}"


def test_q1_guidance_reiterated_on_page_3(q1):
    assert "Estimativas para 2026 reiteradas" in norm(q1[2].text)


def test_q2_guidance_margin(q2):
    needle = "10,0% e 10,6%"
    assert needle in norm(q2[3].text) or needle in norm(q2[2].text)
