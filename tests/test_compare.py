import copy
import json
import re
from pathlib import Path

import pytest

from src.compare import (
    aggregate_tone,
    changed_sentences,
    classify_guidance,
    confirm_theme_status,
    pair_guidance,
)
from src.extract import Page
from src.schemas import Quote, ReleaseExtraction, Theme, ToneSignal
from src.validate import load_pages

ROOT = Path(__file__).resolve().parent.parent
PAGES_JSON = ROOT / "output" / "EMBJ3" / "2026Q1_pages.json"
FIXTURE = ROOT / "tests" / "fixtures" / "embraer_2026Q1_extraction.json"

if not PAGES_JSON.exists():
    pytest.skip("2026Q1_pages.json not available", allow_module_level=True)


@pytest.fixture(scope="module")
def pages():
    return load_pages(PAGES_JSON)


@pytest.fixture(scope="module")
def prev():
    return ReleaseExtraction.model_validate(json.loads(FIXTURE.read_text(encoding="utf-8")))


@pytest.fixture()
def curr(prev):
    ex = copy.deepcopy(prev)
    for g in ex.guidance:
        if g.metric == "Margem EBIT ajustada":
            g.low, g.high = 10.0, 10.6
            g.quote = Quote(page=g.quote.page, text="margem EBIT ajustada de 10,0% a 10,6%")
        elif g.metric == "Fluxo de caixa livre ajustado":
            g.low = 400
            g.quote = Quote(page=g.quote.page, text="fluxo de caixa livre ajustado de mais de US$ 400 milhões")
    return ex


def by_metric(items, metric):
    return next(g for g in items if g.metric == metric)


def replace_in_pages(pages, pattern, repl="xxx"):
    return [Page(p.page, re.sub(pattern, repl, p.text, flags=re.IGNORECASE)) for p in pages]


# ---------- guidance ----------


def test_pairing_and_classification(prev, curr, pages):
    pairs, up, uc = pair_guidance(prev.guidance, curr.guidance)
    assert len(pairs) == 5 and up == [] and uc == []
    res = {p.metric: classify_guidance(p, c, pages, pages) for p, c in pairs}
    assert res["Margem EBIT ajustada"].change_type == "raised"
    assert res["Margem EBIT ajustada"].delta == pytest.approx(1.3)
    assert res["Fluxo de caixa livre ajustado"].change_type == "raised"
    assert res["Fluxo de caixa livre ajustado"].delta == pytest.approx(200)
    for m in ("Receita", "Entregas da Aviação Comercial", "Entregas da Aviação Executiva"):
        assert res[m].change_type == "maintained"


def test_pairing_ignores_case_and_accents(prev):
    c = copy.deepcopy(prev)
    c.guidance[0].metric = c.guidance[0].metric.upper().replace("Ç", "C")
    c.guidance[0].perimeter = "  SEM   Eve "
    pairs, up, uc = pair_guidance(prev.guidance, c.guidance)
    assert len(pairs) == 5 and not up and not uc


def test_range_to_floor_not_comparable(prev, pages):
    p = by_metric(prev.guidance, "Margem EBIT ajustada")
    c = p.model_copy(update={"high": None})
    assert classify_guidance(p, c, pages, pages).change_type == "not_comparable"


def test_unit_or_period_change_not_comparable(prev, pages):
    p = by_metric(prev.guidance, "Receita")
    assert classify_guidance(p, p.model_copy(update={"unit": "US$ milhões"}), pages, pages).change_type == "not_comparable"
    assert classify_guidance(p, p.model_copy(update={"period": "2027"}), pages, pages).change_type == "not_comparable"


def test_assumptions_changed_only_is_maintained(prev, pages):
    p = by_metric(prev.guidance, "Margem EBIT ajustada")
    c = p.model_copy(update={"assumptions": "com tarifas de 20%"})
    r = classify_guidance(p, c, pages, pages)
    assert r.change_type == "maintained" and "assumptions_changed" in r.notes


def test_lowered(prev, pages):
    p = by_metric(prev.guidance, "Receita")
    r = classify_guidance(p, p.model_copy(update={"low": 8.0, "high": 8.3}), pages, pages)
    assert r.change_type == "lowered" and r.delta == pytest.approx(-0.2)


