from datetime import datetime, timezone

import pytest

from src.data.session_dataset import (
    DatasetProcessingResult,
    ValidationIssue,
    process_session_dataset,
)


@pytest.mark.parametrize(
    "dataset",
    [
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
    ],
)
def test_processes_each_supported_dataset_without_forcing_a_schema(dataset):
    source_record = {
        "session_key": 123,
        "custom_dataset_field": {"nested": [1, None]},
    }

    result = process_session_dataset(dataset, [source_record], 123)

    assert isinstance(result, DatasetProcessingResult)
    assert result.records == [source_record]
    assert result.records[0] is not source_record
    assert result.records[0]["custom_dataset_field"] is source_record[
        "custom_dataset_field"
    ]
    assert result.issues == []
    assert result.record_count == 1
    assert result.is_valid


@pytest.mark.parametrize(
    ("timestamp", "expected"),
    [
        (
            "2025-03-23T06:04:41.948000Z",
            datetime(2025, 3, 23, 6, 4, 41, 948000, tzinfo=timezone.utc),
        ),
        (
            "2025-03-23T08:04:41+02:00",
            datetime(2025, 3, 23, 6, 4, 41, tzinfo=timezone.utc),
        ),
        (
            "2025-03-23T01:04:41-05:00",
            datetime(2025, 3, 23, 6, 4, 41, tzinfo=timezone.utc),
        ),
    ],
)
def test_timestamp_strings_are_normalized_to_utc(timestamp, expected):
    result = process_session_dataset(
        "position",
        [{"session_key": 123, "date": timestamp}],
        123,
    )

    assert result.records[0]["date"] == expected
    assert result.records[0]["date"].tzinfo is timezone.utc
    assert result.issues == []


def test_laps_use_date_start_for_timestamp_normalization():
    result = process_session_dataset(
        "laps",
        [{"session_key": 123, "date_start": "2025-03-23T08:00:00+02:00"}],
        123,
    )

    assert result.records[0]["date_start"] == datetime(
        2025, 3, 23, 6, 0, tzinfo=timezone.utc
    )


@pytest.mark.parametrize("value", [None])
def test_null_timestamp_is_preserved(value):
    result = process_session_dataset(
        "weather",
        [{"session_key": 123, "date": value}],
        123,
    )

    assert result.records[0]["date"] is value
    assert result.issues == []


def test_missing_timestamp_field_is_preserved_without_inventing_a_value():
    record = {"session_key": 123, "temperature": 0}

    result = process_session_dataset("weather", [record], 123)

    assert result.records == [record]
    assert "date" not in result.records[0]
    assert result.issues == []


def test_malformed_timestamp_is_reported_and_original_record_is_retained():
    invalid_value = "yesterday-ish"
    record = {"session_key": 123, "date": invalid_value, "reading": 0}

    result = process_session_dataset("location", [record], 123)

    assert result.records == [record]
    assert result.record_count == 1
    assert result.issues == [
        ValidationIssue(
            dataset="location",
            record_index=0,
            field="date",
            original_value=invalid_value,
            code="malformed_timestamp",
            severity="error",
            message="Timestamp is not a valid timezone-aware ISO-8601 value.",
        )
    ]
    assert not result.is_valid


def test_timezone_naive_timestamp_is_retained_and_reported_as_ambiguous():
    value = "2025-03-23T06:04:41"

    result = process_session_dataset(
        "intervals",
        [{"session_key": 123, "date": value}],
        123,
    )

    assert result.records[0]["date"] == value
    assert result.issues[0].code == "ambiguous_timestamp"
    assert result.issues[0].severity == "warning"
    assert result.issues[0].original_value == value
    assert result.is_valid


def test_aware_datetime_input_is_normalized_and_naive_datetime_is_ambiguous():
    aware = datetime.fromisoformat("2025-03-23T08:00:00+02:00")
    naive = datetime(2025, 3, 23, 8, 0)

    result = process_session_dataset(
        "pit",
        [
            {"session_key": 123, "date": aware},
            {"session_key": 123, "date": naive},
        ],
        123,
    )

    assert result.records[0]["date"] == datetime(
        2025, 3, 23, 6, 0, tzinfo=timezone.utc
    )
    assert result.records[1]["date"] is naive
    assert [(issue.record_index, issue.code) for issue in result.issues] == [
        (1, "ambiguous_timestamp")
    ]


