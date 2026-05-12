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
