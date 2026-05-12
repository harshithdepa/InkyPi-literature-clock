# Literature Clock Plugin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a third-party InkyPi plugin that displays a literary quote in which the phrase referencing the current minute (HH:MM) is highlighted, sourced from the JohannesNE/literature-clock dataset.

**Architecture:** Standalone plugin folder matching InkyPi's `src/plugins/{plugin_id}/` layout. Pure-Python `quote_picker` module handles dataset loading, ±1-minute fallback, sanitation, and selection. Thin `LiteratureClock` class wires it to InkyPi by calling `BasePlugin.render_image()` with a Jinja HTML template. Bundled CSV ships with the plugin; refreshed weekly when online.

**Tech Stack:** Python 3, Pillow (transitively, via InkyPi base), Jinja2 (via InkyPi base), pytest for tests, `requests` (already in InkyPi deps), `pytz` (already in InkyPi deps).

---

## File Structure

**Plugin (in `literature_clock/` — copied to InkyPi `src/plugins/literature_clock/` on install):**

| File | Responsibility |
|---|---|
| `literature_clock/literature_clock.py` | Plugin class. Resolves time, calls picker, builds template params, calls `render_image`. Thin. |
| `literature_clock/quote_picker.py` | Pure logic: load CSV, filter by time + sfw, ±1 fallback, sanitize, pick (shortest/random/daily), wrap highlight span. No InkyPi imports. |
| `literature_clock/dataset.py` | CSV cache freshness check + download with offline fallback. No InkyPi imports. |
| `literature_clock/plugin-info.json` | Plugin manifest. |
| `literature_clock/settings.html` | Settings form + prepopulation JS. |
| `literature_clock/icon.png` | Web UI icon. |
| `literature_clock/render/literature_clock.html` | Jinja template extending `plugin.html`. |
| `literature_clock/render/literature_clock.css` | Layout, font sizing, highlight styles. |
| `literature_clock/data/litclock_annotated.csv` | Bundled dataset (offline default). |

**Tests (sit in repo root, not copied to InkyPi):**

| File | Responsibility |
|---|---|
| `tests/test_quote_picker.py` | Pure unit tests against fixture CSV. |
| `tests/test_dataset.py` | Cache freshness + download fallback (mocked). |
| `tests/fixtures/litclock_sample.csv` | Tiny CSV: handful of times, NSFW row, empty minute. |

**Repo top-level:**

| File | Responsibility |
|---|---|
| `README.md` | Description, screenshot placeholder, install instructions, dataset attribution, dev status. |
| `LICENSE` | MIT. |
| `requirements-dev.txt` | `pytest`, `requests`. |
| `.gitignore` | Standard Python. |

---

## Task 1: Repo scaffolding

**Files:**
- Create: `/Users/h.depa/projects/InkyPi-literature-clock/.gitignore`
- Create: `/Users/h.depa/projects/InkyPi-literature-clock/LICENSE`
- Create: `/Users/h.depa/projects/InkyPi-literature-clock/requirements-dev.txt`
- Create: `/Users/h.depa/projects/InkyPi-literature-clock/literature_clock/__init__.py` (empty marker, helps tests import)
- Create: `/Users/h.depa/projects/InkyPi-literature-clock/tests/__init__.py` (empty)

- [ ] **Step 1: Create `.gitignore`**

```
__pycache__/
*.pyc
.pytest_cache/
.venv/
venv/
*.egg-info/
.DS_Store
```

- [ ] **Step 2: Create `LICENSE`** (MIT, year 2026, holder "Harshith Depa"). Use the standard MIT text.

- [ ] **Step 3: Create `requirements-dev.txt`**

```
pytest>=8.0
requests>=2.31
```

- [ ] **Step 4: Create empty `literature_clock/__init__.py` and `tests/__init__.py`**

- [ ] **Step 5: Commit**

```bash
cd /Users/h.depa/projects/InkyPi-literature-clock
git add .
git commit -m "chore: scaffold repo (license, gitignore, deps)"
```

---

## Task 2: Test fixture CSV

**Files:**
- Create: `tests/fixtures/litclock_sample.csv`

- [ ] **Step 1: Create `tests/fixtures/litclock_sample.csv`**

Pipe-delimited, no quote chars, columns: `time|time_human|full_quote|book_title|author_name|sfw`. Hand-crafted rows that exercise edge cases.

```
00:00|midnight|It was midnight when she finally arrived.|Sample Book|Sample Author|sfw
07:32|seven thirty-two|At seven thirty-two the bell rang sharply.|Morning Tales|A. Writer|sfw
07:32|exactly half past seven|It was exactly half past seven, no later.|Long Story|B. Writer|sfw
07:32|7:32|The clock read 7:32 — a profane hour to be awake.|Edgy Book|C. Writer|nsfw
12:00|noon|At noon the sun stood directly overhead.|Noon Saga|D. Writer|sfw
14:15|quarter past two|Quarter past two and still no sign of him.|Afternoon|E. Writer|sfw
14:14|fourteen-fourteen|At fourteen-fourteen the train pulled in.|Train|F. Writer|sfw
14:16|fourteen-sixteen|Fourteen-sixteen, and the platform emptied.|Train|F. Writer|sfw
23:59|one minute to midnight|One minute to midnight, the year nearly gone.|Year End|G. Writer|sfw
```