def test_withdrawn_vs_not_verified(prev, pages):
    p = by_metric(prev.guidance, "Margem EBIT ajustada")
    r = classify_guidance(p, None, pages, pages)
    assert r.change_type == "not_verified" and "metric_still_in_projection_sentence" in r.notes
    stripped = replace_in_pages(pages, r"estima|perspectiva", "xxx")
    assert classify_guidance(p, None, pages, stripped).change_type == "withdrawn"


def test_new_not_verified(prev, pages):
    c = by_metric(prev.guidance, "Margem EBIT ajustada")
    r = classify_guidance(None, c, pages, pages)
    assert r.change_type == "not_verified" and "metric_already_in_projection_sentence" in r.notes
    stripped = replace_in_pages(pages, r"estima|perspectiva", "xxx")
    assert classify_guidance(None, c, stripped, pages).change_type == "new"


# ---------- sentences ----------


def test_changed_sentences(pages):
    phrase = "Todas as unidades de negócios tiveram um bom desempenho no trimestre"
    assert any(phrase in p.text.replace("\n", " ") for p in pages if p.page == 6)
    curr = [
        Page(p.page, re.sub(r"(Todas\s+as\s+unidades\s+de\s+negócios\s+tiveram\s+um\s+)bom", r"\1fraco", p.text))
        if p.page == 6
        else p
        for p in pages
    ]
    added, removed = changed_sentences(pages, curr)
    assert len(added) == 1 and added[0][0] == 6 and "fraco" in added[0][1]
    assert len(removed) == 1 and removed[0][0] == 6 and "bom desempenho" in removed[0][1]


# ---------- tone ----------


def sig(dim, direction, horizon="forward"):
    return ToneSignal(dimension=dim, direction=direction, horizon=horizon, quote=Quote(page=1, text="x"))


def test_tone_labels():
    P = [sig("demand_prices", "neutral"), sig("costs_margins", "neutral"), sig("macro_regulation", "negative")]
    up = [sig("demand_prices", "positive"), sig("costs_margins", "positive"), sig("macro_regulation", "negative")]
    down = [sig("demand_prices", "negative"), sig("costs_margins", "negative"), sig("macro_regulation", "negative")]
    r = aggregate_tone(P, up)
    assert r.label == "more_optimistic" and r.forward_counts == (3, 3)
    assert r.dimension_shifts == {"demand_prices": "improved", "costs_margins": "improved", "macro_regulation": "unchanged"}
    assert aggregate_tone(P, down).label == "more_cautious"
    assert aggregate_tone(P, P).label == "stable"
    assert aggregate_tone(P, up[:2]).label == "insufficient_evidence"
    assert aggregate_tone(P, up[:2]).dimension_shifts  # still filled


def test_tone_one_sided_dimension_and_backward_ignored():
    prev = [sig("demand_prices", "neutral")] * 3 + [sig("cash_balance_sheet", "positive")]
    curr = [sig("demand_prices", "neutral")] * 3 + [sig("operations_execution", "negative"), sig("costs_margins", "negative", "backward")]
    r = aggregate_tone(prev, curr)
    assert r.dimension_shifts == {"demand_prices": "unchanged"}
    assert r.forward_counts == (4, 4)
    assert r.label == "stable"


# ---------- themes ----------


def theme(prev, name):
    return next(t for t in prev.themes if t.name == name)


def test_theme_dropped_confirmed(prev, pages):
    t = theme(prev, "Lançamento Praetor 500/600 E")
    other = replace_in_pages(pages, r"Praetor", "xxx")
    assert confirm_theme_status(t, "dropped", pages, other).status == "dropped"


def test_theme_less_prominent(prev, pages):
    t = theme(prev, "Tarifas de importação dos EUA")
    assert confirm_theme_status(t, "dropped", pages, pages).status == "less_prominent"
    assert confirm_theme_status(t, "new", pages, pages).status == "mentioned_before"


def test_theme_not_verified(prev, pages):
    t = theme(prev, "Eve financiando P&D com dívida").model_copy(update={"keywords": ["Eve"]})
    r = confirm_theme_status(t, "dropped", pages, pages)
    assert r.status == "not_verified" and r.useful_keywords == []
