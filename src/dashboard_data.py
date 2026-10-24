"""Read-only, exact dashboard queries over a verified full-population package."""
from dataclasses import dataclass, fields, replace
import hashlib
import json
from pathlib import Path
import duckdb

SEVERITIES = ('Under 15', '15–29', '30–59', '60–119', '120+', 'Ineligible')
CAUSES = ('CarrierDelay', 'WeatherDelay', 'NASDelay', 'SecurityDelay', 'LateAircraftDelay')
FILTER_COLUMNS = ('month','airline','origin','destination','route','hour','severity')
GROUP_COLUMNS = FILTER_COLUMNS + ('date',)

@dataclass(frozen=True)
class Filters:
    month: tuple | list | None = None
    airline: tuple | list | None = None
    origin: tuple | list | None = None
    destination: tuple | list | None = None
    route: tuple | list | None = None
    hour: tuple | list | None = None
    severity: tuple | list | None = None


def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
    return h.hexdigest()

ELIGIBLE = 'cancelled=0 AND diverted=0 AND arrival_delay IS NOT NULL'
VIEW_SQL = f'''SELECT *, strftime(date,'%Y-%m') AS month, origin || ' → ' || destination AS route,
({ELIGIBLE}) AS eligible,
CASE WHEN NOT ({ELIGIBLE}) THEN 'Ineligible' WHEN arrival_delay<15 THEN 'Under 15'
WHEN arrival_delay<30 THEN '15–29' WHEN arrival_delay<60 THEN '30–59'
WHEN arrival_delay<120 THEN '60–119' ELSE '120+' END AS severity FROM read_parquet(?)'''
METRICS = '''count(*) AS reported_flights,
count(*) FILTER (WHERE eligible) AS eligible_flights,
count(*) FILTER (WHERE eligible AND arrival_delay<15) AS on_time_flights,
count(*) FILTER (WHERE eligible AND arrival_delay>=15) AS late_flights,
count(*) FILTER (WHERE cancelled=1) AS cancelled_flights,
count(*) FILTER (WHERE diverted=1) AS diverted_flights,
100.0*count(*) FILTER (WHERE eligible AND arrival_delay<15)/nullif(count(*) FILTER (WHERE eligible),0) AS on_time_pct,
100.0*count(*) FILTER (WHERE eligible AND arrival_delay>=15)/nullif(count(*) FILTER (WHERE eligible),0) AS late_pct,
100.0*count(*) FILTER (WHERE cancelled=1)/nullif(count(*),0) AS cancellation_pct,
100.0*count(*) FILTER (WHERE diverted=1)/nullif(count(*),0) AS diversion_pct,
avg(arrival_delay) FILTER (WHERE eligible) AS avg_arrival_delay_minutes,
avg(arrival_delay) FILTER (WHERE eligible AND arrival_delay>=15) AS avg_late_arrival_delay_minutes,
sum(arrival_delay) FILTER (WHERE eligible) AS signed_arrival_delay_minutes'''


def where(filters=None):
    filters=filters or Filters()
    if not isinstance(filters,Filters): raise TypeError('filters must be Filters')
    clauses=[];params=[]
    for f in fields(filters):
        values=getattr(filters,f.name)
        if values is None: continue
        if isinstance(values,(str,bytes)) or not isinstance(values,(tuple,list)):
            raise TypeError(f'{f.name} must be a list, tuple, or None')
        if not values: clauses.append('FALSE');continue
        clauses.append('"'+f.name+'" IN ('+','.join('?' for _ in values)+')');params.extend(values)
    return (' WHERE '+' AND '.join(clauses) if clauses else ''), params

