# Data quality report

Measured from complete imported source files. Invalid rows are quarantined; warning cases remain accepted. Duplicate candidates are retained.

| Month | Source | Accepted | Quarantined | Duplicate candidates | Date range |
|---|---:|---:|---:|---:|---|
| 2025-01 | 539,747 | 539,747 | 0 | 0 | 2025-01-01 to 2025-01-31 |
| 2025-02 | 504,884 | 504,884 | 0 | 0 | 2025-02-01 to 2025-02-28 |
| 2025-03 | 600,872 | 600,872 | 0 | 0 | 2025-03-01 to 2025-03-31 |

## Warnings (source rows)

### 2025-01

- overlapping_cancelled_diverted: 0
- cancelled_with_arrival_time: 0
- cancelled_missing_arrival_time_expected: 16,312
- completed_missing_arrival_delay: 0
- completed_missing_arrival_time: 0
- arrival_indicator_mismatch: 0
- unexpected_arrival_delay: 2
- unexpected_departure_delay: 3
- negative_cause_minutes: 0
- cancelled_missing_or_unknown_reason: 0
- noncancelled_with_reason: 0
- status_with_arrival_delay: 0

Raw = accepted + quarantined: **True**. Invalid-value findings: 0.

### 2025-02

- overlapping_cancelled_diverted: 0
- cancelled_with_arrival_time: 0
- cancelled_missing_arrival_time_expected: 7,405
- completed_missing_arrival_delay: 0
- completed_missing_arrival_time: 0
- arrival_indicator_mismatch: 0
- unexpected_arrival_delay: 2
- unexpected_departure_delay: 3
- negative_cause_minutes: 0
- cancelled_missing_or_unknown_reason: 0
- noncancelled_with_reason: 0
- status_with_arrival_delay: 0

Raw = accepted + quarantined: **True**. Invalid-value findings: 0.

### 2025-03

- overlapping_cancelled_diverted: 0
- cancelled_with_arrival_time: 0
- cancelled_missing_arrival_time_expected: 6,923
- completed_missing_arrival_delay: 0
- completed_missing_arrival_time: 0
- arrival_indicator_mismatch: 0
- unexpected_arrival_delay: 1
- unexpected_departure_delay: 1
- negative_cause_minutes: 0
- cancelled_missing_or_unknown_reason: 0
- noncancelled_with_reason: 0
- status_with_arrival_delay: 0

Raw = accepted + quarantined: **True**. Invalid-value findings: 0.

## Missing values (% of source rows)

| Field | 2025-01 | 2025-02 | 2025-03 |
|---|---:|---:|---:|
| FlightDate | 0.0000 | 0.0000 | 0.0000 |
| Year | 0.0000 | 0.0000 | 0.0000 |
| Month | 0.0000 | 0.0000 | 0.0000 |
| DayOfWeek | 0.0000 | 0.0000 | 0.0000 |
| Reporting_Airline | 0.0000 | 0.0000 | 0.0000 |
| DOT_ID_Reporting_Airline | 0.0000 | 0.0000 | 0.0000 |
| Flight_Number_Reporting_Airline | 0.0000 | 0.0000 | 0.0000 |
| OriginAirportID | 0.0000 | 0.0000 | 0.0000 |
| DestAirportID | 0.0000 | 0.0000 | 0.0000 |
| Origin | 0.0000 | 0.0000 | 0.0000 |
| Dest | 0.0000 | 0.0000 | 0.0000 |
| CRSDepTime | 0.0000 | 0.0000 | 0.0000 |
| CRSArrTime | 0.0000 | 0.0000 | 0.0000 |
| DepTime | 2.9432 | 1.4045 | 1.0956 |
| ArrTime | 3.0718 | 1.4936 | 1.1868 |
| DepDelay | 2.9501 | 1.4140 | 1.0999 |
| ArrDelay | 3.2382 | 1.6653 | 1.4264 |
| ArrDel15 | 3.2382 | 1.6653 | 1.4264 |
| Cancelled | 0.0000 | 0.0000 | 0.0000 |
| CancellationCode | 96.9778 | 98.5333 | 98.8478 |
| Diverted | 0.0000 | 0.0000 | 0.0000 |
| Distance | 0.0000 | 0.0000 | 0.0000 |
| CarrierDelay | 81.8193 | 79.5791 | 80.6891 |
| WeatherDelay | 81.8193 | 79.5791 | 80.6891 |
| NASDelay | 81.8193 | 79.5791 | 80.6891 |
| SecurityDelay | 81.8193 | 79.5791 | 80.6891 |
| LateAircraftDelay | 81.8193 | 79.5791 | 80.6891 |

Extreme-delay warnings use review thresholds outside [-120, 2880] minutes. These are not automatic validity limits; records remain unchanged. Missing arrival times for cancellations are expected. Full invalid-value checks, hashes, schema and exact timestamps are in `data/manifests/`. Airport code validation checks format, not membership in an independent registry.
