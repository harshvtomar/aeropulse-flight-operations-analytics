"""AeroPulse interactive reporting over complete, verified BTS flight records."""
from dataclasses import asdict
from pathlib import Path
import json
import pandas as pd
import plotly.express as px
import streamlit as st
from src.dashboard_data import DashboardData, Filters, SEVERITIES

ROOT = Path(__file__).resolve().parent
PAGES = ['Executive Overview', 'Airline Performance', 'Airport Performance', 'Route Analytics',
         'Delay Investigation', 'Cancellations and Delay Causes', 'Business Insights']
st.set_page_config(page_title='AeroPulse | Flight Operations', page_icon='✈', layout='wide')
st.markdown('''<style>
.block-container{max-width:1480px;padding-top:4rem;padding-bottom:3rem}
h1,h2,h3{letter-spacing:-.025em}[data-testid="stMetric"]{border:1px solid #dce5ef;border-radius:12px;padding:14px;background:#fff}
[data-testid="stMetricValue"]{font-variant-numeric:tabular-nums;font-size:1.9rem}
[data-testid="stSidebar"]{background:#f1f5fa}.eyebrow{font-size:.75rem;letter-spacing:.18em;color:#1965a8;font-weight:700}
.hero{border-bottom:1px solid #dce5ef;margin-bottom:1rem;padding-bottom:1rem}.hero h1{margin-bottom:0}.hero p{color:#55677c}
@media(max-width:700px){.block-container{padding:4rem 1rem 1rem}.hero h1{font-size:2rem}}
</style>''', unsafe_allow_html=True)


@st.cache_resource(max_entries=1)
def load_data(stamp, backend_class_identity):
    return DashboardData(ROOT / 'deployment/data')


try:
    # A hot deployment may reload the backend module; never reuse an old-class handle.
    data = load_data((ROOT / 'deployment/data/manifest.json').stat().st_mtime_ns, id(DashboardData))
except (OSError, ValueError) as exc:
    st.error('The verified reporting package is unavailable. No sample data is substituted.')
    st.code('python -m src.build_dashboard_data')
    st.caption(str(exc))
    st.stop()


@st.cache_data(max_entries=128, show_spinner=False)
def query(kind, group, values, package_hash):
    selected = Filters(**dict(values))
    return data.group_metrics(group, selected) if kind == 'group' else getattr(data, kind)(selected)


def q(kind, selected, group=None):
    values = tuple((k, None if v is None else tuple(v)) for k, v in asdict(selected).items())
    return query(kind, group, values, data.manifest['parquet_sha256'])


def reset_filters():
    # Explicit values synchronize existing browser widgets as well as Python state.
    defaults = dict(months=['2025-01', '2025-02', '2025-03'],
                    airlines=data.options('airline'), origin='All', destination='All',
                    route='All', hours=(0, 23), severity=list(SEVERITIES), minimum=1000)
    for key, value in defaults.items():
        st.session_state[key] = value


def cascade(label, key, options):
    options = ['All'] + options
    if st.session_state.get(key, 'All') not in options:
        st.session_state[key] = 'All'
    value = st.selectbox(label, options, key=key)
    return None if value == 'All' else [value]


with st.sidebar:
    st.markdown('### AeroPulse')
    st.caption('AIRLINE OPERATIONS / Q1 2025')
    page = st.radio('Explore', PAGES, key='page', label_visibility='collapsed')
    st.divider()
    st.subheader('Analysis population')
    st.button('Reset filters', on_click=reset_filters, width='stretch')
    months = st.multiselect('Months', ['2025-01', '2025-02', '2025-03'], default=['2025-01', '2025-02', '2025-03'], key='months')
    options = data.options('airline', Filters(month=months))
    if 'airlines' in st.session_state:
        st.session_state.airlines = [x for x in st.session_state.airlines if x in options]
    airlines = st.multiselect('Reporting airlines', options, default=options, key='airlines')
    origin = cascade('Origin airport', 'origin', data.options('origin', Filters(month=months, airline=airlines)))
    destination = cascade('Destination airport', 'destination', data.options('destination', Filters(month=months, airline=airlines, origin=origin)))
    route = cascade('Directed route', 'route', data.options('route', Filters(month=months, airline=airlines, origin=origin, destination=destination)))
    hours = st.slider('Scheduled local departure hours', 0, 23, (0, 23), key='hours')
    severity = st.multiselect('Arrival severity / eligibility', list(SEVERITIES), default=list(SEVERITIES), key='severity')
    minimum = st.number_input('Minimum eligible flights in rankings', min_value=1, max_value=1000000, value=1000, step=100, key='minimum')
    st.caption('The volume screen affects rankings only. Empty month, airline or severity selections mean no matching flights. Airport and route choices follow selections above.')

