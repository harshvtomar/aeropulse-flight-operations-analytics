"""Synthetic common-support examples with known direct-standardized rates."""
import numpy as np
import pandas as pd
import pytest
from src.mix_analysis import direct_standardization

def cells():
    return pd.DataFrame([['A',1,2,1,1,90,81],['A',1,3,1,1,10,1],['B',1,2,1,1,10,9],['B',1,3,1,1,90,9]],columns=['airline','origin_id','destination_id','hour_block','month','n','y'])

def compare(d,**kw):return direct_standardization(d,'A','B',min_cell=1,min_support=1,min_strata=1,min_coverage=0,**kw)

def test_composition_alone_can_explain_raw_gap():
    r,w=compare(cells());assert r['full_raw_difference_pp']==pytest.approx(64)
    assert r['adjusted_a_pct']==pytest.approx(50) and r['adjusted_b_pct']==pytest.approx(50)
    assert w.reference_weight.sum()==pytest.approx(1)

def test_population_restriction_and_omissions():
    d=cells();d.loc[3,'destination_id']=4;r,w=compare(d)
    assert r['common_strata']==1 and r['common_n_a']==90 and r['omitted_n_a']==10
    assert r['coverage_b_pct']==10 and r['adjusted_difference_pp']==pytest.approx(0)

def test_min_cell_requires_both_carriers():
    r,w=direct_standardization(cells(),'A','B',min_cell=20,min_support=1,min_strata=1,min_coverage=0)
    assert w.empty and not r['comparison_eligible'] and np.isnan(r['adjusted_difference_pp'])

def test_screen_does_not_imply_statistical_significance():
    r,w=direct_standardization(cells(),'A','B',min_cell=1,min_support=101,min_strata=1,min_coverage=0)
    assert not r['comparison_eligible'] and np.isfinite(r['adjusted_difference_pp'])

def test_duplicate_strata_fail():
    d=cells();d=pd.concat([d,d.iloc[[0]]])
    with pytest.raises(ValueError,match='Duplicate'):compare(d)

def test_missing_stratum_fail():
    d=cells();d.loc[0,'month']=None
    with pytest.raises(ValueError,match='Missing'):compare(d)

def test_invalid_counts_fail():
    d=cells();d.loc[0,'y']=91
    with pytest.raises(ValueError,match='Invalid'):compare(d)

def test_nonfinite_counts_fail():
    d=cells().astype({'n':float});d.loc[0,'n']=np.inf
    with pytest.raises(ValueError,match='Invalid'):compare(d)

def test_same_carrier_rejected():
    with pytest.raises(ValueError,match='distinct'):direct_standardization(cells(),'A','A')

def test_carrier_reversal_changes_sign():
    d=cells();d.loc[0,'y']=72
    r,_=compare(d);rev,_=direct_standardization(d,'B','A',min_cell=1,min_support=1,min_strata=1,min_coverage=0)
    assert r['adjusted_difference_pp']==pytest.approx(-rev['adjusted_difference_pp'])

def test_disjoint_support_no_extrapolation():
    d=cells();d.loc[d.airline=='B','month']=2;r,w=compare(d)
    assert r['common_strata']==0 and np.isnan(r['adjusted_a_pct'])
