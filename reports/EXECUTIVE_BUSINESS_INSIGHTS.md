# Executive operational insights — Session 2

**Scope:** 1,645,503 genuine reporting-carrier flights, January 1–March 31, 2025; 1,611,046 eligible arrivals, 14 carriers and 333 airports. All source checksums and canonical Session 1 KPIs are preserved. This report supports investigation; it does not estimate causal operational quality or realized financial benefits.

## Decision-relevant findings

1. **Severe delays contribute disproportionately to delay minutes.** The 45,759 arrivals delayed at least 120 minutes are 14.42% of 317,266 delayed arrivals, but account for 47.75% of their 22,733,373 delay minutes. Prioritize recurring severe-delay cases, rather than optimizing only the overall mean.
2. **Delay volume and poor reliability are different questions.** The ten largest destination contributors account for 33.78% of delayed arrivals. DFW contributes 15,484 from 72,008 eligible arrivals (21.50% delayed). High contribution can reflect high traffic; compare rates and sample sizes alongside volume.
3. **Recurring destination gaps deserve focused review.** 24 airports exceed the same-month network delay rate in all three months while retaining at least 1,000 eligible arrivals in each month. The highest delayed-flight-volume examples are ORD, DCA, MCO, MIA, FLL. This is a screening flag, not evidence that airport management caused the delays.
4. **Carrier comparisons change when the population changes.** AA minus DL is -1.87 percentage points on the full networks, 0.84 on overlapping cells and 1.40 after identical pooled weighting of common route/schedule/month strata. Common support retains only 12.85% of AA and 11.02% of DL eligible flights (28,510/25,239). Do not generalize this adjusted result to either whole network. Only 4 of 91 carrier pairs pass the documented support screens.
5. **Day-level variation is much larger than an independence calculation suggests.** Network on-time performance is 80.31%; the month-stratified day-cluster 95% model interval is 78.38–82.17%, versus 80.25–80.37% for the IID reference. These are model-based stability summaries; the observed quarter is already fully counted.
6. **Reported allocations are complete for the specified late-arrival population.** All 317,266 late eligible arrivals have five reported cause fields with matching total minutes. Late-arriving aircraft is the largest allocated category; inspect repeat disruption patterns but do not treat the category label as a proven mechanism.

## Recommended investigation sequence

| Priority | Review | Evidence / guardrail |
|---|---|---|
| 1 | Recurrent severe delays at high-volume destinations and routes | Query 13 severity, 15–16 concentration, 22 recurrence; show volume and denominators |
| 2 | DCA and other recurring destination gaps by month, carrier and hour | Query 22 plus query 14/17; distinguish temporal shocks from persistent patterns |
| 3 | Overlapping AA–DL route/schedule cells | Use explicit common-support counts and weights; no whole-network superiority claim |
| 4 | Source follow-up for the cancelled extreme-delay record | Seven unique warnings traced; canonical rows retained, cancelled timeline unresolved |
| 5 | Dashboard preparation | Use validated BI exports, ratio-of-sums measures and separate raw/adjusted views |

## Limits and next evidence

Only one quarter is observed. Whole-day resampling preserves within-day co-movement but not cross-day storm persistence or all route/carrier dependence. Adjusted comparisons use six-hour blocks and pair-specific reference weights; no adjusted confidence interval or causal model is claimed. Multiple comparisons are exploratory. Source event logs would be needed to resolve the cancelled-flight anomaly. No staff, schedule or financial intervention is justified solely by these descriptive patterns.

## Evidence map

- [Extreme records and sensitivity](EXTREME_DELAY_INVESTIGATION.md)
- [Statistical analysis](STATISTICAL_ANALYSIS.md) and [mix adjustment](MIX_ADJUSTMENT_ANALYSIS.md)
- [Delay allocations](DELAY_CAUSE_ANALYSIS.md)
- `session2/sql/13_*.csv` through `22_*.csv`; all 12 Session 1 outputs remain in `queries/`
- `session2/figures/`: six new figures; original four figures remain intact
- [BI data model](../docs/BI_DATA_MODEL.md), [measure dictionary](../docs/BI_MEASURE_DICTIONARY.md)
