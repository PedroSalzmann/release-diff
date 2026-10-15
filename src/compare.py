"""Compare two earnings releases (prev = t-1, curr = t).

The LLM only pairs items; every classification here is deterministic code.
"""

import re
import unicodedata
from typing import Literal

from src.extract import Page
from src.schemas import GuidanceChange, GuidanceItem, Theme, ThemeStatus, ToneShift, ToneSignal
from src.validate import keywords_present, normalize, useful_keywords

PROJECTION_CUES = ("estima", "estimativa", "projeç", "perspectiva", "guidance", "espera")
_SENTENCE_RE = re.compile(r"(?<=[.;!?])\s+(?=[A-ZÀ-Ý])")
_TOL = 1e-9


def _fold(text: str) -> str:
    """Lowercase, strip accents, collapse whitespace."""
    decomposed = unicodedata.normalize("NFKD", text)
    stripped = "".join(c for c in decomposed if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", stripped).strip().lower()


# ---------- Guidance ----------


def guidance_key(item: GuidanceItem) -> tuple:
    return (_fold(item.metric), _fold(item.period), _fold(item.perimeter or ""))


def pair_guidance(prev: list[GuidanceItem], curr: list[GuidanceItem]):
    curr_by_key = {guidance_key(c): c for c in curr}
    pairs, unmatched_prev = [], []
    used = set()
    for p in prev:
        key = guidance_key(p)
        if key in curr_by_key and key not in used:
            pairs.append((p, curr_by_key[key]))
            used.add(key)
        else:
            unmatched_prev.append(p)
    unmatched_curr = [c for c in curr if guidance_key(c) not in used]
    return pairs, unmatched_prev, unmatched_curr


def has_projection_sentence(metric: str, pages: list[Page]) -> bool:
    m = _fold(metric)
    cues = [_fold(c) for c in PROJECTION_CUES]
    for _, sentence in split_sentences(pages, min_words=1):
        s = _fold(sentence)
        if m in s and any(c in s for c in cues):
            return True
    return False


def _format(item: GuidanceItem) -> str | None:
    if item.low is not None and item.high is not None:
        return "range"
    if item.low is not None:
        return "floor"
    if item.high is not None:
        return "ceiling"
    return None


def _reference(item: GuidanceItem, fmt: str) -> float:
    if fmt == "range":
        return (item.low + item.high) / 2
    return item.low if fmt == "floor" else item.high


def classify_guidance(prev_item, curr_item, prev_pages, curr_pages) -> GuidanceChange:
    if prev_item and curr_item:
        change = GuidanceChange(metric=curr_item.metric, change_type="not_comparable", prev=prev_item, curr=curr_item)
        if _fold(prev_item.unit) != _fold(curr_item.unit) or _fold(prev_item.period) != _fold(curr_item.period):
            return change
        fmt = _format(prev_item)
        if fmt is None or fmt != _format(curr_item):
            return change
        if _fold(prev_item.assumptions or "") != _fold(curr_item.assumptions or ""):
            change.notes.append("assumptions_changed")
        same = all(
            (a is None and b is None) or (a is not None and b is not None and abs(a - b) <= _TOL)
            for a, b in ((prev_item.low, curr_item.low), (prev_item.high, curr_item.high))
        )
        if same:
            change.change_type = "maintained"
            return change
        delta = round(_reference(curr_item, fmt) - _reference(prev_item, fmt), 10)
        change.delta = delta
        change.change_type = "raised" if delta > 0 else "lowered"
        return change
    if prev_item:
        change = GuidanceChange(metric=prev_item.metric, change_type="withdrawn", prev=prev_item)
        if has_projection_sentence(prev_item.metric, curr_pages):
            change.change_type = "not_verified"
            change.notes.append("metric_still_in_projection_sentence")
        return change
    change = GuidanceChange(metric=curr_item.metric, change_type="new", curr=curr_item)
    if has_projection_sentence(curr_item.metric, prev_pages):
        change.change_type = "not_verified"
        change.notes.append("metric_already_in_projection_sentence")
    return change


# ---------- Tone ----------


def split_sentences(pages: list[Page], min_words: int = 6) -> list[tuple[int, str]]:
    out = []
    for p in pages:
        for s in _SENTENCE_RE.split(normalize(p.text)):
            s = s.strip()
            if len(s.split()) >= min_words:
                out.append((p.page, s))
    return out


def changed_sentences(prev_pages, curr_pages):
    prev = split_sentences(prev_pages)
    curr = split_sentences(curr_pages)
    prev_texts = {s for _, s in prev}
    curr_texts = {s for _, s in curr}
    return (
        [x for x in curr if x[1] not in prev_texts],
        [x for x in prev if x[1] not in curr_texts],
    )


_SCORE = {"positive": 1, "neutral": 0, "negative": -1}


def _dimension_means(signals: list[ToneSignal]) -> tuple[dict[str, float], int]:
    scores: dict[str, list[int]] = {}
    for s in signals:
        if s.horizon == "forward":
            scores.setdefault(s.dimension, []).append(_SCORE[s.direction])
    n = sum(len(v) for v in scores.values())
    return {d: sum(v) / len(v) for d, v in scores.items()}, n


def aggregate_tone(prev_signals, curr_signals, min_forward: int = 3) -> ToneShift:
    prev_m, n_prev = _dimension_means(prev_signals)
    curr_m, n_curr = _dimension_means(curr_signals)
    shifts = {}
    for dim in prev_m.keys() & curr_m.keys():
        diff = curr_m[dim] - prev_m[dim]
        shifts[dim] = "unchanged" if abs(diff) <= _TOL else ("improved" if diff > 0 else "worsened")
    improved = sum(v == "improved" for v in shifts.values())
    worsened = sum(v == "worsened" for v in shifts.values())
    if n_prev < min_forward or n_curr < min_forward:
        label = "insufficient_evidence"
    elif improved > worsened:
        label = "more_optimistic"
    elif improved < worsened:
        label = "more_cautious"
    else:
        label = "stable"
    return ToneShift(dimension_shifts=shifts, label=label, forward_counts=(n_prev, n_curr))


# ---------- Themes ----------


def confirm_theme_status(
    theme: Theme, status: Literal["new", "dropped"], own_pages, other_pages
) -> ThemeStatus:
    kws = useful_keywords(theme.keywords, own_pages)
    if not kws:
        final = "not_verified"
    elif keywords_present(kws, other_pages):
        final = "mentioned_before" if status == "new" else "less_prominent"
    else:
        final = status
    return ThemeStatus(name=theme.name, status=final, useful_keywords=kws, theme=theme)