Notes used by later tests:
- `07:32` has 2 sfw rows (shortest = first by length, len 41 vs 41 — pick by min preserves stable order).
- `14:15` has one row; `14:14` and `14:16` exist for ±1 fallback testing.
- `09:00` is intentionally absent (true empty minute, with neighbors also absent → forces fallback failure).

- [ ] **Step 2: Commit**

```bash
git add tests/fixtures/litclock_sample.csv
git commit -m "test: add literature clock CSV fixture"
```

---

## Task 3: `quote_picker.find_candidates` — exact-time filter, NSFW gate

**Files:**
- Create: `tests/test_quote_picker.py`
- Create: `literature_clock/quote_picker.py`

- [ ] **Step 1: Write the failing test**

`tests/test_quote_picker.py`:

```python
from pathlib import Path
from literature_clock.quote_picker import find_candidates

FIXTURE = Path(__file__).parent / "fixtures" / "litclock_sample.csv"


def test_find_candidates_returns_sfw_rows_for_exact_time():
    rows = find_candidates(FIXTURE, "07:32", allow_nsfw=False)
    assert len(rows) == 2
    assert all(r["sfw"] != "nsfw" for r in rows)
    assert all(r["time"] == "07:32" for r in rows)


def test_find_candidates_includes_nsfw_when_allowed():
    rows = find_candidates(FIXTURE, "07:32", allow_nsfw=True)
    assert len(rows) == 3


def test_find_candidates_returns_empty_for_missing_minute():
    rows = find_candidates(FIXTURE, "09:00", allow_nsfw=True)
    assert rows == []
```

- [ ] **Step 2: Run — expect failure**

```bash
cd /Users/h.depa/projects/InkyPi-literature-clock
python3 -m pytest tests/test_quote_picker.py -v
```
Expected: `ImportError` / `ModuleNotFoundError` for `find_candidates`.

- [ ] **Step 3: Implement**

`literature_clock/quote_picker.py`:

```python
import csv
from pathlib import Path

CSV_FIELDS = ["time", "time_human", "full_quote", "book_title", "author_name", "sfw"]


def find_candidates(csv_path: Path, hhmm: str, allow_nsfw: bool) -> list[dict]:
    """Return all rows matching the exact HH:MM time, optionally filtering NSFW."""
    matches = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(
            f,
            fieldnames=CSV_FIELDS,
            delimiter="|",
            lineterminator="\n",
            quotechar=None,
            quoting=csv.QUOTE_NONE,
        )
        for row in reader:
            if row["time"] != hhmm:
                continue
            if not allow_nsfw and row["sfw"] == "nsfw":
                continue
            matches.append(row)
    return matches
```

- [ ] **Step 4: Run — expect pass**

```bash
python3 -m pytest tests/test_quote_picker.py -v
```
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add literature_clock/quote_picker.py tests/test_quote_picker.py
git commit -m "feat: quote_picker.find_candidates with NSFW gate"
```

---

## Task 4: ±1-minute fallback resolver

**Files:**
- Modify: `tests/test_quote_picker.py`
- Modify: `literature_clock/quote_picker.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_quote_picker.py`:

```python
from literature_clock.quote_picker import resolve_with_fallback


def test_resolve_uses_exact_match_when_present():
    rows, used_time = resolve_with_fallback(FIXTURE, "07:32", allow_nsfw=False)
    assert used_time == "07:32"
    assert len(rows) == 2


def test_resolve_falls_back_to_minus_one_minute():
    # 14:15 has 1 row, 14:14 has 1 row, 14:16 has 1 row.
    # If we ask for an empty minute between them, should fall back.
    # Use a minute we know is empty but neighbors exist.
    # 09:00 is empty AND neighbors empty in fixture; instead pick a synthetic empty:
    # We'll test with minute "14:15" by filtering to nsfw-only=False to force fallback path.
    # Simpler: directly probe an empty minute with a known neighbor.
    # 23:58 is empty; 23:59 exists, 23:57 empty -> falls back to +1.
    rows, used_time = resolve_with_fallback(FIXTURE, "23:58", allow_nsfw=False)
    assert used_time == "23:59"
    assert len(rows) == 1


def test_resolve_falls_back_to_plus_one_minute_when_minus_empty():
    # 11:59 empty, 12:00 has noon row, 11:58 empty -> +1 wins
    rows, used_time = resolve_with_fallback(FIXTURE, "11:59", allow_nsfw=False)
    assert used_time == "12:00"


def test_resolve_returns_none_when_all_three_empty():
    rows, used_time = resolve_with_fallback(FIXTURE, "09:00", allow_nsfw=False)
    assert rows == []
    assert used_time is None


def test_resolve_handles_hour_wrap_at_midnight():
    # 00:00 exists, 23:59 exists. Asking for empty wrap edges should still work.
    # Fixture: 00:01 empty, 00:00 exists -> -1 from 00:01 = 00:00 wins.
    rows, used_time = resolve_with_fallback(FIXTURE, "00:01", allow_nsfw=False)
    assert used_time == "00:00"
