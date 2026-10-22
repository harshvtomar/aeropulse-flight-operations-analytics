"""Immutable month bundles, checksum audit, explicit revision rejection."""
import argparse
import hashlib
import json
import shutil
import tempfile
import urllib.request
import zipfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
from .validate import validate

BASE = 'https://www.transtats.bts.gov/PREZIP/'

def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def filename(month):
    y,m=map(int,month.split('-'))
    if not 1<=m<=12: raise ValueError('Invalid month')
    return f'On_Time_Reporting_Carrier_On_Time_Performance_1987_present_{y}_{m}.zip'

@contextmanager
def csv_stream(path):
    if path.suffix.lower()=='.zip':
        with zipfile.ZipFile(path) as z:
            candidates=[n for n in z.namelist() if n.lower().endswith('.csv')]
            if len(candidates)!=1: raise ValueError('ZIP must contain exactly one CSV')
            with z.open(candidates[0]) as f: yield f,candidates[0]
    elif path.suffix.lower()=='.csv':
        with path.open('rb') as f: yield f,path.name
    else: raise ValueError('Expected official .zip or .csv file')

def download(month, raw):
    raw=Path(raw); raw.mkdir(parents=True,exist_ok=True)
    dest=raw/filename(month)
    if dest.exists():
        if not zipfile.is_zipfile(dest): raise ValueError(f'Invalid existing ZIP: {dest}')
        return dest
    temp=dest.with_suffix('.part')
    try:
        with urllib.request.urlopen(BASE+dest.name,timeout=120) as response, temp.open('wb') as f:
            shutil.copyfileobj(response,f)
        if not zipfile.is_zipfile(temp): raise ValueError('Official source did not return ZIP; download manually')
        temp.replace(dest)
    finally:
        temp.unlink(missing_ok=True)
    return dest

def ingest(path, month, root='.', source_url=None):
    path=Path(path);root=Path(root)
    if not path.is_file(): raise FileNotFoundError(f'Missing official input: {path}')
    filename(month)
    digest=sha256(path)
    parent=root/'data/processed';parent.mkdir(parents=True,exist_ok=True)
    target=parent/month
    if target.exists():
        manifest=json.loads((target/'manifest.json').read_text())
        if manifest['source_sha256']!=digest: raise ValueError('Month already imported with different checksum; investigate source revision before replacing')
        for name,h in manifest['artifact_sha256'].items():
            if sha256(target/name)!=h: raise ValueError('Processed artifact checksum mismatch: '+name)
        out=root/'data/manifests';out.mkdir(parents=True,exist_ok=True)
        shutil.copy2(target/'manifest.json',out/f'{month}.json')
        return {**manifest,'rerun':'unchanged'}
    with csv_stream(path) as (f,member):
        raw=pd.read_csv(f,dtype=str,low_memory=False)
    source_columns=raw.columns.tolist()
    # Prevent silent month-to-month source-schema changes; source variants require explicit review.
    for old in sorted(parent.glob('*/manifest.json')):
        if json.loads(old.read_text())['source_columns']!=source_columns:
            raise ValueError('Month-to-month schema drift: review source headers before import')
    accepted,rejected,report=validate(raw,month)
    accepted['source_sha256']=digest
    accepted['source_row']=accepted.index+1
    accepted['flight_record_id']=digest+':'+accepted.source_row.astype(str)
    temp=Path(tempfile.mkdtemp(prefix='.staging-',dir=parent))
    try:
        accepted.to_parquet(temp/'flights.parquet',index=False)
        rejected.to_parquet(temp/'quarantine.parquet',index=False)
        (temp/'quality.json').write_text(json.dumps(report,indent=2))
        manifest={'month':month,'source_file':path.name,'csv_member':member,'source_sha256':digest,
          'source_url':source_url or BASE+filename(month),
          'source_url_note':'Official monthly archive URL; manual inputs must be obtained from BTS.',
          'accessed_at_utc':datetime.now(timezone.utc).isoformat(),'source_columns':source_columns,
          **report,'artifact_sha256':{n:sha256(temp/n) for n in ['flights.parquet','quarantine.parquet','quality.json']}}
        (temp/'manifest.json').write_text(json.dumps(manifest,indent=2))
        temp.rename(target)
    finally:
        if temp.exists(): shutil.rmtree(temp)
    out=root/'data/manifests';out.mkdir(parents=True,exist_ok=True)
    shutil.copy2(target/'manifest.json',out/f'{month}.json')
    return manifest

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',default='.');p.add_argument('--months',nargs='+',default=['2025-01','2025-02','2025-03'])
    p.add_argument('--input',type=Path,help='One official ZIP/CSV; requires one month')
    p.add_argument('--download',action='store_true')
    a=p.parse_args()
    if a.input and len(a.months)!=1: p.error('--input requires exactly one --months value')
    for m in a.months:
        try:
            path=a.input or (download(m,Path(a.root)/'data/raw') if a.download else Path(a.root)/'data/raw'/filename(m))
            r=ingest(path,m,a.root)
            print(json.dumps({k:r.get(k) for k in ['month','source_rows','accepted_rows','quarantined_rows','rerun']}),flush=True)
        except (ValueError,OSError,zipfile.BadZipFile,pd.errors.ParserError) as e: p.exit(1,f'{m}: {e}\n')
if __name__=='__main__': main()
