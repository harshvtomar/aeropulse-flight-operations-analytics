"""Reproduce Session 2 from the existing, checksum-verified Session 1 warehouse."""
import argparse
import json
from pathlib import Path
from .ingest import sha256
from . import advanced_sql, investigate, statistics, mix_analysis, bi_export, session2_report


def run(root='.', reps=2000):
    root = Path(root)
    for month in ('2025-01', '2025-02', '2025-03'):
        manifest = json.loads((root / 'data/manifests' / f'{month}.json').read_text())
        raw = root / 'data/raw' / manifest['source_file']
        if not raw.exists():
            raise FileNotFoundError(f'Missing official archive: {raw}; follow DATA_PROVENANCE.md')
        if sha256(raw) != manifest['source_sha256']:
            raise ValueError(f'Source revision or corruption: {raw}; do not replace the recorded snapshot')
    advanced_sql.run(root)
    investigate.investigate(root)
    statistics.run(root, reps)
    mix_analysis.run(root)
    bi_export.export(root)
    session2_report.run(root)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', default='.')
    parser.add_argument('--reps', type=int, default=2000)
    args = parser.parse_args()
    run(args.root, args.reps)
