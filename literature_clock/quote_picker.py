import csv
from pathlib import Path
from datetime import datetime, timedelta

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
