# AeroPulse — remaining native verification

Continue https://github.com/harshvtomar/aeropulse-flight-operations-analytics on main. Inspect actual HEAD first; verified portfolio checkpoint `0e8da3f2122c5d7d2bdd2f20fe8e97e6fb68d6eb` and fixture CI run 40068665936 passed. Later QA documentation commits may follow. Never reset newer work.

Read PROJECT_STATE.md, SESSION_LOG.md, reports/session4/LIVE_QA.json, docs/NATIVE_BI_COMPLETION_HANDOFF.md and docs/POWER_BI_SESSION3.md. The public seven-page Streamlit product, portfolio PDF and interview guide are delivered. Native Excel and native Power BI are the remaining execution tasks.

```bash
git fetch origin main
git status --short
git log -5 --oneline
python -m pip install -r requirements.txt
python -m pytest -q -m 'not integration'
python -m streamlit run app.py
```

Expected fixture baseline: 189 passed. Eight genuine integration tests previously passed in Session 4; run them only after original archives, processed data and warehouse are restored with committed fingerprints. The committed deployment Parquet supports all dashboard records; it is not a substitute for original-source integration inputs.

1. In accessible Microsoft Excel, follow the exact native checklist, preserve original workbook, test controls B5/B6, refresh seven charts, save/reopen a separate verified copy; record version, hashes and screenshots.
2. In supported Windows Power BI Desktop, use existing typed imports, six relationships, measures and five-page layout. Verify all 33 expected observations in reports/session4/NATIVE_POWER_BI_RESULTS.csv, interactions and refresh, then save/reopen an actual report and record evidence. No paid infrastructure without separate authorization.
3. If neither native application is accessible, leave statuses pending. Do not relabel library/XML checks as native tests.
4. Publish only verified changes to this repository, check remote bytes and CI, update final state with actual evidence. Preserve canonical KPIs, Q1 2025 provenance and all earlier artifacts.
