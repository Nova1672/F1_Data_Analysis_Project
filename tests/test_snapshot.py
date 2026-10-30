from types import SimpleNamespace

import pandas as pd

from src.race_engine.snapshot import (
    DriverSnapshotEngine,
    get_driver_snapshot,
)


def _make_datasets():
    timestamp = pd.Timestamp("2025-03-16T04:00:00Z")
    return {
        "drivers": pd.DataFrame(
            [
                {
                    "driver_number": 44,
                    "name_acronym": "HAM",
                    "full_name": "Lewis Hamilton",
                    "team_name": "Ferrari",
                }
            ]
        ),
        "laps": pd.DataFrame(
            [
                {
                    "driver_number": 44,
                    "lap_number": 2,
                    "date_start": timestamp,
                    "lap_duration": 91.25,
                }
            ]
        ),
        "positions": pd.DataFrame(
            [
                {
                    "driver_number": 44,
                    "date": timestamp - pd.Timedelta(seconds=1),
                    "position": 3,
                }
            ]
        ),
        "intervals": pd.DataFrame(
            [
                {
                    "driver_number": 44,
                    "date": timestamp - pd.Timedelta(seconds=1),
                    "gap_to_leader": 2.5,
                    "interval": 1.2,
                }
            ]
        ),
        "stints": pd.DataFrame(
            [
                {
                    "driver_number": 44,
                    "lap_start": 1,
                    "lap_end": 5,
                    "stint_number": 1,
                    "compound": "MEDIUM",
                    "tyre_age_at_start": 0,
                }
            ]
        ),
        "sample_telemetry": pd.DataFrame(
            [
                {
                    "driver_number": 44,
                    "date": timestamp + pd.Timedelta(milliseconds=200),
                    "speed": 280,
                    "throttle": 95,
                    "brake": 0,
                    "n_gear": 7,
                    "rpm": 11000,
                    "drs": 1,
                }
            ]
        ),
        "sample_location": pd.DataFrame(
            [
                {
                    "driver_number": 44,
                    "date": timestamp,
                    "x": 1.5,
                    "y": 2.5,
                    "z": 0.0,
                }
            ]
        ),
        "weather": pd.DataFrame(
            [
                {
                    "date": timestamp - pd.Timedelta(seconds=2),
                    "track_temperature": 35.0,
                    "air_temperature": 22.0,
                    "rainfall": 0,
                    "humidity": 40.0,
                }
            ]
        ),
    }


def test_get_driver_snapshot_uses_injected_mapping_and_returns_key_fields():
    result = get_driver_snapshot(44, 2, _make_datasets())

    assert result["driver_number"] == 44
    assert result["driver"] == "HAM"
    assert result["driver_name"] == "Lewis Hamilton"
    assert result["team"] == "Ferrari"
    assert result["lap"] == 2
    assert result["lap_time"] == 91.25
    assert result["position"] == 3
    assert result["gap_to_leader"] == 2.5
    assert result["interval"] == 1.2
    assert result["compound"] == "MEDIUM"
    assert result["stint_number"] == 1
    assert result["tyre_age"] == 1
    assert result["speed"] == 280
    assert result["gear"] == 7
    assert result["x"] == 1.5
    assert result["track_temperature"] == 35.0
    assert result["sync_delta_seconds"]["position_last_update"] == 1.0
    assert result["sync_delta_seconds"]["telemetry_nearest"] == 0.2


def test_snapshot_engine_accepts_an_injected_loader_like_object():
    datasets = _make_datasets()

    result = DriverSnapshotEngine(SimpleNamespace(data=datasets)).snapshot(44, 2)

    assert result["driver"] == "HAM"
    assert result["lap"] == 2


def test_missing_driver_returns_error_result():
    result = get_driver_snapshot(7, 2, _make_datasets())

    assert result == {"error": "Driver 7 not found."}


def test_missing_lap_returns_error_result():
    result = get_driver_snapshot(44, 3, _make_datasets())

    assert result == {"error": "Lap 3 not found for driver 44."}
