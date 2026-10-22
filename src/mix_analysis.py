"""Pair-specific, common-support direct standardization; descriptive, not causal."""
from itertools import combinations
from pathlib import Path
import argparse
import json
import duckdb
import numpy as np
import pandas as pd

STRATA = ['origin_id','destination_id','hour_block','month']


def direct_standardization(cells, airline_a, airline_b, min_cell=20, min_support=1000, min_strata=20, min_coverage=.10):
    """Use pooled A+B eligible-flight weights on mutually populated strata.

    Each input row is a carrier x stratum with eligible denominator n and ontime
    numerator y. A common stratum needs >=min_cell observations for BOTH carriers.
    Thresholds screen comparisons, not statistical significance. Estimates remain
    available as exploratory summaries; publishability is a separate flag.
    """
    if airline_a == airline_b: raise ValueError('Compare two distinct carriers')
    if min_cell < 1 or min_support < 1 or min_strata < 1 or not 0 <= min_coverage <= 1:
        raise ValueError('Invalid support thresholds')
    if cells.duplicated(['airline']+STRATA).any(): raise ValueError('Duplicate cells')
    if cells[STRATA+['airline']].isna().any().any(): raise ValueError('Missing stratum key')
    if not np.isfinite(cells[['n','y']].to_numpy(dtype=float)).all() or cells[['n','y']].isna().any().any() or (cells.n < 0).any() or (cells.y < 0).any() or (cells.y > cells.n).any():
        raise ValueError('Invalid cell counts')
    if (cells.n != cells.n.round()).any() or (cells.y != cells.y.round()).any(): raise ValueError('Counts must be integers')
    a=cells[cells.airline.eq(airline_a)].set_index(STRATA)[['n','y']]
    b=cells[cells.airline.eq(airline_b)].set_index(STRATA)[['n','y']]
    na,nb=int(a.n.sum()),int(b.n.sum())
    common=a.join(b,how='inner',lsuffix='_a',rsuffix='_b')
    common=common[(common.n_a>=min_cell)&(common.n_b>=min_cell)].copy()
    sa,sb=int(common.n_a.sum()),int(common.n_b.sum())
    result=dict(airline_a=airline_a,airline_b=airline_b,full_n_a=na,full_n_b=nb,
        full_raw_a_pct=100*a.y.sum()/na if na else np.nan,full_raw_b_pct=100*b.y.sum()/nb if nb else np.nan,
        common_strata=len(common),omitted_strata_a=len(a)-len(common),omitted_strata_b=len(b)-len(common),
        common_n_a=sa,common_n_b=sb,omitted_n_a=na-sa,omitted_n_b=nb-sb,
        coverage_a_pct=100*sa/na if na else 0.,coverage_b_pct=100*sb/nb if nb else 0.,
        common_raw_a_pct=100*common.y_a.sum()/sa if sa else np.nan,
        common_raw_b_pct=100*common.y_b.sum()/sb if sb else np.nan,
        adjusted_a_pct=np.nan,adjusted_b_pct=np.nan,adjusted_difference_pp=np.nan,
        raw_common_difference_pp=np.nan,full_raw_difference_pp=np.nan,
        comparison_eligible=False)
    if na and nb: result['full_raw_difference_pp']=result['full_raw_a_pct']-result['full_raw_b_pct']
    if len(common):
        common['reference_weight']=(common.n_a+common.n_b)/(sa+sb)
        common['rate_a']=common.y_a/common.n_a;common['rate_b']=common.y_b/common.n_b
        result['adjusted_a_pct']=100*(common.reference_weight*common.rate_a).sum()
        result['adjusted_b_pct']=100*(common.reference_weight*common.rate_b).sum()
        result['adjusted_difference_pp']=result['adjusted_a_pct']-result['adjusted_b_pct']
        result['raw_common_difference_pp']=result['common_raw_a_pct']-result['common_raw_b_pct']
        result['comparison_eligible']=bool(sa>=min_support and sb>=min_support and len(common)>=min_strata and sa/na>=min_coverage and sb/nb>=min_coverage)
    return result,common.reset_index()



