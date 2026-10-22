"""Rebuild a queryable warehouse atomically from verified month bundles."""
import argparse
import json
from pathlib import Path
import duckdb
import pandas as pd
from .ingest import sha256

CODE_ROOT=Path(__file__).resolve().parents[1]

def build(root='.'):
    root=Path(root); paths=sorted((root/'data/processed').glob('*/manifest.json'))
    if not paths: raise ValueError('No imported months; run python -m src.ingest first')
    audits=[];files=[]
    for p in paths:
        m=json.loads(p.read_text())
        for name,h in m['artifact_sha256'].items():
            if sha256(p.parent/name)!=h: raise ValueError('Processed artifact checksum mismatch: '+name)
        audits.append({k:m[k] for k in ['month','source_sha256','source_rows','accepted_rows','quarantined_rows']})
        files.append(str(p.parent/'flights.parquet'))
    dest=root/'data/aeropulse.duckdb';temp=dest.with_suffix('.building.duckdb')
    temp.unlink(missing_ok=True)
    try:
        with duckdb.connect(str(temp)) as con:
            con.execute('CREATE TABLE fact_flights AS SELECT * FROM read_parquet(?)',[files])
            con.execute((CODE_ROOT/'sql/schema.sql').read_text())
            audit=pd.DataFrame(audits)
            con.register('audit',audit)
            con.execute('CREATE TABLE data_quality_audit AS SELECT * FROM audit')
            actual=con.execute('SELECT count(*) FROM fact_flights').fetchone()[0]
            if actual!=sum(a['accepted_rows'] for a in audits): raise ValueError('Warehouse row reconciliation failed')
            if any(a['source_rows']!=a['accepted_rows']+a['quarantined_rows'] for a in audits): raise ValueError('Raw reconciliation failed')
            con.execute('CHECKPOINT')
        temp.replace(dest)
    finally:
        temp.unlink(missing_ok=True)
    return dest

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',default='.');a=p.parse_args();print(build(a.root))
