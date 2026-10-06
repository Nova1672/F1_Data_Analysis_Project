# F1 Race Intelligence - Data Dictionary

## Reference Session
- Race: 2025 China Grand Prix - Shanghai
- Session Key: 9998
- Sample Driver: 44

---

## Drivers

One row represents one driver in the session.

Important columns:
- driver_number → unique driver number
- full_name → full driver name
- name_acronym → short code like HAM
- team_name → constructor/team
- team_colour → team UI color
- country_code → nationality
- headshot_url → driver image

Future use:
Driver cards, timing tower, team colors, driver profiles.

---

## Laps

One row represents one completed lap by one driver.

Important columns:
- driver_number
- lap_number
- date_start
- lap_duration
- duration_sector_1
- duration_sector_2
- duration_sector_3
- i1_speed
- i2_speed
- st_speed
- is_pit_out_lap
- segments_sector_1
- segments_sector_2
- segments_sector_3

Future use:
Lap timing, sector comparison, pace analysis, speed analysis.

---

## Positions

One row represents a driver's position at a specific timestamp.

Important columns:
- date
- driver_number
- position

Future use:
Live timing tower, position changes, replay.

---

## Intervals

One row represents timing gaps at a specific timestamp.

Important columns:
- date
- driver_number
- interval
- gap_to_leader

Future use:
Battles, gap closing, gap opening, timing tower.

---

## Stints

One row represents one tyre stint.

Important columns:
- stint_number
- driver_number
- lap_start
- lap_end
- compound
- tyre_age_at_start

Future use:
Tyre strategy, stint length, tyre age, pit strategy.

---

## Location

One row represents a driver's approximate track position at a timestamp.

Important columns:
- date
- driver_number
- x
- y
- z

Future use:
Track map and moving cars.

Note:
Position is approximate and should not be treated as exact racing-line data.

## Pit Stops

One row represents a pit event for a driver.

Important columns:
- date
- driver_number
- lap_number
- stop_duration
- lane_duration
- pit_duration

Future use:
Pit-stop analysis, pit loss estimation, strategy comparison, replay events.

---

## Race Control

One row represents an official race-control event.

Important columns:
- date
- driver_number
- lap_number
- category
- flag
- scope
- sector
- message

Future use:
Yellow flags, red flags, Safety Car, VSC, penalties, investigations, incident timeline.

Note:
Some fields such as driver_number, sector, or flag may be empty depending on the event.

---

## Weather

One row represents a weather reading at a specific timestamp.

Important columns:
- date
- track_temperature
- air_temperature
- rainfall
- humidity
- pressure
- wind_speed
- wind_direction

Future use:
Weather display, wet/dry race detection, tyre analysis, strategy context.

---

## Car Telemetry

One row represents one telemetry sample for a driver.

Sample driver:
44

Important columns:
- date
- driver_number
- speed
- throttle
- brake
- n_gear
- rpm
- drs

Future use:
Speed graphs, throttle/brake traces, gear display, RPM, DRS status, driving-style analysis.