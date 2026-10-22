# Route and schedule-mix analysis — Session 2

Full-quarter raw rates compare different networks. The analysis below changes the question to pair-specific overlapping route/schedule/month strata. It does not estimate causal airline quality.

## Reference population and common support

A stratum is directed DOT origin-airport ID × destination-airport ID × six-hour scheduled local departure block × calendar month. A cell enters common support only when BOTH compared carriers have at least 20 eligible arrivals. Reference weights are pooled A+B eligible flights in retained strata divided by their combined retained count. The two carrier stratum-specific rates receive identical weights.

Of 91 possible carrier pairs, **4** meet all screening rules: at least 20 common strata, 1,000 common eligible arrivals per carrier and 10% coverage of each carrier’s full eligible population. These thresholds are screening choices, not guarantees of unbiased comparisons. The export retains all pairs and a comparison_eligible flag; unsupported pairs must not enter a ranking.

The reference differs by pair. Therefore adjusted carrier rates from different rows are not a common-reference league table. Six-hour blocks leave within-block schedule differences; we also do not control for day, aircraft, weather, staffing or network propagation. Regional and mainline reporting carriers remain distinct.

## Three largest-volume carriers: explicit population changes

| A − B | Full raw gap (pp) | Common raw gap (pp) | Adjusted gap (pp) | Common n A / B | Coverage A / B | Strata | Screen |
|---|---:|---:|---:|---|---|---:|---|
| AA − DL | -1.867 | 0.842 | 1.401 | 28,510 / 25,239 | 12.8% / 11.0% | 560 | Pass |
| AA − WN | -4.571 | -1.081 | -0.574 | 17,478 / 20,143 | 7.9% / 6.2% | 445 | Insufficient support |
| DL − WN | -2.704 | -2.960 | -2.647 | 38,225 / 22,244 | 16.7% / 6.9% | 630 | Insufficient support |

Full raw → common raw reflects restricting the compared population. Common raw → adjusted reflects weighting the same retained strata identically. Combining these changes into a single “mix effect” would obscure selection into common support. Adjusted estimates are point estimates only; raw day-cluster intervals in STATISTICAL_ANALYSIS.md do not transfer to them.

## Composition across operational axes

The complete `carrier_composition.csv` export includes origin airports, destination airports, directed routes, individual scheduled hours, months and quarter-wide route-volume bands (<100, 100–499, 500–999, 1000+ eligible arrivals). Shares use each carrier’s eligible arrivals as denominator, sum to 100% within carrier/axis, and retain cell counts. These marginal profiles explain where overlap exists; they are not separate causal adjustments.

## Investigation priorities

- Use the top-three common-support examples to inspect route/hour/month cells with large observed gaps, then check stability by day and month before recommending action.
- Prioritize high-volume delayed routes and airports identified by concentration tables. A large raw gap on a poorly overlapping network does not establish an airline-level problem.
- For carrier pairs failing support screens, report insufficient overlap rather than extrapolating missing cells or replacing absent rates with zero.

## Evidence

`mix_adjusted_pairs.csv` lists full and retained sample sizes, omitted counts/strata, raw full and common-support rates, adjusted rates and eligibility for every pair. `mix_reference_strata_top3.csv` contains exact weights and counts for the three exposure-selected comparisons. Full input cells are regenerated locally as `data/processed/session2/mix_cells.parquet`; the checksum is in `MIX_RUN.json`. Run `python -m src.mix_analysis`.
