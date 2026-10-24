"""AppTest interaction checks; synthetic fixtures never enter deployed data.

Reference: https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest
AppTest is a simulated Streamlit runtime, not browser or deployment verification.
"""
import io
import json
from pathlib import Path
import shutil

import pandas as pd
import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest

from src.dashboard_data import CAUSES, SEVERITIES, sha256

ROOT = Path(__file__).resolve().parents[1]
PAGES = ['Executive Overview', 'Airline Performance', 'Airport Performance',
         'Route Analytics', 'Delay Investigation', 'Cancellations and Delay Causes', 'Business Insights']


@pytest.fixture
def app(tmp_path, monkeypatch):
    """Run a byte-identical app against an explicitly synthetic isolated package."""
    folder = tmp_path / 'deployment/data'
    folder.mkdir(parents=True)
    rows = []
    for i, delay in enumerate([-10, 0, 14, 15, 29, 30, 59, 60, 119, 120, None, 900, 20]):
        rows.append(dict(date=pd.Timestamp('2025-01-01' if i < 7 else '2025-02-01'),
            airline='AA' if i % 2 else 'DL', origin='ATL' if i % 2 else 'LAX',
            destination='LAX' if i % 2 else 'ATL', hour=i, cancelled=int(i in [10,11]),
            diverted=int(i in [11,12]), cancellation_code='A' if i in [10,11] else None,
            arrival_delay=delay, departure_delay=delay,
            **{cause: None if i < 3 else float(i) for cause in CAUSES}))
    pd.DataFrame(rows).to_parquet(folder / 'flights.parquet', index=False)
    (folder / 'manifest.json').write_text(json.dumps(dict(format_version=1, full_population=True,
        rows=13, parquet_sha256=sha256(folder / 'flights.parquet'), test_fixture=True)))
    shutil.copyfile(ROOT / 'app.py', tmp_path / 'app.py')
    (tmp_path / 'reports').symlink_to(ROOT / 'reports', target_is_directory=True)
    downloads = {}
    original = st.download_button
    def capture(label, data, file_name=None, mime=None, **kwargs):
        downloads[label] = (data, file_name, mime)
        return original(label, data, file_name, mime, **kwargs)
    monkeypatch.setattr(st, 'download_button', capture)
    st.cache_resource.clear()
    st.cache_data.clear()
    at = AppTest.from_file(tmp_path / 'app.py', default_timeout=30).run()
    assert not at.exception
    yield at, downloads
    st.cache_resource.clear()
    st.cache_data.clear()


def metrics(at):
    return {m.label: m.value for m in at.metric}


@pytest.mark.parametrize('page', PAGES)
def test_each_page_has_population_and_usable_output(app, page):
    at, downloads = app
    at.radio(key='page').set_value(page).run()
    assert not at.exception
    assert metrics(at)['Reported flights'] == '13'
    assert metrics(at)['Eligible arrivals'] == '10'
    assert metrics(at)['On-time arrivals'] == '30.00%'
    assert any(page in x.value for x in at.markdown)
    assert len(at.get('download_button')) >= 2
    assert all(filename and mime for _, filename, mime in downloads.values())


def test_month_airline_filters_persist_across_every_page(app):
    at, _ = app
    at.multiselect(key='months').set_value(['2025-01']).run()
    at.multiselect(key='airlines').set_value(['AA']).run()
    for page in PAGES:
        at.radio(key='page').set_value(page).run()
        assert not at.exception
        assert at.multiselect(key='months').value == ['2025-01']
        assert at.multiselect(key='airlines').value == ['AA']
        assert metrics(at)['Reported flights'] == '3'
        assert metrics(at)['On-time arrivals'] == '33.33%'


@pytest.mark.parametrize('key', ['months', 'airlines', 'severity'])
def test_empty_selection_stops_without_fabricated_metrics(app, key):
    at, _ = app
    at.multiselect(key=key).set_value([]).run()
    assert not at.exception
    assert not at.metric
    assert any('No flights match' in item.value for item in at.info)
    assert not at.dataframe


def test_dependent_airports_and_route_reset_on_upstream_change(app):
    at, _ = app
    at.selectbox(key='origin').set_value('ATL').run()
    assert at.selectbox(key='destination').options == ['All', 'LAX']
    at.selectbox(key='destination').set_value('LAX').run()
    at.selectbox(key='route').set_value('ATL → LAX').run()
    assert metrics(at)['Reported flights'] == '6'
    at.multiselect(key='airlines').set_value(['DL']).run()
    assert not at.exception
    assert at.selectbox(key='origin').value == 'All'
    assert at.selectbox(key='destination').value == 'All'
    assert at.selectbox(key='route').value == 'All'
    assert at.selectbox(key='origin').options == ['All', 'LAX']
    assert at.selectbox(key='destination').options == ['All', 'ATL']
    assert metrics(at)['Reported flights'] == '7'


