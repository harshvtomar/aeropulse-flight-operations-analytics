"""Conservative validation: quarantine invalid records, retain warning cases."""
import numpy as np
import pandas as pd

FIELDS = '''FlightDate Year Month DayOfWeek Reporting_Airline DOT_ID_Reporting_Airline Flight_Number_Reporting_Airline OriginAirportID DestAirportID Origin Dest CRSDepTime CRSArrTime DepTime ArrTime DepDelay ArrDelay ArrDel15 Cancelled CancellationCode Diverted Distance CarrierDelay WeatherDelay NASDelay SecurityDelay LateAircraftDelay'''.split()
TEXT = {'FlightDate', 'Reporting_Airline', 'Origin', 'Dest', 'CancellationCode'}
CAUSES = ['CarrierDelay', 'WeatherDelay', 'NASDelay', 'SecurityDelay', 'LateAircraftDelay']
IDENTITY = ['FlightDate','DOT_ID_Reporting_Airline','Flight_Number_Reporting_Airline','OriginAirportID','DestAirportID','CRSDepTime']
# Official selected-field exports sometimes use uppercase SQL column names.
ALIASES = {'FL_DATE':'FlightDate','DAY_OF_WEEK':'DayOfWeek','OP_UNIQUE_CARRIER':'Reporting_Airline',
 'OP_CARRIER_AIRLINE_ID':'DOT_ID_Reporting_Airline','OP_CARRIER_FL_NUM':'Flight_Number_Reporting_Airline',
 'ORIGIN_AIRPORT_ID':'OriginAirportID','DEST_AIRPORT_ID':'DestAirportID'}

def normalize_schema(frame):
    names = {c.replace('_','').lower():c for c in FIELDS}
    rename = {c: ALIASES.get(c,names.get(c.replace('_','').lower(),c)) for c in frame.columns}
    frame = frame.rename(columns=rename)
    if frame.columns.duplicated().any():
        raise ValueError('Ambiguous duplicate column names after normalization')
    missing = sorted(set(FIELDS)-set(frame.columns))
    if missing:
        raise ValueError('Missing required reporting-carrier fields: '+', '.join(missing))
    if any('Marketing' in c or 'MKT_' in c for c in frame.columns):
        raise ValueError('Marketing-carrier schema is not supported')
    return frame[FIELDS].copy()

def valid_hhmm(s):
    return s.isna() | (s.eq(s.round()) & (((s>=0)&(s<=2359)&(s%100<60)) | s.eq(2400)))

def validate(frame, month):
    d = normalize_schema(frame)
    checks = {}
    for c in TEXT:
        d[c] = d[c].astype('string').str.strip().replace('',pd.NA)
    date_text = d.FlightDate
    d['FlightDate'] = pd.to_datetime(date_text, errors='coerce', format='mixed')
    checks['invalid_date'] = d.FlightDate.isna() | d.FlightDate.ne(d.FlightDate.dt.normalize())
    for c in set(FIELDS)-TEXT:
        raw = d[c].replace(r'^\s*$',np.nan,regex=True)
        d[c] = pd.to_numeric(raw, errors='coerce').astype(float)
        checks['parse_'+c] = (raw.notna() & d[c].isna()) | (d[c].notna() & ~np.isfinite(d[c]))
    checks['wrong_month'] = d.FlightDate.dt.strftime('%Y-%m').ne(month)
    for c in ['Origin','Dest']:
        checks['invalid_'+c] = ~d[c].str.fullmatch('[A-Z]{3}',na=False)
    checks['missing_airline'] = d.Reporting_Airline.isna()
    for c in ['Cancelled','Diverted']:
        checks['invalid_'+c] = ~d[c].isin([0,1])
    for c in ['Year','Month','DayOfWeek','DOT_ID_Reporting_Airline','Flight_Number_Reporting_Airline','OriginAirportID','DestAirportID']:
        checks['invalid_'+c] = d[c].isna() | d[c].le(0) | d[c].ne(d[c].round())
    checks['calendar_mismatch'] = d.Year.ne(d.FlightDate.dt.year) | d.Month.ne(d.FlightDate.dt.month) | d.DayOfWeek.ne(d.FlightDate.dt.dayofweek+1)
    for c in ['CRSDepTime','CRSArrTime','DepTime','ArrTime']:
        checks['invalid_'+c] = ~valid_hhmm(d[c])
    checks['missing_schedule'] = d.CRSDepTime.isna() | d.CRSArrTime.isna()
    checks['invalid_distance'] = d.Distance.isna() | d.Distance.le(0)
    checks['invalid_ArrDel15'] = d.ArrDel15.notna() & ~d.ArrDel15.isin([0,1])
    flags = pd.DataFrame(checks,index=d.index).fillna(True)
    bad = flags.any(axis=1)
    normal = d.Cancelled.eq(0)&d.Diverted.eq(0)
    warnings = {
      'overlapping_cancelled_diverted':d.Cancelled.eq(1)&d.Diverted.eq(1),
      'cancelled_with_arrival_time':d.Cancelled.eq(1)&d.ArrTime.notna(),
      'cancelled_missing_arrival_time_expected':d.Cancelled.eq(1)&d.ArrTime.isna(),
      'completed_missing_arrival_delay':normal&d.ArrDelay.isna(),
      'completed_missing_arrival_time':normal&d.ArrTime.isna(),
      'arrival_indicator_mismatch':normal&d.ArrDelay.notna()&d.ArrDel15.notna()&d.ArrDel15.ne(d.ArrDelay.ge(15).astype(int)),
      'unexpected_arrival_delay':d.ArrDelay.lt(-120)|d.ArrDelay.gt(2880),
      'unexpected_departure_delay':d.DepDelay.lt(-120)|d.DepDelay.gt(2880),
      'negative_cause_minutes':d[CAUSES].lt(0).any(axis=1),
      'cancelled_missing_or_unknown_reason':d.Cancelled.eq(1)&~d.CancellationCode.isin(list('ABCD')),
      'noncancelled_with_reason':d.Cancelled.eq(0)&d.CancellationCode.notna(),
      'status_with_arrival_delay':(~normal)&d.ArrDelay.notna(),
    }
    d['arrival_eligible'] = normal & d.ArrDelay.notna()
    d['late_arrival'] = d.arrival_eligible & d.ArrDelay.ge(15)
    d['on_time_arrival'] = d.arrival_eligible & d.ArrDelay.lt(15)
    d['duplicate_candidate'] = d.duplicated(IDENTITY,keep=False)
    rejected = d.loc[bad].copy()
    rejected['rejection_reasons'] = pd.Series(['|'.join(row.index[row]) for _, row in flags.loc[bad].iterrows()], index=rejected.index, dtype='string')
    report = {'source_rows':len(d),'accepted_rows':int((~bad).sum()),'quarantined_rows':int(bad.sum()),
      'invalid_values':{k:int(v.sum()) for k,v in flags.items()},
      'warnings':{k:int(v.sum()) for k,v in warnings.items()},
      'missing_percent':{c:float(d[c].isna().mean()*100) for c in FIELDS},
      'duplicate_candidate_rows':int(d.duplicate_candidate.sum()),
      'duplicate_candidate_excess_rows':int(d.duplicated(IDENTITY).sum()),
      'date_min':str(d.FlightDate.min()),'date_max':str(d.FlightDate.max()),
      'reconciliation_passed':len(d)==int((~bad).sum()+bad.sum())}
    return d.loc[~bad].copy(), rejected, report
