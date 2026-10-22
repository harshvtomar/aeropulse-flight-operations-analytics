"""Execute ten Session 2 queries and independently reconcile every output cell.

The reference calculations use pandas against validated Parquet and rederive status
eligibility. They never read SQL output to calculate expected values.
"""
import argparse
import json
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

from .validate import CAUSES

SQL_DIR = Path(__file__).resolve().parents[1] / 'sql/session2'
KEYS = {
    '13_delay_severity': ['severity'],
    '14_airline_monthly': ['Year', 'Month', 'DOT_ID_Reporting_Airline'],
    '15_route_concentration': ['OriginAirportID', 'DestAirportID'],
    '16_airport_concentration': ['DestAirportID'],
    '17_departure_hour_monthly': ['Year', 'Month', 'departure_hour'],
    '18_weekend_monthly': ['Year', 'Month', 'day_type'],
    '19_daily_normalization': ['flight_date'],
    '20_cause_coverage': ['Year', 'Month', 'cause'],
    '21_cancellation_patterns': ['Year', 'Month', 'DOT_ID_Reporting_Airline', 'OriginAirportID'],
    '22_recurring_airport_delays': ['DestAirportID'],
}


def prepare(d):
    """Derive pandas-only status flags, independent of stored boolean columns."""
    d = d.copy()
    d['FlightDate'] = pd.to_datetime(d.FlightDate)
    d['_eligible'] = d.Cancelled.eq(0) & d.Diverted.eq(0) & d.ArrDelay.notna()
    d['_late'] = d._eligible & d.ArrDelay.ge(15)
    d['_ontime'] = d._eligible & d.ArrDelay.lt(15)
    d['_cancel'] = d.Cancelled.eq(1)
    d['_one'] = 1
    d['departure_hour'] = (d.CRSDepTime // 100 % 24).astype(int)
    d['day_type'] = np.where(d.DayOfWeek >= 6, 'weekend', 'weekday')
    return d


def aggregate(d, keys):
    g = d.groupby(keys, dropna=False).agg(
        reported_flights=('_one', 'sum'), eligible_flights=('_eligible', 'sum'),
        delayed_flights=('_late', 'sum'), on_time_flights=('_ontime', 'sum'),
        cancelled_flights=('_cancel', 'sum')).reset_index()
    g['delay_rate_pct'] = 100 * g.delayed_flights / g.eligible_flights.replace(0, np.nan)
    g['cancellation_pct'] = 100 * g.cancelled_flights / g.reported_flights
    return g


def calendar(d):
    frames = []
    for y, m in d[['Year', 'Month']].drop_duplicates().itertuples(index=False, name=None):
        start = pd.Timestamp(int(y), int(m), 1)
        dates = pd.date_range(start, start + pd.offsets.MonthEnd(), freq='D')
        frames.append(pd.DataFrame({'flight_date': dates, 'Year': y, 'Month': m}))
    return pd.concat(frames, ignore_index=True)


def reference_tables(raw):
    d = prepare(raw)
    out = {}
    eligible = d.loc[d._eligible].copy()
    eligible['severity'] = pd.cut(eligible.ArrDelay, [-np.inf, 15, 30, 60, 120, np.inf],
                                 right=False, labels=['0 under 15', '1 15-29', '2 30-59', '3 60-119', '4 120+'])
    g = eligible.groupby('severity', observed=True).ArrDelay.agg(
        flights='size', signed_arrival_minutes='sum', avg_arrival_minutes='mean').reset_index()
    g['severity'] = g.severity.astype(str)
    g['eligible_share_pct'] = 100 * g.flights / len(eligible)
    g['delayed_share_pct'] = np.where(g.severity.eq('0 under 15'), np.nan,
                                    100 * g.flights / (d._late.sum() or np.nan))
    out['13_delay_severity'] = g

    g = aggregate(d, ['Year', 'Month', 'DOT_ID_Reporting_Airline', 'Reporting_Airline'])
    g = g.sort_values(['DOT_ID_Reporting_Airline', 'Year', 'Month'])
    g['prior_month_change_pp'] = g.groupby('DOT_ID_Reporting_Airline').delay_rate_pct.diff()
    month_index = g.Year * 12 + g.Month
    consecutive = month_index.groupby(g.DOT_ID_Reporting_Airline).diff().eq(1)
    g.loc[~consecutive, 'prior_month_change_pp'] = np.nan
    out['14_airline_monthly'] = g

    for name, keys in [('15_route_concentration', ['OriginAirportID', 'DestAirportID', 'Origin', 'Dest']),
                       ('16_airport_concentration', ['DestAirportID', 'Dest'])]:
        g = aggregate(d, keys)
        sort_keys = ['OriginAirportID', 'DestAirportID'] if name.startswith('15') else ['DestAirportID']
        g = g.sort_values(['delayed_flights'] + sort_keys, ascending=[False] + [True] * len(sort_keys))
        denominator = g.delayed_flights.sum() or np.nan
        g['network_delayed_share_pct'] = 100 * g.delayed_flights / denominator
        if name.startswith('15'):
            g['cumulative_delayed_share_pct'] = 100 * g.delayed_flights.cumsum() / denominator
        g['contribution_rank'] = np.arange(1, len(g) + 1)
        g['rate_comparison_eligible'] = g.eligible_flights >= 1000
        out[name] = g

    keys = ['Year', 'Month', 'departure_hour']
    g = aggregate(d, keys)
    severe = d.assign(_severe=d._eligible & d.ArrDelay.ge(120)).groupby(keys)._severe.sum()
    out['17_departure_hour_monthly'] = g.merge(severe.rename('severe_delayed_flights'), on=keys)

    cal = calendar(d)
    cal['day_type'] = np.where(cal.flight_date.dt.dayofweek >= 5, 'weekend', 'weekday')
    keys = ['Year', 'Month', 'day_type']
    g = aggregate(d, keys).merge(cal.groupby(keys).size().rename('calendar_days'), on=keys)
    g['flights_per_calendar_day'] = g.reported_flights / g.calendar_days
    out['18_weekend_monthly'] = g

    g = aggregate(d.assign(flight_date=d.FlightDate.dt.normalize()), ['flight_date'])
    count_cols = ['reported_flights', 'eligible_flights', 'delayed_flights', 'cancelled_flights']
    daily = cal.drop(columns='day_type').merge(g[['flight_date'] + count_cols], on='flight_date', how='left')
    daily[count_cols] = daily[count_cols].fillna(0).astype(int)
    by_month = daily.groupby(['Year', 'Month'])
    daily['calendar_days_in_month'] = by_month.reported_flights.transform('size')
    daily['monthly_flights'] = by_month.reported_flights.transform('sum')
    daily['monthly_flights_per_day'] = by_month.reported_flights.transform('mean')
    daily['delay_rate_pct'] = 100 * daily.delayed_flights / daily.eligible_flights.replace(0, np.nan)
    daily['cancellation_pct'] = 100 * daily.cancelled_flights / daily.reported_flights.replace(0, np.nan)
    out['19_daily_normalization'] = daily

    records = []
    for (y, m), x in d.groupby(['Year', 'Month']):
        complete = x[CAUSES].notna().all(axis=1)
        total = x[CAUSES].sum(axis=1, min_count=len(CAUSES))
        valid = x._late & complete
        base = dict(Year=y, Month=m, reported_flights=len(x), late_eligible_flights=int(x._late.sum()),
                    late_complete_cause_records=int(valid.sum()),
                    late_incomplete_cause_records=int((x._late & ~complete).sum()),
                    outside_late_any_cause_records=int((~x._late & x[CAUSES].notna().any(axis=1)).sum()),
                    complete_allocation_mismatch_records=int((valid & (total - x.ArrDelay).abs().gt(1e-6)).sum()),
                    complete_allocated_minutes=total[valid].sum(min_count=1),
                    complete_arrival_delay_minutes=x.loc[valid, 'ArrDelay'].sum(min_count=1))
        summed = x[CAUSES].sum(min_count=1)
        denominator = summed.sum(min_count=1)
        for c in CAUSES:
            record = {**base, 'cause': c, 'records_with_value': int(x[c].notna().sum()),
                      'late_records_with_value': int((x._late & x[c].notna()).sum()),
                      'reported_minutes': summed[c], 'late_reported_minutes': x.loc[x._late, c].sum(min_count=1)}
            record['late_coverage_pct'] = 100 * record['late_records_with_value'] / (base['late_eligible_flights'] or np.nan)
            record['allocated_minute_share_pct'] = 100 * summed[c] / (denominator if denominator else np.nan)
            records.append(record)
    out['20_cause_coverage'] = pd.DataFrame(records)

    keys = ['Year', 'Month', 'DOT_ID_Reporting_Airline', 'Reporting_Airline', 'OriginAirportID', 'Origin']
    g = aggregate(d, keys)
    for code, name in [('A', 'carrier'), ('B', 'weather'), ('C', 'nas'), ('D', 'security'), ('?', 'unknown')]:
        condition = ~d.CancellationCode.isin(list('ABCD')) if code == '?' else d.CancellationCode.eq(code).fillna(False)
        counts = d.assign(_reason=d._cancel & condition).groupby(keys)._reason.sum().rename(name + '_cancellations')
        g = g.merge(counts, on=keys)
    g['cancellation_rate_comparison_eligible'] = g.reported_flights >= 100
    out['21_cancellation_patterns'] = g

    months = aggregate(d, ['Year', 'Month'])[['Year', 'Month', 'delay_rate_pct']].rename(columns={'delay_rate_pct': 'network_delay_pct'})
    g = aggregate(d, ['DestAirportID', 'Dest', 'Year', 'Month']).merge(months, on=['Year', 'Month'])
    g['excess_delay_pp'] = g.delay_rate_pct - g.network_delay_pct
    g['screened'] = g.eligible_flights >= 1000
    g['above'] = g.screened & g.excess_delay_pp.gt(0)
    s = g.groupby(['DestAirportID', 'Dest']).agg(
        observed_months=('Month', 'size'), screened_months=('screened', 'sum'), above_network_months=('above', 'sum'),
        reported_flights=('reported_flights', 'sum'), eligible_flights=('eligible_flights', 'sum'),
        delayed_flights=('delayed_flights', 'sum'), min_month_eligible=('eligible_flights', 'min'),
        min_excess_pp=('excess_delay_pp', 'min'), max_excess_pp=('excess_delay_pp', 'max')).reset_index()
    s['required_months'] = len(months)
    s['recurring_above_network'] = s.screened_months.eq(len(months)) & s.above_network_months.eq(len(months))
    out['22_recurring_airport_delays'] = s
    return out


def execute_queries(con):
    return {p.stem: con.execute(p.read_text()).df() for p in sorted(SQL_DIR.glob('*.sql'))}


def compare_tables(actual, expected):
    """Check identical rows/keys/null patterns and every output cell; return counts."""
    counts = {}
    for name, keys in KEYS.items():
        a = actual[name].copy()
        e = expected[name].copy()
        if 'flight_date' in a:
            a['flight_date'] = pd.to_datetime(a.flight_date)
            e['flight_date'] = pd.to_datetime(e.flight_date)
        assert set(a.columns) == set(e.columns), f'{name}: columns differ'
        a = a.sort_values(keys).reset_index(drop=True)
        e = e.sort_values(keys).reset_index(drop=True)
        assert len(a) == len(e), f'{name}: row count differs'
        assert not a.duplicated(keys).any() and not e.duplicated(keys).any(), f'{name}: duplicate keys'
        numeric = labels = 0
        for c in a:
            if pd.api.types.is_numeric_dtype(a[c]) or pd.api.types.is_bool_dtype(a[c]):
                np.testing.assert_allclose(a[c].to_numpy(dtype=float), e[c].to_numpy(dtype=float), rtol=1e-10, atol=1e-8,
                                           equal_nan=True, err_msg=f'{name}.{c}')
                numeric += len(a)
            else:
                assert a[c].fillna('<NULL>').astype(str).tolist() == e[c].fillna('<NULL>').astype(str).tolist(), f'{name}.{c}'
                labels += len(a)
        counts[name] = {'rows': len(a), 'numeric_comparisons': numeric, 'label_comparisons': labels}
    return counts


def run(root='.'):
    root = Path(root)
    with duckdb.connect(str(root / 'data/aeropulse.duckdb'), read_only=True) as con:
        actual = execute_queries(con)
    cols = ['FlightDate', 'Year', 'Month', 'DayOfWeek', 'DOT_ID_Reporting_Airline', 'Reporting_Airline',
            'OriginAirportID', 'DestAirportID', 'Origin', 'Dest', 'CRSDepTime', 'Cancelled', 'Diverted',
            'CancellationCode', 'ArrDelay'] + CAUSES
    paths = sorted((root / 'data/processed').glob('*/flights.parquet'))
    raw = pd.concat([pd.read_parquet(p, columns=cols) for p in paths], ignore_index=True)
    expected = reference_tables(raw)
    counts = compare_tables(actual, expected)
    out = root / 'reports/session2'
    (out / 'sql').mkdir(parents=True, exist_ok=True)
    for name, df in actual.items():
        df.to_csv(out / 'sql' / f'{name}.csv', index=False)
    report = {'passed': True, 'source_rows': len(raw), 'query_count': len(actual),
              'numeric_comparisons': sum(c['numeric_comparisons'] for c in counts.values()),
              'label_comparisons': sum(c['label_comparisons'] for c in counts.values()),
              'queries': counts, 'atol': 1e-8, 'rtol': 1e-10,
              'method': 'All SQL output cells independently recomputed from validated Parquet with pandas; eligibility rederived from original status and delay fields.'}
    (out / 'SQL_RECONCILIATION.json').write_text(json.dumps(report, indent=2))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', default='.')
    args = parser.parse_args()
    print(json.dumps(run(args.root), indent=2))
