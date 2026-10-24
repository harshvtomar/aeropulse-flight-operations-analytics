"""Contract checks only: these cannot execute M, DAX, or native report visuals."""
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('powerbi_build', ROOT / 'powerbi/build_package.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


def test_reproducible_queries_and_contract(tmp_path):
    manifest = json.loads((ROOT / 'reports/session2/BI_EXPORT_VALIDATION.json').read_text())
    build.generate(manifest, tmp_path)
    for generated in tmp_path.rglob('*'):
        if generated.is_file():
            assert generated.read_bytes() == (ROOT / 'powerbi' / generated.relative_to(tmp_path)).read_bytes()
    contract = json.loads((tmp_path / 'model_contract.json').read_text())
    assert len(contract['tables']) == 7
    assert len(contract['relationships']) == 6
    names = {t['name']: {c['name'] for c in t['columns']} for t in contract['tables']}
    for relation in contract['relationships']:
        assert relation['one_column'] in names[relation['one_table']]
        assert relation['many_column'] in names['fact_flights']
        assert relation['active'] and relation['cross_filter'] == 'Single'
    assert set(names) == {'fact_flights', *build.KEYS}


def test_unrecognized_types_fail_instead_of_inferred_conversion(tmp_path):
    manifest = {'inventory': [{'file': 'fact_flights.parquet', 'columns': [{'name': 'id', 'type': 'UNKNOWN'}]}]}
    with pytest.raises(KeyError):
        build.generate(manifest, tmp_path)


def test_preserves_canonical_measures_and_null_semantics():
    measures = (ROOT / 'powerbi/measures.dax').read_text()
    assert measures.startswith((ROOT / 'docs/POWER_BI_MEASURES.dax').read_text())
    for category in ('Carrier', 'Weather', 'NAS', 'Security', 'Late Aircraft'):
        assert f'{category} Cause Late Coverage = DIVIDE([{category} Cause Reported Late Records], [Late Arrivals])' in measures
    assert 'COALESCE(SUM(fact_flights[CarrierDelay])' not in measures


@pytest.mark.integration
def test_relationship_contract_against_export_when_available():
    path = ROOT / 'data/bi/fact_flights.parquet'
    if not path.exists():
        pytest.skip('Regenerate BI exports to run real data relationship check')
    import duckdb
    con = duckdb.connect()
    for table, key in build.KEYS.items():
        dimension = str(ROOT / 'data/bi' / (table + '.csv'))
        assert con.execute(f'SELECT count(*)=count(DISTINCT {key}) AND count(*)=count({key}) FROM read_csv_auto(?)', [dimension]).fetchone()[0]
        assert con.execute(f'SELECT count(*) FROM read_parquet(?) f LEFT JOIN read_csv_auto(?) d ON f.{key}=d.{key} WHERE d.{key} IS NULL', [str(path), dimension]).fetchone()[0] == 0
    con.close()


@pytest.mark.integration
def test_native_reference_matches_export_when_available():
    if not (ROOT / 'data/bi/fact_flights.parquet').exists():
        pytest.skip('Regenerate BI exports for SQL reference check')
    import duckdb
    sql = (ROOT / 'powerbi/native_validation.sql').read_text().replace("'data/bi/fact_flights.parquet'", "'" + str(ROOT / 'data/bi/fact_flights.parquet') + "'")
    con = duckdb.connect()
    result = con.execute(sql)
    names = [column[0] for column in result.description]
    cases = [dict(zip(names, row)) for row in result.fetchall()]
    expected = json.loads((ROOT / 'powerbi/native_validation_expected.json').read_text())['cases']
    assert json.loads(json.dumps(cases, default=float)) == expected
    assert all(case['reported_flights'] > 0 for case in cases)
    con.close()
