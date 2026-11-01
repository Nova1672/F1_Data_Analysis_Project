"""Retrieve OpenF1 datasets for a selected session."""

from __future__ import annotations

from typing import Any, Mapping

from src.openf1.client import OpenF1Client


_SUPPORTED_DATASETS = frozenset(
    {
        "drivers",
        "laps",
        "position",
        "intervals",
        "stints",
        "pit",
        "race_control",
        "weather",
        "car_data",
        "location",
    }
)


def _validate_session_key(session_key: int) -> None:
    if (
        isinstance(session_key, bool)
        or not isinstance(session_key, int)
        or session_key <= 0
    ):
        raise ValueError("session_key must be a positive integer.")


class SessionDataService:
    """Fetch individual OpenF1 datasets for a selected session."""

    def __init__(self, client: OpenF1Client | None = None) -> None:
        self.client = client if client is not None else OpenF1Client()

    def get_dataset(
        self,
        dataset: str,
        session_key: int,
        *,
        driver_number: int | None = None,
        params: Mapping[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Return one dataset, enforcing the selected session in its filters."""
        if not isinstance(dataset, str) or dataset not in _SUPPORTED_DATASETS:
            raise ValueError(f"Unsupported OpenF1 dataset: {dataset!r}.")
        _validate_session_key(session_key)

        query_params = dict(params) if params is not None else {}
        if driver_number is not None:
            query_params["driver_number"] = driver_number
        query_params["session_key"] = session_key
        return self.client.get(dataset, params=query_params)


__all__ = ["SessionDataService"]
