# Power BI Session 3 — reproducible build package

**Status: import/model/report specification prepared; native Power BI artifact not created or verified.** This session runs on Linux; the user uses macOS and no accessible Windows Power BI Desktop is established. No `.pbix` or `.pbip` is supplied. Microsoft documents Windows requirements for Desktop. The files below are ordinary Power Query expressions and a manual model contract, not a native report disguised by an extension. M evaluation, DAX execution, native rendering, slicer interactions, refresh performance and publishing remain unverified until Session 4.

## Contents and reproduction

- `powerbi/queries/pDataFolder.m`: one editable folder parameter, pointing to a locally regenerated `data/bi` directory.
- Seven fact/dimension `.m` expressions: explicit schema/type mapping, CSV UTF-8, empty strings converted to NULL, schema drift errors. Parquet retains nullable and signed values. No population prefilter removes cancellations or diversions.
- `powerbi/model_contract.json`: exact seven-table/six-relationship setup; **not** a Microsoft semantic-model serialization.
- `powerbi/measures.dax`: the original `docs/POWER_BI_MEASURES.dax` preserved verbatim, plus coverage for the four other categories and the airline-origin volume screen. Paste one named measure at a time.
- `powerbi/theme.json`: basic report theme colors.
- `powerbi/native_validation.sql` and `native_validation_expected.json`: independently calculated SQL reference values for full coverage, January and a combined date/carrier/origin/hour population. Native comparison is pending.

From the repository root, regenerate source exports with `python -m src.bi_export` (after warehouse construction). Generate the import scripts and contract with `python powerbi/build_package.py`; its default schema source is the versioned Session 2 audit. To adapt deliberately to a new schema, pass `--manifest data/bi/manifest.json` and review the resulting diff. It ignores aggregate tables deliberately: all report measures below use the detail fact so combined slicers remain supported. Run `python -m pytest tests/test_powerbi_package.py -q`. These tests check generation reproducibility, endpoint/type contracts, preserved measures and, when exports exist, real-data dimension uniqueness and foreign-key coverage. They do not parse or execute M/DAX.

Regenerate SQL reference JSON if source coverage changes; do not compare a new population to old totals. The current references correspond to the source hashes and export audit in `reports/session2/BI_EXPORT_VALIDATION.json`.

## Session 4: Windows Desktop build

1. Use supported Windows Power BI Desktop (a Windows machine, Windows 365 or Azure Virtual Desktop); record Desktop version. Clone the repository and regenerate/copy all seven local fact/dimension export files with their manifest. A macOS browser alone cannot run the Desktop build sequence below.
2. Start a blank report. Disable automatic relationship discovery and Auto date/time for this file before loading. In Transform Data, create a blank query named `pDataFolder`; paste its `.m` expression in Advanced Editor and replace the example path with the actual absolute `data/bi` directory. Disable loading for this parameter.
3. Create seven blank queries, named exactly as each other `.m` filename without its extension. Paste each complete expression in Advanced Editor. Verify the type icons and zero query errors; Close & Apply. No `agg_*` tables are needed. Privacy-level prompts must be resolved for the actual local source.
4. In Model view create the six relationships in `model_contract.json`: dimension key is the one side, matching fact key the many side, active, Single cross-filter direction toward fact. Do not connect route airport IDs to the airport dimensions. Remove accidental auto-created relationships.
5. Mark `dim_dates` as a date table using `flight_date`, after checking continuity. Sort `dim_hours[hour_label]` by `scheduled_hour`. Hide fact foreign keys and source lineage from report view (keep for diagnostics), and set dimension IDs/hour/month/day fields to Don't summarize. Use explicit date fields rather than automatic date hierarchies.
6. Create each measure from `powerbi/measures.dax` on `fact_flights` via New measure. Comments are guidance; this is a collection of independent definitions, not one executable query. Format counts as `#,0`, rate/coverage measures as `0.0%`, minute measures as `0.0`, screen flags as whole numbers. Never multiply percentage fractions by 100. Preserve signed mean arrival delays and BLANK cause minutes.
7. Import `powerbi/theme.json` through the report theme import control. Set page size 16:9 (1280 × 720). Build pages using the matrix below. Use white visual backgrounds, dark navy text, teal primary series and amber disruption series. Add a top title and concise subtitle, slicers below, KPI cards and charts below those. Use text sizes at least 12pt and clear keyboard tab order. Show denominator tooltips on every percentage chart.
8. Synchronize airline, origin, destination, date and hour slicers across analytic pages; add route where useful. All slicers must use dimension columns. Enable filter interactions for charts/cards, and verify each manually. Add a reset bookmark with all filters cleared and a page navigator. Save `AeroPulse.pbix` only after data/model validation; optionally Save As PBIP from Desktop for reviewable native source files. Do not publish as part of this local build without a separate destination decision.

