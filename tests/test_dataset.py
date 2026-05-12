import os
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
    os.utime(csv_path, (old_mtime, old_mtime))

    with patch("literature_clock.dataset.requests.get", side_effect=Exception("network down")):
        ensure_dataset(csv_path)  # must not raise
    assert csv_path.read_text() == "kept\n"


def test_ensure_dataset_raises_when_missing_and_offline(tmp_path):
    csv_path = tmp_path / "missing.csv"
    with patch("literature_clock.dataset.requests.get", side_effect=Exception("network down")):
        with pytest.raises(FileNotFoundError):
            ensure_dataset(csv_path)
