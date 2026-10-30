from __future__ import annotations

from typing import Any, Mapping

import pandas as pd

from src.race_engine.synchronization import get_latest_before_row, get_nearest_row


def _coerce_datasets(datasets):
    if datasets is None:
        raise ValueError("A dataset mapping or RaceDataLoader instance is required.")

    if hasattr(datasets, "data") and isinstance(datasets.data, Mapping):
        return datasets.data

    if isinstance(datasets, Mapping):
        return dict(datasets)

    raise TypeError("Expected a dataset mapping or RaceDataLoader instance.")


def to_python_value(value):
    """
    Convert NumPy/Pandas values into normal Python values.
    """

    if value is None:
        return None

    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass

    if isinstance(value, pd._libs.missing.NAType):
        return None

    if hasattr(value, "item") and not isinstance(value, (str, bytes)):
        try:
            return value.item()
        except (TypeError, ValueError):
            pass

    return value


class DriverSnapshotEngine:
    """Reusable driver snapshot builder using race datasets."""

    def __init__(self, datasets):
        self.datasets = datasets

    def snapshot(self, driver_number, target_lap):
        return get_driver_snapshot(driver_number, target_lap, self.datasets)


def get_driver_snapshot(driver_number, target_lap, datasets):
    """
    Build a synchronized race-state snapshot for one driver
    at the start of a target lap.

    Current limitation:
    telemetry and location data are currently available
    only for driver #44 (Hamilton).
    """

    data = _coerce_datasets(datasets)

    drivers = data["drivers"]
    laps = data["laps"]
    positions = data["positions"]
    intervals = data["intervals"]
    stints = data["stints"]
    telemetry = data.get("telemetry", data.get("sample_telemetry"))
    location = data.get("location", data.get("sample_location"))
    weather = data["weather"]

    # ==========================================================
    # 1. DRIVER INFORMATION
    # ==========================================================

    driver_info = drivers[drivers["driver_number"] == driver_number]

    if driver_info.empty:
        return {"error": f"Driver {driver_number} not found."}

    driver_info = driver_info.iloc[0]

    driver_acronym = driver_info["name_acronym"]
    driver_name = driver_info["full_name"]
    team_name = driver_info["team_name"]

    # ==========================================================
    # 2. TARGET LAP
    # ==========================================================

    driver_laps = laps[laps["driver_number"] == driver_number].copy()

    lap_data = driver_laps[driver_laps["lap_number"] == target_lap]

    if lap_data.empty:
        return {"error": f"Lap {target_lap} not found for driver {driver_number}."}

    lap_row = lap_data.iloc[0]

    lap_timestamp = lap_row["date_start"]

    if pd.isna(lap_timestamp):
        return {"error": f"Lap {target_lap} has no valid timestamp."}

    # ==========================================================
    # 3. POSITION
    # ==========================================================

    driver_positions = positions[positions["driver_number"] == driver_number].copy()

    position_row, position_age = get_latest_before_row(driver_positions, lap_timestamp)

    # ==========================================================
    # 4. INTERVAL / GAP TO LEADER
    # ==========================================================

    driver_intervals = intervals[intervals["driver_number"] == driver_number].copy()

    interval_row, interval_age = get_latest_before_row(driver_intervals, lap_timestamp)

    # ==========================================================
    # 5. TYRE STINT
    # ==========================================================

    driver_stints = stints[stints["driver_number"] == driver_number].copy()

    stint_data = driver_stints[
        (driver_stints["lap_start"] <= target_lap)
        & (driver_stints["lap_end"].isna() | (driver_stints["lap_end"] >= target_lap))
    ]

    compound = None
    tyre_age = None
    stint_number = None

    if not stint_data.empty:
        stint_row = stint_data.iloc[0]

        compound = stint_row["compound"]

        stint_number = to_python_value(stint_row["stint_number"])

        if pd.notna(stint_row["tyre_age_at_start"]) and pd.notna(stint_row["lap_start"]):
            tyre_age = stint_row["tyre_age_at_start"] + (target_lap - stint_row["lap_start"])

    # ==========================================================
    # 6. TELEMETRY
    # ==========================================================

    driver_telemetry = telemetry[telemetry["driver_number"] == driver_number].copy() if telemetry is not None and "driver_number" in telemetry.columns else telemetry.copy() if telemetry is not None else pd.DataFrame()

    telemetry_row, telemetry_offset = get_nearest_row(driver_telemetry, lap_timestamp)

    # ==========================================================
    # 7. LOCATION
    # ==========================================================

    driver_location = location[location["driver_number"] == driver_number].copy() if location is not None and "driver_number" in location.columns else location.copy() if location is not None else pd.DataFrame()

    location_row, location_offset = get_nearest_row(driver_location, lap_timestamp)

    # ==========================================================
    # 8. WEATHER
    # ==========================================================

    weather_row, weather_age = get_latest_before_row(weather, lap_timestamp)

    # ==========================================================
    # 9. BUILD FINAL SNAPSHOT
    # ==========================================================

    snapshot = {
        # -----------------------
        # DRIVER
        # -----------------------

        "driver_number": int(driver_number),
        "driver": driver_acronym,
        "driver_name": driver_name,
        "team": team_name,

        # -----------------------
        # LAP
        # -----------------------

        "lap": int(target_lap),
        "lap_timestamp": lap_timestamp.isoformat(),
        "lap_time": float(lap_row["lap_duration"]) if pd.notna(lap_row["lap_duration"]) else None,

        # -----------------------
        # POSITION
        # -----------------------

        "position": int(position_row["position"]) if position_row is not None and pd.notna(position_row["position"]) else None,

        # -----------------------
        # GAP / INTERVAL
        # -----------------------

        "gap_to_leader": to_python_value(interval_row["gap_to_leader"]) if interval_row is not None else None,
        "interval": to_python_value(interval_row["interval"]) if interval_row is not None else None,

        # -----------------------
        # TYRES
        # -----------------------

        "stint_number": stint_number,
        "compound": compound,
        "tyre_age": int(tyre_age) if tyre_age is not None and pd.notna(tyre_age) else None,

        # -----------------------
        # TELEMETRY
        # -----------------------

        "speed": int(telemetry_row["speed"]) if telemetry_row is not None and pd.notna(telemetry_row["speed"]) else None,
        "throttle": int(telemetry_row["throttle"]) if telemetry_row is not None and pd.notna(telemetry_row["throttle"]) else None,
        "brake": int(telemetry_row["brake"]) if telemetry_row is not None and pd.notna(telemetry_row["brake"]) else None,
        "gear": int(telemetry_row["n_gear"]) if telemetry_row is not None and pd.notna(telemetry_row["n_gear"]) else None,
        "rpm": int(telemetry_row["rpm"]) if telemetry_row is not None and pd.notna(telemetry_row["rpm"]) else None,
        "drs": int(telemetry_row["drs"]) if telemetry_row is not None and pd.notna(telemetry_row["drs"]) else None,

        # -----------------------
        # LOCATION
        # -----------------------

        "x": float(location_row["x"]) if location_row is not None and pd.notna(location_row["x"]) else None,
        "y": float(location_row["y"]) if location_row is not None and pd.notna(location_row["y"]) else None,
        "z": float(location_row["z"]) if location_row is not None and pd.notna(location_row["z"]) else None,

        # -----------------------
        # WEATHER
        # -----------------------

        "track_temperature": float(weather_row["track_temperature"]) if weather_row is not None and pd.notna(weather_row["track_temperature"]) else None,
        "air_temperature": float(weather_row["air_temperature"]) if weather_row is not None and pd.notna(weather_row["air_temperature"]) else None,
        "rainfall": float(weather_row["rainfall"]) if weather_row is not None and pd.notna(weather_row["rainfall"]) else None,
        "humidity": float(weather_row["humidity"]) if weather_row is not None and pd.notna(weather_row["humidity"]) else None,

        # -----------------------
        # SYNCHRONIZATION INFO
        # -----------------------

        "sync_delta_seconds": {
            "position_last_update": round(position_age, 3) if position_age is not None else None,
            "interval_last_update": round(interval_age, 3) if interval_age is not None else None,
            "telemetry_nearest": round(telemetry_offset, 3) if telemetry_offset is not None else None,
            "location_nearest": round(location_offset, 3) if location_offset is not None else None,
            "weather_last_update": round(weather_age, 3) if weather_age is not None else None,
        },
    }

    return snapshot


__all__ = ["DriverSnapshotEngine", "get_driver_snapshot", "to_python_value"]
