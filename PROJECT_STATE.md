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
Final report/CI publication verification is recorded in SESSION_LOG.md and the session's final response. Use `git rev-parse HEAD` to identify the exact checked-out state; never treat a documentation file's parent SHA as its own SHA.
