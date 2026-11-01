# Project Progress

This document explains in simple language what is in place and what still needs
to be done for the F1 Race Intelligence / Virtual Pit Wall project.

## Latest update — 2026-11-01

Milestones 2.3A and 2.3B are complete. The project can discover OpenF1 sessions,
request individual datasets for a selected session, and validate and normalize
the returned records without changing their dataset-specific shape.

## Project data

The current reference event is the 2025 Chinese Grand Prix in Shanghai:

- Session key: `9998`
- Sample driver: Lewis Hamilton, driver number `44`

The saved raw data includes drivers, laps, positions, intervals, stints, pit
stops, race-control messages, weather, car telemetry, and approximate car
locations. The data dictionary describes the main fields and how these datasets
are used.

Each dataset keeps its own purpose and structure. For example, a weather
observation is not a driver observation, and telemetry and location are
high-frequency samples rather than one summary per driver.

## What has been built

### OpenF1 access and session discovery

- `src/openf1/client.py` provides the shared HTTP client for OpenF1.
- It returns lists of JSON records and raises specific errors for request,
  connection, HTTP, timeout, and response problems.
- `src/openf1/session_service.py` discovers available seasons, meetings,
  sessions, and session drivers.
- `src/openf1/session_data_service.py` retrieves one chosen dataset for a
  selected session. It supports the ten datasets listed below, optional driver
  filtering, and additional OpenF1 query parameters.
- The selected `session_key` is always used, even if an additional filter tries
  to provide a different one.
- High-frequency `car_data` and `location` are requested individually. They
  are not automatically fetched for every driver.

Supported dataset endpoints:

- `drivers`
- `laps`
- `position`
- `intervals`
- `stints`
- `pit`
- `race_control`
- `weather`
- `car_data`
- `location`

### Dataset validation and timestamp handling

`src/data/session_dataset.py` provides
`process_session_dataset(dataset, records, session_key)`.

- It checks the selected session key and reports when a returned record has a
  missing, invalid, or different session key.
- It uses explicit timestamp fields for each dataset. Laps use `date_start`;
  position, intervals, pit, race control, weather, car data, and location use
  `date`. Drivers and stints have no timestamp field in this processing step.
- Valid timezone-aware timestamps are converted to UTC while preserving the
  actual instant.
- Missing and null timestamps stay missing.
- Malformed timestamps stay in the returned records and are reported.
- Timezone-naive timestamps are kept as they are and reported as ambiguous;
  the processor does not guess their timezone.
- Issues include the dataset, record index, field, original value, code,
  severity, and a message.
- Errors make the result invalid. Warnings alone do not.

The processor preserves record count and order, nested data, dataset-specific
fields, missing values, and meaningful numeric zeros. It does not discard
records, aggregate, deduplicate, resample, or flatten values.

### Existing data tools

- `src/data/loader.py` loads the saved raw CSV files and normalizes columns that
  look like timestamps. Its existing conversion uses pandas and can turn
  malformed timestamps into missing datetime values; the new session dataset
  processor reports malformed values without changing the source record.
- `src/race_engine/synchronization.py` provides helpers to select the nearest
  observation or the latest observation before a target time. It skips rows
  whose timestamp is missing.
- The API client, session discovery service, CSV loader, and race engine were
  not changed as part of milestones 2.3A or 2.3B.

## Tests and checks

Tests use mocked API clients or in-memory records, so they do not require a live
OpenF1 connection. Coverage includes:

- OpenF1 request parameters and client errors.
- Session and dataset retrieval, including all ten endpoints.
- Invalid and overridden session keys, driver filters, empty results, and
  propagated API exceptions.
- Timestamp conversion, timezone offsets, missing and malformed timestamps,
  and timezone-naive timestamps.
- Session-key matches, mismatches, missing values, and malformed values.
- Preservation of record order, nested sector data, missing telemetry, zeros,
  and high-frequency observations.
- Existing CSV loader and race synchronization behavior.

The last full test run completed with **99 passed**. Python syntax checks passed
for the new processing module and its tests, and `git diff --check` reported no
whitespace errors.

## Current status

The project has working building blocks for retrieving session data and
checking records before they are used. The existing CSV loader and race engine
remain separate; the new session-data processor does not automatically feed
either one.

## Remaining work

The next work should be chosen based on project priorities. Possible next steps
include:

- Decide how the new processor should be used by later data workflows.
- Add further transformation or analysis steps when their requirements are
  defined.
- Build replay, strategy-analysis, or dashboard features when they are in
  scope.
- Continue documenting limitations and verify assumptions against the OpenF1
  endpoint documentation as its data contracts become clearer.

No caching, pagination, API routes, frontend work, or race-state reconstruction
has been added in these milestones.
