"""Small synthetic fixtures validate BI contracts; never used for findings."""
import json
from pathlib import Path
import duckdb
import pandas as pd
import pytest
from src.bi_export import export, FACT_SQL, validate_exports
from src.ingest import ingest
from src.warehouse import build

@pytest.fixture
def bi_root(rows,tmp_path):
    d=pd.concat([rows]*5,ignore_index=True)
    d['Flight_Number_Reporting_Airline']=[1,2,3,4,5]
    d['ArrDelay']=[-5,15,None,100,None]
    d['ArrDel15']=[0,1,None,None,None]
    d['Cancelled']=[0,0,1,0,0]
    d['Diverted']=[0,0,0,1,0]
    d['CancellationCode']=[None,None,'B',None,None]
    for c in ['CarrierDelay','WeatherDelay','NASDelay','SecurityDelay','LateAircraftDelay']:d[c]=None
    d.loc[1,'CarrierDelay']=15
    p=tmp_path/'fixture.csv';d.to_csv(p,index=False);ingest(p,'2025-01',tmp_path);build(tmp_path)
    export(tmp_path)
    return tmp_path

def test_fact_grain_and_identity(bi_root):
    d=pd.read_parquet(bi_root/'data/bi/fact_flights.parquet')
    assert len(d)==d.flight_record_id.nunique()==5
    assert d.source_row.tolist()==[1,2,3,4,5]

def test_correct_eligible_population(bi_root):
    d=pd.read_parquet(bi_root/'data/bi/fact_flights.parquet')
    assert d.eligible_arrival.sum()==2 and d.on_time_arrival.sum()==1 and d.late_arrival.sum()==1
    assert d.eligible_delay_minutes.sum()==10 and d.late_delay_minutes.sum()==15

def test_negative_and_missing_preserved(bi_root):
    d=pd.read_parquet(bi_root/'data/bi/fact_flights.parquet')
    assert d.arrival_delay_minutes.min()==-5 and d.arrival_delay_minutes.isna().sum()==2
    assert d.CarrierDelay.isna().sum()==4 and d.WeatherDelay.isna().all()

def test_cause_null_sum_and_coverage(bi_root):
    d=pd.read_csv(bi_root/'data/bi/agg_delay_causes.csv').set_index('reported_cause')
    assert d.loc['CarrierDelay','records_with_value']==1 and d.loc['CarrierDelay','reported_minutes']==15
    assert d.loc['WeatherDelay','records_with_value']==0 and pd.isna(d.loc['WeatherDelay','reported_minutes'])
    assert d.loc['CarrierDelay','late_records_with_value']==1

def test_aggregate_additivity(bi_root):
    for name in ['daily_airline','monthly_origin','monthly_destination','monthly_route','monthly_hour']:
        d=pd.read_csv(bi_root/f'data/bi/agg_{name}.csv')
        assert d.reported_flights.sum()==5 and d.eligible_arrivals.sum()==2 and d.cancellations.sum()==1 and d.diversions.sum()==1

def test_role_playing_dimensions(bi_root):
    d=pd.read_parquet(bi_root/'data/bi/fact_flights.parquet')
    for name,key in [('origin','origin_airport_id'),('destination','destination_airport_id')]:
        dim=pd.read_csv(bi_root/f'data/bi/dim_{name}_airports.csv')
        assert len(d.merge(dim,on=key,validate='many_to_one'))==5

def test_manifest_and_inventory(bi_root):
    m=json.loads((bi_root/'data/bi/manifest.json').read_text())
    assert m['passed'] and len(m['inventory'])==14 and m['checks_passed']==32
    assert m['source_months']==['2025-01']
    for f in m['inventory']:
        assert len(f['sha256'])==64 and f['bytes']>0 and f['columns']

def test_deterministic_rerun(bi_root):
    a=json.loads((bi_root/'data/bi/manifest.json').read_text());b=export(bi_root)
    assert a==b

def test_tampered_aggregate_detected(bi_root):
    p=bi_root/'data/bi/agg_daily_airline.csv';d=pd.read_csv(p);d['reported_flights']=99;d.to_csv(p,index=False)
    with duckdb.connect(str(bi_root/'data/aeropulse.duckdb'),read_only=True) as c:
        c.execute('CREATE TEMP VIEW bi_source AS '+FACT_SQL)
        with pytest.raises(ValueError,match='reconciliation failed'):validate_exports(c,bi_root/'data/bi')

def test_missing_database_fails(tmp_path):
    with pytest.raises(FileNotFoundError,match='Build the DuckDB'):export(tmp_path)

def test_missing_dimension_member_detected(bi_root):
    p=bi_root/'data/bi/dim_origin_airports.csv';d=pd.read_csv(p);d.iloc[0:0].to_csv(p,index=False)
    with duckdb.connect(str(bi_root/'data/aeropulse.duckdb'),read_only=True) as c:
        c.execute('CREATE TEMP VIEW bi_source AS '+FACT_SQL)
        with pytest.raises(ValueError,match='origin_airports'):validate_exports(c,bi_root/'data/bi')

def test_midnight_hour_normalization(rows,tmp_path):
    rows['CRSDepTime']=2400;p=tmp_path/'f.csv';rows.to_csv(p,index=False);ingest(p,'2025-01',tmp_path);build(tmp_path);export(tmp_path)
    d=pd.read_parquet(tmp_path/'data/bi/fact_flights.parquet');assert d.scheduled_hour.iloc[0]==0