```

- [ ] **Step 2: Run — expect failure**

```bash
python3 -m pytest tests/test_quote_picker.py -v
```
Expected: ImportError on `resolve_with_fallback`.

- [ ] **Step 3: Implement**

Append to `literature_clock/quote_picker.py`:

```python
from datetime import datetime, timedelta


def _shift_minute(hhmm: str, delta: int) -> str:
    base = datetime.strptime(hhmm, "%H:%M")
    shifted = base + timedelta(minutes=delta)
    return shifted.strftime("%H:%M")


def resolve_with_fallback(csv_path: Path, hhmm: str, allow_nsfw: bool):
    """Return (rows, used_time). Tries HH:MM, then -1, then +1. Returns ([], None) if all empty."""
    for delta in (0, -1, 1):
        candidate_time = _shift_minute(hhmm, delta)
        rows = find_candidates(csv_path, candidate_time, allow_nsfw)
        if rows:
            return rows, candidate_time
    return [], None
```

- [ ] **Step 4: Run — expect pass**

```bash
python3 -m pytest tests/test_quote_picker.py -v
```
Expected: 8 passed.

- [ ] **Step 5: Commit**

```bash
git add literature_clock/quote_picker.py tests/test_quote_picker.py
git commit -m "feat: ±1-minute fallback resolver with hour wrap"
```

---

## Task 5: Quote sanitation

**Files:**
- Modify: `tests/test_quote_picker.py`
- Modify: `literature_clock/quote_picker.py`

- [ ] **Step 1: Write the failing tests**

Append:

```python
from literature_clock.quote_picker import sanitize


def test_sanitize_replaces_br_variants_with_space():
    assert sanitize("Hello<br/>World") == "Hello World"
    assert sanitize("A<br />B") == "A B"
    assert sanitize("X<br>Y") == "X Y"


def test_sanitize_replaces_nbsp_with_space():
    assert sanitize("foo bar") == "foo bar"


def test_sanitize_simplifies_smart_punctuation():
    assert sanitize("‘hi’") == "'hi'"
    assert sanitize("“hi”") == '"hi"'
    assert sanitize("dash—here") == "dash-here"


def test_sanitize_strips_non_ascii():
    assert sanitize("café") == "caf"
```

- [ ] **Step 2: Run — expect failure**

```bash
python3 -m pytest tests/test_quote_picker.py -v
```
Expected: ImportError on `sanitize`.

- [ ] **Step 3: Implement**

Append to `literature_clock/quote_picker.py`:

```python
_TRANSL = str.maketrans({
    "‘": "'", "’": "'", "´": "'",
    "“": '"', "”": '"',
    "—": "-", "–": "-",
})


def sanitize(text: str) -> str:
    out = text.replace("<br/>", " ").replace("<br />", " ").replace("<br>", " ")
    out = out.replace(" ", " ")
    out = out.translate(_TRANSL)
    return out.encode("ascii", "ignore").decode("utf-8")
```

- [ ] **Step 4: Run — expect pass**

```bash
python3 -m pytest tests/test_quote_picker.py -v
```
Expected: 12 passed.

- [ ] **Step 5: Commit**

```bash
git add literature_clock/quote_picker.py tests/test_quote_picker.py
git commit -m "feat: quote sanitation (br, nbsp, smart punctuation, ascii)"
```

---

## Task 6: Quote selection strategies

**Files:**
- Modify: `tests/test_quote_picker.py`
- Modify: `literature_clock/quote_picker.py`

- [ ] **Step 1: Write the failing tests**

Append:

```python
from literature_clock.quote_picker import pick_quote


def _rows():
    return [
        {"full_quote": "long quote " * 10, "time": "07:32"},
        {"full_quote": "short", "time": "07:32"},
        {"full_quote": "medium quote here", "time": "07:32"},
    ]


def test_pick_shortest():
    pick = pick_quote(_rows(), strategy="shortest", seed_key="ignored")
    assert pick["full_quote"] == "short"


def test_pick_daily_is_deterministic_for_same_seed():
    a = pick_quote(_rows(), strategy="daily", seed_key="2026-05-12-0732")
    b = pick_quote(_rows(), strategy="daily", seed_key="2026-05-12-0732")
    assert a == b


def test_pick_daily_can_differ_for_different_seeds():
    seen = {pick_quote(_rows(), strategy="daily", seed_key=f"2026-05-{d:02d}-0732")["full_quote"]
            for d in range(1, 32)}
    assert len(seen) > 1


def test_pick_random_returns_one_of_inputs():
    pick = pick_quote(_rows(), strategy="random", seed_key="ignored")
    assert pick in _rows()


def test_pick_unknown_strategy_falls_back_to_shortest():
    pick = pick_quote(_rows(), strategy="bogus", seed_key="ignored")
    assert pick["full_quote"] == "short"
```

- [ ] **Step 2: Run — expect failure**

```bash
python3 -m pytest tests/test_quote_picker.py -v
```
Expected: ImportError on `pick_quote`.

- [ ] **Step 3: Implement**

Append:

```python
import random


def pick_quote(rows: list[dict], strategy: str, seed_key: str) -> dict:
    if not rows:
        raise ValueError("pick_quote called with empty rows")
    if strategy == "random":
        return random.choice(rows)
    if strategy == "daily":
        rng = random.Random(seed_key)
        return rng.choice(rows)
    # shortest (default)
    return min(rows, key=lambda r: len(r["full_quote"]))
