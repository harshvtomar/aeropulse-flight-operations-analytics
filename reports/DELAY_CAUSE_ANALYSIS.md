# Reported delay-cause analysis — Session 2

Analysis population: **317,266** normal completed flights arriving at least 15 minutes late. All **317,266** have nonmissing values for all five cause fields; **0** complete records fail the allocated-minute = arrival-delay check. **0** records outside this late-arrival population contain any cause-minute value. Zero values mean a reported zero; missing values remain missing.

| Source category | Allocated minutes | Share of observed allocated minutes |
|---|---:|---:|
| Late-arriving aircraft | 8,427,350 | 37.07% |
| Carrier | 7,786,238 | 34.25% |
| National Aviation System | 4,881,464 | 21.47% |
| Weather | 1,608,364 | 7.07% |
| Security | 29,957 | 0.13% |

The five categories sum to **22,733,373 minutes**, equal to summed arrival delay over the 317,266 late eligible records. Coverage is 100% for each category in each month in this snapshot. This is an observed reconciliation, not a certification of carrier reporting compliance or independently verified root causes.

[BTS Technical Directive 39](https://www.bts.gov/explore-topics-and-geography/modes/aviation/number-39-technical-directive-reporting-time), effective January 1, 2025, sections 5 and 7, distinguishes cancellation reasons from late-arrival minute allocations. It does not require cause minutes for on-time or diverted flights. Its allocation rules reconcile minutes to arrival delay and allow predominant-cause reporting. Those conventions limit causal interpretation.

Cancellation reasons are analyzed separately in query 21; cancelled flights are not treated as missing late-arrival reports. Do not substitute zero for unavailable allocations or sum the repeated population denominators across category rows. Minute shares use total observed allocated minutes, not flight counts. Categories need not represent unique independent incidents, and weather effects can appear indirectly in other reported categories.

Evidence: `session2/sql/20_cause_coverage.csv`, `session2/figures/05_reported_delay_causes.png`, and the independent `session2/SQL_RECONCILIATION.json`. Reproduce through `python -m src.advanced_sql` then `python -m src.session2_report`.