def test_reset_restores_entire_population(app):
    at, _ = app
    at.multiselect(key='months').set_value(['2025-02']).run()
    at.multiselect(key='airlines').set_value(['AA']).run()
    at.selectbox(key='origin').set_value('ATL').run()
    at.slider(key='hours').set_value((7, 10)).run()
    at.multiselect(key='severity').set_value(['120+']).run()
    at.number_input(key='minimum').set_value(1).run()
    at.button[0].click().run()
    assert not at.exception
    assert metrics(at)['Reported flights'] == '13'
    assert at.multiselect(key='months').value == ['2025-01','2025-02','2025-03']
    assert at.multiselect(key='airlines').value == ['AA','DL']
    assert at.multiselect(key='severity').value == list(SEVERITIES)
    assert at.slider(key='hours').value == (0,23)
    assert at.number_input(key='minimum').value == 1000
    assert all(at.selectbox(key=k).value == 'All' for k in ['origin','destination','route'])


def test_ineligible_population_has_unavailable_arrival_rates(app):
    at, _ = app
    at.multiselect(key='severity').set_value(['Ineligible']).run()
    assert not at.exception
    result = metrics(at)
    assert result['Reported flights'] == '3'
    assert result['Eligible arrivals'] == '0'
    for label in ['On-time arrivals', 'Delayed arrivals', 'Mean arrival delay', 'Mean late-arrival delay']:
        assert result[label] == 'Not available'
    assert result['Cancellation rate'] == '66.67%'
    assert at.warning


def test_route_volume_threshold_changes_ranking_not_headlines(app):
    at, _ = app
    at.radio(key='page').set_value('Route Analytics').run()
    baseline = metrics(at)
    assert at.dataframe[0].value.empty
    at.number_input(key='minimum').set_value(1).run()
    assert not at.exception
    assert set(at.dataframe[0].value.route) == {'ATL → LAX','LAX → ATL'}
    assert metrics(at) == baseline
    at.number_input(key='minimum').set_value(6).run()
    assert at.dataframe[0].value.empty
    assert metrics(at) == baseline


def test_csv_payload_is_exact_displayed_table_with_filter_context(app):
    at, downloads = app
    at.multiselect(key='months').set_value(['2025-01']).run()
    at.multiselect(key='airlines').set_value(['AA']).run()
    raw, filename, mime = downloads['Download monthly overview CSV']
    assert filename == 'aeropulse_monthly_overview.csv' and mime == 'text/csv'
    assert raw.startswith(b'\xef\xbb\xbf')
    exported = pd.read_csv(io.BytesIO(raw), encoding='utf-8-sig')
    context = exported.pop('population_filters_json').map(json.loads)
    pd.testing.assert_frame_equal(exported, at.dataframe[0].value, check_dtype=False)
    assert exported.reported_flights.tolist() == [3]
    assert exported.on_time_pct.tolist() == pytest.approx([100/3])
    assert context.iloc[0]['month'] == ['2025-01']
    assert context.iloc[0]['airline'] == ['AA']
    assert json.loads(downloads['Download filter context'][0]) == context.iloc[0]


@pytest.mark.integration
def test_authentic_app_all_pages_baseline():
    if not (ROOT / 'deployment/data/manifest.json').exists():
        pytest.skip('authentic deployment package unavailable')
    st.cache_resource.clear()
    st.cache_data.clear()
    at = AppTest.from_file(ROOT / 'app.py', default_timeout=90).run()
    try:
        for page in PAGES:
            at.radio(key='page').set_value(page).run()
            assert not at.exception
            assert metrics(at)['Reported flights'] == '1,645,503'
            assert len(at.get('download_button')) >= 2
    finally:
        st.cache_resource.clear()
        st.cache_data.clear()


def test_single_month_chart_uses_categorical_axis(app):
    at, _ = app
    at.multiselect(key='months').set_value(['2025-01']).run()
    charts = at.get('plotly_chart')
    assert len(charts) == 3
    for chart in charts[:2]:
        spec = json.loads(chart.proto.spec)
        assert spec['layout']['xaxis']['type'] == 'category'
    assert json.loads(charts[1].proto.spec)['layout']['yaxis']['title']['text'] == 'Delayed arrivals (%)'
