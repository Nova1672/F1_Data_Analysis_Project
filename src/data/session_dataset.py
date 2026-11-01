"""Dataset-specific validation and timestamp normalization."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable, Literal, Mapping


_TIMESTAMP_FIELDS = {
    "drivers": None,
    "laps": "date_start",
    "position": "date",
    "intervals": "date",
    "stints": None,
    "pit": "date",
    "race_control": "date",
    "weather": "date",
    "car_data": "date",
    "location": "date",
}


@dataclass(frozen=True)
class ValidationIssue:
    """A validation finding attached to one input record."""

    dataset: str
    record_index: int
    field: str
    original_value: Any
    code: str
    severity: Literal["error", "warning"]
    message: str


@dataclass(frozen=True)
class DatasetProcessingResult:
    """Processed records and validation findings for one dataset."""

    records: list[dict[str, Any]]
    issues: list[ValidationIssue]

    @property
    def record_count(self) -> int:
        return len(self.records)

    @property
    def is_valid(self) -> bool:
        return not any(issue.severity == "error" for issue in self.issues)


def _validate_selected_session_key(session_key: int) -> None:
    if (
        isinstance(session_key, bool)
        or not isinstance(session_key, int)
        or session_key <= 0
    ):
        raise ValueError("session_key must be a positive integer.")


def _normalize_timestamp(value: Any) -> tuple[datetime | None, str | None]:
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError:
            return None, "malformed_timestamp"
    else:
        return None, "malformed_timestamp"

    if parsed.utcoffset() is None:
        return None, "ambiguous_timestamp"

    try:
        return parsed.astimezone(timezone.utc), None
    except (OverflowError, ValueError):
        return None, "malformed_timestamp"


def process_session_dataset(
    dataset: str,
    records: Iterable[Mapping[str, Any]],
    session_key: int,
) -> DatasetProcessingResult:
    """Normalize documented timestamps and report record-level consistency issues."""
    if not isinstance(dataset, str) or dataset not in _TIMESTAMP_FIELDS:
        raise ValueError(f"Unsupported OpenF1 dataset: {dataset!r}.")
    _validate_selected_session_key(session_key)

    processed_records: list[dict[str, Any]] = []
    issues: list[ValidationIssue] = []
    timestamp_field = _TIMESTAMP_FIELDS[dataset]

    for record_index, record in enumerate(records):
        if not isinstance(record, Mapping):
            raise TypeError("records must contain mapping objects.")
        processed = dict(record)

        if "session_key" not in record:
            issues.append(
                ValidationIssue(
                    dataset=dataset,
                    record_index=record_index,
                    field="session_key",
                    original_value=None,
                    code="missing_session_key",
                    severity="warning",
                    message="Session consistency cannot be verified.",
                )
            )
        else:
            record_session_key = record["session_key"]
            if (
                isinstance(record_session_key, bool)
                or not isinstance(record_session_key, int)
                or record_session_key <= 0
            ):
                issues.append(
                    ValidationIssue(
                        dataset=dataset,
                        record_index=record_index,
                        field="session_key",
                        original_value=record_session_key,
                        code="malformed_session_key",
                        severity="error",
                        message="session_key must be a positive integer.",
                    )
                )
            elif record_session_key != session_key:
                issues.append(
                    ValidationIssue(
                        dataset=dataset,
                        record_index=record_index,
                        field="session_key",
                        original_value=record_session_key,
                        code="session_key_mismatch",
                        severity="error",
                        message=(
                            f"Record belongs to session {record_session_key}, "
                            f"not selected session {session_key}."
                        ),
                    )
                )

        if timestamp_field is not None and timestamp_field in record:
            original_value = record[timestamp_field]
            if original_value is not None:
                normalized, issue_code = _normalize_timestamp(original_value)
                if issue_code is None:
                    processed[timestamp_field] = normalized
                else:
                    severity: Literal["error", "warning"] = (
                        "warning"
                        if issue_code == "ambiguous_timestamp"
                        else "error"
                    )
                    message = (
                        "Timestamp has no timezone and is ambiguous."
                        if issue_code == "ambiguous_timestamp"
                        else "Timestamp is not a valid timezone-aware ISO-8601 value."
                    )
                    issues.append(
                        ValidationIssue(
                            dataset=dataset,
                            record_index=record_index,
                            field=timestamp_field,
                            original_value=original_value,
                            code=issue_code,
                            severity=severity,
                            message=message,
                        )
                    )

        processed_records.append(processed)

    return DatasetProcessingResult(records=processed_records, issues=issues)


__all__ = [
    "DatasetProcessingResult",
    "ValidationIssue",
    "process_session_dataset",
]
