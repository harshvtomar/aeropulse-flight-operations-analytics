"""Trace extreme delays to immutable raw CSV rows; canonical data are read-only."""
import json
from pathlib import Path
import duckdb
import numpy as np
import pandas as pd
from .ingest import csv_stream, sha256
from .metrics import python_kpis
from .validate import CAUSES

DIRECTIVE='https://www.bts.gov/explore-topics-and-geography/modes/aviation/number-39-technical-directive-reporting-time'
EXTRA=['CRSElapsedTime','ActualElapsedTime','AirTime','TaxiOut','TaxiIn','WheelsOff','WheelsOn','Tail_Number','FirstDepTime','TotalAddGTime','LongestAddGTime','DivAirportLandings']

def extreme_mask(d, field):
    return d[field].lt(-120)|d[field].gt(2880)

def sensitivities(d):
    masks={'canonical_all':pd.Series(True,index=d.index),
      'exclude_arrival_warning_only':~extreme_mask(d,'ArrDelay'),
      'exclude_any_arrival_or_departure_warning':~(extreme_mask(d,'ArrDelay')|extreme_mask(d,'DepDelay'))}
    base=python_kpis(d);rows=[]
    for label,mask in masks.items():
        k=python_kpis(d.loc[mask]);k.update(scenario=label,excluded_source_rows=int((~mask).sum()))
        for c in ['avg_arrival_delay_minutes','avg_late_arrival_delay_minutes','on_time_pct','cancellation_pct']:
            k[c+'_difference_from_canonical']=k[c]-base[c] if k[c] is not None and base[c] is not None else None
        rows.append(k)
    return pd.DataFrame(rows)

def hhmm_minutes(s):
    return (np.floor(s/100)*60+s%100)%1440