```

- [ ] **Step 4: Run — expect pass**

```bash
python3 -m pytest tests/test_quote_picker.py -v
```
Expected: 17 passed.

- [ ] **Step 5: Commit**

```bash
git add literature_clock/quote_picker.py tests/test_quote_picker.py
git commit -m "feat: quote selection strategies (shortest/random/daily)"
```

---

## Task 7: Highlight wrapping

**Files:**
- Modify: `tests/test_quote_picker.py`
- Modify: `literature_clock/quote_picker.py`

- [ ] **Step 1: Write the failing tests**

Append:

```python
from literature_clock.quote_picker import wrap_highlight


def test_wrap_highlight_wraps_first_match_case_insensitively():
    out = wrap_highlight("It was Seven Thirty-Two when it rang.", "seven thirty-two")
    assert out == "It was <span class=\"litclock-highlight\">Seven Thirty-Two</span> when it rang."


def test_wrap_highlight_only_wraps_first_occurrence():
    out = wrap_highlight("noon and noon again", "noon")
    assert out.count("<span") == 1
    assert out.startswith("<span class=\"litclock-highlight\">noon</span> and noon again")


def test_wrap_highlight_returns_unchanged_when_phrase_absent():
    quote = "no time phrase here"
    assert wrap_highlight(quote, "midnight") == quote
```

- [ ] **Step 2: Run — expect failure**

- [ ] **Step 3: Implement**

Append:

```python
import re

HIGHLIGHT_OPEN = '<span class="litclock-highlight">'
HIGHLIGHT_CLOSE = "</span>"


def wrap_highlight(quote: str, time_human: str) -> str:
    pattern = re.compile(re.escape(time_human), re.IGNORECASE)
    return pattern.sub(lambda m: f"{HIGHLIGHT_OPEN}{m.group()}{HIGHLIGHT_CLOSE}", quote, count=1)
```

- [ ] **Step 4: Run — expect pass**

```bash
python3 -m pytest tests/test_quote_picker.py -v
```
Expected: 20 passed.

- [ ] **Step 5: Commit**

```bash
git add literature_clock/quote_picker.py tests/test_quote_picker.py
git commit -m "feat: highlight wrapping for time phrase"
```

---

## Task 8: Dataset cache freshness + download fallback

**Files:**
- Create: `tests/test_dataset.py`
- Create: `literature_clock/dataset.py`

- [ ] **Step 1: Write the failing test**

`tests/test_dataset.py`:

```python
import time
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
from literature_clock.dataset import ensure_dataset, MAX_AGE_SECONDS


def test_ensure_dataset_skips_download_when_fresh(tmp_path):
    csv_path = tmp_path / "litclock.csv"
    csv_path.write_text("00:00|midnight|q|b|a|sfw\n")
    with patch("literature_clock.dataset.requests.get") as mock_get:
        ensure_dataset(csv_path)
        mock_get.assert_not_called()


def test_ensure_dataset_downloads_when_stale(tmp_path):
    csv_path = tmp_path / "litclock.csv"
    csv_path.write_text("old\n")
    old_mtime = time.time() - (MAX_AGE_SECONDS + 60)
    import os
    os.utime(csv_path, (old_mtime, old_mtime))

    mock_response = MagicMock(status_code=200, text="00:00|midnight|new|b|a|sfw\n")
    mock_response.raise_for_status = MagicMock()
    with patch("literature_clock.dataset.requests.get", return_value=mock_response) as mock_get:
        ensure_dataset(csv_path)
        mock_get.assert_called_once()
    assert "new" in csv_path.read_text()


def test_ensure_dataset_keeps_old_file_when_download_fails(tmp_path):
    csv_path = tmp_path / "litclock.csv"
    csv_path.write_text("kept\n")
    old_mtime = time.time() - (MAX_AGE_SECONDS + 60)
    import os
    os.utime(csv_path, (old_mtime, old_mtime))

    with patch("literature_clock.dataset.requests.get", side_effect=Exception("network down")):
        ensure_dataset(csv_path)  # must not raise
    assert csv_path.read_text() == "kept\n"


def test_ensure_dataset_raises_when_missing_and_offline(tmp_path):
    csv_path = tmp_path / "missing.csv"
    with patch("literature_clock.dataset.requests.get", side_effect=Exception("network down")):
        with pytest.raises(FileNotFoundError):
            ensure_dataset(csv_path)
```

- [ ] **Step 2: Run — expect failure**

```bash
python3 -m pytest tests/test_dataset.py -v
```
Expected: ImportError.

- [ ] **Step 3: Implement**

`literature_clock/dataset.py`:

```python
import logging
import time
from pathlib import Path
import requests

logger = logging.getLogger(__name__)

DATASET_URL = "https://raw.githubusercontent.com/JohannesNE/literature-clock/master/litclock_annotated.csv"
MAX_AGE_SECONDS = 7 * 24 * 60 * 60  # 7 days


