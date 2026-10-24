"""Focused boundary fixtures plus separately marked authentic package integration."""
import json
from pathlib import Path
import duckdb
import pandas as pd
import pytest
from src.dashboard_data import DashboardData, Filters, SEVERITIES, CAUSES, sha256, where

@pytest.fixture
def package(tmp_path):
    delays=[-10,0,14,15,29,30,59,60,119,120,None,900,20]
    rows=[]
    for i,delay in enumerate(delays):
        rows.append(dict(date=pd.Timestamp('2025-01-01' if i<7 else '2025-02-01'),airline='AA' if i%2 else 'DL',origin='ATL' if i%2 else 'LAX',destination='LAX' if i%2 else 'ATL',hour=i%24,cancelled=int(i in [10,11]),diverted=int(i in [11,12]),cancellation_code='A' if i in [10,11] else None,arrival_delay=delay,departure_delay=delay,**{c:None if i<3 else float(i) for c in CAUSES}))
    df=pd.DataFrame(rows);df.to_parquet(tmp_path/'flights.parquet',index=False)
    manifest={'format_version':1,'full_population':True,'rows':len(df),'parquet_sha256':sha256(tmp_path/'flights.parquet')}
    (tmp_path/'manifest.json').write_text(json.dumps(manifest))
    return tmp_path

@pytest.fixture
def data(package): return DashboardData(package)

def test_all_canonical_kpis(data):
    k=data.get_kpis(); assert (k['reported_flights'],k['eligible_flights'],k['on_time_flights'],k['late_flights'])==(13,10,3,7)
    assert k['on_time_pct']==30

def test_signed_delays(data): assert data.get_kpis()['avg_arrival_delay_minutes']==43.6

def test_late_average(data): assert data.get_kpis()['avg_late_arrival_delay_minutes']==pytest.approx(432/7)

def test_overlapping_statuses(data):
    k=data.get_kpis();assert k['cancelled_flights']==2 and k['diverted_flights']==2 and k['eligible_flights']==10

@pytest.mark.parametrize('field,value,expected', [('month','2025-01',7),('airline','AA',6),('origin','ATL',6),('destination','LAX',6),('route','ATL → LAX',6),('hour',0,1),('severity','Ineligible',3)])
def test_each_filter(data,field,value,expected): assert data.get_kpis(Filters(**{field:[value]}))['reported_flights']==expected

@pytest.mark.parametrize('field', ['month','airline','origin','destination','route','hour','severity'])
def test_empty_filter_means_no_matches(data,field):
    k=data.get_kpis(Filters(**{field:[]}));assert k['reported_flights']==0 and k['on_time_pct'] is None

@pytest.mark.parametrize('severity,expected',zip(SEVERITIES,[3,2,2,2,1,3]))
def test_severity_boundaries(data,severity,expected): assert data.get_kpis(Filters(severity=[severity]))['reported_flights']==expected

def test_intersection_and_union(data): assert data.get_kpis(Filters(month=['2025-01','2025-02'],airline=['AA'],origin=['LAX']))['reported_flights']==0

def test_directed_route(data): assert data.get_kpis(Filters(route=['LAX → ATL']))['reported_flights']==7

def test_severity_changes_denominator(data):
    k=data.get_kpis(Filters(severity=['120+']));assert k['late_pct']==100 and k['eligible_flights']==1 and k['reported_flights']==1

def test_cascade_ignores_own_selection(data): assert data.options('origin',Filters(origin=['BOGUS'],airline=['AA']))==['ATL']

def test_options_empty_other_field(data): assert data.options('origin',Filters(month=[]))==[]

def test_all_groupings_reconcile(data):
    for group in ['date','month','airline','origin','destination','route','hour','severity']:
        assert data.group_metrics(group).reported_flights.sum()==13

def test_multiple_grouping(data): assert data.group_metrics(['origin','destination']).reported_flights.sum()==13

def test_cause_nulls_preserved(data):
    row=data.cause_metrics(Filters(hour=[0,1,2])).iloc[0]
    assert row.records_with_value==0 and pd.isna(row.reported_minutes)

def test_cause_coverage(data):
    row=data.cause_metrics().iloc[0]; assert row.records_with_value==10 and row.late_records_with_value==7 and row.reported_minutes==75

def test_cancellation_reason(data):
    row=data.cancellation_metrics().iloc[0];assert row.cancellation_code=='A' and row.cancelled_flights==2

def test_severity_shares(data):
    df=data.severity_metrics();assert df.eligible_share_pct.sum()==100 and df.delayed_share_pct.sum()==pytest.approx(100)

def test_sql_injection_is_literal(data): assert data.get_kpis(Filters(airline=["AA' OR 1=1 --"]))['reported_flights']==0

@pytest.mark.parametrize('operation', ['group','option'])
def test_identifier_injection_rejected(data,operation):
    with pytest.raises(ValueError): (data.group_metrics if operation=='group' else data.options)('airline; DROP TABLE flights')

def test_string_filter_rejected(data):
    with pytest.raises(TypeError):data.get_kpis(Filters(airline='AA'))

def test_checksum_tamper_rejected(package):
    with open(package/'flights.parquet','ab') as f:f.write(b'tamper')
    with pytest.raises(ValueError,match='checksum'):DashboardData(package)

def test_missing_package_fails_clear(tmp_path):
    with pytest.raises(ValueError,match='no sample fallback'):DashboardData(tmp_path)

def test_manifest_count_rejected(package):
    path=package/'manifest.json';m=json.loads(path.read_text());m['rows']=14;path.write_text(json.dumps(m))
    with pytest.raises(ValueError,match='row count'):DashboardData(package)

def test_no_connection_state_leak(data):
    assert data.get_kpis(Filters(month=[]))['reported_flights']==0
    assert data.get_kpis()['reported_flights']==13

@pytest.mark.integration
def test_authentic_package_baseline():
    root=Path(__file__).resolve().parents[1]
    if not (root/'deployment/data/manifest.json').exists():pytest.skip('authentic deployment package unavailable')
    d=DashboardData(root/'deployment/data');k=d.get_kpis()
    assert k['reported_flights']==1645503
    baseline=json.loads((root/'reports/KPI_RECONCILIATION.json').read_text())['kpis']
    for name,value in baseline.items():
        if name in k: assert k[name]==pytest.approx(value)
    assert d.options('month')==['2025-01','2025-02','2025-03']
