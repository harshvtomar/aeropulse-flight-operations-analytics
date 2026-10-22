import numpy as np
import pandas as pd
from src.investigate import extreme_mask,hhmm_minutes,sensitivities

def test_strict_warning_boundaries():
    d=pd.DataFrame({'ArrDelay':[-121,-120,2880,2881,np.nan]})
    assert extreme_mask(d,'ArrDelay').tolist()==[True,False,False,True,False]

def test_clock_midnight():
    assert hhmm_minutes(pd.Series([0,2400,1234])).tolist()==[0,0,754]

def test_sensitivity_preserves_original_and_distinguishes_denominators(rows):
    d=pd.concat([rows]*4,ignore_index=True);d['ArrDelay']=[-5,3000,20,np.nan];d['DepDelay']=[0,3005,2900,3100];d['Cancelled']=[0,0,0,1]
    original=d.copy(deep=True);r=sensitivities(d).set_index('scenario');pd.testing.assert_frame_equal(d,original)
    assert r.loc['canonical_all','reported_flights']==4
    assert r.loc['exclude_arrival_warning_only','excluded_source_rows']==1
    assert r.loc['exclude_arrival_warning_only','eligible_flights']==2
    assert r.loc['exclude_any_arrival_or_departure_warning','excluded_source_rows']==3
    assert r.loc['exclude_any_arrival_or_departure_warning','cancellation_pct']==0

def test_no_outliers_no_metric_change(rows):
    r=sensitivities(rows);assert r.excluded_source_rows.eq(0).all();assert r.avg_arrival_delay_minutes_difference_from_canonical.eq(0).all()