f = Filters(month=months, airline=airlines, origin=origin, destination=destination, route=route,
            hour=list(range(hours[0], hours[1] + 1)), severity=severity)
context = json.dumps(asdict(f), ensure_ascii=False, sort_keys=True)
k = q('get_kpis', f)
st.markdown(f'<div class="hero"><div class="eyebrow">AEROPULSE INTELLIGENCE</div><h1>{page}</h1><p>Airline operations, flight delay and network performance</p></div>', unsafe_allow_html=True)
st.caption('US DOT / Bureau of Transportation Statistics · Reporting carriers · January–March 2025 · Complete records, never sampled')
with st.expander('Selected population and KPI definitions'):
    st.write(f"{k['reported_flights']:,} reported flights match the filters; {k['eligible_flights']:,} qualify for arrival analysis.")
    st.write('Eligible arrivals are not cancelled or diverted and have a known arrival delay. On time means less than 15 minutes late, including early arrivals. Cancellation and diversion rates use all selected reported flights. Statuses may overlap. Severity selection changes the population and every denominator.')
    st.json(asdict(f))
    st.download_button('Download filter context', context, 'aeropulse_filter_context.json', 'application/json')
if set(severity) != set(SEVERITIES):
    st.warning('Severity filter is active. Rates describe this restricted population. Ineligible includes cancelled, diverted and missing-delay records.')
if k['reported_flights'] == 0:
    st.info('No flights match these selections. Reset filters or broaden the population.')
    st.stop()


def fmt(value, unit=''):
    if value is None or pd.isna(value):
        return 'Not available'
    return f'{value:,.2f}{unit}' if unit else f'{value:,.0f}'


def headline():
    cards = [('Reported flights', 'reported_flights', '', 'All source rows matching every filter.'),
             ('Eligible arrivals', 'eligible_flights', '', 'Not cancelled or diverted; known arrival delay.'),
             ('On-time arrivals', 'on_time_pct', '%', 'Arrivals <15 minutes late / eligible arrivals.'),
             ('Delayed arrivals', 'late_pct', '%', 'Arrivals ≥15 minutes late / eligible arrivals.'),
             ('Cancellation rate', 'cancellation_pct', '%', 'Cancelled / all selected reported flights.'),
             ('Diversion rate', 'diversion_pct', '%', 'Diverted / all selected reported flights.'),
             ('Mean arrival delay', 'avg_arrival_delay_minutes', ' min', 'Signed mean across eligible arrivals.'),
             ('Mean late-arrival delay', 'avg_late_arrival_delay_minutes', ' min', 'Mean among arrivals ≥15 minutes late.')]
    for offset in [0, 4]:
        for col, (label, key, unit, helptext) in zip(st.columns(4), cards[offset:offset + 4]):
            col.metric(label, fmt(k[key], unit), help=helptext)


def chart(frame, x, y, title, line=False, color=None):
    if frame.empty or not frame[y].notna().any():
        st.info('No eligible values for ' + title.lower() + '.')
        return
    kwargs = dict(data_frame=frame, x=x, y=y, color=color, title=title,
                  labels={x: x.replace('_', ' ').title(), y: {'late_pct': 'Delayed arrivals (%)', 'on_time_pct': 'On-time arrivals (%)', 'cancellation_pct': 'Cancellation rate (%)', 'reported_flights': 'Reported flights', 'late_flights': 'Delayed arrivals', 'reported_minutes': 'Reported delay minutes'}.get(y, y.replace('_', ' ').title())},
                  color_discrete_sequence=['#1965A8', '#008779', '#D97724', '#9467bd', '#65758b'])
    fig = px.line(**kwargs, markers=True) if line else px.bar(**kwargs)
    fig.update_layout(template='plotly_white', font=dict(family='Arial', size=13, color='#20344b'),
                      margin=dict(l=8, r=16, t=55, b=12), height=380, legend_title_text='')
    if x not in {'date', 'hour'}:
        fig.update_xaxes(type='category')
    if y.endswith('_pct'):
        fig.update_yaxes(ticksuffix='%', rangemode='tozero')
    st.plotly_chart(fig, width='stretch', config={'displaylogo': False})


