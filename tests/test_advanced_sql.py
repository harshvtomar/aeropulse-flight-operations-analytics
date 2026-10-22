"""Synthetic boundary and denominator fixtures only; never business findings."""
import duckdb
import numpy as np
import pandas as pd
import pytest

from src.advanced_sql import execute_queries, reference_tables, compare_tables, SQL_DIR
from src.validate import CAUSES


def frame(rows, records):
    d = pd.DataFrame([{**rows.iloc[0].to_dict(), **r} for r in records])
    d['FlightDate'] = pd.to_datetime(d.FlightDate)
    d['Year'] = d.FlightDate.dt.year
    d['Month'] = d.FlightDate.dt.month
    d['DayOfWeek'] = d.FlightDate.dt.dayofweek + 1
    d['arrival_eligible'] = d.Cancelled.eq(0) & d.Diverted.eq(0) & d.ArrDelay.notna()
    d['late_arrival'] = d.arrival_eligible & d.ArrDelay.ge(15)
    d['on_time_arrival'] = d.arrival_eligible & d.ArrDelay.lt(15)
    return d


def query(d, name):
    with duckdb.connect() as con:
        con.register('fact_flights', d.reset_index(drop=True))
        return con.execute((SQL_DIR / (name + '.sql')).read_text()).df()


@pytest.mark.parametrize('delay,band', [(-20,'0 under 15'), (14,'0 under 15'), (15,'1 15-29'),
 (29,'1 15-29'),(30,'2 30-59'),(59,'2 30-59'),(60,'3 60-119'),(119,'3 60-119'),(120,'4 120+')])
def test_severity_boundaries(rows,delay,band):
    result=query(frame(rows,[{'ArrDelay':delay}]),'13_delay_severity')
    assert result.severity.tolist()==[band]
    assert result.flights.iloc[0]==1
    assert result.signed_arrival_minutes.iloc[0]==delay


def test_severity_excludes_status_and_missing(rows):
    d=frame(rows,[{'ArrDelay':15},{'ArrDelay':50,'Cancelled':1},
                  {'ArrDelay':60,'Diverted':1},{'ArrDelay':None}])
    r=query(d,'13_delay_severity')
    assert r.flights.sum()==1 and r.eligible_share_pct.iloc[0]==100


def test_no_late_no_concentration_denominator(rows):
    r=query(frame(rows,[{'ArrDelay':-1}]),'15_route_concentration')
    assert np.isnan(r.network_delayed_share_pct.iloc[0])
    assert np.isnan(r.cumulative_delayed_share_pct.iloc[0])
    assert not r.rate_comparison_eligible.iloc[0]


def test_concentration_ties_deterministic(rows):
    d=frame(rows,[{'DestAirportID':12892,'Dest':'LAX','ArrDelay':15},
                  {'DestAirportID':11298,'Dest':'DFW','ArrDelay':20}])
    r=query(d,'15_route_concentration')
    assert r.Dest.tolist()==['DFW','LAX']
    assert r.cumulative_delayed_share_pct.tolist()==[50.,100.]
    pd.testing.assert_frame_equal(r,query(d.iloc[::-1],'15_route_concentration'))


def test_concentration_screen_1000(rows):
    d=frame(rows,[{'ArrDelay':20}]*1000)
    assert query(d,'15_route_concentration').rate_comparison_eligible.iloc[0]
    assert not query(d.iloc[:-1],'15_route_concentration').rate_comparison_eligible.iloc[0]


def test_monthly_difference_uses_percentage_points(rows):
    d=frame(rows,[{'ArrDelay':0},{'ArrDelay':15},{'FlightDate':'2025-02-01','ArrDelay':20}])
    r=query(d,'14_airline_monthly')
    assert np.isnan(r.prior_month_change_pp.iloc[0])
    assert r.prior_month_change_pp.iloc[1]==50.


def test_scheduled_2400_maps_to_zero(rows):
    d=frame(rows,[{'CRSDepTime':2400,'ArrDelay':120},{'CRSDepTime':0,'ArrDelay':119}])
    r=query(d,'17_departure_hour_monthly')
    assert len(r)==1 and r.departure_hour.iloc[0]==0
    assert r.severe_delayed_flights.iloc[0]==1


def test_weekend_calendar_not_operating_day_denominator(rows):
    d=frame(rows,[{'FlightDate':'2025-02-01'},{'FlightDate':'2025-02-03'}])
    r=query(d,'18_weekend_monthly').set_index('day_type')
    assert r.loc['weekend','calendar_days']==8
    assert r.loc['weekday','calendar_days']==20
    assert r.loc['weekend','flights_per_calendar_day']==1/8


