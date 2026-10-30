from pathlib import Path

import pandas as pd
import pytest

from src.data.loader import RaceDataLoader


def _write_required_csvs(raw_dir: Path, *, omit: str | None = None) -> None:
    for filename in RaceDataLoader.DATASET_FILES.values():
        if filename == omit:
            continue
        pd.DataFrame(
            {
                "date": ["2025-03-16T04:00:00Z"],
                "lap_time": [90.5],
            }
        ).to_csv(raw_dir / filename, index=False)


def test_loads_all_configured_datasets_and_normalizes_timestamps(tmp_path):
    _write_required_csvs(tmp_path)

    loader = RaceDataLoader(raw_dir=tmp_path)

    assert set(loader.datasets) == set(RaceDataLoader.DATASET_FILES)
    assert all(isinstance(frame, pd.DataFrame) for frame in loader.datasets.values())
    assert loader.drivers.loc[0, "date"] == pd.Timestamp("2025-03-16T04:00:00Z")
    assert isinstance(loader.drivers["date"].dtype, pd.DatetimeTZDtype)
    assert str(loader.drivers["date"].dt.tz) == "UTC"
    assert loader.drivers.loc[0, "lap_time"] == 90.5


def test_missing_required_csv_raises_file_not_found_error(tmp_path):
    missing_filename = RaceDataLoader.DATASET_FILES["weather"]
    _write_required_csvs(tmp_path, omit=missing_filename)

    with pytest.raises(FileNotFoundError, match=missing_filename):
        RaceDataLoader(raw_dir=tmp_path)