def table(frame, name):
    st.dataframe(frame, width='stretch', hide_index=True)
    exported = frame.copy()
    exported['population_filters_json'] = context
    st.download_button('Download ' + name + ' CSV', exported.to_csv(index=False).encode('utf-8-sig'),
                       'aeropulse_' + name.replace(' ', '_') + '.csv', 'text/csv', key='download_' + name)
    st.caption('CSV includes exact filter context. Rates use 0–100 percentage units; missing values remain empty.')


def ranking(group, name):
    frame = q('group', f, group)
    screen = frame[frame.eligible_flights >= minimum].sort_values(['late_pct', group], ascending=[False, True])
    st.caption(f'At least {minimum:,} eligible arrivals required in the selected population: {len(screen):,} of {len(frame):,} groups qualify. Raw rates and sample sizes do not establish causal quality.')
    if len(screen):
        chart(screen.head(15), group, 'late_pct', name.title() + ': highest arrival-delay rates')
    else:
        st.info('No groups meet the volume screen. Lower the threshold to explore smaller samples.')
    table(screen, name + ' ranking')
    return frame


headline()
if page == 'Executive Overview':
    monthly = q('group', f, 'month')
    cols = st.columns(2)
    with cols[0]:
        chart(monthly, 'month', 'reported_flights', 'Monthly flight volume')
        normalized = monthly.copy()
        normalized['calendar_days'] = pd.to_datetime(normalized.month + '-01').dt.days_in_month
        normalized['reported_flights_per_calendar_day'] = normalized.reported_flights / normalized.calendar_days
        st.caption('Month lengths differ: January 31 days, February 28, March 31. Compare daily-normalized volumes in the download.')
    with cols[1]:
        chart(monthly, 'month', 'late_pct', 'Monthly arrival-delay rate', line=True)
    chart(q('group', f, 'date'), 'date', 'reported_flights', 'Daily reported flight volume', line=True)
    table(normalized, 'monthly overview')
    st.subheader('Investigation priorities')
    st.write('Locate severe-delay concentrations, compare rates with flight volumes, and review common-support limits before interpreting airline differences. These priorities guide investigation; they do not estimate realized improvements.')
elif page == 'Airline Performance':
    ranking('airline', 'airline')
    chart(q('group', f, ('month', 'airline')), 'month', 'on_time_pct', 'Airline on-time trends', line=True, color='airline')
    chart(q('severity_metrics', f), 'severity', 'reported_flights', 'Selected airlines: arrival severity')
    with st.expander('Raw versus mix-adjusted comparisons — fixed Q1 study'):
        st.warning('This study uses the original full-quarter populations. Dashboard filters do not recalculate reference weights or intervals.')
        mix = pd.read_csv(ROOT / 'reports/session2/mix_adjusted_pairs.csv')
        st.dataframe(mix.loc[mix.comparison_eligible, ['airline_a', 'airline_b', 'full_raw_difference_pp', 'raw_common_difference_pp', 'adjusted_difference_pp', 'common_n_a', 'common_n_b', 'coverage_a_pct', 'coverage_b_pct']], hide_index=True, width='stretch')
        st.caption('Only 4 of 91 pairs pass support screens. Pair-specific adjusted point estimates cannot form a common-reference leaderboard. No adjusted interval or causal superiority is claimed.')
elif page == 'Airport Performance':
    role = st.radio('Airport role', ['Destination', 'Origin'], horizontal=True, key='airport_role')
    group = role.lower()
    airports = ranking(group, group + ' airport')
    chart(airports.sort_values('late_flights', ascending=False).head(15), group, 'late_flights', 'Largest delayed-arrival concentrations')
    airport_months = q('group', f, ('month', group))
    table(airport_months, 'monthly airport performance')
    reference = q('group', f, 'month')[['month', 'late_pct']].rename(columns={'late_pct': 'selected_network_late_pct'})
    stability = airport_months.merge(reference, on='month', validate='many_to_one')
    stability['above_network'] = (stability.late_pct > stability.selected_network_late_pct) & (stability.eligible_flights >= minimum)
    recurring = stability.groupby(group).agg(months_observed=('month', 'nunique'), months_above_network=('above_network', 'sum'), eligible_flights=('eligible_flights', 'sum'), late_flights=('late_flights', 'sum')).reset_index()
    recurring = recurring[(recurring.months_observed == len(months)) & (recurring.months_above_network == len(months))].sort_values('late_flights', ascending=False)
    st.subheader('Recurring above-network delay rates')
    st.caption('Each selected month must exceed the same-month selected-network delay rate and meet the volume screen. Airport filters also restrict the reference population; selecting one airport yields no relative comparison.')
    table(recurring, 'recurring airport patterns')
    st.caption('Origin and destination are separate roles. This attribution does not establish airport responsibility. No coordinates are assumed.')
