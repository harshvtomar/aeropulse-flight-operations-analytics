# Statistical methods and interpretation

## What the intervals mean
January–March 2025 is the complete imported reporting-carrier population, not a random sample. Its observed counts/rates are finite-population descriptions. We report model-based stability intervals under exchangeable calendar dates within each month. These are not margins of error for records already observed, predictions for future months, or evidence of causal operational quality.

## Rate estimates and IID reference
On-time numerator: eligible arrivals with signed arrival delay <15 minutes. Denominator: noncancelled, nondiverted arrivals with nonmissing arrival delay. Cancellation numerator: Cancelled=1; denominator: all reported flights. Ratios use sums of counts; daily or group percentages are never averaged equally.

The Wilson interval uses the standard score inversion with z=1.95996398454 at 95% confidence. For zero exposure it returns missing bounds. All-zero/all-one event cases retain nonzero uncertainty where appropriate. Wilson treats each event as independent; it is published solely as an explicitly IID reference because flights share weather, dates, routes, aircraft and airline processes.

## Month-stratified day-cluster bootstrap
Use seed 202501 and 2,000 replicates. Within January, February and March, sample the observed calendar dates with replacement, preserving each month's 31/28/31 dates. One sampled date carries all network/carrier counts for that day. Recompute ratio-of-sums each replicate; the 2.5th and 97.5th percentiles form the interval. Shared weights for paired carrier differences preserve same-day covariance. All three months contain every calendar date and every carrier has daily observations in this snapshot.

At least seven calendar dates within each included month are required by the resampling helper. This is an implementation screening rule, not a confidence guarantee. Zero-denominator draws remain missing; exports disclose valid replicate counts. Months are also reported separately. The three largest carriers by flight exposure (WN, DL, AA) determine pair selection; outcome extremes do not determine selection. Effects are A-minus-B percentage points. One point corresponds descriptively to 10 events per 1,000 denominator flights, not a change achievable through intervention.

Day resampling retains dependence within a day but does not account for persistent route/airline effects or multi-day storms. No serial block bootstrap or causal model is claimed. Pair intervals are exploratory; there is no multiplicity correction, superiority leaderboard or operational decision based solely on interval overlap.

## Common-support direct standardization
For each carrier pair, strata are directed origin ID × destination ID × six-hour local departure block × month. Each retained stratum must have at least 20 eligible arrivals for both carriers. Reference weights are the two carriers' pooled eligible counts in retained strata, normalized to one. Each carrier's stratum-specific on-time rates receive those identical weights.

The output separately reports full-network raw rates, common-support raw rates, and common-support standardized rates. Full-to-common differences include population restriction; common-to-standardized differences reflect weighting within the same retained strata. Omitted strata/observations and carrier coverage are explicit. A comparison passes screening only with 20 common strata, 1,000 retained arrivals per carrier and at least 10% of each carrier's full eligible population. Unsupported estimates are exploratory and must not be ranked.

Reference populations differ by pair, so adjusted values are not an all-carrier league table. Six-hour blocks retain finer schedule differences, and date/weather/staffing/aircraft differences remain uncontrolled. Adjusted results are point estimates; the raw bootstrap intervals must not be attached to adjusted estimates.

## Verification and reproduction
`python -m src.statistics` and `python -m src.mix_analysis` regenerate reports/CSV outputs. Daily counts and route/schedule/month cells are independently rebuilt from validated Parquet with pandas, deriving eligibility from source statuses/delays; exact SQL/Python count equality is asserted. Reconciliation JSONs record the comparison counts. Unit tests use known Wilson values, boundary and invalid-input cases, conserved monthly bootstrap weights, paired effects, deterministic seeds, and a handcrafted composition example where a 64-point raw gap disappears under common reference weights. These test numerical implementation, not the truth of modelling assumptions.
