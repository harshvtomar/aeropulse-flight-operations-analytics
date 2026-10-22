"""Hand-calculated statistical and resampling contracts; synthetic counts only."""
import numpy as np
import pandas as pd
import pytest
from src.statistics import wilson_interval, month_day_weights, resampled_rates, percentile_interval, rate_summary, paired_difference

def test_wilson_known_half_sample():
    lo,hi=wilson_interval(50,100)
    assert lo==pytest.approx(.4038315304) and hi==pytest.approx(.5961684696)

def test_wilson_no_events_not_false_certainty():
    lo,hi=wilson_interval(0,10);assert lo==pytest.approx(0,abs=1e-15) and 0<hi<1

def test_wilson_all_events_symmetry():
    a,b=wilson_interval(0,10);c,d=wilson_interval(10,10)
    assert c==pytest.approx(1-b) and d==pytest.approx(1-a)

def test_wilson_empty_population():
    assert all(np.isnan(wilson_interval(0,0)))

@pytest.mark.parametrize('s,n',[(2,1),(-1,1),(1,1.5),(np.inf,10),(np.nan,10)])
def test_invalid_wilson_counts(s,n):
    with pytest.raises(ValueError):wilson_interval(s,n)

def test_month_weights_preserve_each_month():
    d=pd.date_range('2025-01-01','2025-02-28');w=month_day_weights(d,100,12)
    assert (w[:,:31].sum(1)==31).all() and (w[:,31:].sum(1)==28).all()

def test_seed_reproducible_not_identical_all_rows():
    d=pd.date_range('2025-01-01',periods=10)
    a=month_day_weights(d,100,12);b=month_day_weights(d,100,12)
    assert np.array_equal(a,b) and np.unique(a,axis=0).shape[0]>1

def test_short_month_rejected():
    with pytest.raises(ValueError,match='Insufficient'):month_day_weights(pd.date_range('2025-01-01',periods=6),100)

def test_duplicate_dates_rejected():
    with pytest.raises(ValueError,match='unique'):month_day_weights(['2025-01-01']*7,100)

def test_unsorted_dates_rejected():
    with pytest.raises(ValueError,match='sorted'):month_day_weights(pd.date_range('2025-01-01',periods=7)[::-1],100)

def test_empty_dates_rejected():
    with pytest.raises(ValueError,match='observed'):month_day_weights([],100)

def test_ratio_of_sums_not_mean_of_rates():
    r=resampled_rates([1,0],[1,9],np.array([[1,1],[2,0],[0,2]]))
    assert r.tolist()==pytest.approx([.1,1,0])

def test_zero_resampled_denominator_stays_missing():
    r=resampled_rates([0,1],[0,1],np.array([[2,0],[0,2]]))
    assert np.isnan(r[0]) and r[1]==1

def test_fractional_daily_counts_rejected_before_summary_rounding():
    with pytest.raises(ValueError,match='integers'):rate_summary([.5],[1],np.ones((100,1)))

def test_negative_weights_rejected():
    with pytest.raises(ValueError,match='Weights'):resampled_rates([1],[1],np.array([[-1]]))

def test_shared_resampling_identical_carriers_zero_gap():
    w=month_day_weights(pd.date_range('2025-01-01',periods=7),100)
    s=np.arange(7);n=np.repeat(10,7);r=paired_difference(s,n,s,n,w)
    assert r['difference_pp']==0 and r['day_cluster_low_pp']==0 and r['day_cluster_high_pp']==0

def test_paired_effect_direction_and_percentage_points():
    w=np.ones((100,2));r=paired_difference([8,8],[10,10],[5,5],[10,10],w)
    assert r['difference_pp']==pytest.approx(30) and r['day_cluster_low_pp']==pytest.approx(30)

def test_percentiles_ignore_invalid_replicates():
    assert percentile_interval([np.nan,0,1],.8)==pytest.approx((.1,.9))

def test_empty_rate_summary():
    r=rate_summary([0],[0],np.ones((100,1)))
    assert r['valid_replicates']==0 and np.isnan(r['rate_pct'])
