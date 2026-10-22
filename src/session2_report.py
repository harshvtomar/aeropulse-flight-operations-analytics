"""Evidence-linked Session 2 figures and business findings from verified exports."""
from pathlib import Path
import json
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .investigate import DIRECTIVE

COLORS=['#0072B2','#E69F00','#009E73','#CC79A7','#D55E00']

def run(root='.'):
    root=Path(root);out=root/'reports/session2';figdir=out/'figures';figdir.mkdir(parents=True,exist_ok=True)
    def read(n):return pd.read_csv(out/'sql'/n)
    severity=read('13_delay_severity.csv');routes=read('15_route_concentration.csv');airports=read('16_airport_concentration.csv')
    monthly=read('14_airline_monthly.csv');causes=read('20_cause_coverage.csv');recurring=read('22_recurring_airport_delays.csv')
    mix=pd.read_csv(out/'mix_adjusted_pairs.csv');intervals=pd.read_csv(out/'rate_intervals.csv')
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.titleweight':'bold','figure.facecolor':'#f8fafc','axes.facecolor':'#f8fafc','axes.labelcolor':'#24354b','text.color':'#24354b'})
    figures=[]
    def save(fig,name):
        fig.text(.02,.015,'AeroPulse • Official BTS reporting carriers • Jan–Mar 2025 • Descriptive analysis',fontsize=8,color='#536477')
        fig.tight_layout(rect=[0,.055,1,.98]);fig.savefig(figdir/(name+'.png'),dpi=150);plt.close(fig);figures.append(name+'.png')
    delayed=severity[severity.severity.ne('0 under 15')];late=int(delayed.flights.sum());minutes=float(delayed.signed_arrival_minutes.sum())
    fig,ax=plt.subplots(1,2,figsize=(11,4.7));labels=delayed.severity.str[2:]
    ax[0].bar(labels,delayed.flights/1000,color=COLORS[:4]);ax[0].set(title='Delayed arrivals by severity',xlabel='Arrival delay (minutes)',ylabel='Flights (thousands)')
    ax[1].bar(labels,100*delayed.signed_arrival_minutes/minutes,color=COLORS[:4]);ax[1].set(title='Share of late-arrival delay minutes',xlabel='Arrival delay (minutes)',ylabel='% of minutes among arrivals ≥15 min late',ylim=(0,60))
    save(fig,'01_delay_severity')
    fig,ax=plt.subplots(1,2,figsize=(12,5.7));a=airports.head(10).iloc[::-1];r=routes.head(10).iloc[::-1]
    ax[0].barh(a.Dest,a.delayed_flights/1000,color=COLORS[0]);ax[0].set(title='Top destinations by delayed arrivals',xlabel='Delayed eligible arrivals (thousands)')
    ax[1].barh(r.Origin+' → '+r.Dest,r.delayed_flights,color=COLORS[2]);ax[1].set(title='Top directed routes by delayed arrivals',xlabel='Delayed eligible arrivals (count)')
    save(fig,'02_delay_concentration')
    matrix=monthly.pivot(index='Reporting_Airline',columns='Month',values='delay_rate_pct').sort_index()
    fig,ax=plt.subplots(figsize=(8,7));im=ax.imshow(matrix.to_numpy(),cmap='cividis',vmin=0,vmax=40,aspect='auto')
    ax.set(xticks=range(3),xticklabels=['January','February','March'],yticks=range(len(matrix)),yticklabels=matrix.index,title='Monthly airline arrival-delay rates')
    for i in range(len(matrix)):
        for j in range(3):
            v=matrix.iloc[i,j];ax.text(j,i,f'{v:.1f}%',ha='center',va='center',color='white' if v<18 else '#111111')
    fig.colorbar(im,ax=ax,label='% of eligible arrivals delayed ≥15 minutes');save(fig,'03_airline_monthly')
    a=mix[mix.comparison_eligible].copy();labels=a.airline_a+' − '+a.airline_b
    fig,ax=plt.subplots(figsize=(10,5.4))
    for col,offset,color,label in [('full_raw_difference_pp',-.2,COLORS[0],'Full networks: raw'),('raw_common_difference_pp',0,COLORS[1],'Common support: raw'),('adjusted_difference_pp',.2,COLORS[2],'Common support: same pooled weights')]:
        ax.scatter(a[col],pd.Series(range(len(a)))+offset,color=color,label=label,s=55)
    ax.axvline(0,color='#777',linewidth=1);ax.set(yticks=range(len(a)),yticklabels=labels,xlabel='On-time rate A − B (percentage points)',title='Raw and mix-adjusted gaps — supported carrier pairs')
    ax.legend(loc='best',fontsize=8);save(fig,'04_raw_adjusted_comparisons')
    totals=causes.groupby('cause',sort=True).reported_minutes.sum(min_count=1).sort_values();mapping={'CarrierDelay':'Carrier','WeatherDelay':'Weather','NASDelay':'National Aviation System','SecurityDelay':'Security','LateAircraftDelay':'Late-arriving aircraft'}
    fig,ax=plt.subplots(figsize=(10,5.2));ax.barh([mapping[x] for x in totals.index],totals/1e6,color=COLORS[0]);ax.set(title='Source-reported delay-cause allocations',xlabel='Reported allocated minutes (millions)')
    for i,v in enumerate(totals):ax.text(v/1e6+.05,i,f'{100*v/totals.sum():.2f}%',va='center',fontsize=9)
    ax.set_xlim(0,totals.max()/1e6*1.18);save(fig,'05_reported_delay_causes')
    hours=read('17_departure_hour_monthly.csv');fig,ax=plt.subplots(figsize=(10,4.7))
    for i,(month,g) in enumerate(hours.groupby('Month')):ax.plot(g.departure_hour,g.delay_rate_pct,marker='.',color=COLORS[i],label=['January','February','March'][int(month)-1])
    ax.set(title='Scheduled departure-hour reliability by month',xlabel='Scheduled local departure hour (2400 → 0)',ylabel='% of eligible arrivals delayed ≥15 min',xticks=range(0,24,2),ylim=(0,45));ax.legend();save(fig,'06_departure_hours')
    # Category populations repeat five times: keep one record per month for population totals.
    coverage=causes.drop_duplicates(['Year','Month']);eligible=int(coverage.late_eligible_flights.sum());complete=int(coverage.late_complete_cause_records.sum());bad=int(coverage.complete_allocation_mismatch_records.sum());outside=int(coverage.outside_late_any_cause_records.sum())
    cause_report=f'''# Reported delay-cause analysis — Session 2

Analysis population: **{eligible:,}** normal completed flights arriving at least 15 minutes late. All **{complete:,}** have nonmissing values for all five cause fields; **{bad}** complete records fail the allocated-minute = arrival-delay check. **{outside}** records outside this late-arrival population contain any cause-minute value. Zero values mean a reported zero; missing values remain missing.

| Source category | Allocated minutes | Share of observed allocated minutes |
|---|---:|---:|
'''
    for name,v in totals.sort_values(ascending=False).items():cause_report+=f'| {mapping[name]} | {v:,.0f} | {100*v/totals.sum():.2f}% |\n'
    cause_report+=f'''
The five categories sum to **{totals.sum():,.0f} minutes**, equal to summed arrival delay over the {eligible:,} late eligible records. Coverage is 100% for each category in each month in this snapshot. This is an observed reconciliation, not a certification of carrier reporting compliance or independently verified root causes.

[BTS Technical Directive 39]({DIRECTIVE}), effective January 1, 2025, sections 5 and 7, distinguishes cancellation reasons from late-arrival minute allocations. It does not require cause minutes for on-time or diverted flights. Its allocation rules reconcile minutes to arrival delay and allow predominant-cause reporting. Those conventions limit causal interpretation.

Cancellation reasons are analyzed separately in query 21; cancelled flights are not treated as missing late-arrival reports. Do not substitute zero for unavailable allocations or sum the repeated population denominators across category rows. Minute shares use total observed allocated minutes, not flight counts. Categories need not represent unique independent incidents, and weather effects can appear indirectly in other reported categories.

Evidence: `session2/sql/20_cause_coverage.csv`, `session2/figures/05_reported_delay_causes.png`, and the independent `session2/SQL_RECONCILIATION.json`. Reproduce through `python -m src.advanced_sql` then `python -m src.session2_report`.
'''
    (root/'reports/DELAY_CAUSE_ANALYSIS.md').write_text(cause_report)
    severe=delayed.iloc[-1];top10=float(airports.head(10).network_delayed_share_pct.sum());rec=recurring[recurring.recurring_above_network]
    aa=mix[(mix.airline_a=='AA')&(mix.airline_b=='DL')].iloc[0]
    ci=intervals[(intervals.airline=='ALL')&(intervals.metric=='on_time')].iloc[0]
    s=f'''# Executive operational insights — Session 2

**Scope:** 1,645,503 genuine reporting-carrier flights, January 1–March 31, 2025; 1,611,046 eligible arrivals, 14 carriers and 333 airports. All source checksums and canonical Session 1 KPIs are preserved. This report supports investigation; it does not estimate causal operational quality or realized financial benefits.

## Decision-relevant findings

1. **Severe delays contribute disproportionately to delay minutes.** The {int(severe.flights):,} arrivals delayed at least 120 minutes are {severe.delayed_share_pct:.2f}% of {late:,} delayed arrivals, but account for {100*severe.signed_arrival_minutes/minutes:.2f}% of their {minutes:,.0f} delay minutes. Prioritize recurring severe-delay cases, rather than optimizing only the overall mean.
2. **Delay volume and poor reliability are different questions.** The ten largest destination contributors account for {top10:.2f}% of delayed arrivals. DFW contributes {int(airports.iloc[0].delayed_flights):,} from {int(airports.iloc[0].eligible_flights):,} eligible arrivals ({airports.iloc[0].delay_rate_pct:.2f}% delayed). High contribution can reflect high traffic; compare rates and sample sizes alongside volume.
3. **Recurring destination gaps deserve focused review.** {len(rec)} airports exceed the same-month network delay rate in all three months while retaining at least 1,000 eligible arrivals in each month. The highest delayed-flight-volume examples are {', '.join(rec.head(5).Dest)}. This is a screening flag, not evidence that airport management caused the delays.
4. **Carrier comparisons change when the population changes.** AA minus DL is {aa.full_raw_difference_pp:.2f} percentage points on the full networks, {aa.raw_common_difference_pp:.2f} on overlapping cells and {aa.adjusted_difference_pp:.2f} after identical pooled weighting of common route/schedule/month strata. Common support retains only {aa.coverage_a_pct:.2f}% of AA and {aa.coverage_b_pct:.2f}% of DL eligible flights ({int(aa.common_n_a):,}/{int(aa.common_n_b):,}). Do not generalize this adjusted result to either whole network. Only {int(mix.comparison_eligible.sum())} of {len(mix)} carrier pairs pass the documented support screens.
5. **Day-level variation is much larger than an independence calculation suggests.** Network on-time performance is {ci.rate_pct:.2f}%; the month-stratified day-cluster 95% model interval is {ci.day_cluster_low_pct:.2f}–{ci.day_cluster_high_pct:.2f}%, versus {ci.iid_wilson_low_pct:.2f}–{ci.iid_wilson_high_pct:.2f}% for the IID reference. These are model-based stability summaries; the observed quarter is already fully counted.
6. **Reported allocations are complete for the specified late-arrival population.** All {eligible:,} late eligible arrivals have five reported cause fields with matching total minutes. Late-arriving aircraft is the largest allocated category; inspect repeat disruption patterns but do not treat the category label as a proven mechanism.

## Recommended investigation sequence

| Priority | Review | Evidence / guardrail |
|---|---|---|
| 1 | Recurrent severe delays at high-volume destinations and routes | Query 13 severity, 15–16 concentration, 22 recurrence; show volume and denominators |
| 2 | DCA and other recurring destination gaps by month, carrier and hour | Query 22 plus query 14/17; distinguish temporal shocks from persistent patterns |
| 3 | Overlapping AA–DL route/schedule cells | Use explicit common-support counts and weights; no whole-network superiority claim |
| 4 | Source follow-up for the cancelled extreme-delay record | Seven unique warnings traced; canonical rows retained, cancelled timeline unresolved |
| 5 | Dashboard preparation | Use validated BI exports, ratio-of-sums measures and separate raw/adjusted views |

## Limits and next evidence

Only one quarter is observed. Whole-day resampling preserves within-day co-movement but not cross-day storm persistence or all route/carrier dependence. Adjusted comparisons use six-hour blocks and pair-specific reference weights; no adjusted confidence interval or causal model is claimed. Multiple comparisons are exploratory. Source event logs would be needed to resolve the cancelled-flight anomaly. No staff, schedule or financial intervention is justified solely by these descriptive patterns.

## Evidence map

- [Extreme records and sensitivity](EXTREME_DELAY_INVESTIGATION.md)
- [Statistical analysis](STATISTICAL_ANALYSIS.md) and [mix adjustment](MIX_ADJUSTMENT_ANALYSIS.md)
- [Delay allocations](DELAY_CAUSE_ANALYSIS.md)
- `session2/sql/13_*.csv` through `22_*.csv`; all 12 Session 1 outputs remain in `queries/`
- `session2/figures/`: six new figures; original four figures remain intact
- [BI data model](../docs/BI_DATA_MODEL.md), [measure dictionary](../docs/BI_MEASURE_DICTIONARY.md)
'''
    (root/'reports/EXECUTIVE_BUSINESS_INSIGHTS.md').write_text(s)
    (out/'REPORT_RUN.json').write_text(json.dumps({'figures':figures,'cause_eligible_records':eligible,'complete_cause_records':complete,'cause_mismatch_records':bad,'late_delay_minutes':minutes,'recurring_airports':len(rec)},indent=2))
    print(json.dumps({'figures':len(figures),'recurring_airports':len(rec),'cause_complete':complete}))
if __name__=='__main__':run()
