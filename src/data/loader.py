from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, Optional

import pandas as pd


class RaceDataLoader:
    """Load F1 race data from the saved CSV files in the raw data directory."""

    DATASET_FILES = {
        "drivers": "drivers.csv",
        "laps": "laps.csv",
        "positions": "positions.csv",
        "intervals": "intervals.csv",
        "stints": "stints.csv",
        "pits": "pits.csv",
        "race_control": "race_control.csv",
        "weather": "weather.csv",
        "sample_telemetry": "sample_telemetry.csv",
        "sample_location": "sample_location.csv",
    }

    def __init__(self, raw_dir: Optional[str | Path] = None):
        base_dir = Path(raw_dir) if raw_dir is not None else self._default_raw_dir()
        self.raw_dir = Path(base_dir)
        self.data = self.load_all()

    @staticmethod
    def _default_raw_dir() -> Path:
        return Path(__file__).resolve().parents[2] / "data" / "raw"

    @property
    def datasets(self) -> Dict[str, pd.DataFrame]:
        return self.data

    @property
    def drivers(self) -> pd.DataFrame:
        return self.data["drivers"]

    @property
    def laps(self) -> pd.DataFrame:
        return self.data["laps"]

    @property
    def positions(self) -> pd.DataFrame:
        return self.data["positions"]

    @property
    def intervals(self) -> pd.DataFrame:
        return self.data["intervals"]

    @property
    def stints(self) -> pd.DataFrame:
        return self.data["stints"]

    @property
    def pits(self) -> pd.DataFrame:
        return self.data["pits"]

    @property
    def race_control(self) -> pd.DataFrame:
        return self.data["race_control"]

    @property
    def weather(self) -> pd.DataFrame:
        return self.data["weather"]

    @property
    def sample_telemetry(self) -> pd.DataFrame:
        return self.data["sample_telemetry"]

    @property
    def sample_location(self) -> pd.DataFrame:
        return self.data["sample_location"]

    def __getitem__(self, name: str) -> pd.DataFrame:
        return self.data[name]

    def __getattr__(self, name: str) -> pd.DataFrame:
        if name in self.data:
            return self.data[name]
        raise AttributeError(f"{type(self).__name__!r} object has no attribute {name!r}")

    def get(self, name: str, default: Optional[pd.DataFrame] = None) -> Optional[pd.DataFrame]:
        return self.data.get(name, default)

    def load_all(self) -> Dict[str, pd.DataFrame]:
        loaded: Dict[str, pd.DataFrame] = {}

        for dataset_name, filename in self.DATASET_FILES.items():
            csv_path = self.raw_dir / filename
            if not csv_path.exists():
                raise FileNotFoundError(f"Missing raw CSV file: {csv_path}")

            frame = pd.read_csv(csv_path)
            frame = self._normalize_timestamp_columns(frame)
            loaded[dataset_name] = frame

        return loaded

    @staticmethod
    def _normalize_timestamp_columns(frame: pd.DataFrame) -> pd.DataFrame:
        normalized = frame.copy()

        for column_name in normalized.columns:
            if not RaceDataLoader._looks_like_datetime_column(column_name):
                continue

            normalized[column_name] = pd.to_datetime(
                normalized[column_name],
                format="mixed",
                utc=True,
                errors="coerce",
            )

        return normalized

    @staticmethod
    def _looks_like_datetime_column(column_name: str) -> bool:
        name = str(column_name).lower()

        if name in {"lap_time", "duration", "interval", "gap_to_leader"}:
            return False

        if any(token in name for token in ("date", "datetime", "timestamp")):
            return True

        if name.endswith("_at") or name.endswith("_on"):
            return True

        return False


__all__ = ["RaceDataLoader"]