elif page == 'Route Analytics':
    ranking('route', 'directed route')
    st.caption('Choose a directed route in the sidebar for its trend and severity. All summarizes the selected network.')
    chart(q('group', f, 'month'), 'month', 'on_time_pct', 'Selected route population: on-time trend', line=True)
    table(q('severity_metrics', f), 'route severity')
elif page == 'Delay Investigation':
    sev = q('severity_metrics', f)
    sev = sev.assign(_order=sev.severity.map({name: i for i, name in enumerate(SEVERITIES)})).sort_values('_order').drop(columns='_order')
    delayed = sev[sev.severity.isin(['15–29', '30–59', '60–119', '120+'])]
    cols = st.columns(2)
    with cols[0]:
        chart(delayed, 'severity', 'late_flights', 'Delayed arrivals by severity')
    with cols[1]:
        chart(delayed, 'severity', 'signed_arrival_delay_minutes', 'Arrival-delay minutes by severity')
    table(sev, 'delay severity')
    severe_f = Filters(**{**asdict(f), 'severity': [x for x in f.severity if x == '120+']})
    st.subheader('Routes contributing most 120+ minute arrivals')
    table(q('group', severe_f, 'route').sort_values('late_flights', ascending=False).head(20), 'severe delay routes')
    with st.expander('Extreme records and sensitivity — fixed Q1 study'):
        st.write('Seven original records triggered five arrival and seven departure warnings. Six completed flights are internally consistent outliers, externally unconfirmed. Cancelled AA1115 MCI–ORD on January 15 remains unresolved. Original records are retained.')
        st.caption('These sensitivity scenarios describe the original full quarter and do not follow dashboard filters.')
        st.dataframe(pd.read_csv(ROOT / 'reports/session2/extreme_sensitivity.csv'), hide_index=True)
        st.download_button('Download extreme-delay investigation', (ROOT / 'reports/EXTREME_DELAY_INVESTIGATION.md').read_bytes(), 'AeroPulse_Extreme_Delay_Investigation.md', 'text/markdown')
elif page == 'Cancellations and Delay Causes':
    chart(q('group', f, 'month'), 'month', 'cancellation_pct', 'Cancellation rate by month', line=True)
    reasons = q('cancellation_metrics', f)
    reasons['reported_reason'] = reasons.cancellation_code.map({'A': 'Carrier', 'B': 'Weather', 'C': 'National Aviation System', 'D': 'Security', 'Unknown': 'Unknown'}).fillna(reasons.cancellation_code)
    st.subheader('Cancellation reasons')
    st.caption('Reason counts include cancelled records only. Headline rates use all selected reported flights.')
    table(reasons, 'cancellation reasons')
    causes = q('cause_metrics', f)
    causes['late_coverage_pct'] = causes.late_records_with_value.div(causes.late_flights.replace(0, float('nan'))) * 100
    chart(causes, 'cause', 'reported_minutes', 'Source-reported delay allocations')
    st.caption('Allocations are not independently established root causes. Missing values are not zero. Coverage uses late eligible arrivals, repeated per category; do not sum denominators across categories.')
    table(causes, 'reported delay causes')
else:
    st.subheader('Full-quarter evidence and recommendations')
    st.info('The study below covers the complete quarter. Findings and statistical intervals are fixed and do not follow sidebar filters; the cards above describe the selected population.')
    report = (ROOT / 'reports/EXECUTIVE_BUSINESS_INSIGHTS.md').read_text()
    st.markdown(report.split('## Decision-relevant findings', 1)[1].split('## Evidence map', 1)[0])
    st.download_button('Download executive summary', report, 'AeroPulse_Executive_Summary.md', 'text/markdown')
    excel = ROOT / 'reports/session3/excel/AeroPulse_Airline_Operations_Business_Report.xlsx'
    if excel.exists():
        st.download_button('Download Excel business report', excel.read_bytes(), excel.name, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    st.link_button('Source code, methodology and verification', 'https://github.com/harshvtomar/aeropulse-flight-operations-analytics')
    st.caption('Native Power BI execution remains unverified; see the repository Windows handoff.')
st.divider()
st.caption('AeroPulse Intelligence · Official BTS reporting-carrier records · Descriptive analysis · Q1 2025')
