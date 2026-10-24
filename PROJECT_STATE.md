# Current project state — Session 4

Verified portfolio checkpoint: `0e8da3f2122c5d7d2bdd2f20fe8e97e6fb68d6eb`; hosted fixture CI run 40068665936 passed. Fetch current main for subsequent evidence/documentation commits; do not reset to a historical SHA. Verified 24 October 2026.

- Live seven-page dashboard and complete 1,645,503-flight deployment package remain unchanged; canonical KPI recheck passed.
- Session 4: 189 fixtures + 8 genuine integrations passed before workspace maintenance. Their committed logs and source-fingerprint checks survive. Raw/warehouse files are excluded from Git and were not restored after cleanup; do not misdescribe the post-cleanup package check as a new raw-source integration run.
- Six-page rendered/visually reviewed portfolio PDF, three resume bullets, 28 interview answers and precise native execution handoff are published.
- Final browser evidence and mobile screenshot are in reports/session4. Selected live hour/severity/reset cases passed; earlier Session 3 coverage remains preserved.
- Excel: eight sheets/seven charts, XML verification passed, original artifact unchanged; native Excel opening/recalculation/chart refresh/save/reopen pending.
- Power BI: existing build package and 33 reference observations ready; native Windows model/DAX/report execution pending. No PBIX claimed.

Overall completion is partial only for outstanding native BI acceptance. Continue with NEXT_SESSION_PROMPT.md; do not rebuild delivered analytics or dashboard.

## Preserved historical state

# Current project state — Session 3

Verified implementation: `ffc105c8e19a643a3d1662b1999d90f44fa515ec`. Repository: https://github.com/harshvtomar/aeropulse-flight-operations-analytics. Live dashboard: https://aeropulse-flight-operations-analytics.streamlit.app/. Verified on 24 October 2026. Later documentation commits may follow this tested implementation; fetch current main without resetting to this historical SHA.

- Seven public Streamlit pages function with shared fact-based filters, screening, clear empty states and contextual CSV downloads. Full-quarter reference studies are visibly separate.
- All 1,645,503 genuine Jan–Mar 2025 records retained in a 7,088,684-byte deployment Parquet; source hashes, all canonical KPIs and original analytical files preserved.
- 197 local tests pass: 189 fixtures and 8 genuine-data integrations; 69 additional tests over Session 2. [Hosted fixture CI passed](https://github.com/harshvtomar/aeropulse-flight-operations-analytics/actions/runs/40045724415); CI does not execute the full raw-source integration workflow.
- Deployment package: 26 checks, 144 independent filtered KPI comparisons, complete bidirectional retained-record reconciliation. Earlier 286,717 numeric / 21,390 label comparisons and 32 BI-export checks remain preserved.
- Excel workbook delivered at `reports/session3/excel/AeroPulse_Airline_Operations_Business_Report.xlsx`: eight sheets, seven charts, formula-driven carrier/month controls. Recalculation and saved XML checked; native Excel open/refresh unverified, chart caches empty.
- Power BI build assets are in `powerbi/`; no native PBIX/PBIP, M/DAX execution or rendering is claimed. A supported Windows environment is required for Session 4 verification.
- Real desktop/mobile screenshots, live filter/download evidence and local resource measurements are in `reports/session3/`.

## Remaining work

Session 4: native Excel chart refresh/recalculation and Power BI Desktop build/verification; final integrated QA, accessible interaction review, portfolio narrative and resume bullets. Free-host cold starts and limited live-browser coverage are documented. No paid infrastructure, causal business effects or financial savings are claimed. Session 3 dashboard and Excel delivery is complete; full native-BI acceptance remains partial.

## Historical checkpoints below

Earlier sections are retained as historical records; their then-outstanding dashboard tasks are superseded by the current state above.

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
