from unittest.mock import Mock

import pytest

from src.openf1.session_data_service import SessionDataService


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
def test_each_supported_dataset_uses_selected_session(dataset):
    client = Mock()
    records = [{"driver_number": 44, "nested": {"value": None}}]
    client.get.return_value = records

    result = SessionDataService(client).get_dataset(dataset, 123)

    assert result is records
    client.get.assert_called_once_with(dataset, params={"session_key": 123})


def test_driver_number_and_additional_filters_are_forwarded():
    client = Mock()
    client.get.return_value = []
    filters = {"date_start": "2025-03-16T14:00:00+00:00", "lap_number": 12}

    result = SessionDataService(client).get_dataset(
        "car_data",
        123,
        driver_number=44,
        params=filters,
    )

    assert result == []
    client.get.assert_called_once_with(
        "car_data",
        params={
            "session_key": 123,
            "driver_number": 44,
            "date_start": "2025-03-16T14:00:00+00:00",
            "lap_number": 12,
        },
    )
    assert filters == {
        "date_start": "2025-03-16T14:00:00+00:00",
        "lap_number": 12,
    }


def test_additional_parameters_cannot_override_selected_session():
    client = Mock()
    client.get.return_value = []

    SessionDataService(client).get_dataset(
        "location",
        123,
        params={"session_key": 999, "driver_number": 44},
    )

    client.get.assert_called_once_with(
        "location",
        params={"session_key": 123, "driver_number": 44},
    )


@pytest.mark.parametrize("session_key", [0, -1, True, 123.0, "123", None])
def test_invalid_session_keys_raise_value_error_without_request(session_key):
    client = Mock()

    with pytest.raises(ValueError, match="session_key must be a positive integer"):
        SessionDataService(client).get_dataset("laps", session_key)

    client.get.assert_not_called()


@pytest.mark.parametrize("dataset", ["session", "telemetry", "", None, []])
def test_unsupported_datasets_raise_value_error_without_request(dataset):
    client = Mock()

    with pytest.raises(ValueError, match="Unsupported OpenF1 dataset"):
        SessionDataService(client).get_dataset(dataset, 123)

    client.get.assert_not_called()


def test_empty_api_response_is_returned_unchanged():
    client = Mock()
    client.get.return_value = []

    result = SessionDataService(client).get_dataset("laps", 123)

    assert result == []


def test_api_exceptions_are_propagated():
    client = Mock()
    error = RuntimeError("OpenF1 request failed")
    client.get.side_effect = error

    with pytest.raises(RuntimeError, match="OpenF1 request failed") as raised:
        SessionDataService(client).get_dataset("laps", 123)

    assert raised.value is error