def investigate(root='.'):
    root=Path(root);out=root/'reports/session2';out.mkdir(parents=True,exist_ok=True)
    with duckdb.connect(str(root/'data/aeropulse.duckdb'),read_only=True) as c:
        d=c.execute('SELECT * FROM fact_flights ORDER BY FlightDate,source_row').df()
    flags=extreme_mask(d,'ArrDelay')|extreme_mask(d,'DepDelay')
    selected=d.loc[flags].copy();raw_matches=[]
    for p in sorted((root/'data/manifests').glob('*.json')):
        m=json.loads(p.read_text());part=selected[selected.source_sha256==m['source_sha256']]
        if part.empty: continue
        path=root/'data/raw'/m['source_file']
        if sha256(path)!=m['source_sha256']:raise ValueError('Raw source checksum mismatch')
        with csv_stream(path) as (f,member):
            raw=pd.read_csv(f,usecols=lambda c:c in EXTRA or c in selected.columns,low_memory=False)
        for _,r in part.iterrows():
            row=raw.iloc[int(r.source_row)-1]
            for col in ['Origin','Dest','Reporting_Airline','DepDelay','ArrDelay','Cancelled','Diverted']:
                x,y=row[col],r[col]
                if not ((pd.isna(x) and pd.isna(y)) or x==y):raise AssertionError(f'Raw lineage mismatch: {col}')
            raw_matches.append({'flight_record_id':r.flight_record_id,'source_file':m['source_file'],'csv_member':member,
                                **{k:row[k] for k in EXTRA}})
    detail=selected.merge(pd.DataFrame(raw_matches),on='flight_record_id',validate='one_to_one')
    detail['arrival_warning']=extreme_mask(detail,'ArrDelay');detail['departure_warning']=extreme_mask(detail,'DepDelay')
    detail['elapsed_identity_residual_minutes']=(detail.ArrDelay-detail.DepDelay)-(detail.ActualElapsedTime-detail.CRSElapsedTime)
    detail['departure_clock_residual_mod_1440']=(detail.DepDelay-(hhmm_minutes(detail.DepTime)-hhmm_minutes(detail.CRSDepTime)))%1440
    detail['arrival_clock_residual_mod_1440']=(detail.ArrDelay-(hhmm_minutes(detail.ArrTime)-hhmm_minutes(detail.CRSArrTime)))%1440
    detail['cause_sum_minus_arrival_delay']=detail[CAUSES].sum(axis=1,min_count=len(CAUSES))-detail.ArrDelay
    detail['assessment']=np.where(detail.Cancelled.eq(1),'Unresolved cancellation/gate-return anomaly; source follow-up required',
      np.where(detail.elapsed_identity_residual_minutes.eq(0)&detail.departure_clock_residual_mod_1440.eq(0)&detail.arrival_clock_residual_mod_1440.eq(0)&detail.cause_sum_minus_arrival_delay.eq(0),
      'Internally consistent multi-day operational outlier; externally unconfirmed','Unresolved internal inconsistency; source follow-up required'))
    detail.to_csv(out/'extreme_records.csv',index=False)
    sensitivity=sensitivities(d);sensitivity.to_csv(out/'extreme_sensitivity.csv',index=False)
    s='# Extreme-delay investigation\n\nCanonical calculations and source records remain unchanged. Warning thresholds are below −120 or above 2,880 minutes, not automatic error boundaries.\n\n'
    s+=f"Found **{int(detail.arrival_warning.sum())} arrival warnings**, **{int(detail.departure_warning.sum())} departure warnings**, covering **{len(detail)} unique source records**. Every listed row was located in its original CSV by archive SHA-256 and one-based data-row number; raw values matched warehouse values.\n\n"
    s+='| Date | Carrier / flight | Route | Source row | Dep delay (min) | Arr delay (min) | Cancelled / diverted | Assessment |\n|---|---|---|---:|---:|---:|---|---|\n'
    for _,r in detail.iterrows():s+=f"| {str(r.FlightDate)[:10]} | {r.Reporting_Airline} {int(r.Flight_Number_Reporting_Airline)} | {r.Origin} → {r.Dest} | {int(r.source_row)} | {r.DepDelay:g} | {r.ArrDelay if pd.notna(r.ArrDelay) else 'missing'} | {int(r.Cancelled)} / {int(r.Diverted)} | {r.assessment} |\n"
    s+='\n## Traceable identities and supporting fields\n\n'
    for _,r in detail.iterrows():
        s+=f"### {str(r.FlightDate)[:10]} — {r.Reporting_Airline} {int(r.Flight_Number_Reporting_Airline)}\n\n- Technical source identity: `{r.flight_record_id}`.\n- Archive: `{r.source_file}`; CSV member: `{r.csv_member}`.\n- Scheduled/actual departure HHMM: {r.CRSDepTime:g}/{r.DepTime:g}; scheduled/actual arrival: {r.CRSArrTime:g}/{r.ArrTime}.\n- Scheduled/actual elapsed minutes: {r.CRSElapsedTime:g}/{r.ActualElapsedTime}; air time: {r.AirTime}; taxi-out/in: {r.TaxiOut}/{r.TaxiIn}.\n- First gate departure: {r.FirstDepTime}; total/longest additional ground time: {r.TotalAddGTime}/{r.LongestAddGTime}; diversion landings: {r.DivAirportLandings}; cancellation reason: {r.CancellationCode}.\n- Elapsed identity residual: {r.elapsed_identity_residual_minutes}; departure/arrival clock residual modulo 1,440: {r.departure_clock_residual_mod_1440}/{r.arrival_clock_residual_mod_1440}; allocated-cause sum minus arrival delay: {r.cause_sum_minus_arrival_delay}.\n- Assessment: **{r.assessment}**.\n\n"
    s+='''The six completed flights pass signed elapsed-time, local-clock modulo-day and cause-allocation consistency checks. These checks make the large delays internally plausible; they do not independently prove that a multi-day disruption occurred. No operational event is invented. The seventh flight is cancelled, so arrival/elapsed checks are unavailable. Gate-return fields provide context but cannot establish the cancellation timeline without dated event logs. Its classification remains unresolved, not a confirmed source error.

## Sensitivity (not canonical results)

| Scenario | Rows removed | Eligible arrivals | Mean arrival delay (min) | Mean late-arrival delay (min) | On-time % | Cancellation % |
|---|---:|---:|---:|---:|---:|---:|
'''
    for _,r in sensitivity.iterrows():s+=f"| {r.scenario} | {r.excluded_source_rows} | {r.eligible_flights:,.0f} | {r.avg_arrival_delay_minutes:.6f} | {r.avg_late_arrival_delay_minutes:.6f} | {r.on_time_pct:.6f} | {r.cancellation_pct:.6f} |\n"
    s+='\nExcluding all flagged rows also removes one cancellation and changes the all-flight denominator. This is a sensitivity exercise only, not a proposed cleaning rule. Machine-readable metrics and exact differences are in `session2/extreme_sensitivity.csv`.\n\n'
    s+=f'## Reporting guidance consulted\n\n[BTS Technical Directive 39, effective January 1, 2025]({DIRECTIVE}), sections 3.a, 5 and 7, accessed October 22, 2026: cancelled flights can retain departure fields after leaving the gate; on-time/diverted flights do not require delay-cause minutes, and reported cause allocations for late arrivals should reconcile to arrival delay. This supports the field checks, not independent confirmation of any event.\n'
    (root/'reports/EXTREME_DELAY_INVESTIGATION.md').write_text(s)
    return detail,sensitivity

if __name__=='__main__':
    a,b=investigate();print(a[['FlightDate','Reporting_Airline','DepDelay','ArrDelay','assessment']].to_string(index=False));print(b.to_string(index=False))
