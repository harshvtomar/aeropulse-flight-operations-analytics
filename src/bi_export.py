"""Export a reconciled, role-playing BI star schema without changing the warehouse."""
import argparse
import json
import shutil
import tempfile
from pathlib import Path
import duckdb
from .ingest import sha256

CAUSES = ['CarrierDelay','WeatherDelay','NASDelay','SecurityDelay','LateAircraftDelay']
FACT_SQL = '''SELECT flight_record_id,
 CAST(strftime(FlightDate,'%Y%m%d') AS INTEGER) AS date_key,
 CAST(FlightDate AS DATE) AS flight_date,
 CAST(DOT_ID_Reporting_Airline AS INTEGER) AS airline_id,
 CAST(OriginAirportID AS INTEGER) AS origin_airport_id,
 CAST(DestAirportID AS INTEGER) AS destination_airport_id,
 CAST(OriginAirportID AS INTEGER)::VARCHAR || '_' || CAST(DestAirportID AS INTEGER)::VARCHAR AS route_key,
 CAST(floor(CRSDepTime/100)%24 AS INTEGER) AS scheduled_hour,
 CAST(Flight_Number_Reporting_Airline AS INTEGER) AS flight_number,
 CAST(Cancelled AS INTEGER) AS cancelled,
 CAST(Diverted AS INTEGER) AS diverted,
 CancellationCode AS cancellation_code,
 CAST(arrival_eligible AS INTEGER) AS eligible_arrival,
 CAST(on_time_arrival AS INTEGER) AS on_time_arrival,
 CAST(late_arrival AS INTEGER) AS late_arrival,
 ArrDelay AS arrival_delay_minutes, DepDelay AS departure_delay_minutes,
 CASE WHEN arrival_eligible THEN ArrDelay END AS eligible_delay_minutes,
 CASE WHEN late_arrival THEN ArrDelay END AS late_delay_minutes,
 Distance AS distance_miles,
 CarrierDelay, WeatherDelay, NASDelay, SecurityDelay, LateAircraftDelay,
 source_sha256, source_row
 FROM fact_flights'''
SUMMARIES = '''count(*) AS reported_flights, sum(eligible_arrival) AS eligible_arrivals,
 sum(on_time_arrival) AS on_time_arrivals, sum(late_arrival) AS late_arrivals,
 sum(cancelled) AS cancellations, sum(diverted) AS diversions,
 sum(eligible_delay_minutes) AS eligible_delay_minutes,
 sum(late_delay_minutes) AS late_delay_minutes'''
