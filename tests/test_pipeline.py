import json
import zipfile
import pandas as pd
import pytest
import duckdb
from src.ingest import ingest
from src.warehouse import build,CODE_ROOT
from src.metrics import python_kpis,reconcile

def save(rows,tmp_path,name='input.csv'):
    p=tmp_path/name;rows.to_csv(p,index=False);return p

def test_csv_ingest(rows,tmp_path):
    m=ingest(save(rows,tmp_path),'2025-01',tmp_path);assert m['source_rows']==1 and m['accepted_rows']==1

def test_zip_ingest(rows,tmp_path):
    p=save(rows,tmp_path);z=tmp_path/'input.zip'
    with zipfile.ZipFile(z,'w') as f: f.write(p,'records.csv');f.writestr('readme.html','test fixture')
    assert ingest(z,'2025-01',tmp_path)['source_rows']==1

def test_ambiguous_zip(tmp_path):
    z=tmp_path/'input.zip'
    with zipfile.ZipFile(z,'w') as f: f.writestr('a.csv','a');f.writestr('b.csv','b')
    with pytest.raises(ValueError,match='exactly one'): ingest(z,'2025-01',tmp_path)

def test_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError): ingest(tmp_path/'none.csv','2025-01',tmp_path)

def test_bad_zip_recovery(rows,tmp_path):
    z=tmp_path/'bad.zip';z.write_text('bad')
    with pytest.raises(zipfile.BadZipFile): ingest(z,'2025-01',tmp_path)
    assert not (tmp_path/'data/processed/2025-01').exists()
    assert ingest(save(rows,tmp_path),'2025-01',tmp_path)['accepted_rows']==1

def test_idempotence(rows,tmp_path):
    p=save(rows,tmp_path);a=ingest(p,'2025-01',tmp_path);b=ingest(p,'2025-01',tmp_path)
    assert b['rerun']=='unchanged' and a['source_sha256']==b['source_sha256']

def test_revision_rejected(rows,tmp_path):
    p=save(rows,tmp_path);ingest(p,'2025-01',tmp_path);rows['ArrDelay']=8;save(rows,tmp_path)
    with pytest.raises(ValueError,match='different checksum'): ingest(p,'2025-01',tmp_path)

def test_tamper_detected(rows,tmp_path):
    p=save(rows,tmp_path);ingest(p,'2025-01',tmp_path)
    (tmp_path/'data/processed/2025-01/quality.json').write_text('{}')
    with pytest.raises(ValueError,match='checksum mismatch'): ingest(p,'2025-01',tmp_path)
    with pytest.raises(ValueError,match='checksum mismatch'): build(tmp_path)

def test_schema_drift(rows,tmp_path):
    ingest(save(rows,tmp_path),'2025-01',tmp_path);rows['extra']=1
    with pytest.raises(ValueError,match='schema drift'): ingest(save(rows,tmp_path,'feb.csv'),'2025-02',tmp_path)

def test_incremental(rows,tmp_path):
    ingest(save(rows,tmp_path),'2025-01',tmp_path)
    rows['FlightDate']='2025-02-01';rows['Month']=2;rows['DayOfWeek']=6
    ingest(save(rows,tmp_path,'feb.csv'),'2025-02',tmp_path)
    with duckdb.connect(str(build(tmp_path))) as con: assert con.execute('select count(*) from fact_flights').fetchone()[0]==2

def test_warehouse_queries_and_reconciliation(rows,tmp_path):
    d=pd.concat([rows]*5,ignore_index=True)
    d['ArrDelay']=[-5,15,None,100,None];d['Cancelled']=[0,0,1,0,0];d['Diverted']=[0,0,0,1,0]
    ingest(save(d,tmp_path),'2025-01',tmp_path)
    with duckdb.connect(str(build(tmp_path))) as con:
        k=con.execute('select * from v_reliability').df().iloc[0]
        assert k.reported_flights==5 and k.eligible_flights==2 and k.on_time_pct==50 and k.cancellation_pct==20
        assert k.avg_arrival_delay_minutes==5 and k.avg_late_arrival_delay_minutes==15
        assert con.execute('select count(*) from fact_flights join dim_airlines using (DOT_ID_Reporting_Airline)').fetchone()[0]==5
        assert con.execute('select count(*) from fact_flights f join dim_airports a on f.OriginAirportID=a.airport_id').fetchone()[0]==5
        files=list((CODE_ROOT/'sql/queries').glob('*.sql'));assert len(files)==12
        for p in files: con.execute(p.read_text()).fetchall()
    assert reconcile(tmp_path)['passed']

def test_empty_denominator(rows):
    rows['Cancelled']=1;k=python_kpis(rows);assert k['on_time_pct'] is None and k['eligible_flights']==0

def test_all_quarantined_reconciles(rows,tmp_path):
    rows['Origin']='BAD!';m=ingest(save(rows,tmp_path),'2025-01',tmp_path)
    assert m['source_rows']==m['quarantined_rows']==1
    with duckdb.connect(str(build(tmp_path))) as con: assert con.execute('select count(*) from fact_flights').fetchone()[0]==0
