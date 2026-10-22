# BI measure contract — Session 2

Canonical populations and signed delays remain identical to Session 1. No PBIX or live dashboard is created by this export. DAX in `POWER_BI_MEASURES.dax` is a specification for Session 3, not a claim of tested Power BI execution.

## Detail-fact measures

| Measure | Formula and filters | Zero / missing denominator behavior |
|---|---|---|
| Reported flights | COUNTROWS(fact_flights) | 0 for empty population |
| Eligible arrivals | SUM(eligible_arrival) | Flag is 1 only when Cancelled=0, Diverted=0, ArrDelay nonmissing |
| On-time arrivals | SUM(on_time_arrival) | Eligible ArrDelay <15, including negative values |
| Late arrivals | SUM(late_arrival) | Eligible ArrDelay >=15 |
| On-time arrival rate | SUM(on_time_arrival) / SUM(eligible_arrival) | BLANK when denominator=0 |
| Late arrival rate | SUM(late_arrival) / SUM(eligible_arrival) | BLANK when denominator=0 |
| Cancellation rate | SUM(cancelled) / COUNTROWS(fact_flights) | BLANK for empty population |
| Diversion rate | SUM(diverted) / COUNTROWS(fact_flights) | BLANK for empty population; overlaps could count in both status rates |
| Mean eligible arrival delay | SUM(eligible_delay_minutes) / SUM(eligible_arrival) | BLANK without eligible arrivals; preserve negative delays |
| Mean delay among late arrivals | SUM(late_delay_minutes) / SUM(late_arrival) | BLANK without late arrivals |
| Cause reported minutes (each category) | SUM(original cause column) | BLANK when every source value is missing; do not COALESCE to zero |
| Cause coverage among late arrivals | COUNT of late rows with nonmissing category / SUM(late_arrival) | BLANK without late arrivals; zero coverage if late rows exist but none have a reported value |

Rate measures yield fractions and should use Power BI percentage format; exported reports elsewhere may use 0–100 percentage units. Never multiply a DAX fraction by 100 and then apply percentage formatting.

## Additive aggregate measures

`reported_flights`, `eligible_arrivals`, `on_time_arrivals`, `late_arrivals`, `cancellations`, `diversions`, `eligible_delay_minutes`, and `late_delay_minutes` can be summed **within a single aggregate table**. Compute every rate as SUM(numerator)/SUM(denominator). Never average row percentages, and never sum counts from different aggregate tables covering the same flights.

`agg_delay_causes` repeats each month/carrier's population once per category. Its population columns are valid within a single selected category; summing them across categories multiplies flight counts by five. Its minute allocations may be summed across categories, but that sum describes reported allocations and excludes missing data. `records_with_value` counts nonmissing entries including reported zeros. `late_records_with_value / late_arrivals` gives category-specific coverage.

`agg_cancellations` includes cancelled flights only and is suitable for reason shares. It cannot provide cancellation rates by itself; use the full fact or a population-matched aggregate denominator. Unknown reason codes remain visible as `UNKNOWN` when missing.

## Filters and screening

Carrier, origin, destination, date, hour and directed route filters should propagate from the matching dimension to the detail fact. Canonical on-time metrics exclude cancelled/diverted rows through the eligibility flag; do not remove these rows from the fact before computing cancellation/diversion rates.

Route league tables require at least 1,000 eligible arrivals in the specified analysis coverage. Airline-origin comparisons use at least 500. Recompute threshold eligibility after filtering; do not reuse a full-quarter qualification flag for a smaller selected period. Display the eligible denominator, date coverage and applied rule. These volume rules are screening policies, not statistical significance tests.

## Comparison measures

Raw and mix-adjusted outputs are separate analytical products. Do not overwrite raw on-time measures with standardized rates. Adjustment weights and support are comparison-specific; adjusted rates are generally nonadditive and cannot be averaged or regrouped arbitrarily. Use the statistical module's precomputed estimates, intervals and support metadata with their original grouping.