DIMENSIONS = {
 'dim_airlines': "SELECT CAST(DOT_ID_Reporting_Airline AS INTEGER) AS airline_id, Reporting_Airline AS airline_code FROM dim_airlines ORDER BY 1",
 'dim_origin_airports': "SELECT CAST(airport_id AS INTEGER) AS origin_airport_id, airport_code AS origin_airport_code FROM dim_airports ORDER BY 1",
 'dim_destination_airports': "SELECT CAST(airport_id AS INTEGER) AS destination_airport_id, airport_code AS destination_airport_code FROM dim_airports ORDER BY 1",
 'dim_dates': "SELECT CAST(strftime(flight_date,'%Y%m%d') AS INTEGER) AS date_key, flight_date, CAST(Year AS INTEGER) AS year, CAST(Month AS INTEGER) AS month, CAST(DayOfWeek AS INTEGER) AS day_of_week, DayOfWeek>=6 AS is_weekend FROM dim_dates ORDER BY 1",
 'dim_routes': "SELECT DISTINCT route_key, origin_airport_id, destination_airport_id FROM bi_source ORDER BY 1",
 'dim_hours': "SELECT range::INTEGER AS scheduled_hour, printf('%02d:00–%02d:59',range,range) AS hour_label FROM range(24) ORDER BY 1"
}
AGGREGATES = {
 'agg_daily_airline': f'SELECT date_key, airline_id, {SUMMARIES} FROM bi_source GROUP BY ALL ORDER BY 1,2',
 'agg_monthly_origin': f"SELECT strftime(flight_date,'%Y-%m') AS month,origin_airport_id,{SUMMARIES} FROM bi_source GROUP BY ALL ORDER BY 1,2",
 'agg_monthly_destination': f"SELECT strftime(flight_date,'%Y-%m') AS month,destination_airport_id,{SUMMARIES} FROM bi_source GROUP BY ALL ORDER BY 1,2",
 'agg_monthly_route': f"SELECT strftime(flight_date,'%Y-%m') AS month,route_key,{SUMMARIES} FROM bi_source GROUP BY ALL ORDER BY 1,2",
 'agg_monthly_hour': f"SELECT strftime(flight_date,'%Y-%m') AS month,scheduled_hour,{SUMMARIES} FROM bi_source GROUP BY ALL ORDER BY 1,2",
 'agg_cancellations': "SELECT strftime(flight_date,'%Y-%m') AS month,airline_id,origin_airport_id,coalesce(cancellation_code,'UNKNOWN') AS cancellation_code,count(*) AS cancellations FROM bi_source WHERE cancelled=1 GROUP BY ALL ORDER BY 1,2,3,4",
 'agg_delay_causes': "SELECT * FROM ("+' UNION ALL '.join(f"SELECT strftime(flight_date,'%Y-%m') AS month,airline_id,'{c}' AS reported_cause,count(*) AS reported_flights,sum(late_arrival) AS late_arrivals,count({c}) AS records_with_value,count(*) FILTER (WHERE late_arrival=1 AND {c} IS NOT NULL) AS late_records_with_value,sum({c}) AS reported_minutes FROM bi_source GROUP BY 1,2" for c in CAUSES)+") ORDER BY 1,2,3"
}


def sql_path(p):
    return "'" + str(p).replace("'","''") + "'"


def validate_exports(con, directory):
    """Compare actual read-back tables with original warehouse queries, bidirectionally."""
    directory = Path(directory)
    checks = {}
    files = {'fact_flights': ('parquet', 'SELECT * FROM bi_source'), **{k:('csv',v) for k,v in DIMENSIONS.items()}, **{k:('csv',v) for k,v in AGGREGATES.items()}}
    inventory = []
    for name,(ext,query) in files.items():
        path = directory/f'{name}.{ext}'
        expected=con.execute(query)
        schema=[{'name':x[0],'type':str(x[1])} for x in expected.description]
        # Explicit types preserve numeric NULL-only columns and empty CSV tables.
        types="{"+", ".join(sql_path(x['name'])+": "+sql_path(x['type']) for x in schema)+"}"
        reader = f"read_parquet({sql_path(path)})" if ext=='parquet' else f"read_csv({sql_path(path)}, header=true, nullstr='', columns={types}, auto_detect=false)"
        con.execute(f'CREATE OR REPLACE TEMP VIEW readback_{name} AS SELECT * FROM {reader}')
        view=f'readback_{name}'
        # EXCEPT ALL catches row loss, duplication and cell differences, including NULLs.
        mismatch=con.execute(f'SELECT count(*) FROM (({query}) EXCEPT ALL SELECT * FROM {view})').fetchone()[0]
        reverse=con.execute(f'SELECT count(*) FROM (SELECT * FROM {view} EXCEPT ALL ({query}))').fetchone()[0]
        checks[name+'_bidirectional_rows']=mismatch==reverse==0
        rows=con.execute(f'SELECT count(*) FROM {view}').fetchone()[0]
        inventory.append({'file':path.name,'rows':rows,'bytes':path.stat().st_size,'sha256':sha256(path),'columns':schema})
    fact='readback_fact_flights'
    n=con.execute(f'SELECT count(*) FROM {fact}').fetchone()[0]
    checks['fact_unique_nonnull_key']=con.execute(f'SELECT count(DISTINCT flight_record_id)=count(*) FROM {fact}').fetchone()[0]
    for dim,key in [('airlines','airline_id'),('origin_airports','origin_airport_id'),('destination_airports','destination_airport_id'),('dates','date_key'),('routes','route_key'),('hours','scheduled_hour')]:
        d='readback_dim_'+dim
        checks[dim+'_unique_nonnull_key']=con.execute(f'SELECT count(DISTINCT {key})=count(*) FROM {d}').fetchone()[0]
        joined=con.execute(f'SELECT count(*) FROM {fact} f JOIN {d} d USING({key})').fetchone()[0]
        checks[dim+'_complete_no_fanout']=joined==n
    # Additive count and delay-sum rollups must reproduce warehouse totals.
    rollup_cols=['reported_flights','eligible_arrivals','on_time_arrivals','late_arrivals','cancellations','diversions','eligible_delay_minutes','late_delay_minutes']
    expected=con.execute('SELECT '+SUMMARIES+' FROM bi_source').fetchone()
    for name in ['agg_daily_airline','agg_monthly_origin','agg_monthly_destination','agg_monthly_route','agg_monthly_hour']:
        actual=con.execute('SELECT '+','.join(f'sum({c})' for c in rollup_cols)+' FROM readback_'+name).fetchone()
        # Empty count rollups sum to NULL; interpret only count columns as zero for comparison.
        actual=tuple(0 if i<6 and v is None else v for i,v in enumerate(actual))
        expected_normalized=tuple(0 if i<6 and v is None else v for i,v in enumerate(expected))
        checks[name+'_additive_metrics']=actual==expected_normalized
    failed=[k for k,v in checks.items() if not v]
    if failed: raise ValueError('BI export reconciliation failed: '+', '.join(failed))
    return {'passed':True,'checks_passed':len(checks),'checks':checks,'source_rows':n,'inventory':inventory}


