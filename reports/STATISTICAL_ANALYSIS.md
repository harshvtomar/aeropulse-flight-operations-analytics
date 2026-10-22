# Statistical analysis — Session 2

Coverage: complete imported BTS reporting-carrier quarter, January–March 2025. These observed rates are finite-population descriptions. The intervals ask how rates might vary under a model of exchangeable days within each month; they are not uncertainty about the already observed records.

Used 2,000 seeded replicates of whole calendar dates, stratified within January (31 days), February (28) and March (31). The same day weights are used across carriers for pair differences. Within-day network/weather clustering is retained. Cross-day serial dependence and future-year generalization are not covered. IID Wilson bounds are included only as a reference and do not account for clustering.

| Network metric | Events / denominator | Observed % | Day-cluster 95% interval (%) | IID Wilson reference (%) |
|---|---:|---:|---|---|
| on_time | 1,293,780 / 1,611,046 | 80.3068 | 78.3751–82.1702 | 80.2454–80.3682 |
| cancellation | 30,640 / 1,645,503 | 1.8620 | 1.3571–2.4335 | 1.8415–1.8828 |

## Preselected exposure-based comparisons

The three largest carriers by reported flight volume (WN, DL, AA) were selected before examining pair effects. Differences are A minus B in percentage points. These are raw, unadjusted comparisons; consult MIX_ADJUSTMENT_ANALYSIS.md for composition sensitivity. No operational superiority is inferred.

| A − B | Metric | Difference (pp) | Shared-day 95% interval (pp) | A / B denominator |
|---|---|---:|---|---|
| WN − DL | on_time | 2.704 | 1.031–4.398 | 322,744 / 228,943 |
| WN − DL | cancellation | 0.231 | -0.522–0.849 | 327,938 / 232,126 |
| WN − AA | on_time | 4.571 | 3.217–5.905 | 322,744 / 221,933 |
| WN − AA | cancellation | -0.789 | -1.538–-0.122 | 327,938 / 227,500 |
| DL − AA | on_time | 1.867 | 0.310–3.448 | 228,943 / 221,933 |
| DL − AA | cancellation | -1.019 | -1.894–-0.313 | 232,126 / 227,500 |

## Interpretation and rules

- A one-percentage-point difference corresponds descriptively to 10 additional events per 1,000 denominator flights. This is an effect-size interpretation, not an estimated policy impact.
- Monthly estimates use each month separately; quarter bootstraps retain calendar-month day counts and compute ratios of resampled count sums, never averages of daily percentages.
- At least seven observed dates per month are required for cluster intervals. Zero denominators return missing intervals; valid replicate counts are published. This quarter supports every listed carrier/month estimate.
- All airline intervals are descriptive. Pair intervals are exploratory, without family-wise multiple-testing correction. We do not run a significance leaderboard or treat crossing/non-crossing intervals as operational quality evidence.
- The source population is one quarter, not a random sample of all flights or future operations. Day clustering does not fully account for persistent carrier/route dependence or multi-day storms.
- Outlier sensitivity preserves canonical metrics and is reported separately in EXTREME_DELAY_INVESTIGATION.md.

## Reproducible evidence

`reports/session2/rate_intervals.csv`, `monthly_rate_intervals.csv`, `paired_carrier_differences.csv`, `statistical_daily_counts.csv` and `STATISTICAL_RUN.json`. Run `python -m src.statistics`.
