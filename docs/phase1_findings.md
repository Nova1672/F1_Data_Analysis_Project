# Phase 1 Findings

## Reference Race
2025 China GP - Shanghai
Session Key: 9998

## Sample Driver
44 - Lewis Hamilton

## Data Available

### Race State
- positions
- intervals
- laps

### Car Data
- speed
- throttle
- brake
- gear
- RPM
- DRS

### Strategy
- tyre compound
- stint length
- pit stops
- tyre age

### Events
- flags
- Safety Car / VSC
- race control messages

### Environment
- air temperature
- track temperature
- rainfall
- wind

### Location
- X/Y/Z approximate coordinates

## Important Observation

The combination of:
timestamp + driver_number

will allow us to synchronize multiple datasets during the replay engine.

### Driver Initial Testing
{'driver_number': 44,
 'driver': 'HAM',
 'lap': 28,
 'lap_time': np.float64(96.989),
 'position': np.int64(5),
 'gap_to_leader': 10.073,
 'interval': np.float64(3.102),
 'compound': 'HARD',
 'speed': np.int64(267),
 'throttle': np.int64(98),
 'brake': np.int64(0),
 'gear': np.int64(7),
 'rpm': np.int64(10695),
 'drs': np.int64(0)}