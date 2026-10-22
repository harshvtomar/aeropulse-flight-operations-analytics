import json
from pathlib import Path
import duckdb
import pytest
from src.metrics import reconcile

@pytest.mark.integration
def test_real_quarter():
    root=Path(__file__).resolve().parents[1]
    if not (root/'data/aeropulse.duckdb').exists(): pytest.skip('Run official-data pipeline before integration check')
    manifests=[json.loads((root/f'data/processed/2025-{m:02}/manifest.json').read_text()) for m in [1,2,3]]
    assert all(x['source_rows']>0 and x['source_rows']==x['accepted_rows']+x['quarantined_rows'] for x in manifests)
    with duckdb.connect(str(root/'data/aeropulse.duckdb'),read_only=True) as c:
        assert c.execute('select count(*) from fact_flights').fetchone()[0]==sum(x['accepted_rows'] for x in manifests)
        assert c.execute('select count(distinct Month) from fact_flights').fetchone()[0]==3
    assert reconcile(root)['passed']