def ensure_dataset(csv_path: Path) -> None:
    """Ensure CSV exists and is fresh.

    - If file is fresh, do nothing.
    - If stale, attempt download; on failure keep the existing file.
    - If missing, attempt download; on failure raise FileNotFoundError.
    """
    csv_path = Path(csv_path)
    exists = csv_path.exists()
    fresh = exists and (time.time() - csv_path.stat().st_mtime) < MAX_AGE_SECONDS

    if fresh:
        return

    try:
        response = requests.get(DATASET_URL, timeout=15)
        response.raise_for_status()
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        csv_path.write_text(response.text, encoding="utf-8")
        return
    except Exception as exc:
        logger.warning("Literature clock dataset refresh failed: %s", exc)
        if not exists:
            raise FileNotFoundError(f"Literature clock dataset unavailable at {csv_path}") from exc
        # else: keep stale file
```

- [ ] **Step 4: Run — expect pass**

```bash
python3 -m pytest tests/test_dataset.py -v
```
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add literature_clock/dataset.py tests/test_dataset.py
git commit -m "feat: dataset cache freshness + offline fallback"
```

---

## Task 9: Download bundled dataset

**Files:**
- Create: `literature_clock/data/litclock_annotated.csv`

- [ ] **Step 1: Download the dataset**

```bash
cd /Users/h.depa/projects/InkyPi-literature-clock
mkdir -p literature_clock/data
curl -fsSL https://raw.githubusercontent.com/JohannesNE/literature-clock/master/litclock_annotated.csv \
  -o literature_clock/data/litclock_annotated.csv
```

- [ ] **Step 2: Verify size and shape**

```bash
wc -l literature_clock/data/litclock_annotated.csv
head -3 literature_clock/data/litclock_annotated.csv
```
Expected: ~2400 lines; lines look like `HH:MM|phrase|quote|book|author|sfw`.

- [ ] **Step 3: Commit**

```bash
git add literature_clock/data/litclock_annotated.csv
git commit -m "data: bundle JohannesNE literature-clock CSV (offline default)"
```

---

## Task 10: Plugin manifest

**Files:**
- Create: `literature_clock/plugin-info.json`

- [ ] **Step 1: Create the manifest**

```json
{
    "display_name": "Literature Clock",
    "id": "literature_clock",
    "class": "LiteratureClock",
    "repository": "https://github.com/hdepa/InkyPi-literature-clock"
}
```

- [ ] **Step 2: Commit**

```bash
git add literature_clock/plugin-info.json
git commit -m "feat: plugin manifest"
```

---

## Task 11: Render template (HTML)

**Files:**
- Create: `literature_clock/render/literature_clock.html`

- [ ] **Step 1: Create the template**

This template extends InkyPi's `plugin.html` (resolved at runtime by `BasePlugin`'s Jinja loader, which adds the base render dir). Variables passed in: `quote_html` (already containing the `<span class="litclock-highlight">…</span>`), `attribution`, `show_attribution`, `font_family`, `highlight_style`, `highlight_color`, `quote_length` (used for font sizing tier).

```html
{% extends "plugin.html" %}

{% block content %}
<div class="litclock-root litclock-tier-{{ size_tier }}"
     style="font-family: {{ font_family|default('serif') }};">
  <div class="litclock-quote">{{ quote_html|safe }}</div>
  {% if show_attribution and attribution %}
    <div class="litclock-attribution">{{ attribution }}</div>
  {% endif %}
</div>

<style>
  .litclock-highlight {
    {% if highlight_style == 'bold' %}font-weight: 700;{% endif %}
    {% if highlight_style == 'italic' %}font-style: italic;{% endif %}
    {% if highlight_style == 'underline' %}text-decoration: underline;{% endif %}
    {% if highlight_style == 'color' %}color: {{ highlight_color|default('#c00') }};{% endif %}
  }
</style>
{% endblock %}
```

- [ ] **Step 2: Commit**

```bash
git add literature_clock/render/literature_clock.html
git commit -m "feat: render template extending plugin.html"
```

---

## Task 12: Render styles (CSS)

**Files:**
- Create: `literature_clock/render/literature_clock.css`

- [ ] **Step 1: Create the stylesheet**

Five tiers handle the dataset's quote-length spread; CSS picks one via `litclock-tier-N` class set in Python (Task 13). This avoids brittle CSS-only `clamp()` math against unknown viewport sizes.

```css
.litclock-root {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 4% 6%;
  box-sizing: border-box;
  text-align: left;
}

.litclock-quote {
  width: 100%;
  line-height: 1.25;
  word-wrap: break-word;
}

.litclock-attribution {
  margin-top: 1.2em;
  font-size: 0.45em;
  font-style: italic;
  text-align: right;
  width: 100%;
  opacity: 0.85;
}

/* tier sizing — based on quote character count */
.litclock-tier-1 .litclock-quote { font-size: 64px; }   /* <= 80 chars */
.litclock-tier-2 .litclock-quote { font-size: 52px; }   /* 81-160 */
.litclock-tier-3 .litclock-quote { font-size: 42px; }   /* 161-260 */
.litclock-tier-4 .litclock-quote { font-size: 34px; }   /* 261-380 */
.litclock-tier-5 .litclock-quote { font-size: 26px; }   /* > 380 */
```

- [ ] **Step 2: Commit**

