# AeroPulse: resume and interview guide

Independent portfolio project by Harsh Vardhan Tomar. Use claims you can explain and demonstrate. This is not client employment or measured operational impact. Native Power BI Desktop and native Excel verification remain pending; do not claim a tested PBIX or native DAX execution.

## Three resume bullets

- Built a reproducible Python, SQL and DuckDB analytics pipeline for 1.65 million official BTS flight records, with checksum-based provenance, data-quality audits and 22 operational analyses.
- Deployed a seven-page Streamlit dashboard with fact-based cross-filtering and CSV exports; validated 197 automated tests and reconciled deployment data through 144 independent filtered KPI comparisons.
- Analyzed severe-delay concentration and airline schedule mix using month-stratified day resampling and common-support comparisons; delivered an eight-sheet Excel report and documented investigation priorities without causal claims.

Use “197 local tests; 189 fixture tests in CI” when discussing test scope. Counts are verified project results, not personal tenure or business savings. Native Power BI development is not part of these bullets.

## Stack and evidence

Python 3.12, Pandas, NumPy, DuckDB, SQL, Parquet, Matplotlib, Plotly, Streamlit, Pytest, Git and GitHub Actions. Excel: tables, SUMIFS-driven controls, formulas and chart definitions; library/XML validation. Power BI preparation: star-schema design, Power Query scripts and DAX specifications; native execution pending.

- Source: US DOT/BTS Reporting Carrier On-Time Performance, Jan-Mar 2025; 1,645,503 records, 14 carriers, 333 airports.
- Eligible arrivals: 1,611,046; on-time: 1,293,780; late: 317,266; cancellations: 30,640.
- Rates: 80.3068% on time among eligible arrivals; 1.8620% cancelled among all reported flights.
- 22 SQL analyses; Session 2 reconciliation: 286,717 numeric comparisons plus 21,390 labels. Deployment evidence is a separate 26-check/144-comparison audit; do not add unlike counts into one inflated total.
- Live: https://aeropulse-flight-operations-analytics.streamlit.app/
- Code: https://github.com/harshvtomar/aeropulse-flight-operations-analytics

## 60-second explanation

AeroPulse is my airline operations analytics portfolio project using 1.65 million official BTS records for the first quarter of 2025. The business question is where delays and cancellations concentrate, and which comparisons remain credible after accounting for flight volumes and schedule mix. The pipeline preserves source checksums, validates flight statuses and builds a DuckDB warehouse with 22 SQL analyses. The public Streamlit dashboard recalculates rates from filtered flight counts rather than averaging percentages. One finding is that arrivals delayed at least two hours represent 14.42% of delayed flights but 47.75% of their delay minutes. I use that as an investigation priority, not a claim of savings or proven cause. The project has 197 local tests, an Excel report and documented statistical limitations. Power BI import and measure assets are prepared, but native Desktop execution is still pending.

## Two-minute explanation

The starting problem was to turn flight records into reliable operational comparisons. I used the complete January-March 2025 BTS reporting-carrier archives, rather than a convenience sample or mixed reporting/marketing datasets. Each archive has a recorded checksum, and imports are incremental and idempotent. The fact grain preserves the original source row, so duplicate-looking flights are investigated rather than silently deleted.

The most important modeling decision was the eligible-arrival denominator. A flight must not be cancelled or diverted and must have a known arrival delay. On time means less than 15 minutes late, including negative early-arrival values. Cancellation rates instead use all reported flights. That gives 80.3068% on time and 1.8620% cancelled for the quarter. The SQL layer covers volume, severity, time patterns, routes, recurrence and reported causes, with explicit volume screens and sample counts.

I then examined how comparisons change. A day-cluster bootstrap stratified by month retains same-day co-movement, while a common-support airline comparison uses identical weights across overlapping route/schedule/month cells. Only four of 91 pairs pass the support rules, so the adjusted results cannot become a general airline leaderboard. Severe delays are an operational priority because they account for nearly half of observed delayed-arrival minutes, but there is no claimed causal effect or measured financial improvement.

The deployed dashboard queries a 6.8 MB complete-population Parquet package. Filters use the detailed fact, empty populations are explicit, and exported reports include filter context. Python independently reconciles SQL outputs, and fixture and genuine-data tests are reported separately. I also delivered an Excel management report. Native Power BI and Excel checks are documented honestly as remaining verification work. In a production extension, I would seek richer event data, additional quarters and operational stakeholder validation before recommending an intervention.

## Interview questions and defensible answers