def export(root='.'):
    root=Path(root)
    db=root/'data/aeropulse.duckdb'
    if not db.is_file(): raise FileNotFoundError('Build the DuckDB warehouse before BI export')
    parent=root/'data';target=parent/'bi';temp=Path(tempfile.mkdtemp(prefix='.bi-staging-',dir=parent))
    try:
        with duckdb.connect(str(db),read_only=True) as con:
            con.execute('CREATE TEMP VIEW bi_source AS '+FACT_SQL)
            # Deterministic file order; IDs and NULL source values remain intact.
            con.execute(f"COPY (SELECT * FROM bi_source ORDER BY flight_record_id) TO {sql_path(temp/'fact_flights.parquet')} (FORMAT PARQUET, COMPRESSION ZSTD)")
            for name,query in {**DIMENSIONS,**AGGREGATES}.items():
                con.execute(f"COPY ({query}) TO {sql_path(temp/(name+'.csv'))} (HEADER, DELIMITER ',', NULL '')")
            report=validate_exports(con,temp)
            report['source_months']=con.execute("SELECT DISTINCT strftime(FlightDate,'%Y-%m') FROM fact_flights ORDER BY 1").fetchnumpy()["strftime(FlightDate, '%Y-%m')"].tolist()
            report['source_snapshot']=[{'month':r[0],'source_sha256':r[1]} for r in con.execute('SELECT month,source_sha256 FROM data_quality_audit ORDER BY month').fetchall()]
        (temp/'manifest.json').write_text(json.dumps(report,indent=2))
        # Publish the validated directory, with rollback if replacing an existing export fails.
        backup=parent/'.bi-previous'
        if backup.exists(): raise FileExistsError('Previous BI backup exists; inspect before rerunning')
        if target.exists(): target.rename(backup)
        try: temp.rename(target)
        except Exception:
            if backup.exists(): backup.rename(target)
            raise
        if backup.exists(): shutil.rmtree(backup)
        out=root/'reports/session2';out.mkdir(parents=True,exist_ok=True)
        (out/'BI_EXPORT_VALIDATION.json').write_text(json.dumps(report,indent=2))
        return report
    finally:
        if temp.exists():shutil.rmtree(temp)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',default='.');a=p.parse_args()
    r=export(a.root);print(json.dumps({'passed':r['passed'],'checks':r['checks_passed'],'rows':r['source_rows'],'files':len(r['inventory'])}))
