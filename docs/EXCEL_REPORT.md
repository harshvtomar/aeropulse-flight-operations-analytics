# AeroPulse Excel business report

The workbook is `reports/session3/excel/AeroPulse_Airline_Operations_Business_Report.xlsx`. It summarizes all 1,645,503 accepted BTS records for January–March 2025, with seven native charts, editable Executive carrier/month controls, and formula-based rates. It is a compact management report; it does not embed the 1.6 million detail records.

| Sheet | Scope and behavior |
|---|---|
| Executive | B5 selects a carrier; B6 selects a month. Selected KPIs use both controls. The three-month chart uses carrier only. Amber indicates editable controls. Q1 recommendations remain fixed. |
| Airlines | All 14 carriers, fixed Q1. Counts and formula-based raw on-time/cancellation rates. |
| Airports | Top 20 destination airports by late-flight contribution, fixed Q1. Chart shows top 10. |
| Routes | Top 20 directed routes by late-flight contribution among routes with at least 1,000 eligible arrivals, fixed Q1. Chart shows top 10. |
| Severity | All five canonical severity bands, eligible and late-flight shares, and late-minute shares. |
| Disruptions | Cancellation reason shares and reported cause minutes, with category-specific coverage. |
| Monthly source | 42 airline-month rows rolled up from the verified daily airline export. |
| Methodology | Definitions, control boundaries, interpretation, source SHA-256 fingerprints and refresh notes. |

Eligible arrivals exclude cancelled/diverted flights and missing arrival delay. On time is signed arrival delay below 15 minutes. Rates divide matching summed counts. Cancellation rate uses all reported flights. Source cause populations repeat for each category and must not be summed across categories. Raw comparisons do not establish causal airline quality. The tables are ordinary filterable Excel Tables, not PivotTables or slicers.

## Rebuild

First reproduce the warehouse, Session 2 reports and BI exports using the repository workflow. The builder reads only their existing CSV outputs and writes its own Session 3 directory. Source data and earlier reports remain unchanged.

Authoring requires the bundled Codex primary runtime with `@oai/artifact-tool`. From the repository root:

```bash
EXCEL_REPO="$PWD"
EXCEL_TMP=$(mktemp -d /tmp/aeropulse-excel.XXXXXX)
ln -s "$CODEX_PRIMARY_RUNTIME_NODE_MODULES" "$EXCEL_TMP/node_modules"
cp scripts/build_excel.mjs "$EXCEL_TMP/build_excel.mjs"
"$CODEX_PRIMARY_RUNTIME_NODE" "$EXCEL_TMP/build_excel.mjs" "$EXCEL_REPO"
python tests/test_excel_report.py
```

The spreadsheet authoring marker was successfully run before the first creation in this session. Subsequent rebuilds use the same executable builder; no alternate authoring library or manual ZIP/XML edits are used. The builder aggregates source data in JavaScript, creates native spreadsheet objects, recalculates, tests controls, renders each sheet, and exports one XLSX.

## Verification and limitations

- Five carrier/month scenarios passed in artifact-tool, including all data, WN February, AA March, invalid carrier and blank carrier. No-match rates return `n.a.`. Temporary edits were restored to All / All.
- All 14 airline on-time rates were independently checked after fixing a numerator-parentheses issue during QA. Cancellation counts, severity totals and complete airport/route late counts reconcile to the full population.
- Formula scanning found no spreadsheet errors. Saved XML checks confirm cached headline results, airline rates, two validation lists, eight sheets and seven native charts with source-cell references and teal series colors.
- All eight sheet previews were visually reviewed. The corrected airline preview was reviewed again. Tables, labels and charts are readable; the source preview shows its opening section while all 42 rows are retained in the workbook.
- Validation evidence: `EXCEL_VALIDATION.json`, `EXCEL_XML_VALIDATION.json`, formula inspection/error-scan NDJSON, and eight PNG previews in `reports/session3/excel/`.
- **Microsoft Excel was not available for native open/recalculate/refresh testing.** Exported charts have valid source formulas but empty chart caches. Artifact-tool renders the charts; native Excel chart rendering and cache refresh remain unverified. This is not a claim of native Excel acceptance testing.

The builder records input hashes and calculations; binary XLSX byte identity is not promised across runtime versions. Refresh through the builder when data changes. Fixed ranking inputs and written recommendations are a Q1 snapshot and require review for a new period.