1. **What is the fact-table grain?** One accepted BTS source CSV row. Archive SHA-256 and one-based source row retain identity and lineage. Route/date/flight number alone is not assumed unique.
2. **Why DuckDB and Parquet?** They support local analytical SQL and columnar scans without a paid server. The complete deployment package reads only needed columns; concurrency and load still require evaluation for larger production use.
3. **How do imports stay idempotent?** Monthly manifests and file checksums identify already imported inputs. Changed fingerprints fail for review rather than silently appending or replacing history.
4. **What did cleaning change?** It validates schema, dates, codes, statuses, parsing and values while preserving raw archives. No rows were quarantined and no duplicate candidates were found in this snapshot; that is an observed result, not a disabled check.
5. **Why preserve negative delay?** An arrival ten minutes early is -10. Replacing it with zero changes the signed mean and loses operational information.
6. **How do you define on-time percentage?** Count eligible flights with signed arrival delay below 15, divided by eligible arrivals. Cancelled, diverted and missing-delay records are excluded from that denominator.
7. **Why not use the same denominator for cancellations?** Cancellation is a status among all reported flights. Restricting to completed arrivals would omit the events being measured; using a cancelled-only reason table would produce misleading rates.
8. **Why sum counts before division?** An average of group percentages weights small and large groups equally. SUM(on-time)/SUM(eligible) weights each flight once and remains correct under filters.
9. **What advanced SQL is demonstrated?** CTEs organize eligibility and segmentation; conditional aggregation calculates populations; windows support concentration, ranking and comparisons; joins add dimensions while cardinality checks prevent fanout. See sql/queries and sql/session2.
10. **How do you test joins?** Dimension keys must be unique and nonmissing; every fact key must match; joined row counts must equal fact counts. BI export validation also compares tables in both directions with EXCEPT ALL.
11. **What does zero missing cause coverage mean here?** All 317,266 eligible late arrivals have complete cause fields in this snapshot. It does not imply all source flights need cause reporting or that a missing value should become zero.
12. **Are delay causes causal explanations?** They are source-reported minute allocations. Establishing independent mechanisms would require event histories or a causal research design.
13. **What was the key finding?** 45,759 arrivals delayed at least 120 minutes make up 14.42% of late arrivals and 47.75% of their minutes. Prioritize recurring severe disruptions, retaining sample counts and denominators.
14. **Why require a route volume screen?** A very small route can have an extreme rate by chance. A minimum of 1,000 eligible flights screens route rankings; it is a policy for comparison, not proof of statistical significance.
15. **Why confidence intervals for a complete quarter?** The observed quarter is fully counted. Intervals are model-based stability summaries under resampling assumptions, not uncertainty about the counted totals.
16. **Why resample days rather than flights?** Flights share weather, schedules and network disruptions. Whole-day resampling preserves within-day co-movement; month stratification preserves seasonal composition. It still does not fully model multi-day storm persistence.
17. **What is the statistical result?** The on-time rate is 80.3068%; the 95% day-cluster interval is 78.3751-82.1702%, much wider than the IID Wilson reference. Do not describe either as a guaranteed future-quarter range.
18. **How does mix adjustment work?** Restrict each airline pair to sufficiently populated shared directed-route/six-hour-block/month cells and weight both by the same pooled common-support population. Report raw full-network, raw common-support and adjusted values together.
19. **What is the main adjustment limitation?** Only four of 91 pairs pass support criteria. Pair-specific references and omitted flights prevent a common adjusted leaderboard; unmeasured operational factors remain.
20. **Why separate airport roles in Power BI?** Separate origin and destination dimensions support two active one-to-many relationships without ambiguity. Six single-direction relationships filter the fact; route-airport cross-links are avoided.
21. **How would DAX handle zero denominators?** DIVIDE([On-Time Arrivals], [Eligible Arrivals]) returns BLANK for zero denominator. Count measures can use COALESCE to show zero, but cause sums should preserve BLANK. These specifications still require native execution.
22. **What is DAX filter context?** A slicer changes the rows visible to a measure through relationships. Measures should recompute counts and ratios in that context; a calculated column cannot substitute for a dynamic aggregate rate.
23. **Have you built a native Power BI report?** Not yet for AeroPulse. I prepared typed import scripts, the model contract, DAX and SQL reference cases. Native report creation, refresh and interaction testing remain pending; I can demonstrate the live Streamlit implementation today.
24. **What Excel controls work?** Executive B5 and B6 select airline and month; SUMIFS-based KPIs use both. Fixed Q1 ranking sheets do not pretend to follow those controls. Library recalculation and saved XML passed; native chart refresh remains unverified.
25. **How were extreme values handled?** Seven unique source records were traced; six completed-flight cases were internally consistent and one cancelled timeline remained unresolved. Canonical rows are retained and any exclusion is a separately labeled sensitivity analysis.
26. **What would you recommend to operations?** Investigate recurring severe-delay segments, compare volume and rate, and validate the reported category against event logs. Do not change staffing or claim savings solely from this descriptive quarter.
27. **How did live QA improve the app?** It exposed single-month date-axis labeling, cached backend identity after module reload and reset-control synchronization problems. Fixes were validated locally and on the deployed app; source KPIs stayed unchanged.
28. **How do you prevent fabricated filter behavior?** All supported filters use the complete minimal fact. Fixed statistical studies explicitly do not follow sidebar filters; downloads include population context.

## Demo sequence and preparation

Open Executive Overview and explain the two denominators. Select January and AA; show 75,088 reported flights and 72,082 eligible arrivals. Select DFW to LAX: 380 reported / 364 eligible. Lower the route screen from 1,000 to 100 and explain why only the ranking changes. Reset; show severe-delay concentration and explain reported allocations. Finish with methodology, test evidence and native software limitations.

Before interviews, run and explain one ingestion command, one SQL query and one test yourself. Adapt the scripts above into your own words; do not imply employer collaboration or unsupported native-tool experience.
