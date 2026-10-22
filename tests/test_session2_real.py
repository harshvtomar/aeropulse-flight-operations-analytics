"""Authentic-data checks, deliberately excluded from offline hosted CI."""
from pathlib import Path
import json
import duckdb
import pytest
from src import advanced_sql, bi_export

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.integration


@pytest.fixture
def real_root():
    if not (ROOT / 'data/aeropulse.duckdb').exists():
        pytest.skip('Import official quarter and build warehouse first')
    return ROOT


def test_advanced_sql_against_real_parquet(real_root):
    result = advanced_sql.run(real_root)
    assert result['passed'] and result['query_count'] == 10
    assert result['source_rows'] == 1645503


def test_real_bi_roundtrip(real_root):
    result = bi_export.export(real_root)
    assert result['passed'] and result['checks_passed'] == 32
    assert result['source_rows'] == 1645503


def test_real_severity_and_cause_populations(real_root):
    with duckdb.connect(str(real_root / 'data/aeropulse.duckdb'), read_only=True) as con:
        counts = con.execute('''SELECT count(*) FILTER (WHERE ArrDelay>=15),
            count(*) FILTER (WHERE ArrDelay>=120),
            sum(ArrDelay) FILTER (WHERE ArrDelay>=15)
            FROM fact_flights WHERE Cancelled=0 AND Diverted=0 AND ArrDelay IS NOT NULL''').fetchone()
    assert counts == (317266, 45759, 22733373)
