# Project state — Session 1

Date: 22 October 2026. Repository: https://github.com/harshvtomar/aeropulse-flight-operations-analytics

## Working and verified locally
- Complete official BTS reporting-carrier records for 2025-01, 2025-02 and 2025-03: 539,747 + 504,884 + 600,872 = 1,645,503 rows.
- All accepted, zero quarantined, zero duplicate candidates; matching schemas and raw-to-fact reconciliation.
- Monthly immutable Parquet bundles, provenance fingerprints, incremental ingestion and unchanged-checksum reruns.
- DuckDB: fact_flights (1,645,503), dim_airlines (14), dim_airports (333), dim_dates (90), data_quality_audit (3); two reporting views.
- 12 executable SQL analyses and CSV exports; four Matplotlib figures.
- 2,749 independent numeric SQL/Python comparisons passed.
- 49 local tests passed: 48 fixture tests plus one authentic-data integration test.
- On-time eligible arrivals: 80.3068317105781%; cancellation rate: 1.862044614929295%.

## Data and architecture
Raw ZIP → validated monthly Parquet + audit JSON → atomic DuckDB rebuild → SQL CSV results → independent pandas reconciliation → charts and findings. Raw/processed/database files are intentionally not committed; re-download with recorded URLs and compare source hashes. Monthly manifests and measured reports are committed.

## Limits and outstanding work
No interactive dashboard, Power BI report, causal model, full-year analysis or financial-impact model exists. Physical macOS execution is not tested. Source-derived dimensions provide IDs/codes only. Official summary-report reconciliation remains future work. Extreme-delay warning records remain unchanged. Single-writer operations are required; official source revisions need explicit investigation.

## Publication checkpoint
Initial implementation checkpoint: `391d3e9437a1c50f5dae4ccd89f44f2d3e4795d8` (published).
Verified full implementation/report commit: `3f9cb13f68eda26617bb87e50d68cd4b9f788a97`. Hosted CI run 39715414479 passed. Session 1 acceptance criteria are complete; final evidence is in SESSION_LOG.md. Use `git rev-parse HEAD` to identify the exact checked-out state; never treat a documentation file's parent SHA as its own SHA.


## Session 2 checkpoint — October 23, 2026

Session 1 source, warehouse, dimensions, 12 SQL queries, KPI definitions and provenance are preserved. All 1,645,503 records remain accepted; canonical metrics are unchanged.

Implemented and executed: 10 new SQL analyses; independent SQL/pandas checks (161,389 numeric + 21,390 labels); daily statistical-input checks (5,040); mix-cell checks (120,288); seeded grouped bootstrap; pair-specific common-support standardization; 14 BI exports with 32 validation checks; six new figures and five analytical reports. Seven extreme source records were traced: six internally consistent completed-flight outliers and one unresolved cancelled-flight timeline. No canonical row was removed or capped.

Source fingerprints remain unchanged. Full facts and BI exports are local/ignored and can be regenerated through `python -m src.session2` after the Session 1 import/warehouse commands. Aggregate analytical CSVs and measured evidence are committed. See `docs/BI_DATA_MODEL.md` for inventory, keys and relationship rules.

Network on-time performance is 80.3068%; the day-cluster model interval is 78.3751–82.1702%. This models variation across exchangeable days within months, not sampling error for the counted quarter or complete serial dependence. Only four of 91 carrier pairs meet overlap rules. No adjusted interval, causal superiority or financial impact is asserted.

Remaining scope: Session 3 dashboards, native Power BI verification and Excel deliverables; external evidence for the cancelled outlier; additional quarters and richer dependence modeling if justified. No source access or implementation blocker remains. Consult SESSION_LOG.md for actual final test/CI/publication evidence and NEXT_SESSION_PROMPT.md to resume.

Session 2 publication verified: implementation `10bd8c570245b0e8c9a0577a0948d8452819d6c0`, hosted fixture CI [39833796318](https://github.com/harshvtomar/aeropulse-flight-operations-analytics/actions/runs/39833796318) passed; local tests 124 fixtures + 4 genuine-data integration = 128 passed. All Session 2 acceptance criteria are satisfied within the documented descriptive-analysis scope.
