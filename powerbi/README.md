# AeroPulse Power BI build package

Start with [Session 3 status and Session 4 build instructions](../docs/POWER_BI_SESSION3.md).

This is a reproducible import/measure/theme/manual-layout package, not a native Power BI report. Native M, DAX, rendering and interaction validation require supported Windows Power BI Desktop and remain pending. No PBIX or PBIP is claimed.

```bash
python powerbi/build_package.py
python -m pytest tests/test_powerbi_package.py -q
```

Regenerate `data/bi` with the canonical exporter before native import. Only the seven-table detail star is loaded; overlapping aggregate tables are intentionally excluded from this model.
