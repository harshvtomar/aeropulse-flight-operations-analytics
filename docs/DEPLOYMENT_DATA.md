# Dashboard deployment data

The public application uses `deployment/data/flights.parquet`: the complete 1,645,503 accepted BTS reporting-carrier records for January–March 2025. No sampling, synthetic replacement, identity hash, aircraft identifier, flight number, source-row identifier, or network fetch is needed at runtime. The package retains dates, airline and airport codes, scheduled departure hour, independent cancellation/diversion flags, cancellation reason, signed arrival/departure delay, and the five nullable reported cause-minute columns. Parquet dictionary encoding and ZSTD reduce repeated categories without rounding measures.

Run `python -m src.build_dashboard_data` from the repository root after authentic ingestion and warehouse construction. Building requires the local raw ZIPs, ingestion manifests, processed Parquet and warehouse; they are deliberately excluded from the deployment. The builder verifies each raw and processed SHA256, matches warehouse source fingerprints, and checks every retained cell and row multiplicity with bidirectional `EXCEPT ALL`. It independently recomputes KPI classifications in pandas from processed source data for twelve filter scenarios. `reports/session3/DATA_PACKAGE_VALIDATION.json` records the results. Source archive URLs and SHA256s are included in the deployment manifest. The temporary build is outside the workspace to avoid mounted-filesystem read-after-write issues.

`DashboardData` validates package checksum, full-population declaration, format version and row count on startup. Missing or corrupt data causes an actionable error, never a sample fallback. Each query uses its own in-memory DuckDB connection with two threads and a 256 MB memory limit. Filter values use bound parameters and selectable SQL identifiers are allowlisted. The file path is local and escaped. All runtime operations are read-only.

## Filter and measure contract

`Filters(month, airline, origin, destination, route, hour, severity)` accepts lists or tuples; `None` selects all, and an empty list returns no matches. Fields combine with AND; values within a field combine with OR. Month is `YYYY-MM`, airlines and airports use BTS codes, a route is directed (`ATL → LAX`), and scheduled hour is an integer 0–23. `options(field, filters)` applies the other six selections and intentionally ignores the selection for that field. Independent status flags preserve records marked both cancelled and diverted.

Eligibility requires neither cancellation nor diversion and a present arrival delay. On-time is signed arrival delay below 15 minutes; late is at least 15 minutes. Severity boundaries are Under 15, 15–29, 30–59, 60–119, 120+, and Ineligible. Filtering severity restricts the population before computing every denominator: eligible severity shares are within selected eligible arrivals, and late shares within selected late arrivals. Cancellation and diversion rates use selected reported flights. An empty denominator returns null, never 0%. Mean arrival delay includes negative early arrivals; mean late delay only includes eligible late arrivals. Cause coverage counts non-null cells, including recorded zeros; missing cause minutes remain null. Cause minutes are reported attribution, not causal inference. Cancellation reasons apply only to cancelled flights.

## Python interface

- `DashboardData(package_dir=None)` uses the repository's deployment package by default; `.manifest` exposes verified metadata.
- `get_kpis(filters=None)` returns counts, percentages, mean signed delays, and signed eligible arrival-minute sum.
- `group_metrics(group, filters=None)` returns a DataFrame for a field or list of fields from month, date, airline, origin, destination, route, hour, severity.
- `severity_metrics(filters=None)` adds eligible and late share percentages.
- `cause_metrics(filters=None)` returns one row per cause with reported and late population counts, non-null coverage counts, and nullable minute sums.
- `cancellation_metrics(filters=None)` returns reason and cancelled-flight count.
- `options(field, filters=None)` returns sorted cascading choices.

Focused fixture tests exercise threshold boundaries, overlap, signed means, null causes, empty populations, directional routes, cascading filters, parameter safety and integrity failures. The separately marked integration test reconciles the committed authentic package to the independently validated Session 1 baseline.

## Source and reuse evidence

Reviewed on 2026-10-23: the official [Data.gov BTS Flight Data catalog](https://catalog.data.gov/dataset/bts-flight-data) describes carrier monthly on-time performance, names BTS as publisher, links its distribution to TranStats, marks access public, and specifies `https://www.usa.gov/government-works` in its license field. This catalog record is maintained under DHS; its distribution link is the TranStats homepage rather than an individual monthly ZIP. The three actual source ZIPs each contain the monthly CSV and `readme.html`; inspection of the readmes found background and field definitions, with no separate license restriction or grant. The official [TranStats database description](https://transtats.bts.gov/DatabaseInfo.asp?QO_VQ=EFD) confirms that the reporting-carrier table provides individual domestic flight data for download.

The package republishes the tabular flight facts with BTS attribution and the exact source archive URLs and fingerprints. It does not claim a Creative Commons license, copy third-party logos, or imply government endorsement. The catalog's government-works designation is the recorded reuse evidence; no license is inferred from an unrelated BTS publication. U.S. [Copyright Office guidance](https://www.copyright.gov/help/faq/faq-protect.html) distinguishes unprotected facts from protected expression, while [USA.gov guidance](https://www.usa.gov/government-copyright) cautions that not everything on a government website is a government work. These qualifications are preserved rather than treating a `.gov` hostname as blanket permission.
