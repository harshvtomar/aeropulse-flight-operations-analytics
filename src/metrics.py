"""Independent pandas calculations from validated Parquet, compared with SQL."""
import json
from pathlib import Path
import duckdb
import numpy as np
import pandas as pd


def python_kpis(d):
    # Recompute eligibility and classifications, without using derived boolean columns.
    eligible=d.Cancelled.eq(0)&d.Diverted.eq(0)&d.ArrDelay.notna()
    a=d.loc[eligible,'ArrDelay']; late=a.ge(15)
    n=len(d);e=len(a)
    return dict(reported_flights=n,eligible_flights=e,on_time_flights=int(a.lt(15).sum()),late_flights=int(late.sum()),
      cancelled_flights=int(d.Cancelled.eq(1).sum()),diverted_flights=int(d.Diverted.eq(1).sum()),
      on_time_pct=100*a.lt(15).sum()/e if e else None,late_pct=100*late.sum()/e if e else None,
      cancellation_pct=100*d.Cancelled.eq(1).sum()/n if n else None,diversion_pct=100*d.Diverted.eq(1).sum()/n if n else None,
      avg_arrival_delay_minutes=a.mean() if e else None,avg_late_arrival_delay_minutes=a[late].mean() if late.any() else None)

def assert_equal(actual,expected):
    if pd.isna(actual) and pd.isna(expected): return
    if not np.isclose(actual,expected,atol=1e-9,rtol=1e-10): raise AssertionError(f'{actual} != {expected}')

def reconcile(root='.'):
    root=Path(root)
    d=pd.concat([pd.read_parquet(p) for p in sorted((root/'data/processed').glob('*/flights.parquet'))],ignore_index=True)
    checks=0
    with duckdb.connect(str(root/'data/aeropulse.duckdb'),read_only=True) as con:
        sql=con.execute('SELECT * FROM v_reliability').df().iloc[0].to_dict()
        for k,v in python_kpis(d).items(): assert_equal(sql[k],v);checks+=1
        # Independent per-month, airline, origin and destination counts, means and denominators.
        for key in ['Month','DOT_ID_Reporting_Airline','OriginAirportID','DestAirportID']:
            result=con.execute(f'''SELECT {key},count(*) AS n,count(*) FILTER (WHERE arrival_eligible) AS e,
            count(*) FILTER (WHERE on_time_arrival) AS o,avg(ArrDelay) FILTER (WHERE arrival_eligible) AS a
            FROM fact_flights GROUP BY {key}''').df().set_index(key)
            for value,g in d.groupby(key):
                py=python_kpis(g)
                for col,k in [('n','reported_flights'),('e','eligible_flights'),('o','on_time_flights'),('a','avg_arrival_delay_minutes')]:
                    assert_equal(result.loc[value,col],py[k]);checks+=1
        for c in ['CarrierDelay','WeatherDelay','NASDelay','SecurityDelay','LateAircraftDelay']:
            assert_equal(con.execute(f'SELECT sum({c}) FROM fact_flights').fetchone()[0],d[c].sum(min_count=1));checks+=1
    report={'passed':True,'numeric_comparisons':checks,'kpis':sql,'tolerance':{'atol':1e-9,'rtol':1e-10}}
    out=root/'reports';out.mkdir(exist_ok=True)
    (out/'KPI_RECONCILIATION.json').write_text(json.dumps(report,indent=2))
    return report
if __name__=='__main__': print(json.dumps(reconcile(),indent=2))
