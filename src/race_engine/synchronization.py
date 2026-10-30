from __future__ import annotations

import pandas as pd


def get_nearest_row(df, target_time, time_column="date"):
    """
    Return the row closest to target_time.

    Useful for high-frequency datasets such as
    telemetry and location.

    Returns:
        nearest_row
        time_difference_seconds
    """

    if df.empty:
        return None, None

    valid_df = df.dropna(subset=[time_column]).copy()

    if valid_df.empty:
        return None, None

    differences = (valid_df[time_column] - target_time).abs()

    nearest_index = differences.idxmin()

    nearest_row = valid_df.loc[nearest_index]

    time_difference_seconds = differences.loc[nearest_index].total_seconds()

    return nearest_row, time_difference_seconds


def get_latest_before_row(df, target_time, time_column="date"):
    """
    Return the latest available row at or before target_time.

    This avoids using future information when recreating
    historical race state.

    Returns:
        row
        seconds_since_last_update
    """

    if df.empty:
        return None, None

    valid_df = df.dropna(subset=[time_column]).copy()

    if valid_df.empty:
        return None, None

    previous_rows = valid_df[valid_df[time_column] <= target_time]

    if previous_rows.empty:
        return None, None

    latest_index = previous_rows[time_column].idxmax()

    latest_row = previous_rows.loc[latest_index]

    time_difference_seconds = (target_time - latest_row[time_column]).total_seconds()

    return latest_row, time_difference_seconds


__all__ = ["get_nearest_row", "get_latest_before_row"]
