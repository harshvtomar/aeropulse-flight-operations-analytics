# Data provenance

Government publisher: US Department of Transportation, Bureau of Transportation Statistics (BTS).
Dataset: **Reporting Carrier On-Time Performance (1987–present)**, consistent across all months.

- Selection page: https://www.transtats.bts.gov/DL_SelectFields.aspx?QO_fu146_anzr=b0-gvzr&gnoyr_VQ=FGJ
- Official schema: https://www.transtats.bts.gov/Fields.asp?gnoyr_VQ=FGJ
- Table profile: https://www.transtats.bts.gov/Tables.asp?QO_VQ=EFD
- Access date: 22 October 2026 (precise UTC retrieval/import times in manifests).

The selection page timed out through the research tool. The official public PREZIP archive endpoint returned ZIP files successfully; no CAPTCHA, access controls or rate limits were bypassed. Complete monthly archives were downloaded without geography, carrier or row sampling filters. Raw ZIPs were left unchanged. All selected fields were verified against actual CSV headers and the official field listing.

## Downloaded archives

| Month | Raw ZIP | Observed source rows | Accepted | Quarantined |
|---|---|---:|---:|---:|
| 2025-01 | On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2025_1.zip | 539,747 | 539,747 | 0 |
| 2025-02 | On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2025_2.zip | 504,884 | 504,884 | 0 |
| 2025-03 | On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2025_3.zip | 600,872 | 600,872 | 0 |

### 2025-01

URL: https://www.transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2025_1.zip

CSV member: `On_Time_Reporting_Carrier_On_Time_Performance_(1987_present)_2025_1.csv`

SHA-256: `868387dcedaef1b8d8392e608e642219fde50d594c3cf2094aec858167629ccf`

Import/access timestamp: 2026-10-22T03:01:41.252321+00:00

### 2025-02

URL: https://www.transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2025_2.zip

CSV member: `On_Time_Reporting_Carrier_On_Time_Performance_(1987_present)_2025_2.csv`

SHA-256: `12dc8dbdb3c8b3c20d4c00a8b188196ae202f781a8760871ae502a9c733d0ecd`

Import/access timestamp: 2026-10-22T03:01:55.311933+00:00

### 2025-03

URL: https://www.transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2025_3.zip

CSV member: `On_Time_Reporting_Carrier_On_Time_Performance_(1987_present)_2025_3.csv`

SHA-256: `9c80fbc2112cdbf3f0613ec2001ba019b3ad75511cd69657080736e7eda9cef4`

Import/access timestamp: 2026-10-22T03:02:12.169397+00:00

## Selected fields

`FlightDate`, `Year`, `Month`, `DayOfWeek`, `Reporting_Airline`, `DOT_ID_Reporting_Airline`, `Flight_Number_Reporting_Airline`, `OriginAirportID`, `DestAirportID`, `Origin`, `Dest`, `CRSDepTime`, `CRSArrTime`, `DepTime`, `ArrTime`, `DepDelay`, `ArrDelay`, `ArrDel15`, `Cancelled`, `CancellationCode`, `Diverted`, `Distance`, `CarrierDelay`, `WeatherDelay`, `NASDelay`, `SecurityDelay`, `LateAircraftDelay`.

## Extraction and use
These are publicly downloadable US federal statistical records. No paid API, account or special access mechanism was used. Source attribution is retained. Each ZIP also includes the publisher's readme; keep it with the original archive. This project does not assert a separate license over source data or third-party site assets. Do not infer that every asset on the BTS website shares the data's reuse conditions.

The pipeline reads the CSV within the ZIP without extracting arbitrary member paths. Original archives and generated databases/Parquet are excluded from Git; reproducible URLs, SHA-256 fingerprints, observed record counts and analysis outputs are committed. Manually selected official exports must contain every required field and the complete requested month. The importer validates row content but cannot prove that a user-supplied export was unfiltered; reconcile it with the committed complete-archive counts and hashes.

## Limitations
Reporting-carrier domestic operations are not the entire US aviation universe. No marketing-carrier table is mixed in. Delay allocations are carrier-reported categories. Null delay-cause fields are unreported, not filled with zero. Source revisions are possible. We have not independently matched this snapshot to an Air Travel Consumer Report; our independently checked KPIs use the definitions in KPI_DEFINITIONS.md, which may differ from published summary denominators.

## Reproduction
Run `python -m src.ingest --download`, then `python -m src.warehouse`, `python -m src.analysis`, and `python -m pytest -q`. For manual downloads see README. Compare the new `data/manifests` fingerprints to this document before asserting identical provenance.
