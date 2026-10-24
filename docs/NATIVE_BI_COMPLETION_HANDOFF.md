# Remaining native software execution only

Session 4 environment assessment: Linux Python 3.12.14. No accessible Excel or Power BI Desktop executable/control surface was available; native computer automation is disabled. Available connectors do not execute native Excel or DAX. This does not establish whether Excel is installed on the user's Mac. No Windows infrastructure was purchased. Both native statuses remain **not executed**, not failed or passed.

## Excel: preserve, open, verify, save, reopen

Use the existing reports/session3/excel/AeroPulse_Airline_Operations_Business_Report.xlsx. Record its SHA-256, actual Excel version/build, OS, date and reviewer. Save a separately named verified copy; preserve the original audit artifact.

1. Open in Microsoft Excel, record any repair/warning dialog. Do not dismiss a repair without recording it.
2. Recalculate all formulas. Inspect all eight worksheets: Executive, Airlines, Airports, Routes, Severity, Disruptions, Monthly source, Methodology. Check headings, tables, number formats, column widths and readable chart labels.
3. Refresh all seven charts and inspect visible bars/labels against their source cells. The original caches are empty; XML presence is not proof of native chart rendering. Capture each chart and its source range.
4. Executive B5=All / B6=All must show 1,645,503 reported, 1,611,046 eligible and 80.3068317105781% on time. B5=AA / B6=2025-01: 75,088 reported, 72,082 eligible, 58,222 on time; 2,802 cancelled. Compare unrounded underlying values.
5. Also test WN/2025-02, AA/2025-03, invalid carrier and blank carrier against reports/session3/excel/EXCEL_VALIDATION.json. For validation-list blocking, record that behavior; paste/clear only in a disposable copy to exercise formula no-match handling. No-match rates must be n.a., not misleading 0%.
6. Confirm fixed Q1 sheets remain fixed; the executive trend uses carrier only. Reset All/All, save and close. Reopen the saved copy and verify formulas, controls, seven charts and canonical totals again. Record output SHA-256 and screenshots.

## Windows Power BI: continue existing package

Use docs/POWER_BI_SESSION3.md, powerbi/queries, model_contract.json, measures.dax, theme.json and native_validation_expected.json. Do not use the reduced dashboard fact for native drill-through: it omits original identifiers. Copy/regenerate the original full data/bi fact and six dimensions, compare their manifest fingerprints, and set pDataFolder.

1. On an accessible supported Windows Desktop installation, record exact Power BI build/OS. Import seven typed tables. Disable unintended auto relationships/date tables.
2. Create the six one-to-many, active, single-direction relationships exactly as in model_contract.json. Use separate origin/destination dimensions. Confirm uniqueness, unmatched keys and fact count; capture Model view.
3. Create the existing DAX measures individually and format rates as percentage fractions. Preserve signed delays, BLANK causes and denominator behavior.
4. Build five pages from the existing layout matrix: executive; airline/airport; routes/hours; disruptions/reported causes; flight detail with source identity, route drill-through and Back. Synchronize dimension slicers, label sample screens, add a verified reset bookmark.
5. Enter each observed native measure in reports/session4/NATIVE_POWER_BI_RESULTS.csv. Its expected values come directly from the committed JSON; blank observed/status columns deliberately mean pending. Compare every count exactly and every unrounded rate/mean within absolute tolerance 1e-9. Do not compare rounded card labels.
6. Cases: all; January; January plus airline_id=19805, origin_airport_id=10397, scheduled_hour=8. The last case must yield 30 reported / 29 eligible / 24 on-time / 1 cancelled. Validate cause minutes and coverage too.
7. Test empty intersections, cancelled-only/diverted-only populations, missing causes, negative delays, 14/15-minute boundary, route >=1,000 and airline-origin >=500 screens. Use a separately identified synthetic native validation model only if boundaries cannot be isolated in authentic data. Never blend its rows into the report.
8. Test all slicers, origin+destination combinations, visual cross-filtering, tooltips, drill-through, Back and reset. Refresh using the same verified export and rerun reference cases.
9. Save actual PBIX or Desktop-generated PBIP, close/reopen, rerun reference values, record SHA-256 and screenshots. Only then mark native acceptance passed. No browser dashboard or text file is a native Power BI artifact.

## Evidence required before full completion

Native Excel version/open/recalc/chart/controls/save/reopen evidence; native Power BI version/model/DAX/interactions/refresh/save/reopen evidence; actual artifact hashes. The Streamlit app, data pipeline and portfolio documentation do not need rebuilding. Update PROJECT_STATE.md and the verification report only after real observations are recorded.
