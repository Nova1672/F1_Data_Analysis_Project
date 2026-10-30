from unittest.mock import Mock

import pytest

from src.openf1.session_service import SessionService


def test_available_seasons_are_derived_from_meeting_metadata():
    client = Mock()
    client.get.return_value = [
        {"year": 2025, "meeting_key": 1},
        {"year": "2023", "meeting_key": 2},
        {"year": 2025, "meeting_key": 3},
        {"meeting_key": 4},
        {"year": "invalid", "meeting_key": 5},
    ]

    seasons = SessionService(client).get_available_seasons()

    assert seasons == [2023, 2025]
    client.get.assert_called_once_with("meetings")


def test_meetings_are_requested_and_filtered_by_selected_year():
    client = Mock()
    selected_meeting = {
        "meeting_key": 9998,
        "meeting_name": "Chinese Grand Prix",
        "year": 2025,
        "location": "Shanghai",
    }
    client.get.return_value = [
        selected_meeting,
        {"meeting_key": 9693, "meeting_name": "Australian Grand Prix", "year": 2025},
        {"meeting_key": 1, "meeting_name": "Other Season", "year": 2024},
    ]

    meetings = SessionService(client).get_meetings(2025)

    assert meetings == [selected_meeting, client.get.return_value[1]]
    assert meetings[0]["location"] == "Shanghai"
    client.get.assert_called_once_with("meetings", params={"year": 2025})


def test_sessions_use_selected_meeting_key_and_preserve_metadata():
    client = Mock()
    race_session = {
        "session_key": 9998,
        "meeting_key": 77,
        "session_name": "Race",
        "date_start": "2025-03-23T07:00:00+00:00",
    }
    client.get.return_value = [
        race_session,
        {"session_key": 4, "meeting_key": 78, "session_name": "Race"},
    ]

    sessions = SessionService(client).get_sessions(77)

    assert sessions == [race_session]
    client.get.assert_called_once_with("sessions", params={"meeting_key": 77})


def test_drivers_use_selected_session_key():
    client = Mock()
    selected_driver = {
        "session_key": 9998,
        "driver_number": 44,
        "full_name": "Lewis Hamilton",
        "team_name": "Ferrari",
    }
    client.get.return_value = [
        selected_driver,
        {"session_key": 9693, "driver_number": 44, "full_name": "Lewis Hamilton"},
    ]

    drivers = SessionService(client).get_drivers(9998)

    assert drivers == [selected_driver]
    client.get.assert_called_once_with("drivers", params={"session_key": 9998})


@pytest.mark.parametrize(
    ("method_name", "endpoint", "params"),
    [
        ("get_meetings", "meetings", {"year": 2025}),
        ("get_sessions", "sessions", {"meeting_key": 77}),
        ("get_drivers", "drivers", {"session_key": 9998}),
    ],
)
def test_empty_api_results_return_empty_lists(method_name, endpoint, params):
    client = Mock()
    client.get.return_value = []

    result = getattr(SessionService(client), method_name)(next(iter(params.values())))

    assert result == []
    client.get.assert_called_once_with(endpoint, params=params)


@pytest.mark.parametrize(
    ("method_name", "identifier"),
    [
        ("get_meetings", 0),
        ("get_sessions", 0),
        ("get_drivers", 0),
    ],
)
def test_invalid_identifiers_raise_clear_errors(method_name, identifier):
    client = Mock()

    with pytest.raises(ValueError, match="positive integer"):
        getattr(SessionService(client), method_name)(identifier)

    client.get.assert_not_called()


def test_empty_meeting_metadata_produces_no_available_seasons():
    client = Mock()
    client.get.return_value = []

    assert SessionService(client).get_available_seasons() == []
