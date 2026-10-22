"""Descriptive rate uncertainty with reproducible month-stratified day resampling.

The dataset is a finite observed quarter: rates are exact descriptions. Intervals
are model-based stability summaries, not sampling error for this census.
"""
from itertools import combinations
from pathlib import Path
from statistics import NormalDist
import argparse
import json
import duckdb
import numpy as np
import pandas as pd


def wilson_interval(successes, total, confidence=0.95):
    """IID binomial reference interval; does not account for flight clustering."""
    if not np.isfinite(successes) or not np.isfinite(total):
        raise ValueError('Counts must be finite')
    if not 0 < confidence < 1 or total < 0 or successes < 0 or successes > total:
        raise ValueError('Invalid binomial inputs or confidence')
    if int(successes) != successes or int(total) != total:
        raise ValueError('Counts must be integers')
    if total == 0:
        return (np.nan, np.nan)
    z = NormalDist().inv_cdf((1 + confidence) / 2)
    p = successes / total
    denom = 1 + z*z/total
    center = (p + z*z/(2*total))/denom
    half = z*np.sqrt(p*(1-p)/total + z*z/(4*total*total))/denom
    return max(0., center-half), min(1., center+half)


def month_day_weights(dates, reps=2000, seed=202501, min_days=7):
    """Resample whole dates within calendar months, preserving dates per month.

    One weight matrix can be reused across carriers/metrics for paired comparisons.
    Dates must be unique, normalized daily timestamps. Serial dependence between
    days is not modelled; shared within-day shocks are retained.
    """
    dates = pd.DatetimeIndex(dates)
    if dates.has_duplicates or dates.isna().any() or not dates.equals(dates.normalize()):
        raise ValueError('Dates must be unique, nonmissing daily dates')
    if not dates.is_monotonic_increasing:
        raise ValueError('Dates must be sorted')
    if not len(dates):
        raise ValueError('Need observed dates')
    if int(reps) != reps or int(min_days) != min_days or reps < 100 or min_days < 2:
        raise ValueError('Need >=100 replicates and >=2 dates per stratum')
    rng = np.random.default_rng(seed)
    weights = np.zeros((reps, len(dates)), dtype=np.int32)
    months = dates.to_period('M')
    for month in months.unique():
        idx = np.flatnonzero(months == month)
        if len(idx) < min_days:
            raise ValueError('Insufficient dates in a month for cluster uncertainty')
        weights[:, idx] = rng.multinomial(len(idx), np.full(len(idx), 1/len(idx)), size=reps)
    return weights


def resampled_rates(successes, totals, weights):
    weights = np.asarray(weights, dtype=float)
    if weights.ndim != 2 or np.any(~np.isfinite(weights)) or np.any(weights < 0) or np.any(weights != np.floor(weights)):
        raise ValueError('Weights must be a matrix of nonnegative integer counts')
    successes = np.asarray(successes, dtype=float)
    totals = np.asarray(totals, dtype=float)
    if successes.shape != totals.shape or successes.ndim != 1 or weights.shape[1] != len(totals):
        raise ValueError('Mismatched daily counts and resampling weights')
    if np.any(~np.isfinite(successes)) or np.any(~np.isfinite(totals)) or np.any(successes < 0) or np.any(totals < successes):
        raise ValueError('Invalid daily counts')
    if np.any(successes != np.floor(successes)) or np.any(totals != np.floor(totals)):
        raise ValueError('Daily counts must be integers')
    numerator, denominator = weights @ successes, weights @ totals
    return np.divide(numerator, denominator, out=np.full(len(weights), np.nan), where=denominator > 0)


def percentile_interval(values, confidence=.95):
    if not 0 < confidence < 1: raise ValueError('Invalid confidence')
    values = np.asarray(values)
    values = values[np.isfinite(values)]
    if not len(values): return (np.nan, np.nan)
    return tuple(np.quantile(values, [(1-confidence)/2, (1+confidence)/2]))


def rate_summary(successes, totals, weights):
    successes, totals = np.asarray(successes), np.asarray(totals)
    draws = resampled_rates(successes, totals, weights)
    s, n = int(successes.sum()), int(totals.sum())
    lo, hi = percentile_interval(draws)
    wlo, whi = wilson_interval(s, n)
    return dict(successes=s, denominator=n, rate_pct=100*s/n if n else np.nan,
                day_cluster_low_pct=100*lo, day_cluster_high_pct=100*hi,
                iid_wilson_low_pct=100*wlo, iid_wilson_high_pct=100*whi,
                valid_replicates=int(np.isfinite(draws).sum()))


