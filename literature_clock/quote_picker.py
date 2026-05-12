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
