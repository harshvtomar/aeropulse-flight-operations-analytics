# AeroPulse Intelligence — Session 3 continuation

Continue https://github.com/harshvtomar/aeropulse-flight-operations-analytics on main. Do not rebuild or replace Sessions 1–2. Fetch live main, record its actual SHA and inspect newer work before editing. SESSION_LOG.md records the verified implementation/publication checkpoint; never reset blindly to a historical commit.

## Reproduce before dashboards

Read README.md, PROJECT_STATE.md, SESSION_LOG.md, docs/DATA_PROVENANCE.md, docs/KPI_DEFINITIONS.md, docs/METHODOLOGY.md, docs/STATISTICAL_METHODS.md, docs/BI_DATA_MODEL.md, docs/BI_MEASURE_DICTIONARY.md and the five Session 2 reports. Inspect source and tests.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q -m 'not integration'
# Only if genuine local archives/bundles are absent:
python -m src.ingest --download
python -m src.warehouse
# Reuse the immutable source fingerprints; investigate any mismatch.
python -m src.session2
python -m pytest -q -m integration
```

Expect 1,645,503 accepted official BTS flights (January–March 2025), 14 carriers, 333 airports and 90 days; 22 SQL analyses total; 124 fixture tests plus four genuine-data integration tests. Session 2 reconciles 286,717 numeric values and 21,390 labels independently; BI export validation has 32 checks. Baseline 2,749 KPI comparisons remain intact. Raw/processed data and the DuckDB file are intentionally excluded from Git.

## Session 3 deliverables

1. Build a tested Streamlit dashboard with executive overview, airline, airport, route, severe-delay investigation, cancellations and reported delay allocations. Use compact BI aggregates where their grain supports the selected filters; use the detail Parquet for combined filters and drill-through. Do not apply unsupported filters to aggregates.
2. Implement a native Power BI report only where Power BI can actually be opened and tested. Start from the six-dimension fact model and DAX specifications; retain single-direction relationships and separate origin/destination roles. If native tooling is unavailable, state that blocker and preserve model specifications without claiming a PBIX is verified.
3. Create Excel business deliverables with documented denominators, reproducible data extracts and checked formulas. Use the appropriate spreadsheet skill.
4. Test slicer combinations, empty populations, missing cause values, numerator/denominator behavior, download correctness and small screens. Reconcile every headline number to the existing warehouse.
5. Publish incrementally to this repository. Deploy only an actual working dashboard; verify its live behavior, remote source and hosted CI. Preserve Session 2 findings and all established tests.
6. Update PROJECT_STATE, SESSION_LOG and NEXT_SESSION_PROMPT with actual results and the exact final commit/CI evidence.

## Analytical guardrails and unresolved evidence

- Canonical on-time rate is 80.3068317105781% of 1,611,046 eligible arrivals. Cancellation rate is 1.862044614929295% of all reported flights. Never classify cancellations/diversions as normal on-time arrivals.
- Seven extreme source records remain unchanged. Six completed outliers are internally consistent, not externally confirmed; the cancelled AA1115 MCI–ORD record on January 15 needs event-level source follow-up. Sensitivity scenarios must remain separately labeled.
- Day-cluster intervals model exchangeable days within months; they do not fully address serial weather effects or future-quarter uncertainty.
- Only 4/91 carrier pairs pass common-support screens. Pair-specific adjusted point estimates are not a common-reference league table; raw intervals cannot be attached to adjusted rates.
- Delay-cause missing values remain missing. Category denominators repeat across five category rows. Cancellation-reason exports contain cancelled flights only and cannot supply an all-flight cancellation denominator.
- No realized savings, causal superiority or scientifically established root cause is demonstrated. No native Power BI report, Streamlit app or Excel workbook existed at the Session 2 checkpoint.