def test_dataset_without_timestamp_mapping_does_not_infer_date_field():
    record = {"session_key": 123, "date": "not parsed"}

    result = process_session_dataset("drivers", [record], 123)

    assert result.records[0]["date"] == "not parsed"
    assert result.issues == []


def test_matching_session_keys_are_valid():
    result = process_session_dataset(
        "drivers",
        [{"session_key": 123}],
        123,
    )

    assert result.issues == []
    assert result.is_valid


def test_mismatching_session_key_is_reported_without_discarding_record():
    record = {"session_key": 456, "driver_number": 44}

    result = process_session_dataset("drivers", [record], 123)

    assert result.records == [record]
    assert result.issues[0].code == "session_key_mismatch"
    assert result.issues[0].severity == "error"
    assert result.issues[0].record_index == 0
    assert result.issues[0].original_value == 456
    assert not result.is_valid


def test_missing_session_key_produces_a_nonfatal_warning():
    result = process_session_dataset("weather", [{"date": None}], 123)

    assert result.issues == [
        ValidationIssue(
            dataset="weather",
            record_index=0,
            field="session_key",
            original_value=None,
            code="missing_session_key",
            severity="warning",
            message="Session consistency cannot be verified.",
        )
    ]
    assert result.is_valid


@pytest.mark.parametrize("value", [None, 0, -5, True, 123.0, "123"])
def test_malformed_record_session_key_is_reported(value):
    result = process_session_dataset(
        "stints",
        [{"session_key": value}],
        123,
    )

    assert result.issues[0].code == "malformed_session_key"
    assert result.issues[0].severity == "error"
    assert result.issues[0].record_index == 0
    assert result.issues[0].original_value == value
    assert not result.is_valid


@pytest.mark.parametrize("session_key", [0, -1, True, 123.0, "123", None])
def test_invalid_selected_session_key_raises_value_error(session_key):
    with pytest.raises(ValueError, match="session_key must be a positive integer"):
        process_session_dataset("drivers", [], session_key)


def test_unsupported_dataset_raises_value_error():
    with pytest.raises(ValueError, match="Unsupported OpenF1 dataset"):
        process_session_dataset("telemetry", [], 123)


def test_record_count_order_and_nested_values_are_preserved():
    records = [
        {
            "session_key": 123,
            "lap_number": 2,
            "segments_sector_1": [2048, {"status": None}],
        },
        {
            "session_key": 123,
            "lap_number": 1,
            "segments_sector_2": [2051, 2049],
        },
    ]

    result = process_session_dataset("laps", records, 123)

    assert result.record_count == 2
    assert [record["lap_number"] for record in result.records] == [2, 1]
    assert result.records[0]["segments_sector_1"] == [2048, {"status": None}]
    assert result.records[1]["segments_sector_2"] == [2051, 2049]


def test_missing_telemetry_and_meaningful_zeros_are_preserved():
    record = {
        "session_key": 123,
        "date": "2025-03-23T06:04:41Z",
        "speed": 0,
        "throttle": None,
        "brake": 0,
    }

    result = process_session_dataset("car_data", [record], 123)

    assert result.records[0]["speed"] == 0
    assert result.records[0]["throttle"] is None
    assert result.records[0]["brake"] == 0
    assert result.record_count == 1


def test_high_frequency_observations_are_not_aggregated_or_deduplicated():
    records = [
        {"session_key": 123, "date": "2025-03-23T06:04:41Z", "x": 0},
        {"session_key": 123, "date": "2025-03-23T06:04:41.100Z", "x": 0},
        {"session_key": 123, "date": "2025-03-23T06:04:41.200Z", "x": 1},
    ]

    result = process_session_dataset("location", records, 123)

    assert result.record_count == 3
    assert [record["x"] for record in result.records] == [0, 0, 1]
    assert [record["date"].microsecond for record in result.records] == [
        0,
        100000,
        200000,
    ]


def test_race_control_without_driver_number_is_valid():
    record = {
        "session_key": 123,
        "date": "2025-03-23T06:20:01Z",
        "category": "Flag",
        "flag": "GREEN",
        "message": "GREEN LIGHT",
    }

    result = process_session_dataset("race_control", [record], 123)

    assert result.records[0]["date"] == datetime(
        2025, 3, 23, 6, 20, 1, tzinfo=timezone.utc
    )
    assert "driver_number" not in result.records[0]
    assert result.is_valid