def paired_difference(a_success, a_total, b_success, b_total, weights):
    """A minus B in percentage points, with shared sampled calendar dates."""
    a = resampled_rates(a_success, a_total, weights)
    b = resampled_rates(b_success, b_total, weights)
    lo, hi = percentile_interval(100*(a-b))
    na, nb = np.sum(a_total), np.sum(b_total)
    delta = 100*(np.sum(a_success)/na - np.sum(b_success)/nb) if na and nb else np.nan
    return dict(difference_pp=delta, day_cluster_low_pp=lo, day_cluster_high_pp=hi,
                valid_replicates=int(np.isfinite(a-b).sum()))



def validate_daily_inputs(root, daily):
    """Independently rederive numerator/denominator counts from Parquet in pandas."""
    fields=['FlightDate','Reporting_Airline','Cancelled','Diverted','ArrDelay']
    frame=pd.concat([pd.read_parquet(p,columns=fields) for p in sorted((Path(root)/'data/processed').glob('*/flights.parquet'))],ignore_index=True)
    eligible=frame.Cancelled.eq(0)&frame.Diverted.eq(0)&frame.ArrDelay.notna()
    frame=frame.assign(reported=1,eligible=eligible.astype(int),ontime=(eligible&frame.ArrDelay.lt(15)).astype(int),cancelled=frame.Cancelled.eq(1).astype(int))
    cols=['reported','eligible','ontime','cancelled']
    expected=frame.groupby(['FlightDate','Reporting_Airline'])[cols].sum().sort_index()
    actual=daily.set_index(['flight_date','airline'])[cols].sort_index()
    expected.index.names=actual.index.names
    pd.testing.assert_frame_equal(actual,expected,check_dtype=False,check_index_type=False)
    return {'passed':True,'daily_groups':len(expected),'numeric_comparisons':len(expected)*len(cols),
            'method':'pandas from validated Parquet; statuses and delay rederived independently of SQL flags'}


