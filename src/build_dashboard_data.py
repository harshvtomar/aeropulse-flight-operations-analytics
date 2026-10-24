"""Build an authentic, complete compact deployment package from the local warehouse."""
import argparse
import json
from pathlib import Path
import tempfile
import shutil
import duckdb
import pandas as pd
from .dashboard_data import DashboardData, Filters, sha256, CAUSES
from .metrics import python_kpis, assert_equal

PROJECTION = '''SELECT CAST(FlightDate AS DATE) AS date, Reporting_Airline AS airline,
Origin AS origin, Dest AS destination, CAST(floor(CRSDepTime/100)%24 AS UTINYINT) AS hour,
CAST(Cancelled AS UTINYINT) AS cancelled, CAST(Diverted AS UTINYINT) AS diverted,
CancellationCode AS cancellation_code, ArrDelay AS arrival_delay, DepDelay AS departure_delay,
CarrierDelay, WeatherDelay, NASDelay, SecurityDelay, LateAircraftDelay FROM fact_flights'''


def build(root='.'):
    root=Path(root).resolve(); dest=root/'deployment/data'; dest.parent.mkdir(parents=True,exist_ok=True)
    checks={};sources=[]
    for p in sorted((root/'data/manifests').glob('2025-0[123].json')):
        m=json.loads(p.read_text()); raw=root/'data/raw'/m['source_file']
        checks[m['month']+'_raw_sha256']=sha256(raw)==m['source_sha256']
        checks[m['month']+'_accepted_rows']=m['accepted_rows']==m['source_rows'] and m['quarantined_rows']==0
        processed=root/'data/processed'/m['month']/'flights.parquet'
        checks[m['month']+'_processed_sha256']=sha256(processed)==m['artifact_sha256']['flights.parquet']
        sources.append({'month':m['month'],'source_sha256':m['source_sha256'],'rows':m['accepted_rows'],'source_url':m['source_url']})
    if len(sources)!=3 or not all(checks.values()): raise ValueError('Authentic source fingerprint validation failed')
    temp=Path(tempfile.mkdtemp(prefix='aeropulse-dashboard-'))
    try:
        with duckdb.connect(str(root/'data/aeropulse.duckdb'),read_only=True) as con:
            con.execute('SET threads=2'); con.execute("SET memory_limit='768MB'")
            audit=con.execute('SELECT month,source_sha256 FROM data_quality_audit ORDER BY month').fetchall()
            checks['warehouse_source_fingerprints']=audit==[(s['month'],s['source_sha256']) for s in sources]
            path=str(temp/'flights.parquet').replace("'","''")
            con.execute(f"COPY ({PROJECTION} ORDER BY date,airline,origin,destination,hour) TO '{path}' (FORMAT PARQUET, COMPRESSION ZSTD, COMPRESSION_LEVEL 9)")
            # Multiset comparisons check every retained cell and duplicate multiplicity in both directions.
            missing=con.execute(f"SELECT count(*) FROM (({PROJECTION}) EXCEPT ALL SELECT * FROM read_parquet('{path}'))").fetchone()[0]
            extra=con.execute(f"SELECT count(*) FROM (SELECT * FROM read_parquet('{path}') EXCEPT ALL ({PROJECTION}))").fetchone()[0]
            checks['warehouse_all_rows_all_retained_cells']=missing==extra==0
            rows=con.execute(f"SELECT count(*) FROM read_parquet('{path}')").fetchone()[0]
            checks['full_population_rows']=rows==sum(s['rows'] for s in sources)==1645503
        parquet=temp/'flights.parquet'
        checks['below_25MB']=parquet.stat().st_size<25_000_000
        manifest={'format_version':1,'full_population':True,'rows':rows,'parquet_sha256':sha256(parquet),'bytes':parquet.stat().st_size,'sources':sources,'coverage':'2025-01-01 through 2025-03-31','filter_semantics':'AND across fields; OR within fields; None all; empty list no matches. Severity restricts the population and every denominator.','source':'BTS Reporting Carrier On-Time Performance','build_command':'python -m src.build_dashboard_data'}
        (temp/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
        data=DashboardData(temp)
        # Independent pandas classifications from source Parquet, never dashboard booleans.
        columns=['FlightDate','Reporting_Airline','Origin','Dest','CRSDepTime','Cancelled','Diverted','ArrDelay']
        frame=pd.concat([pd.read_parquet(root/'data/processed'/s['month']/'flights.parquet',columns=columns) for s in sources],ignore_index=True)
        cases=[Filters(),Filters(month=['2025-01']),Filters(airline=['AA']),Filters(origin=['ATL']),Filters(destination=['LAX']),Filters(route=['ATL → LAX']),Filters(hour=[0,6,23]),Filters(month=['2025-02'],airline=['DL'],origin=['ATL'],hour=[6,7,8]),Filters(severity=['120+']),Filters(severity=['Ineligible']),Filters(month=[]),Filters(origin=['LAX'],destination=['ATL'])]
        comparisons=0
        for i,f in enumerate(cases):
            mask=pd.Series(True,index=frame.index)
            values={'month':pd.to_datetime(frame.FlightDate).dt.strftime('%Y-%m'),'airline':frame.Reporting_Airline,'origin':frame.Origin,'destination':frame.Dest,'route':frame.Origin+' → '+frame.Dest,'hour':(frame.CRSDepTime//100)%24}
            eligible=frame.Cancelled.eq(0)&frame.Diverted.eq(0)&frame.ArrDelay.notna()
            severity=pd.Series('Ineligible',index=frame.index)
            for lo,hi,label in [(-float('inf'),15,'Under 15'),(15,30,'15–29'),(30,60,'30–59'),(60,120,'60–119'),(120,float('inf'),'120+')]:
                severity.loc[eligible&frame.ArrDelay.ge(lo)&frame.ArrDelay.lt(hi)]=label
            values['severity']=severity
            for key,series in values.items():
                if getattr(f,key) is not None: mask &= series.isin(getattr(f,key))
            actual=data.get_kpis(f); expected=python_kpis(frame.loc[mask])
            for key,val in expected.items(): assert_equal(actual[key],val);comparisons+=1
            checks[f'pandas_filtered_scenario_{i:02}']=True
        if not all(checks.values()): raise ValueError('Data package validation failed: '+str(checks))
        report={'passed':True,'checks':checks,'checks_passed':len(checks),'independent_pandas_comparisons':comparisons,'rows':rows,'bytes':parquet.stat().st_size,'parquet_sha256':manifest['parquet_sha256'],'sources':sources,'warehouse_missing_rows':missing,'warehouse_extra_rows':extra}
        dest.mkdir(exist_ok=True)
        shutil.copy2(parquet,dest/'flights.parquet');shutil.copy2(temp/'manifest.json',dest/'manifest.json')
        published=DashboardData(dest)
        report['checks']['published_checksum_and_rows']=published.manifest['parquet_sha256']==manifest['parquet_sha256'] and published.get_kpis()['reported_flights']==rows
        if not report['checks']['published_checksum_and_rows']: raise ValueError('Published package readback failed')
        report['checks_passed']=len(report['checks'])
        out=root/'reports/session3';out.mkdir(exist_ok=True,parents=True)
        (out/'DATA_PACKAGE_VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n')
        return report
    finally: shutil.rmtree(temp)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',default='.');args=parser.parse_args()
    print(json.dumps(build(args.root),indent=2))
