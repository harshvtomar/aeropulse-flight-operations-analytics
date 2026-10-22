"""Run all versioned SQL, export actual results, and render initial EDA."""
import json
from pathlib import Path
import duckdb
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .warehouse import CODE_ROOT
from .metrics import reconcile
from .reporting import quality_report

def run(root='.'):
    root=Path(root);out=root/'reports';(out/'queries').mkdir(parents=True,exist_ok=True);(out/'figures').mkdir(exist_ok=True)
    results={}
    with duckdb.connect(str(root/'data/aeropulse.duckdb'),read_only=True) as con:
        for p in sorted((CODE_ROOT/'sql/queries').glob('*.sql')):
            df=con.execute(p.read_text()).df();df.to_csv(out/'queries'/f'{p.stem}.csv',index=False)
            results[p.stem]=df
        table_counts={t:con.execute(f'SELECT count(*) FROM {t}').fetchone()[0] for t in ['fact_flights','dim_airlines','dim_airports','dim_dates','data_quality_audit']}
    recon=reconcile(root)
    quality_report(root)
    plt.rcParams.update({'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False,'axes.titleweight':'bold','axes.labelcolor':'#24354b','text.color':'#24354b','figure.facecolor':'#f8fafc','axes.facecolor':'#f8fafc'})
    def save(fig,name):
        fig.text(.02,.015,'Source: US DOT / BTS reporting-carrier records • Jan–Mar 2025 • AeroPulse Intelligence',fontsize=8,color='#536477')
        fig.tight_layout(rect=[0,.05,1,1]);fig.savefig(out/'figures'/f'{name}.png',dpi=160);plt.close(fig)
    m=results['06_monthly'];fig,ax=plt.subplots(1,2,figsize=(11,4.8));labels=['Jan','Feb','Mar'] if len(m)==3 and m.Month.tolist()==[1,2,3] else m.Month.astype(str)
    ax[0].bar(labels,m.reported_flights/1000,color='#167b91');ax[0].set(title='Reported flight volume',ylabel='Flights (thousands)')
    ax[1].plot(labels,100-m.on_time_pct,marker='o',color='#d27935',linewidth=2);ax[1].set(title='Arrival delay rate (15+ minutes)',ylabel='% of eligible arrivals',ylim=(0,max(30,(100-m.on_time_pct).max()*1.2)))
    save(fig,'01_monthly')
    a=results['02_airlines'].sort_values('on_time_pct');fig,ax=plt.subplots(figsize=(10,6))
    ax.barh(a.Reporting_Airline,a.on_time_pct,color='#167b91');ax.set(title='Reporting-carrier on-time arrival performance',xlabel='% of eligible arrivals (<15 minutes late)',xlim=(0,100))
    for i,(_,r) in enumerate(a.iterrows()): ax.text(r.on_time_pct+.5,i,f'{r.on_time_pct:.1f}% · n={r.eligible_flights:,.0f}',va='center',fontsize=8)
    save(fig,'02_airlines')
    a=results['04_destination_airports'].head(10).sort_values('on_time_pct');fig,ax=plt.subplots(figsize=(10,5.8))
    ax.barh(a.Dest,a.on_time_pct,color='#167b91');ax.set(title='Arrival reliability at the 10 busiest destinations',xlabel='% of eligible arrivals (<15 minutes late)',xlim=(0,100))
    for i,(_,r) in enumerate(a.iterrows()): ax.text(r.on_time_pct+.5,i,f'{r.on_time_pct:.1f}%',va='center',fontsize=9)
    save(fig,'03_airports')
    a=results['11_delay_causes'].sort_values('reported_minutes');fig,ax=plt.subplots(figsize=(10,5))
    ax.barh(a.reported_cause,a.reported_minutes/1e6,color='#d27935');ax.set(title='Reported delay-cause minutes',xlabel='Allocated minutes (millions); missing values excluded')
    save(fig,'04_delay_causes')
    k=recon['kpis'];best=results['02_airlines'].sort_values('on_time_pct',ascending=False).iloc[0];worst=results['02_airlines'].sort_values('on_time_pct').iloc[0]
    leading=results['11_delay_causes'].sort_values('reported_minutes',ascending=False).iloc[0]
    findings=f'''# Initial business findings — Session 1

Coverage: complete downloaded BTS reporting-carrier monthly archives for January–March 2025. This is a US domestic reporting-carrier population, not every flight worldwide or every US operation.

- Reported flights: **{k['reported_flights']:,.0f}**; eligible normal arrivals with a reported delay: **{k['eligible_flights']:,.0f}**.
- **{k['on_time_pct']:.2f}%** of eligible arrivals were under 15 minutes late; **{k['late_pct']:.2f}%** were at least 15 minutes late.
- **{k['cancelled_flights']:,.0f} cancellations ({k['cancellation_pct']:.2f}%)** and **{k['diverted_flights']:,.0f} diversions ({k['diversion_pct']:.2f}%)**, each using all reported flights as denominator.
- Mean arrival delay across eligible flights was **{k['avg_arrival_delay_minutes']:.2f} minutes**, preserving early arrivals. Among arrivals at least 15 minutes late, mean delay was **{k['avg_late_arrival_delay_minutes']:.2f} minutes**. The overall mean masks a long late-arrival tail.
- Within this quarter, reporting carrier **{best.Reporting_Airline}** had the highest unadjusted on-time rate (**{best.on_time_pct:.2f}%**, n={best.eligible_flights:,.0f}); **{worst.Reporting_Airline}** had the lowest (**{worst.on_time_pct:.2f}%**, n={worst.eligible_flights:,.0f}). This is descriptive, not a fair causal ranking: schedules, routes and operating conditions differ.
- **{leading.reported_cause}** accounted for the largest sum of reported cause minutes (**{leading.reported_minutes:,.0f} minutes**). These are reported allocations, not independent proof of underlying root causes.

## Business use and next investigation
Use route and airline-origin tables to shortlist recurrent reliability problems. Route rankings require at least 1,000 eligible arrivals; airline-origin comparisons require 500. Examine monthly stability and route/schedule mix before recommending operational action. Do not infer cost savings from these data.

## Evidence and reproduction
All values above derive from `reports/queries/01_overall.csv`, `02_airlines.csv` and `11_delay_causes.csv`. The 12 executable SQL exports are in `reports/queries/`. `KPI_RECONCILIATION.json` records {recon['numeric_comparisons']:,} independent SQL/Python numeric comparisons. Four figures are in `reports/figures/`.

## Resume-safe description
Built a Python–DuckDB analytics foundation processing {k['reported_flights']:,.0f} authentic BTS flight records, with auditable monthly imports, 12 SQL analyses and independently reconciled reliability KPIs. No financial impact or deployed dashboard is claimed.
'''
    (out/'INITIAL_BUSINESS_FINDINGS.md').write_text(findings)
    (out/'ANALYSIS_RUN.json').write_text(json.dumps({'query_count':len(results),'query_rows':{k:len(v) for k,v in results.items()},'tables':table_counts,'figures':4},indent=2))
    print(json.dumps({'tables':table_counts,'queries':len(results),'figures':4}))
if __name__=='__main__':run()
