# Session log

## 2026-10-22 — Session 1
1. Inspected intended repository through GitHub API (404) and official BTS schema. Created only the requested public repository using the signed-in GitHub UI.
2. Downloaded all three complete official PREZIP archives. Recorded original ZIP filenames, member names, source SHA-256 and observed schemas.
3. Built the importer, conservative validation and atomic month bundles. First real-data run found an empty-quarantine handling error; fixed it and added regression coverage before publishing implementation.
4. Imported 539,747 / 504,884 / 600,872 rows. No hard-invalid rows or duplicate candidates. Five extreme arrival and seven extreme departure delays retained with warnings.
5. Built the DuckDB warehouse, 12 SQL analyses, independent pandas reconciliation and four figures. Visually reviewed figures for labeling/layout.
6. Executed fixture suite (48 passed), then full suite (49 passed). Independently compared 2,749 numeric values. Repeated imports returned unchanged for all three months; raw files were never modified.
7. Published implementation checkpoint `391d3e9437a1c50f5dae4ccd89f44f2d3e4795d8`, after initial repository commit `281d87e381f7c31f4163bcfe9324ef631844bcc2`.
8. Added provenance, KPI contract, dictionary, methodology, measured findings/quality report, reproduction instructions and Session 2 handoff. Added GitHub Actions fixture-only workflow.

## Reproduction / verification commands executed
```bash
python -m src.ingest
python -m src.warehouse
python -m src.metrics
python -m src.analysis
python -m pytest -q -m 'not integration'
python -m pytest -q --junitxml=reports/local-tests.xml
python -m src.ingest  # all three months unchanged
```

Downloads were obtained with Python urllib from the documented public BTS PREZIP URLs; `python -m src.ingest --download` provides the reusable equivalent. Source-level raw-to-accepted reconciliation, 12 query executions and dimension cardinalities are recorded in committed manifests/reports.

## Publication verification
Verified implementation/report commit: `3f9cb13f68eda26617bb87e50d68cd4b9f788a97`.
Hosted GitHub Actions run **39715414479 completed successfully**: https://github.com/harshvtomar/aeropulse-flight-operations-analytics/actions/runs/39715414479
The public repository tree contained 61 files before this evidence-only update; fetched main matched local tracked file contents. Requirements and source files were readable, and the README rendered with its chart. No raw archives, processed Parquet, databases or detected credential patterns were committed. A publication screenshot is in `reports/evidence/github-publication.png` (captured before CI completed).

Session 1 acceptance criteria are complete. The subsequent documentation/evidence commit preserves this verified implementation. No deployed dashboard is claimed. Full-data verification ran locally; CI deliberately tests fixtures without downloading source data.


## Session 2 — October 22–23, 2026

Inspected live main at `b422890be32e1efa609c28222f17f68a0212b7b0`, repository source, tests, reports and provenance before changes. Reproduced the 49-test baseline and 2,749 KPI comparisons using all three authentic month archives; confirmed original source hashes. Preserved Session 1 code, SQL, KPI definitions and measured outputs. Two tied-volume baseline CSVs were restored to their original byte order after verifying identical keyed values.

Published investigation checkpoint `2b90931ec7907179ec183c1fccc6f0451af4fced`. Added ten independent SQL/pandas analyses; statistics and composition-aware comparisons; BI export contracts and readback validation; six figures; analytical reports. Fixed nonconsecutive-month comparison handling and explicit CSV types for all-NULL numeric measures. Fixed the heatmap scale to include the observed 36.2% cell. Synthetic records occur only in automated tests.

Commands executed (from repository root):
```bash
python -m pip install -r requirements.txt
python -m src.ingest --download
python -m src.warehouse
python -m src.analysis
python -m src.investigate
python -m src.advanced_sql
python -m src.statistics
python -m src.mix_analysis
python -m src.bi_export
python -m src.session2_report
python -m src.session2
python -m pytest -q -m 'not integration'
python -m pytest -q -m integration
```

The runtime reset during continuation; pinned requirements were reinstalled. No source records were reconstructed or substituted. The full runner validates the archived fingerprints. Existing pandas downcasting FutureWarnings come from the preserved ingestion implementation; they are recorded, not suppressed.

Session 2 numeric reconciliation: 161,389 SQL-output values + 5,040 statistical-input values + 120,288 mix-cell values = 286,717; plus 21,390 labels. Six figures were visually reviewed. BI exports are excluded from Git, with their inventory/hashes/32-check report committed. Native Power BI and interactive dashboards remain explicitly unimplemented.

