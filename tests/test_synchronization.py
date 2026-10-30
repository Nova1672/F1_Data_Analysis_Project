import pandas as pd
import pytest

from src.race_engine.synchronization import (
    get_latest_before_row,
    get_nearest_row,
)


@pytest.fixture
def observations():
    return pd.DataFrame(
        {
            "date": pd.to_datetime(
                [
                    "2025-03-16T04:00:00Z",
                    "2025-03-16T04:00:05Z",
                    "2025-03-16T04:00:12Z",
                ],
                utc=True,
            ),
            "value": [10, 20, 30],
        }
    )


def test_latest_before_returns_latest_prior_observation_and_age(observations):
    target = pd.Timestamp("2025-03-16T04:00:08Z")

    row, age_seconds = get_latest_before_row(observations, target)

    assert row["value"] == 20
    assert age_seconds == pytest.approx(3.0)


def test_latest_before_does_not_use_future_observations(observations):
    target = pd.Timestamp("2025-03-16T03:59:59Z")

    row, age_seconds = get_latest_before_row(observations, target)

    assert row is None
    assert age_seconds is None


def test_nearest_returns_closest_observation_and_absolute_difference(observations):
    target = pd.Timestamp("2025-03-16T04:00:08Z")

    row, difference_seconds = get_nearest_row(observations, target)

    assert row["value"] == 20
    assert difference_seconds == pytest.approx(3.0)


def test_nearest_can_select_a_future_observation(observations):
    target = pd.Timestamp("2025-03-16T04:00:10Z")

    row, difference_seconds = get_nearest_row(observations, target)

    assert row["value"] == 30
    assert difference_seconds == pytest.approx(2.0)


@pytest.mark.parametrize(
    "selector",
    [get_latest_before_row, get_nearest_row],
)
def test_empty_dataframe_returns_no_row(selector):
    empty = pd.DataFrame(columns=["date", "value"])

    row, difference_seconds = selector(
        empty,
        pd.Timestamp("2025-03-16T04:00:00Z"),
    )

    assert row is None
    assert difference_seconds is None


@pytest.mark.parametrize(
    "selector",
    [get_latest_before_row, get_nearest_row],
)
def test_missing_timestamps_are_ignored(selector):
    observations = pd.DataFrame(
        {
            "date": [pd.NaT],
            "value": [10],
        }
    )

    row, difference_seconds = selector(
        observations,
        pd.Timestamp("2025-03-16T04:00:00Z"),
    )

    assert row is None
    assert difference_seconds is None
