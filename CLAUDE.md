# CLAUDE.md — release-diff

Compares two consecutive quarterly earnings releases of a B3-listed company and reports what changed in guidance, management tone, themes and capital allocation. Every finding points to a page and a verbatim quote. Parsing KPI tables is out of scope for the MVP.

## Principles

1. **Numbers come from code, never from the LLM.** The LLM extracts and pairs; code compares numbers and classifies changes.
2. **Everything is auditable.** Every finding carries page + verbatim quote, and code checks that the quote exists on that page (`src/validate.py`). Items that fail are kept and flagged `verified=False` with `issues`, never silently dropped. When in doubt, the item is "not verified".
3. **Pipeline, not agent.** Fixed steps: extract text → LLM structured extraction (one call per release) → LLM pairing of leftovers → code classification and validation → render.
4. **Small and finished first.** MVP vs v2 is explicit; nothing "for later".

## Pipeline and code

```
raw/<TICKER>/<YYYY>Q<n>_release.pdf      input PDFs, never edited
  └─ src/extract.py   PyMuPDF blocks, reading order column → y      → output/<TICKER>/<period>_pages.json
  └─ prompts/extract_release.md   LLM structured extraction         → ReleaseExtraction (src/schemas.py)
  └─ src/validate.py  quote on page, numbers in quote, theme keywords
  └─ src/compare.py   guidance classes, sentence diff, tone and theme status
```

Key rules implemented in code (rationale in `docs/DECISOES.md`):
- **Guidance** = explicit quantitative target (value, range, floor or ceiling) for a future period. Paired by metric + period + perimeter. Classes: maintained / raised / lowered (midpoint or the existing bound) / new / withdrawn / not_comparable / not_verified. `withdrawn`/`new` only if no projection sentence in the other release mentions the metric.
- **Tone** = change per dimension in forward-looking sentences that changed between releases; overall label by rule; fewer than 3 forward signals on either side → `insufficient_evidence`.
- **Theme** = specific, nameable topic; `new`/`dropped` confirmed only if none of its specific keywords appears in the other release.

## Repo map

```
raw/      input PDFs (never edited)
wiki/     per-company notes and parsing gotchas
output/   generated files only
prompts/  versioned LLM prompts
src/      code
tests/    pytest (+ tests/fixtures)
docs/     DECISOES.md (decision log), ROTEAMENTO.md (which model does what)
```

## Working rules

1. **Think before coding.** State assumptions; ask when the request is ambiguous.
2. **Simple first.** Minimum code that solves the task.
3. **Surgical changes.** Touch only what the task requires.
4. **Define "done" and verify.** Only say "done" after running the check (`python3 -m pytest -q`).

Code, identifiers, commits and README in English. Never commit `.env` or API keys.