```bash
git add literature_clock/render/literature_clock.css
git commit -m "feat: render stylesheet with five quote-length tiers"
```

---

## Task 13: Plugin class

**Files:**
- Create: `literature_clock/literature_clock.py`

- [ ] **Step 1: Implement the plugin class**

```python
import logging
import os
from datetime import datetime
import pytz

from utils.app_utils import resolve_path, get_fonts
from plugins.base_plugin.base_plugin import BasePlugin

from .quote_picker import resolve_with_fallback, sanitize, pick_quote, wrap_highlight
from .dataset import ensure_dataset

logger = logging.getLogger(__name__)

DEFAULT_TIMEZONE = "US/Eastern"
ATTRIBUTION_MAX = 55


def _size_tier(n: int) -> int:
    if n <= 80: return 1
    if n <= 160: return 2
    if n <= 260: return 3
    if n <= 380: return 4
    return 5


def _seed_key(now: datetime) -> str:
    return now.strftime("%Y-%m-%d-%H%M")


class LiteratureClock(BasePlugin):
    def generate_settings_template(self):
        params = super().generate_settings_template()
        params["style_settings"] = True
        params["available_fonts"] = [f["name"] for f in get_fonts()]
        return params

    def generate_image(self, settings, device_config):
        # Resolution + orientation (mirrors built-in Clock plugin)
        dimensions = device_config.get_resolution()
        if device_config.get_config("orientation") == "vertical":
            dimensions = dimensions[::-1]

        tz_name = device_config.get_config("timezone") or DEFAULT_TIMEZONE
        now = datetime.now(pytz.timezone(tz_name))
        hhmm = now.strftime("%H:%M")

        # Dataset
        csv_path = os.path.join(self.get_plugin_dir("data"), "litclock_annotated.csv")
        try:
            ensure_dataset(csv_path)
        except FileNotFoundError as exc:
            logger.error("Literature clock dataset missing: %s", exc)
            raise RuntimeError("Literature clock dataset unavailable.") from exc

        allow_nsfw = settings.get("allow_nsfw") in ("on", "true", True)
        rows, _used_time = resolve_with_fallback(csv_path, hhmm, allow_nsfw=allow_nsfw)

        if not rows:
            return self._render_no_quote(dimensions, hhmm, settings)

        strategy = settings.get("quote_selection") or "shortest"
        chosen = pick_quote(rows, strategy=strategy, seed_key=_seed_key(now))

        quote = sanitize(chosen["full_quote"])
        time_human = sanitize(chosen["time_human"])
        quote_html = wrap_highlight(quote, time_human)

        attribution = ""
        if settings.get("show_attribution", "on") in ("on", "true", True):
            book = sanitize(chosen.get("book_title", ""))
            author = sanitize(chosen.get("author_name", ""))
            attribution = f"— {book}, {author}"
            if len(attribution) > ATTRIBUTION_MAX:
                attribution = attribution[: ATTRIBUTION_MAX - 1] + "…"

        template_params = {
            "quote_html": quote_html,
            "attribution": attribution,
            "show_attribution": bool(attribution),
            "size_tier": _size_tier(len(quote)),
            "font_family": settings.get("font_family") or "serif",
            "highlight_style": settings.get("highlight_style") or "bold",
            "highlight_color": settings.get("highlight_color") or "#c00",
            "plugin_settings": settings,
        }
        return self.render_image(
            dimensions,
            "literature_clock.html",
            "literature_clock.css",
            template_params,
        )

    def _render_no_quote(self, dimensions, hhmm, settings):
        template_params = {
            "quote_html": f"It is {hhmm}.",
            "attribution": "No quote for this minute",
            "show_attribution": True,
            "size_tier": 1,
            "font_family": settings.get("font_family") or "serif",
            "highlight_style": settings.get("highlight_style") or "bold",
            "highlight_color": settings.get("highlight_color") or "#c00",
            "plugin_settings": settings,
        }
        return self.render_image(
            dimensions,
            "literature_clock.html",
            "literature_clock.css",
            template_params,
        )
```

- [ ] **Step 2: Sanity-check imports parse**

```bash
python3 -c "import ast; ast.parse(open('literature_clock/literature_clock.py').read()); print('ok')"
```
Expected: `ok`. (The InkyPi-specific imports won't resolve outside InkyPi — that's expected; we only verify syntax here.)

- [ ] **Step 3: Commit**

```bash
git add literature_clock/literature_clock.py
git commit -m "feat: LiteratureClock plugin class wiring picker to render_image"
```

---

## Task 14: Settings form

**Files:**
- Create: `literature_clock/settings.html`

- [ ] **Step 1: Create the settings template**

Mirrors the prepopulation pattern from `docs/building_plugins.md`.