## Report layout build matrix

| Page | Visuals and exact fields | Filters / interpretation |
|---|---|---|
| Executive overview | Cards: Reported Flights, Eligible Arrivals, On-Time Arrival Rate, Cancellation Rate, Mean Eligible Arrival Delay Minutes. Line: `dim_dates[flight_date]` → On-Time Arrival Rate. Bar: `dim_airlines[airline_code]` → On-Time Arrival Rate. Tooltips: Eligible Arrivals, Late Arrivals. | All six dimensions can filter detail. Subtitle: “Eligible arrivals exclude cancelled, diverted and missing arrival delays; on time <15 minutes.” |
| Airlines & airports | Matrix rows `dim_airlines[airline_code]`, `dim_origin_airports[origin_airport_code]`; values Eligible Arrivals, On-Time Arrival Rate, Cancellation Rate, Mean Eligible Arrival Delay Minutes. Bar: destination code → Late Arrivals. | Matrix visual filter Airline Origin Meets Volume Screen = 1. Display “≥500 eligible arrivals in current selection.” Screen is a volume policy, not a significance test. |
| Routes & hours | Table: `dim_routes[route_key]`, Eligible Arrivals, On-Time Arrival Rate, Mean Late Arrival Delay Minutes. Column chart: `dim_hours[hour_label]` → On-Time Arrival Rate. | Route table visual filter Route Meets Volume Screen = 1; sort by rate ascending. Label “Directed routes; ≥1,000 eligible arrivals in current selection.” Hours are scheduled local time, not UTC. Hour chart is not route-screened unless explicitly filtered. |
| Disruptions & reported causes | Cards: Cancellations, Diversions, Cancellation Rate. Bar: `fact_flights[cancellation_code]` → Cancellations, visual filter cancelled=1. Two multi-measure cards: all five Reported Minutes measures and all five Cause Late Coverage measures. | Keep cancelled-only filter on reason visual only; applying it to page would corrupt cancellation-rate interpretation. Explain reported minutes are incomplete source allocations; coverage denominator is Late Arrivals. BLANK is missing, not zero. |
| Flight detail | Table: flight_record_id, flight_date, airline_id, origin_airport_id, destination_airport_id, flight_number, arrival_delay_minutes, cancelled, diverted. Add route_key as drill-through field and Back button. | Keep all filters on drill-through. Limit rendered rows through a narrow date/route selection. Signed negatives remain visible. This page supports tracing observations, not ranking individual people. |

Raw KPI pages do not import mix-adjusted estimates. If added later, show them separately with original grouping, confidence intervals and support metadata; never average/regroup adjustment outputs.

## Session 4 native acceptance and evidence

Compare native cards to every case in `native_validation_expected.json`: first clear filters, then January 1–31, then also airline ID 19805, origin ID 10397, hour 8. Match counts exactly and rates/minutes within 1e-9 before display rounding. Include the JSON's carrier minutes/coverage values. Save screenshots of filters and cards, a Model view screenshot, Desktop version, refresh status and the artifact hash.

Also test: an empty intersection (counts 0, rates BLANK); cancelled-only and diverted-only populations (no eligible arrivals); 14-minute arrival on time and 15-minute arrival late; negative delays retained; all-missing cause values BLANK and reported zero included in coverage. Use a small isolated validation model if these boundary populations cannot be selected cleanly in the real data. Check each dimension slicer changes fact measures without fanout. Confirm route threshold drops/requalifies when dates change and airline-origin threshold uses ≥500. Verify combined origin/destination/route filtering, clear/reset behavior, chart interactions, tooltips, drill-through and Back. Refresh after changing `pDataFolder` to another copy of the same export; totals must remain identical. Confirm the SQL source audit still matches.

Record pass/fail per check and actual observed values under `reports/session4/` when performed; do not mark native tests passed based on Python tests. A valid Session 4 completion requires a successfully opened/saved native file plus these runtime checks, not only JSON or DAX text validation.

## Primary documentation consulted

- [Desktop requirements and supported virtual environments](https://learn.microsoft.com/en-us/power-bi/fundamentals/desktop-get-the-desktop)
- [Parquet connector](https://learn.microsoft.com/en-us/power-query/connectors/parquet)
- [File.Contents](https://learn.microsoft.com/en-us/powerquery-m/file-contents)
- [Csv.Document](https://learn.microsoft.com/en-us/powerquery-m/csv-document)
- [Table.TransformColumnTypes](https://learn.microsoft.com/en-us/powerquery-m/table-transformcolumntypes)
- [Create custom report themes](https://learn.microsoft.com/en-us/power-bi/create-reports/report-themes-create-custom)
- [Power BI Desktop projects](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview)

Consulted 2026-10-22. These establish supported building blocks; they do not establish execution of this package.
