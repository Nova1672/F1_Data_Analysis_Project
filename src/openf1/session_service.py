"""Dynamic season, meeting, session, and driver discovery."""

from __future__ import annotations

from typing import Any

from src.openf1.client import OpenF1Client


def _validate_identifier(value: int, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer.")


def _metadata_integer(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


class SessionService:
    """Discover OpenF1 metadata while preserving each returned record."""

    def __init__(self, client: OpenF1Client | None = None) -> None:
        self.client = client if client is not None else OpenF1Client()

    def get_available_seasons(self) -> list[int]:
        """Return sorted unique years found in available meeting metadata."""
        meetings = self.client.get("meetings")
        years = {
            year
            for meeting in meetings
            if (year := _metadata_integer(meeting.get("year"))) is not None
        }
        return sorted(years)

    def get_meetings(self, year: int) -> list[dict[str, Any]]:
        """Return meetings for a selected season, retaining their metadata."""
        _validate_identifier(year, "year")
        meetings = self.client.get("meetings", params={"year": year})
        return [
            meeting
            for meeting in meetings
            if _metadata_integer(meeting.get("year")) == year
        ]

    def get_sessions(self, meeting_key: int) -> list[dict[str, Any]]:
        """Return sessions belonging to the selected meeting."""
        _validate_identifier(meeting_key, "meeting_key")
        sessions = self.client.get(
            "sessions",
            params={"meeting_key": meeting_key},
        )
        return [
            session
            for session in sessions
            if _metadata_integer(session.get("meeting_key")) == meeting_key
        ]

    def get_drivers(self, session_key: int) -> list[dict[str, Any]]:
        """Return drivers belonging to the selected session."""
        _validate_identifier(session_key, "session_key")
        drivers = self.client.get(
            "drivers",
            params={"session_key": session_key},
        )
        return [
            driver
            for driver in drivers
            if _metadata_integer(driver.get("session_key")) == session_key
        ]


__all__ = ["SessionService"]
