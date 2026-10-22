"""Regenerate the human-readable data quality report from audited month bundles."""
import json
from pathlib import Path

def quality_report(root='.'):
    root=Path(root);ms=[json.loads(p.read_text()) for p in sorted((root/'data/processed').glob('*/manifest.json'))]
    s='# Data quality report\n\nMeasured from complete imported source files. Invalid rows are quarantined; warning cases remain accepted. Duplicate candidates are retained.\n\n| Month | Source | Accepted | Quarantined | Duplicate candidates | Date range |\n|---|---:|---:|---:|---:|---|\n'
    for m in ms:s+=f"| {m['month']} | {m['source_rows']:,} | {m['accepted_rows']:,} | {m['quarantined_rows']:,} | {m['duplicate_candidate_rows']:,} | {m['date_min'][:10]} to {m['date_max'][:10]} |\n"
    s+='\n## Warnings (source rows)\n\n'
    for m in ms:
        s+=f"### {m['month']}\n\n"
        for k,v in m['warnings'].items():s+=f'- {k}: {v:,}\n'
        s+=f"\nRaw = accepted + quarantined: **{m['reconciliation_passed']}**. Invalid-value findings: {sum(m['invalid_values'].values())}.\n\n"
    s+='## Missing values (% of source rows)\n\n| Field | '+' | '.join(m['month'] for m in ms)+' |\n|---|'+ '|'.join('---:' for m in ms)+'|\n'
    for c in ms[0]['missing_percent']:s+='| '+c+' | '+' | '.join(f"{m['missing_percent'][c]:.4f}" for m in ms)+' |\n'
    s+='\nExtreme-delay warnings use review thresholds outside [-120, 2880] minutes. These are not automatic validity limits; records remain unchanged. Missing arrival times for cancellations are expected. Full invalid-value checks, hashes, schema and exact timestamps are in `data/manifests/`. Airport code validation checks format, not membership in an independent registry.\n'
    (root/'reports/DATA_QUALITY_REPORT.md').write_text(s)