def validate_mix_inputs(root,cells):
    """Rebuild exact stratum counts using pandas and source status columns."""
    cols=['Reporting_Airline','OriginAirportID','DestAirportID','CRSDepTime','Month','Cancelled','Diverted','ArrDelay']
    d=pd.concat([pd.read_parquet(p,columns=cols) for p in sorted((Path(root)/'data/processed').glob('*/flights.parquet'))],ignore_index=True)
    d=d[d.Cancelled.eq(0)&d.Diverted.eq(0)&d.ArrDelay.notna()].copy()
    d=d.assign(airline=d.Reporting_Airline,origin_id=d.OriginAirportID.astype(int),destination_id=d.DestAirportID.astype(int),
               hour_block=((d.CRSDepTime//100)%24//6).astype(int),month=d.Month.astype(int),n=1,y=d.ArrDelay.lt(15).astype(int))
    keys=['airline']+STRATA
    expected=d.groupby(keys)[['n','y']].sum().sort_index()
    actual=cells.set_index(keys)[['n','y']].sort_index()
    pd.testing.assert_frame_equal(actual,expected,check_dtype=False,check_index_type=False)
    return {'passed':True,'strata':len(expected),'numeric_comparisons':len(expected)*2,
            'method':'pandas original status/delay fields from validated Parquet, independent SQL grouping'}


def run(root='.'):
    root=Path(root);out=root/'reports/session2';out.mkdir(parents=True,exist_ok=True)
    with duckdb.connect(str(root/'data/aeropulse.duckdb'),read_only=True) as con:
        cells=con.execute('''SELECT Reporting_Airline AS airline,CAST(OriginAirportID AS INTEGER) AS origin_id,
          CAST(DestAirportID AS INTEGER) AS destination_id,CAST(floor((floor(CRSDepTime/100)%24)/6) AS INTEGER) AS hour_block,
          CAST(Month AS INTEGER) AS month,count(*) AS n,count(*) FILTER(WHERE ArrDelay<15) AS y
          FROM fact_flights WHERE arrival_eligible GROUP BY ALL ORDER BY ALL''').df()
        # Marginal composition summaries show how reference populations differ.
        composition=[]
        for axis,expression in [('origin','Origin'),('destination','Dest'),('route',"Origin || '→' || Dest"),('departure_hour','CAST(floor(CRSDepTime/100)%24 AS INTEGER)'),('month','CAST(Month AS INTEGER)')]:
            g=con.execute(f'''SELECT Reporting_Airline AS airline,CAST({expression} AS VARCHAR) AS category,
              count(*) AS eligible_flights,count(*) FILTER(WHERE ArrDelay<15) AS ontime
              FROM fact_flights WHERE arrival_eligible GROUP BY ALL ORDER BY ALL''').df()
            g['axis']=axis;g['carrier_share_pct']=100*g.eligible_flights/g.groupby('airline').eligible_flights.transform('sum')
            composition.append(g)
        volume=con.execute('''WITH volume AS (SELECT OriginAirportID,DestAirportID,count(*) AS route_n FROM fact_flights WHERE arrival_eligible GROUP BY ALL)
          SELECT Reporting_Airline AS airline,
          CASE WHEN route_n<100 THEN '<100' WHEN route_n<500 THEN '100–499' WHEN route_n<1000 THEN '500–999' ELSE '1000+' END AS category,
          count(*) AS eligible_flights,count(*) FILTER(WHERE ArrDelay<15) AS ontime
          FROM fact_flights JOIN volume USING(OriginAirportID,DestAirportID) WHERE arrival_eligible GROUP BY ALL ORDER BY ALL''').df()
        volume['axis']='route_volume';volume['carrier_share_pct']=100*volume.eligible_flights/volume.groupby('airline').eligible_flights.transform('sum')
        composition.append(volume)
    validation=validate_mix_inputs(root,cells)
    (out/'MIX_INPUT_RECONCILIATION.json').write_text(json.dumps(validation,indent=2))
    rows=[];support_examples=[]
    for a,b in combinations(sorted(cells.airline.unique()),2):
        summary,support=direct_standardization(cells,a,b)
        rows.append(summary)
        if (a,b) in [('AA','DL'),('AA','WN'),('DL','WN')]:
            support.insert(0,'airline_b',b);support.insert(0,'airline_a',a);support_examples.append(support)
    result=pd.DataFrame(rows)
    result.to_csv(out/'mix_adjusted_pairs.csv',index=False)
    pd.concat(composition,ignore_index=True).to_csv(out/'carrier_composition.csv',index=False)
    pd.concat(support_examples,ignore_index=True).to_csv(out/'mix_reference_strata_top3.csv',index=False)
    # Publish the actual cell inputs for reproducibility, compact Parquet locally.
    dataout=root/'data/processed/session2';dataout.mkdir(exist_ok=True)
    cells.to_parquet(dataout/'mix_cells.parquet',index=False)
    import hashlib
    metadata={'cell_count':len(cells),'eligible_pairs':int(result.comparison_eligible.sum()),'all_pairs':len(result),
      'strata':STRATA,'hour_blocks':'00–05,06–11,12–17,18–23 local; 2400→00',
      'min_cell_per_carrier':20,'min_common_n_per_carrier':1000,'min_common_strata':20,'min_coverage_per_carrier':.10,
      'reference_population':'pooled eligible flights of the two compared carriers, restricted to common support',
      'mix_cells_sha256':hashlib.sha256((dataout/'mix_cells.parquet').read_bytes()).hexdigest(),
      'adjusted_interval':'not estimated; point estimates only; raw paired intervals are not adjusted intervals'}
    (out/'MIX_RUN.json').write_text(json.dumps(metadata,indent=2))
    lines=['# Route and schedule-mix analysis — Session 2','',
      'Full-quarter raw rates compare different networks. The analysis below changes the question to pair-specific overlapping route/schedule/month strata. It does not estimate causal airline quality.','',
      '## Reference population and common support','',
      'A stratum is directed DOT origin-airport ID × destination-airport ID × six-hour scheduled local departure block × calendar month. A cell enters common support only when BOTH compared carriers have at least 20 eligible arrivals. Reference weights are pooled A+B eligible flights in retained strata divided by their combined retained count. The two carrier stratum-specific rates receive identical weights.',
      '',f'Of {len(result)} possible carrier pairs, **{int(result.comparison_eligible.sum())}** meet all screening rules: at least 20 common strata, 1,000 common eligible arrivals per carrier and 10% coverage of each carrier’s full eligible population. These thresholds are screening choices, not guarantees of unbiased comparisons. The export retains all pairs and a comparison_eligible flag; unsupported pairs must not enter a ranking.',
      '', 'The reference differs by pair. Therefore adjusted carrier rates from different rows are not a common-reference league table. Six-hour blocks leave within-block schedule differences; we also do not control for day, aircraft, weather, staffing or network propagation. Regional and mainline reporting carriers remain distinct.',
      '', '## Three largest-volume carriers: explicit population changes','',
      '| A − B | Full raw gap (pp) | Common raw gap (pp) | Adjusted gap (pp) | Common n A / B | Coverage A / B | Strata | Screen |',
      '|---|---:|---:|---:|---|---|---:|---|']
    for _,r in result[(result.airline_a.isin(['AA','DL','WN']))&(result.airline_b.isin(['AA','DL','WN']))].iterrows():
        lines.append(f'| {r.airline_a} − {r.airline_b} | {r.full_raw_difference_pp:.3f} | {r.raw_common_difference_pp:.3f} | {r.adjusted_difference_pp:.3f} | {r.common_n_a:,} / {r.common_n_b:,} | {r.coverage_a_pct:.1f}% / {r.coverage_b_pct:.1f}% | {r.common_strata:,} | {"Pass" if r.comparison_eligible else "Insufficient support"} |')
    lines+=['','Full raw → common raw reflects restricting the compared population. Common raw → adjusted reflects weighting the same retained strata identically. Combining these changes into a single “mix effect” would obscure selection into common support. Adjusted estimates are point estimates only; raw day-cluster intervals in STATISTICAL_ANALYSIS.md do not transfer to them.',
      '', '## Composition across operational axes','',
      'The complete `carrier_composition.csv` export includes origin airports, destination airports, directed routes, individual scheduled hours, months and quarter-wide route-volume bands (<100, 100–499, 500–999, 1000+ eligible arrivals). Shares use each carrier’s eligible arrivals as denominator, sum to 100% within carrier/axis, and retain cell counts. These marginal profiles explain where overlap exists; they are not separate causal adjustments.',
      '', '## Investigation priorities','',
      '- Use the top-three common-support examples to inspect route/hour/month cells with large observed gaps, then check stability by day and month before recommending action.',
      '- Prioritize high-volume delayed routes and airports identified by concentration tables. A large raw gap on a poorly overlapping network does not establish an airline-level problem.',
      '- For carrier pairs failing support screens, report insufficient overlap rather than extrapolating missing cells or replacing absent rates with zero.',
      '', '## Evidence','',
      '`mix_adjusted_pairs.csv` lists full and retained sample sizes, omitted counts/strata, raw full and common-support rates, adjusted rates and eligibility for every pair. `mix_reference_strata_top3.csv` contains exact weights and counts for the three exposure-selected comparisons. Full input cells are regenerated locally as `data/processed/session2/mix_cells.parquet`; the checksum is in `MIX_RUN.json`. Run `python -m src.mix_analysis`.']
    (root/'reports/MIX_ADJUSTMENT_ANALYSIS.md').write_text('\n'.join(lines)+'\n')
    return metadata

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',default='.');a=p.parse_args();print(json.dumps(run(a.root),indent=2))
