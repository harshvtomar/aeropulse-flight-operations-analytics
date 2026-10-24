# AeroPulse Intelligence — Session 4 continuation

Continue the existing repository https://github.com/harshvtomar/aeropulse-flight-operations-analytics on main. Do not rebuild or replace Sessions 1–3. Fetch remote main and inspect its actual HEAD before edits. Last verified implementation: `ffc105c8e19a643a3d1662b1999d90f44fa515ec`; subsequent documentation commits preserve this implementation. [Its hosted fixture CI passed](https://github.com/harshvtomar/aeropulse-flight-operations-analytics/actions/runs/40045724415). Live app: https://aeropulse-flight-operations-analytics.streamlit.app/.

Read README.md, PROJECT_STATE.md, SESSION_LOG.md, docs/DASHBOARD_DEPLOYMENT.md, docs/DEPLOYMENT_DATA.md, docs/EXCEL_REPORT.md, docs/POWER_BI_SESSION3.md and reports/session3/LIVE_QA.json. Preserve every canonical KPI and source fingerprint. Complete records: 1,645,503; eligible: 1,611,046; on-time 80.3068317105781%; cancellations 1.862044614929295%.

```bash
git fetch origin main
git status --short
git log -5 --oneline
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q -m 'not integration'
python -m streamlit run app.py
# Only when original local data/warehouse are present and fingerprints verified:
python -m pytest -q -m integration
```

Expected baseline: 189 fixture tests and 8 genuine integrations, 197 total. Fixture CI does not download BTS archives. The committed complete minimal deployment Parquet runs the dashboard without original raw archives; full integrations need the excluded original datasets. Do not substitute synthetic data into production. Rebuild package only with `python -m src.build_dashboard_data` after source fingerprint checks.

Priorities:
1. Inspect live seven-page dashboard, cross-page filters, empty state, reset, hourly/severity controls and CSV/Excel downloads. Prior live QA fixed single-month axes, header spacing, backend reload cache identity and browser reset synchronization; preserve those regression tests.
2. On an available supported Windows machine, follow docs/POWER_BI_SESSION3.md exactly: import seven typed tables, create six relationships, implement DAX and five report pages, compare native filtered totals against powerbi/native_validation_expected.json. Save/open/test the actual report before claiming native completion. Do not purchase Windows infrastructure without separate authorization.
3. Open the delivered workbook in actual Microsoft Excel if available, recalculate airline/month controls, refresh all seven charts (saved caches are empty), inspect references and save a verified native copy. Existing artifact-tool and XML checks are not native Excel verification.
4. Recheck mobile layouts, accessible colors/labels, method/tooltips and links. Expand browser coverage only where useful. Add screenshots if behavior changes.
5. Refine recruiter case study and factual resume bullets. No fabricated financial impacts or causal airline-quality claims.
6. Commit incrementally to this repository only, verify remote bytes/HEAD and Actions, update continuation records and record exact final SHA in delivery. A commit cannot contain its own SHA; reference its tested parent/checkpoint and resolve live main for later documentation commits.