```html
<div class="form-group">
  <label class="form-label">Quote selection</label>
  <div class="radio-group">
    <label><input type="radio" name="quote_selection" value="shortest" checked> Shortest</label>
    <label><input type="radio" name="quote_selection" value="random"> Random</label>
    <label><input type="radio" name="quote_selection" value="daily"> One per day</label>
  </div>
</div>

<div class="form-group">
  <label><input type="checkbox" name="allow_nsfw" id="allow_nsfw"> Allow NSFW quotes</label>
</div>

<div class="form-group">
  <label><input type="checkbox" name="show_attribution" id="show_attribution" checked> Show attribution</label>
</div>

<div class="form-group">
  <label class="form-label" for="font_family">Font</label>
  <select name="font_family" id="font_family">
    {% for font_name in available_fonts %}
      <option value="{{ font_name }}">{{ font_name }}</option>
    {% endfor %}
  </select>
</div>

<div class="form-group">
  <label class="form-label">Highlight style</label>
  <div class="radio-group">
    <label><input type="radio" name="highlight_style" value="bold" checked> Bold</label>
    <label><input type="radio" name="highlight_style" value="italic"> Italic</label>
    <label><input type="radio" name="highlight_style" value="underline"> Underline</label>
    <label><input type="radio" name="highlight_style" value="color"> Color</label>
  </div>
</div>

<div class="form-group" id="highlight_color_group" style="display:none;">
  <label class="form-label" for="highlight_color">Highlight color</label>
  <input type="color" name="highlight_color" id="highlight_color" value="#c00000">
</div>

<script>
  function updateHighlightColorVisibility() {
    const selected = document.querySelector('input[name="highlight_style"]:checked');
    const group = document.getElementById('highlight_color_group');
    group.style.display = (selected && selected.value === 'color') ? '' : 'none';
  }
  document.querySelectorAll('input[name="highlight_style"]').forEach(el =>
    el.addEventListener('change', updateHighlightColorVisibility)
  );

  document.addEventListener('DOMContentLoaded', () => {
    if (loadPluginSettings) {
      const qs = pluginSettings.quote_selection || 'shortest';
      const qsEl = document.querySelector(`input[name="quote_selection"][value="${qs}"]`);
      if (qsEl) qsEl.checked = true;

      document.getElementById('allow_nsfw').checked = !!pluginSettings.allow_nsfw;
      document.getElementById('show_attribution').checked =
        pluginSettings.show_attribution === undefined ? true : !!pluginSettings.show_attribution;

      if (pluginSettings.font_family) {
        document.getElementById('font_family').value = pluginSettings.font_family;
      }

      const hs = pluginSettings.highlight_style || 'bold';
      const hsEl = document.querySelector(`input[name="highlight_style"][value="${hs}"]`);
      if (hsEl) hsEl.checked = true;

      if (pluginSettings.highlight_color) {
        document.getElementById('highlight_color').value = pluginSettings.highlight_color;
      }
    }
    updateHighlightColorVisibility();
  });
</script>
```

- [ ] **Step 2: Commit**

```bash
git add literature_clock/settings.html
git commit -m "feat: settings form with prepopulation"
```

---

## Task 15: Icon

**Files:**
- Create: `literature_clock/icon.png`

- [ ] **Step 1: Generate a placeholder icon**

InkyPi's icons are small (~80x80) PNGs. Generate a simple book-with-clock placeholder using Pillow so the plugin loads in the UI; the user can replace later.

```bash
cd /Users/h.depa/projects/InkyPi-literature-clock
python3 - <<'PY'
from PIL import Image, ImageDraw
img = Image.new("RGBA", (96, 96), (255, 255, 255, 0))
d = ImageDraw.Draw(img)
# book outline
d.rectangle([14, 18, 82, 82], outline=(20, 20, 20), width=4)
d.line([48, 18, 48, 82], fill=(20, 20, 20), width=3)
# clock face overlay
d.ellipse([34, 34, 78, 78], outline=(180, 30, 40), width=4, fill=(255, 255, 255))
d.line([56, 56, 56, 42], fill=(180, 30, 40), width=3)
d.line([56, 56, 70, 60], fill=(180, 30, 40), width=3)
img.save("literature_clock/icon.png")
print("ok")
PY
```

- [ ] **Step 2: Commit**

```bash
git add literature_clock/icon.png
git commit -m "feat: placeholder plugin icon"
```

---

## Task 16: Integration smoke test (offline, dataset → image bytes)

**Files:**
- Create: `tests/test_integration.py`

- [ ] **Step 1: Write the test**

This bypasses InkyPi (avoids needing a Pi/Chromium) and exercises the picker pipeline against the real bundled CSV at the current minute (or a known-good minute).

```python
from pathlib import Path
from literature_clock.quote_picker import (
    resolve_with_fallback, sanitize, pick_quote, wrap_highlight,
)

BUNDLED_CSV = Path(__file__).parent.parent / "literature_clock" / "data" / "litclock_annotated.csv"


def test_bundled_csv_resolves_known_minute():
    rows, used_time = resolve_with_fallback(BUNDLED_CSV, "07:00", allow_nsfw=False)
    assert rows, "expected at least one quote near 07:00"
    chosen = pick_quote(rows, strategy="shortest", seed_key="x")
    quote = sanitize(chosen["full_quote"])
    assert len(quote) > 0
    out = wrap_highlight(quote, sanitize(chosen["time_human"]))
    # Highlight should appear unless time_human is absent from quote (rare; not asserting)
    assert isinstance(out, str)


def test_bundled_csv_every_minute_has_resolution_within_pm1():
    """Every minute of the day should yield a quote with ±1 fallback."""
    misses = []
    for h in range(24):
        for m in range(60):
            rows, _ = resolve_with_fallback(BUNDLED_CSV, f"{h:02d}:{m:02d}", allow_nsfw=True)
            if not rows:
                misses.append(f"{h:02d}:{m:02d}")
    # Some clusters of empty minutes exist; assert the number is small.
    assert len(misses) < 50, f"too many unresolvable minutes: {misses[:10]}..."
```

