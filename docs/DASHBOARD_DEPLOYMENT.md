# Streamlit dashboard: operation and deployment

Live app: https://aeropulse-flight-operations-analytics.streamlit.app/

Verified implementation: `ffc105c8e19a643a3d1662b1999d90f44fa515ec`. Hosted fixture CI [passed](https://github.com/harshvtomar/aeropulse-flight-operations-analytics/actions/runs/40045724415). Seven pages and the principal controls were checked in the live Chrome browser. Evidence: [LIVE_QA.json](../reports/session3/LIVE_QA.json), desktop/mobile screenshots and separate local test logs. The free Community Cloud app can sleep after inactivity; allow a cold start. No uptime guarantee or load-test claim is made.

## Local operation

Use Python 3.12 and the pinned root requirements:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
python -m pytest -q -m 'not integration'
```

The committed `deployment/data/flights.parquet` and `manifest.json` are sufficient to run the application. Both must be present and match checksums. Never replace them with test fixtures. The complete minimal fact is 7,088,684 bytes; all 1,645,503 rows are retained. See [deployment data](DEPLOYMENT_DATA.md) for source reuse evidence and build verification. To rebuild after reproducing the original warehouse and verifying archived source hashes:

```bash
python -m src.build_dashboard_data
python -m pytest -q -m integration
```

## Hosting configuration

Streamlit Community Cloud uses the existing `harshvtomar/aeropulse-flight-operations-analytics` repository, branch `main`, entrypoint `app.py`, Python 3.12 and the root `requirements.txt`. The assigned subdomain is `aeropulse-flight-operations-analytics`. No application secrets, paid database, source downloads at startup or external API keys are required. Commit verified changes to main for automatic redeployment; check the app after each change. Cached backend handles are invalidated when backend modules reload.

## Interaction contract

All seven pages share month, airline, origin, destination, directed route, scheduled local departure-hour and arrival severity filters. Airport and route choices cascade from upstream selections. Empty month/airline/severity selections mean no matching records. Reset explicitly restores controls and the full population. The minimum eligible-flight screen affects rankings only, not headline cards. Airport recurrence requires the screen in each selected month and compares against the same-month selected network.

Every ratio is computed from the filtered fact's numerators and denominators. Early arrivals remain negative. Cancelled/diverted/missing-delay flights are not eligible arrivals. Cause nulls remain null and coverage counts are displayed. CSV files contain their exact population filters; percentage values are 0–100. Routes are directed. No geospatial coordinates are assumed.

The full-quarter executive study, outlier sensitivity and pair-specific mix-adjusted comparisons are explicitly fixed reference studies: sidebar filters do not recalculate them. The user is told this at the point of use. No causal superiority, realized financial savings or population-wide adjusted ranking is claimed.

## Verification limits

AppTest verifies runtime behavior and download bytes, not CSS or browsers. Live checks cover desktop and a 390×844 viewport, including sidebar navigation; they are not exhaustive cross-browser or assistive-technology certification. Local resource measurements in `RESOURCE_CHECK.json` are a single Linux process, not a cloud capacity guarantee. Native Excel/Power BI checks remain Session 4 tasks.