def run(root='.', reps=2000, seed=202501):
    root = Path(root); out = root/'reports/session2'; out.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(root/'data/aeropulse.duckdb'), read_only=True) as con:
        daily = con.execute('''SELECT CAST(FlightDate AS DATE) AS flight_date, Reporting_Airline AS airline,
          count(*) AS reported, count(*) FILTER(WHERE arrival_eligible) AS eligible,
          count(*) FILTER(WHERE on_time_arrival) AS ontime,
          count(*) FILTER(WHERE Cancelled=1) AS cancelled
          FROM fact_flights GROUP BY ALL ORDER BY flight_date, airline''').df()
    validation=validate_daily_inputs(root,daily)
    (out/'STATISTICAL_INPUT_RECONCILIATION.json').write_text(json.dumps(validation,indent=2))
    dates = pd.DatetimeIndex(sorted(daily.flight_date.unique()))
    weights = month_day_weights(dates, reps, seed)
    summaries = []
    network = daily.groupby('flight_date')[['reported','eligible','ontime','cancelled']].sum().reindex(dates,fill_value=0)
    carrier_daily = {name:g.set_index('flight_date').reindex(dates,fill_value=0) for name,g in daily.groupby('airline')}
    populations = {'ALL':network, **carrier_daily}
    for name,g in populations.items():
        for metric,num,den in [('on_time','ontime','eligible'),('cancellation','cancelled','reported')]:
            summaries.append({'airline':name,'metric':metric,'period':'2025-Q1',
                              **rate_summary(g[num].to_numpy(),g[den].to_numpy(),weights)})
    monthly = []
    for period in dates.to_period('M').unique():
        idx = np.flatnonzero(dates.to_period('M') == period)
        mw = month_day_weights(dates[idx],reps,seed)
        for name,g in populations.items():
            for metric,num,den in [('on_time','ontime','eligible'),('cancellation','cancelled','reported')]:
                monthly.append({'airline':name,'metric':metric,'period':str(period),
                                **rate_summary(g[num].to_numpy()[idx],g[den].to_numpy()[idx],mw)})
    rate_table = pd.DataFrame(summaries); month_table = pd.DataFrame(monthly)
    # Pick comparisons by exposure, not by extreme observed outcome.
    top3 = daily.groupby('airline').reported.sum().sort_values(ascending=False).head(3).index.tolist()
    comparisons = []
    for a,b in combinations(top3,2):
        ga,gb=carrier_daily[a],carrier_daily[b]
        for period,idx in [('2025-Q1',np.arange(len(dates)))]+[(str(m),np.flatnonzero(dates.to_period('M')==m)) for m in dates.to_period('M').unique()]:
            w=weights if period=='2025-Q1' else month_day_weights(dates[idx],reps,seed)
            for metric,num,den in [('on_time','ontime','eligible'),('cancellation','cancelled','reported')]:
                comparisons.append({'airline_a':a,'airline_b':b,'period':period,'metric':metric,
                    'denominator_a':int(ga[den].to_numpy()[idx].sum()),'denominator_b':int(gb[den].to_numpy()[idx].sum()),
                    **paired_difference(ga[num].to_numpy()[idx],ga[den].to_numpy()[idx],gb[num].to_numpy()[idx],gb[den].to_numpy()[idx],w)})
    comparison_table=pd.DataFrame(comparisons)
    daily.to_csv(out/'statistical_daily_counts.csv',index=False)
    rate_table.to_csv(out/'rate_intervals.csv',index=False)
    month_table.to_csv(out/'monthly_rate_intervals.csv',index=False)
    comparison_table.to_csv(out/'paired_carrier_differences.csv',index=False)
    metadata={'bootstrap_replicates':reps,'seed':seed,'calendar_dates':len(dates),'months':len(dates.to_period('M').unique()),
              'pair_selection':'three highest reported-flight-volume carriers','selected_carriers':top3,
              'bootstrap_unit':'calendar date shared across carriers; stratified within month',
              'confidence':.95,'interval_type':'model-based descriptive day stability, not sampling uncertainty of observed census',
              'serial_correlation_modelled':False,'multiple_comparison_correction':False}
    (out/'STATISTICAL_RUN.json').write_text(json.dumps(metadata,indent=2))
    lines=['# Statistical analysis — Session 2','',
      'Coverage: complete imported BTS reporting-carrier quarter, January–March 2025. These observed rates are finite-population descriptions. The intervals ask how rates might vary under a model of exchangeable days within each month; they are not uncertainty about the already observed records.','',
      f'Used {reps:,} seeded replicates of whole calendar dates, stratified within January (31 days), February (28) and March (31). The same day weights are used across carriers for pair differences. Within-day network/weather clustering is retained. Cross-day serial dependence and future-year generalization are not covered. IID Wilson bounds are included only as a reference and do not account for clustering.','',
      '| Network metric | Events / denominator | Observed % | Day-cluster 95% interval (%) | IID Wilson reference (%) |',
      '|---|---:|---:|---|---|']
    for _,r in rate_table[rate_table.airline.eq('ALL')].iterrows():
        lines.append(f'| {r.metric} | {r.successes:,} / {r.denominator:,} | {r.rate_pct:.4f} | {r.day_cluster_low_pct:.4f}–{r.day_cluster_high_pct:.4f} | {r.iid_wilson_low_pct:.4f}–{r.iid_wilson_high_pct:.4f} |')
    lines+=['','## Preselected exposure-based comparisons','',
      f'The three largest carriers by reported flight volume ({", ".join(top3)}) were selected before examining pair effects. Differences are A minus B in percentage points. These are raw, unadjusted comparisons; consult MIX_ADJUSTMENT_ANALYSIS.md for composition sensitivity. No operational superiority is inferred.','',
      '| A − B | Metric | Difference (pp) | Shared-day 95% interval (pp) | A / B denominator |',
      '|---|---|---:|---|---|']
    for _,r in comparison_table[comparison_table.period.eq('2025-Q1')].iterrows():
        lines.append(f'| {r.airline_a} − {r.airline_b} | {r.metric} | {r.difference_pp:.3f} | {r.day_cluster_low_pp:.3f}–{r.day_cluster_high_pp:.3f} | {r.denominator_a:,} / {r.denominator_b:,} |')
    lines+=['','## Interpretation and rules','',
      '- A one-percentage-point difference corresponds descriptively to 10 additional events per 1,000 denominator flights. This is an effect-size interpretation, not an estimated policy impact.',
      '- Monthly estimates use each month separately; quarter bootstraps retain calendar-month day counts and compute ratios of resampled count sums, never averages of daily percentages.',
      '- At least seven observed dates per month are required for cluster intervals. Zero denominators return missing intervals; valid replicate counts are published. This quarter supports every listed carrier/month estimate.',
      '- All airline intervals are descriptive. Pair intervals are exploratory, without family-wise multiple-testing correction. We do not run a significance leaderboard or treat crossing/non-crossing intervals as operational quality evidence.',
      '- The source population is one quarter, not a random sample of all flights or future operations. Day clustering does not fully account for persistent carrier/route dependence or multi-day storms.',
      '- Outlier sensitivity preserves canonical metrics and is reported separately in EXTREME_DELAY_INVESTIGATION.md.',
      '', '## Reproducible evidence','',
      '`reports/session2/rate_intervals.csv`, `monthly_rate_intervals.csv`, `paired_carrier_differences.csv`, `statistical_daily_counts.csv` and `STATISTICAL_RUN.json`. Run `python -m src.statistics`.']
    (root/'reports/STATISTICAL_ANALYSIS.md').write_text('\n'.join(lines)+'\n')
    return metadata

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',default='.');parser.add_argument('--reps',type=int,default=2000);args=parser.parse_args()
    print(json.dumps(run(args.root,args.reps),indent=2))
