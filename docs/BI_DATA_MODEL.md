# BI export model — Session 2

Reproduce with `python -m src.bi_export` after the canonical warehouse is built. All export data lives in ignored `data/bi/`; the versioned audit is `reports/session2/BI_EXPORT_VALIDATION.json`. No raw datasets or large BI fact files are committed. Session 3 can regenerate them from the same source fingerprints.

## Inventory (verified January–March 2025)

| File | Rows | Bytes | Purpose |
|---|---:|---:|---|
| fact_flights.parquet | 1,645,503 | 19,616,533 | Complete accepted flight grain; executive and drill-through model |
| dim_airlines.csv | 14 | 150 | DOT airline ID and source unique code |
| dim_origin_airports.csv | 333 | 3,368 | Origin role-playing airport dimension |
| dim_destination_airports.csv | 333 | 3,378 | Destination role-playing airport dimension |
| dim_dates.csv | 90 | 3,179 | Date key, actual date, month, weekday/weekend |
| dim_routes.csv | 5,914 | 141,987 | Directed origin/destination ID pair |
| dim_hours.csv | 24 | 424 | 24 scheduled local hours |
| agg_daily_airline.csv | 1,260 | 64,847 | Executive / airline time series |
| agg_monthly_origin.csv | 991 | 47,513 | Origin airport performance |
| agg_monthly_destination.csv | 991 | 47,359 | Destination airport performance |
| agg_monthly_route.csv | 16,997 | 825,180 | Route analytics |
| agg_monthly_hour.csv | 72 | 4,087 | Scheduled departure-hour performance |
| agg_cancellations.csv | 4,410 | 106,540 | Cancelled-only reason investigation |
| agg_delay_causes.csv | 210 | 12,135 | Category-specific source coverage and minute totals |

## Detail star schema and keys

One accepted source CSV data row is one fact. `flight_record_id` retains the archive fingerprint and one-based source row, so duplicate-looking operations are not silently collapsed. The fact includes source SHA/row lineage, signed delay values, source status flags and nullable reported cause minutes. Its integer `eligible_arrival`, `on_time_arrival` and `late_arrival` flags implement the canonical KPI contract.

| Dimension key (unique, nonmissing) | Fact foreign key | Cardinality / filter direction |
|---|---|---|
| dim_airlines.airline_id | airline_id | One-to-many, dimension → fact |
| dim_origin_airports.origin_airport_id | origin_airport_id | One-to-many, dimension → fact |
| dim_destination_airports.destination_airport_id | destination_airport_id | One-to-many, dimension → fact |
| dim_dates.date_key | date_key | One-to-many, dimension → fact |
| dim_routes.route_key | route_key | One-to-many, dimension → fact |
| dim_hours.scheduled_hour | scheduled_hour | One-to-many, dimension → fact |

Use separate origin and destination airport tables so both relationships can be active. Do not also relate route dimension airport IDs to the airport dimensions: that introduces alternative filter paths. Route attributes identify a directed pair; origin→destination differs from destination→origin. Airports and airlines use source IDs, not display codes as keys. `date_key` is integer YYYYMMDD; `flight_date` is a DATE. Hours are local scheduled clock buckets (2400 normalized to 0), not UTC instants.

## Power BI / Streamlit import

For Power BI, import the Parquet fact using its Parquet connector and CSV dimensions; assign explicit column types from the manifest, then create the six single-direction relationships above. Mark the date dimension as a date table using `flight_date` after confirming it is continuous for the loaded coverage. Import CSV IDs as whole numbers, route keys as text, flags as whole numbers, dates as dates and nullable delays as decimal numbers. Empty CSV cells are NULL, not zeros. CSV auto-detection is not the model contract; manifest source schemas are authoritative.

For Streamlit, read the Parquet with DuckDB or PyArrow and query only the requested aggregates/columns. The compact CSV aggregates support responsive default pages without scanning all detail records. The full fact supports drill-through and combined airline/route/hour filters. Several single-purpose aggregates omit dimensions; do not apply unsupported cross-filters to them or pretend their totals have been sliced. Each aggregate's full grain is its non-measure columns.

The month/carrier/cause table has five category rows per population. Display nonmissing coverage by category, and avoid multiplying denominators by summing them across categories. Do not use the cancelled-only reason table as the denominator for a cancellation rate.

## Validation and publication

The exporter validates every emitted table by bidirectional `EXCEPT ALL` against warehouse-derived queries, catching missing/extra/duplicated rows and changed cells, including NULL differences. It verifies unique fact and dimension keys, foreign-key coverage and no join fanout for every dimension. Five aggregate rollups reconcile eight additive count/delay metrics back to the detail source. The current run passes 32 checks for 1,645,503 facts. Each output's SHA-256, byte size, row count and typed column inventory is recorded, along with all three original source hashes.

Exports are written to a staging directory and validated before replacing the prior export directory. Existing exports are backed up and restored if publication fails. Run one exporter at a time. The audit JSON intentionally contains no execution timestamp, enabling deterministic rerun comparisons for unchanged inputs/runtime. Source snapshot fingerprints preserve provenance; export hashes can change with runtime/library changes even when values are identical.

## Scope boundary

These are tested data exports and measure specifications, not an implemented or verified native Power BI report. Session 3 must build/open/test any PBIX, verify slicers and DAX in Power BI and separately test dashboard behavior. No Excel workbook or Streamlit application is claimed here.
