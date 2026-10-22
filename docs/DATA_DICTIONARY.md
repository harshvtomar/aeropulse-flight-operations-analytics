# Data dictionary and warehouse grain

Source names are retained; aliases are explicitly defined in `src/validate.py`.

| Field | Definition |
|---|---|
| FlightDate | Local scheduled flight date; parsed timestamp, dimension cast to DATE |
| Year | Calendar year |
| Month | Calendar month 1–12 |
| DayOfWeek | Monday=1 through Sunday=7 |
| Reporting_Airline | Reporting carrier unique code, not marketing carrier |
| DOT_ID_Reporting_Airline | Stable DOT airline ID; dimension key |
| Flight_Number_Reporting_Airline | Reporting-carrier flight number |
| OriginAirportID | DOT origin airport ID; dimension key |
| DestAirportID | DOT destination airport ID; dimension key |
| Origin | Origin IATA airport code |
| Dest | Destination IATA airport code |
| CRSDepTime | Scheduled local clock HHMM, 2400 allowed; not UTC |
| CRSArrTime | Scheduled local clock HHMM, 2400 allowed; not UTC |
| DepTime | Actual local clock HHMM, 2400 allowed; not UTC |
| ArrTime | Actual local clock HHMM, 2400 allowed; not UTC |
| DepDelay | Signed departure delay, minutes; negative=early |
| ArrDelay | Signed arrival delay, minutes; negative=early |
| ArrDel15 | Source arrival delay indicator, 1 if at least 15 minutes |
| Cancelled | 1 cancelled; 0 otherwise |
| CancellationCode | A carrier / B weather / C NAS / D security; nullable |
| Diverted | 1 diverted; 0 otherwise |
| Distance | Nonstop distance, miles |
| CarrierDelay | Reported allocated delay minutes; nullable |
| WeatherDelay | Reported allocated delay minutes; nullable |
| NASDelay | Reported allocated delay minutes; nullable |
| SecurityDelay | Reported allocated delay minutes; nullable |
| LateAircraftDelay | Reported allocated delay minutes; nullable |

## Derived fields
- `arrival_eligible`: neither cancelled nor diverted and ArrDelay is nonmissing.
- `late_arrival` / `on_time_arrival`: eligible delay >=15 / <15.
- `duplicate_candidate`: member of a duplicate-looking scheduled-operation group; never dropped.
- `source_sha256`, `source_row`, `flight_record_id`: archive fingerprint, one-based CSV data-row position, and concatenated technical key.

## Tables and relationships
| Table | Grain / key | Relationship |
|---|---|---|
| fact_flights | One accepted source row / flight_record_id | Many to one to all dimensions |
| dim_airlines | DOT airline ID; observed unique carrier code | fact.DOT_ID_Reporting_Airline |
| dim_airports | DOT airport ID; observed code | fact.OriginAirportID and fact.DestAirportID |
| dim_dates | Calendar date observed in facts | DATE(fact.FlightDate) |
| data_quality_audit | Imported month | source/accepted/quarantined counts and source hash |

Detailed validation findings are in committed monthly JSON manifests. Dimensions are derived only from observed data; no invented airline display names or airport coordinates. Unique indexes stop ambiguous ID mappings. `v_arrival_eligible` and `v_reliability` provide reporting contracts. SQL construction lives in `sql/schema.sql`; Parquet binding and audit loading in `src/warehouse.py`.
