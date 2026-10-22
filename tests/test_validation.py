import pandas as pd
import pytest
from src.validate import validate,normalize_schema

def test_valid_no_quarantine(rows):
    a,q,r=validate(rows,'2025-01');assert len(a)==1 and q.empty and r['reconciliation_passed']

@pytest.mark.parametrize('field,value,reason',[
 ('FlightDate','bad','invalid_date'),('Origin','12X','invalid_Origin'),('Dest',None,'invalid_Dest'),
 ('Cancelled',2,'invalid_Cancelled'),('Diverted',None,'invalid_Diverted'),('Distance',-1,'invalid_distance'),
 ('Distance','abc','parse_Distance'),('CRSDepTime',1260,'invalid_CRSDepTime'),('CRSArrTime',None,'missing_schedule'),
 ('DayOfWeek',4,'calendar_mismatch'),('DOT_ID_Reporting_Airline',1.5,'invalid_DOT_ID_Reporting_Airline'),
 ('Reporting_Airline',None,'missing_airline'),('ArrDel15',2,'invalid_ArrDel15'),('ArrDelay','inf','parse_ArrDelay'),
 ('DepTime',2500,'invalid_DepTime'),('Month',2,'calendar_mismatch')])
def test_quarantine(rows,field,value,reason):
    rows[field]=value;a,q,r=validate(rows,'2025-01');assert a.empty and len(q)==1 and r['invalid_values'][reason]==1

@pytest.mark.parametrize('delay,late,on_time',[(-20,False,True),(0,False,True),(14,False,True),(15,True,False),(200,True,False)])
def test_threshold(rows,delay,late,on_time):
    rows['ArrDelay']=delay;a,_,_=validate(rows,'2025-01');assert bool(a.late_arrival.iloc[0])==late and bool(a.on_time_arrival.iloc[0])==on_time;assert a.ArrDelay.iloc[0]==delay

@pytest.mark.parametrize('cancel,divert,delay,eligible',[(1,0,None,False),(0,1,30,False),(1,1,None,False),(0,0,None,False),(0,0,-5,True)])
def test_eligibility(rows,cancel,divert,delay,eligible):
    rows['Cancelled']=cancel;rows['Diverted']=divert;rows['ArrDelay']=delay
    a,_,_=validate(rows,'2025-01');assert bool(a.arrival_eligible.iloc[0])==eligible

def test_duplicate_preserved(rows):
    a,_,r=validate(pd.concat([rows,rows],ignore_index=True),'2025-01');assert len(a)==2 and r['duplicate_candidate_rows']==2 and r['duplicate_candidate_excess_rows']==1

def test_missing_schema(rows):
    with pytest.raises(ValueError,match='Missing required'): normalize_schema(rows.drop(columns='ArrDelay'))

def test_alias(rows):
    assert 'FlightDate' in normalize_schema(rows.rename(columns={'FlightDate':'FL_DATE'}))

def test_ambiguous_alias(rows):
    rows['FL_DATE']=rows.FlightDate
    with pytest.raises(ValueError,match='Ambiguous'): normalize_schema(rows)

def test_wrong_month(rows):
    a,q,_=validate(rows,'2025-02');assert a.empty and len(q)==1

def test_midnight_2400(rows):
    rows['CRSDepTime']=2400;a,_,_=validate(rows,'2025-01');assert len(a)==1

def test_warning_does_not_drop_extreme_delay(rows):
    rows['ArrDelay']=3000;a,_,r=validate(rows,'2025-01');assert len(a)==1 and r['warnings']['unexpected_arrival_delay']==1

def test_cancelled_missing_arrival_expected(rows):
    rows['Cancelled']=1;rows['ArrTime']=None;a,q,r=validate(rows,'2025-01');assert len(a)==1 and q.empty and r['warnings']['cancelled_missing_arrival_time_expected']==1
