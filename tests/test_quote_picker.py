from pathlib import Path
from literature_clock.quote_picker import find_candidates, resolve_with_fallback

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


def test_resolve_uses_exact_match_when_present():
    rows, used_time = resolve_with_fallback(FIXTURE, "07:32", allow_nsfw=False)
    assert used_time == "07:32"
    assert len(rows) == 2


def test_resolve_falls_back_to_minus_one_minute():
    # 23:58 empty; 23:59 exists; 23:57 empty -> -1 wins
    rows, used_time = resolve_with_fallback(FIXTURE, "23:58", allow_nsfw=False)
    assert used_time == "23:59"
    assert len(rows) == 1


def test_resolve_falls_back_to_plus_one_minute_when_minus_empty():
    # 11:59 empty; 11:58 empty; 12:00 exists -> +1 wins
    rows, used_time = resolve_with_fallback(FIXTURE, "11:59", allow_nsfw=False)
    assert used_time == "12:00"


def test_resolve_returns_none_when_all_three_empty():
    rows, used_time = resolve_with_fallback(FIXTURE, "09:00", allow_nsfw=False)
    assert rows == []
    assert used_time is None


def test_resolve_handles_hour_wrap_at_midnight():
    # 00:01 empty; 00:00 exists -> -1 from 00:01 = 00:00 wins.
    rows, used_time = resolve_with_fallback(FIXTURE, "00:01", allow_nsfw=False)
    assert used_time == "00:00"


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