def test_full_month_includes_zero_flight_dates(rows):
    d=frame(rows,[{'FlightDate':'2025-02-01','ArrDelay':20}])
    r=query(d,'19_daily_normalization')
    assert len(r)==28 and r.reported_flights.sum()==1
    assert (r.monthly_flights_per_day==1/28).all()
    assert r.loc[r.reported_flights.eq(0),'delay_rate_pct'].isna().all()


def test_leap_year_calendar(rows):
    r=query(frame(rows,[{'FlightDate':'2024-02-02'}]),'19_daily_normalization')
    assert len(r)==29 and r.calendar_days_in_month.eq(29).all()


def test_cause_null_is_not_zero_and_partial_coverage(rows):
    missing=dict.fromkeys(CAUSES,None)
    d=frame(rows,[{**missing,'ArrDelay':20},{**missing,'ArrDelay':30,'CarrierDelay':30}])
    r=query(d,'20_cause_coverage').set_index('cause')
    assert pd.isna(r.loc['WeatherDelay','reported_minutes'])
    assert r.loc['CarrierDelay','late_coverage_pct']==50
    assert r.late_incomplete_cause_records.eq(2).all()
    assert r.complete_allocated_minutes.isna().all()


def test_cause_allocation_mismatch_detected(rows):
    d=frame(rows,[{'ArrDelay':30,'CarrierDelay':20}])
    r=query(d,'20_cause_coverage')
    assert r.complete_allocation_mismatch_records.eq(1).all()
    assert r.complete_allocated_minutes.eq(20).all()
    assert r.complete_arrival_delay_minutes.eq(30).all()


def test_cause_values_outside_late_population_remain_visible(rows):
    r=query(frame(rows,[{'ArrDelay':0,'CarrierDelay':3}]),'20_cause_coverage')
    assert r.outside_late_any_cause_records.eq(1).all()
    assert r.late_coverage_pct.isna().all()


def test_cancellation_reason_partition_and_denominator(rows):
    d=frame(rows,[{'Cancelled':1,'CancellationCode':'A','ArrDelay':None},
      {'Cancelled':1,'CancellationCode':None,'ArrDelay':None},
      {'Cancelled':0,'CancellationCode':'B','ArrDelay':0}])
    r=query(d,'21_cancellation_patterns').iloc[0]
    assert r.cancelled_flights==2 and r.cancellation_pct==pytest.approx(200/3)
    assert r.carrier_cancellations==1 and r.unknown_cancellations==1 and r.weather_cancellations==0


def test_recurring_requires_every_month_and_sufficient_volume(rows):
    records=[]
    for month in [1,2,3]:
        records += [{'FlightDate':f'2025-{month:02}-01','ArrDelay':0,'Dest':'LAX','DestAirportID':12892}]*1000
        if month<3: records += [{'FlightDate':f'2025-{month:02}-01','ArrDelay':20,'Dest':'DFW','DestAirportID':11298}]*1000
    r=query(frame(rows,records),'22_recurring_airport_delays').set_index('Dest')
    assert r.loc['DFW','observed_months']==2 and r.loc['DFW','required_months']==3
    assert not r.loc['DFW','recurring_above_network']


def test_all_ten_sql_reconcile_independently_on_fixture(rows):
    missing=dict.fromkeys(CAUSES,None)
    d=frame(rows,[{'ArrDelay':-10},{'ArrDelay':15,'CarrierDelay':15},
      {**missing,'ArrDelay':30}, {'ArrDelay':None,'Cancelled':1,'CancellationCode':'B'},
      {'FlightDate':'2025-02-01','ArrDelay':130,'CarrierDelay':100,'WeatherDelay':30},
      {'FlightDate':'2025-02-02','ArrDelay':15,'Diverted':1}])
    with duckdb.connect() as con:
        con.register('fact_flights',d)
        actual=execute_queries(con)
    assert len(actual)==10
    counts=compare_tables(actual,reference_tables(d))
    assert all(x['numeric_comparisons']>0 for x in counts.values())


def test_missing_month_is_not_previous_month_comparison(rows):
    d=frame(rows,[{'ArrDelay':0},{'FlightDate':'2025-03-01','ArrDelay':20}])
    r=query(d,'14_airline_monthly')
    assert r.prior_month_change_pp.isna().all()
    assert reference_tables(d)['14_airline_monthly'].prior_month_change_pp.isna().all()


def test_comparator_rejects_wrong_denominator(rows):
    d=frame(rows,[{'ArrDelay':20}])
    with duckdb.connect() as c:
        c.register('fact_flights',d);a=execute_queries(c)
    a['14_airline_monthly'].loc[0,'delay_rate_pct']=50
    with pytest.raises(AssertionError):compare_tables(a,reference_tables(d))
