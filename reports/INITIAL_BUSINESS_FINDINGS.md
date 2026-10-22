# Initial business findings — Session 1

Coverage: complete downloaded BTS reporting-carrier monthly archives for January–March 2025. This is a US domestic reporting-carrier population, not every flight worldwide or every US operation.

- Reported flights: **1,645,503**; eligible normal arrivals with a reported delay: **1,611,046**.
- **80.31%** of eligible arrivals were under 15 minutes late; **19.69%** were at least 15 minutes late.
- **30,640 cancellations (1.86%)** and **3,817 diversions (0.23%)**, each using all reported flights as denominator.
- Mean arrival delay across eligible flights was **4.98 minutes**, preserving early arrivals. Among arrivals at least 15 minutes late, mean delay was **71.65 minutes**. The overall mean masks a long late-arrival tail.
- Within this quarter, reporting carrier **HA** had the highest unadjusted on-time rate (**84.02%**, n=19,212); **OH** had the lowest (**71.31%**, n=57,658). This is descriptive, not a fair causal ranking: schedules, routes and operating conditions differ.
- **LateAircraftDelay** accounted for the largest sum of reported cause minutes (**8,427,350 minutes**). These are reported allocations, not independent proof of underlying root causes.

## Business use and next investigation
Use route and airline-origin tables to shortlist recurrent reliability problems. Route rankings require at least 1,000 eligible arrivals; airline-origin comparisons require 500. Examine monthly stability and route/schedule mix before recommending operational action. Do not infer cost savings from these data.

## Evidence and reproduction
All values above derive from `reports/queries/01_overall.csv`, `02_airlines.csv` and `11_delay_causes.csv`. The 12 executable SQL exports are in `reports/queries/`. `KPI_RECONCILIATION.json` records 2,749 independent SQL/Python numeric comparisons. Four figures are in `reports/figures/`.

## Resume-safe description
Built a Python–DuckDB analytics foundation processing 1,645,503 authentic BTS flight records, with auditable monthly imports, 12 SQL analyses and independently reconciled reliability KPIs. No financial impact or deployed dashboard is claimed.
