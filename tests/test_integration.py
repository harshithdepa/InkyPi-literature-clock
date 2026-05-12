from pathlib import Path
from literature_clock.quote_picker import (
    resolve_with_fallback,
    sanitize,
    pick_quote,
    wrap_highlight,
)

BUNDLED_CSV = Path(__file__).parent.parent / "literature_clock" / "data" / "litclock_annotated.csv"


def test_bundled_csv_resolves_known_minute():
    rows, _used_time = resolve_with_fallback(BUNDLED_CSV, "07:00", allow_nsfw=False)
    assert rows, "expected at least one quote near 07:00"
    chosen = pick_quote(rows, strategy="shortest", seed_key="x")
    quote = sanitize(chosen["full_quote"])
    assert len(quote) > 0
    out = wrap_highlight(quote, sanitize(chosen["time_human"]))
    assert isinstance(out, str)


def test_bundled_csv_every_minute_has_resolution_within_pm1():
    """Every minute of the day should yield a quote with ±1 fallback (allowing a small gap)."""
    misses = []
    for h in range(24):
        for m in range(60):
            rows, _ = resolve_with_fallback(BUNDLED_CSV, f"{h:02d}:{m:02d}", allow_nsfw=True)
            if not rows:
                misses.append(f"{h:02d}:{m:02d}")
    assert len(misses) < 50, f"too many unresolvable minutes: {misses[:10]}..."