class DashboardData:
    """One bounded in-memory DuckDB connection per call; never mutates a source."""
    def __init__(self,package_dir=None):
        self.directory=Path(package_dir) if package_dir else Path(__file__).resolve().parents[1]/'deployment/data'
        try:
            self.manifest=json.loads((self.directory/'manifest.json').read_text())
            self.path=self.directory/'flights.parquet'
            if self.manifest.get('format_version')!=1 or self.manifest.get('full_population') is not True:
                raise ValueError('unsupported manifest or incomplete population')
            if sha256(self.path)!=self.manifest['parquet_sha256']: raise ValueError('Parquet checksum mismatch')
            with self._connect() as con:
                actual=con.execute('SELECT count(*) FROM flights').fetchone()[0]
                if actual!=self.manifest['rows']: raise ValueError('row count mismatch')
        except (OSError,ValueError,KeyError,duckdb.Error) as exc:
            raise ValueError(f'Dashboard data package unavailable or invalid: {exc}. Rebuild with python -m src.build_dashboard_data; no sample fallback is used.') from exc

    def _connect(self):
        con=duckdb.connect(config={'threads':2,'memory_limit':'256MB'})
        # Table functions accept bound paths. A temporary table-free view uses escaped literal only for the trusted local path.
        con.execute('CREATE VIEW flights AS '+VIEW_SQL.replace('?', "'"+str(self.path).replace("'","''")+"'"))
        return con

    def _query(self,sql,params=(),frame=True):
        with self._connect() as con:
            result=con.execute(sql,params)
            if frame: return result.df()
            return dict(zip([x[0] for x in result.description],result.fetchone()))

    def get_kpis(self,filters=None):
        clause,params=where(filters)
        return self._query('SELECT '+METRICS+' FROM flights'+clause,params,False)

    def group_metrics(self,group,filters=None):
        groups=[group] if isinstance(group,str) else list(group)
        if not groups or any(g not in GROUP_COLUMNS for g in groups): raise ValueError('Unsupported grouping')
        cols=','.join('"'+g+'"' for g in groups); clause,params=where(filters)
        return self._query('SELECT '+cols+','+METRICS+' FROM flights'+clause+' GROUP BY '+cols+' ORDER BY '+cols,params)

    def options(self,field,filters=None):
        if field not in FILTER_COLUMNS: raise ValueError('Unsupported filter')
        clause,params=where(replace(filters or Filters(),**{field:None}))
        result=self._query(f'SELECT DISTINCT "{field}" FROM flights'+clause+f' ORDER BY "{field}"',params)
        values=result[field].tolist()
        return [s for s in SEVERITIES if s in values] if field=='severity' else values

    def severity_metrics(self,filters=None):
        result=self.group_metrics('severity',filters)
        total=self.get_kpis(filters)
        result['eligible_share_pct']=result.eligible_flights*100/total['eligible_flights'] if total['eligible_flights'] else float('nan')
        result['delayed_share_pct']=result.late_flights*100/total['late_flights'] if total['late_flights'] else float('nan')
        result.loc[result.severity.isin(['Under 15','Ineligible']),'delayed_share_pct']=float('nan')
        result.loc[result.severity.eq('Ineligible'),'eligible_share_pct']=float('nan')
        return result

    def cause_metrics(self,filters=None):
        clause,params=where(filters)
        queries=[]
        for cause in CAUSES:
            queries.append(f'''SELECT '{cause}' AS cause, count(*) AS reported_flights,
 count(*) FILTER (WHERE eligible AND arrival_delay>=15) AS late_flights,
 count({cause}) AS records_with_value,
 count(*) FILTER (WHERE eligible AND arrival_delay>=15 AND {cause} IS NOT NULL) AS late_records_with_value,
 sum({cause}) AS reported_minutes FROM flights{clause}''')
        return self._query(' UNION ALL '.join(queries),params*len(CAUSES))

    def cancellation_metrics(self,filters=None):
        clause,params=where(filters)
        return self._query("SELECT coalesce(cancellation_code,'Unknown') AS cancellation_code, count(*) AS cancelled_flights FROM flights"+clause+(' AND ' if clause else ' WHERE ')+"cancelled=1 GROUP BY 1 ORDER BY 1",params)