Final local verification: **128 passed, zero failures, zero skips**: 124 fixtures (four integration tests deselected) and four genuine-data integration tests (124 fixtures deselected). Logs: `reports/session2/FIXTURE_TEST_RESULTS.txt` and `INTEGRATION_TEST_RESULTS.txt`. The real tests reran all ten new SQL/pandas comparisons, rebuilt/read back all BI exports, checked severe-delay/cause populations and reran original KPI reconciliation. The unified `python -m src.session2` command completed successfully with original source fingerprints. Hosted CI status is recorded separately after publication; it runs fixtures only.

Verified implementation commit: `10bd8c570245b0e8c9a0577a0948d8452819d6c0`. [Hosted CI run 39833796318](https://github.com/harshvtomar/aeropulse-flight-operations-analytics/actions/runs/39833796318) completed successfully; the fixture test step passed. All 66 changed/new files were fetched and compared byte-for-byte to the verified local files. GitHub README returned HTTP 200 with rendered Session 2 content and figure references; local document links passed. No raw ZIPs, full BI datasets, databases or credential-pattern matches were present in the publication set (largest added file 708,720 bytes).

Session 2 acceptance criteria are complete. The final documentation/evidence commit follows this tested implementation and does not change analytical code. Record its actual SHA from remote main; a commit cannot contain its own SHA. Session 3 instructions are committed in NEXT_SESSION_PROMPT.md. Outstanding external evidence and future dashboard scope are documented, not represented as completed work.


## Session 3 — implementation, deployment and QA (24 October 2026)

Started from remote `34c3b3cd8a8704cc9148d965217a4f09aec2791a`. Preserved all Session 1–2 analytical code/reports and raw fingerprints. Runtime interruptions required dependency reinstalls; incomplete test runs were not counted. Initial baseline BI-export integration encountered one transient mounted-filesystem Parquet read-after-write error; original failure and successful retry logs are retained. Final integrations passed.

Built seven Streamlit pages, a complete minimal 6.8 MB deployment fact, contextual CSV downloads, Excel workbook and Power BI implementation package. Dataset build verified all retained cells/multiplicity, 26 checks and 144 independent filtered KPI comparisons. Excel has eight sheets and seven charts; native Excel and Windows Power BI remain unverified.

Executed pinned dependency installation, `python -m src.build_dashboard_data`, fixture and genuine integration pytest runs, Excel builder/validation, Power BI contract checks and live Chrome QA. Final local outcome: 189 fixtures + 8 genuine integrations = 197 passing tests, no failures. Existing 40 pandas FutureWarnings are recorded unchanged. Resource check measured about 81 MiB peak RSS for standalone data queries; this is not hosted application memory or a capacity guarantee.

Publication checkpoints:
- `a4503bd9e3d7b07ebee7effcd8e1f92fa5c1e14a`: 53 files published and compared byte-for-byte; [fixture CI passed](https://github.com/harshvtomar/aeropulse-flight-operations-analytics/actions/runs/40044687939).
- `267463dbbe3e3214fb1a0f616c6fed212676594b`: categorical single-month charts, clearer axis labels and header spacing.
- `cc2f7f3fcdfa232b4bb50ee5f18ab01a8d2a4b60`: cached-backend invalidation on module reload, regression test.
- `ffc105c8e19a643a3d1662b1999d90f44fa515ec`: explicit browser-control reset synchronization; [fixture CI passed](https://github.com/harshvtomar/aeropulse-flight-operations-analytics/actions/runs/40045724415).

Public deployment configured through the authorized connected Streamlit account: existing repository main, app.py, Python 3.12, no secrets. Assigned URL https://aeropulse-flight-operations-analytics.streamlit.app/. Seven live pages, canonical cards, month/airline/route/hour/severity populations, minimum-volume screen, separate origin role, empty state, reset, desktop and 390×844 layout were checked. Excel and filtered CSV downloads completed. Anonymous HTTP request with session-cookie continuity returned 200; no cookie/auth payload is committed. LIVE_QA.json records scope and limits. Two additional live-discovered regression tests raise Session 2's 128 tests to 197.

Session 3 dashboard/Excel deliverables are implemented and published; full native-BI acceptance remains partial. Session 4 must verify Excel in native software and create/test the native Power BI report in supported Windows, then complete portfolio QA. The following documentation/evidence commit does not change analytical or application code; resolve current remote main for its exact SHA.