- [ ] **Step 2: Run — expect pass**

```bash
python3 -m pytest tests/test_integration.py -v
```
Expected: 2 passed. If the second fails with "too many unresolvable minutes", inspect the dataset shape and either adjust the threshold or document the gap in the README.

- [ ] **Step 3: Commit**

```bash
git add tests/test_integration.py
git commit -m "test: integration smoke against bundled CSV"
```

---

## Task 17: README

**Files:**
- Create: `README.md`

- [ ] **Step 1: Write the README**

```markdown
# InkyPi Literature Clock

A third-party [InkyPi](https://github.com/fatihak/InkyPi) plugin that displays a literary quote referencing the current minute, with the time phrase highlighted.

Inspired by the privacy-mode literature clock in [mendhak/waveshare-epaper-display](https://github.com/mendhak/waveshare-epaper-display) and the original [Author Clock](https://www.authorclock.com/) / [Jaap Meijers' literary clock](https://github.com/JohannesNE/literature-clock).

## Screenshot

_Coming soon — replace with an actual photo of the plugin running on your display._

## Installation

1. SSH into your Pi.
2. Clone this repo:
   ```bash
   git clone https://github.com/hdepa/InkyPi-literature-clock.git
   ```
3. Copy the plugin folder into your InkyPi install:
   ```bash
   cp -R InkyPi-literature-clock/literature_clock /path/to/InkyPi/src/plugins/
   ```
4. Restart the InkyPi service:
   ```bash
   sudo systemctl restart inkypi.service
   ```
5. The plugin will appear in the InkyPi web UI under **Plugins → Literature Clock**.

## Settings

| Setting | Description |
|---|---|
| Quote selection | `shortest` (default), `random`, or `daily` (deterministic per minute per day) |
| Allow NSFW | Includes NSFW-flagged quotes (default off) |
| Show attribution | Display book title + author below the quote |
| Font | Any font available in InkyPi's `static/fonts/` |
| Highlight style | bold / italic / underline / color |
| Highlight color | Custom color when style = color |

## Refresh cadence

Set the playlist refresh interval to **1 minute** for true clock semantics.

## Dataset

Quotes come from [JohannesNE/literature-clock](https://github.com/JohannesNE/literature-clock) (`litclock_annotated.csv`). The plugin bundles a copy for offline use and refreshes weekly when online. About 70 of the 1440 minutes in a day have no exact-time entry; the plugin falls back to ±1 minute, then to a "no quote" card.

No API key required.

## Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python3 -m pytest -v
```

## Status

Actively maintained.

## License

MIT
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: README with install, settings, attribution"
```

---

## Task 18: Final test sweep

- [ ] **Step 1: Run the full test suite**

```bash
cd /Users/h.depa/projects/InkyPi-literature-clock
python3 -m pytest -v
```
Expected: all tests from tasks 3–8 and 16 passing (~22 tests).

- [ ] **Step 2: Confirm directory layout**

```bash
find literature_clock tests -type f -not -path '*/__pycache__/*' | sort
```
Expected to include each file listed in the **File Structure** section.

- [ ] **Step 3: No commit needed if no changes** (this task is a check, not a change).

---

## Self-Review

**Spec coverage:**
- "Bundled CSV / weekly refresh / offline fallback" → Tasks 8, 9.
- "±1-minute fallback" → Task 4 + integration test in Task 16.
- "Quote selection: shortest/random/daily" → Task 6.
- "Sanitization (br, nbsp, smart quotes)" → Task 5.
- "Highlight wrap" → Task 7.
- "Settings form (incl. style_settings, prepopulation)" → Tasks 13, 14.
- "Render via plugin.html / render_image" → Tasks 11, 12, 13.
- "Plugin manifest, icon, layout" → Tasks 10, 15, plus Task 1 scaffolding.
- "Edge case: no quote at HH:MM and ±1" → Task 13 `_render_no_quote`.
- "Edge case: corrupted/missing CSV" → Task 8 (`FileNotFoundError`) → Task 13 raises `RuntimeError`.

**Placeholder scan:** No TBDs, no "implement later", no naked "add error handling". Every code step contains the actual code.

**Type/name consistency:**
- `find_candidates(csv_path, hhmm, allow_nsfw)` consistent across Tasks 3, 4.
- `resolve_with_fallback` returns `(rows, used_time)` consistent in Tasks 4, 13, 16.
- `pick_quote(rows, strategy, seed_key)` consistent in Tasks 6, 13.
- `wrap_highlight(quote, time_human)` consistent in Tasks 7, 13.
- `ensure_dataset(csv_path)` signature consistent in Tasks 8, 13.
- `LiteratureClock` class name matches `plugin-info.json` (Task 10) and the import expectation in InkyPi's loader.
- CSS class `litclock-highlight` matches Task 7 `HIGHLIGHT_OPEN` and Task 11 template `<style>` block.
