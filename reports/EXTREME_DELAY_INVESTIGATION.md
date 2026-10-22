# Extreme-delay investigation

Canonical calculations and source records remain unchanged. Warning thresholds are below −120 or above 2,880 minutes, not automatic error boundaries.

Found **5 arrival warnings**, **7 departure warnings**, covering **7 unique source records**. Every listed row was located in its original CSV by archive SHA-256 and one-based data-row number; raw values matched warehouse values.

| Date | Carrier / flight | Route | Source row | Dep delay (min) | Arr delay (min) | Cancelled / diverted | Assessment |
|---|---|---|---:|---:|---:|---|---|
| 2025-01-03 | MQ 3373 | MLU → DFW | 502119 | 2983 | 2955.0 | 0 / 0 | Internally consistent multi-day operational outlier; externally unconfirmed |
| 2025-01-15 | AA 1115 | MCI → ORD | 25470 | 3100 | missing | 1 / 0 | Unresolved cancellation/gate-return anomaly; source follow-up required |
| 2025-01-28 | AA 2420 | IAH → DFW | 57435 | 3298 | 3282.0 | 0 / 0 | Internally consistent multi-day operational outlier; externally unconfirmed |
| 2025-02-21 | AA 1502 | MFE → DFW | 55787 | 3092 | 3103.0 | 0 / 0 | Internally consistent multi-day operational outlier; externally unconfirmed |
| 2025-02-24 | AA 3063 | SJU → PHL | 17371 | 3403 | 3407.0 | 0 / 0 | Internally consistent multi-day operational outlier; externally unconfirmed |
| 2025-02-28 | AA 1361 | RNO → DFW | 44259 | 2883 | 2872.0 | 0 / 0 | Internally consistent multi-day operational outlier; externally unconfirmed |
| 2025-03-24 | AA 2241 | RSW → CLT | 59770 | 3288 | 3275.0 | 0 / 0 | Internally consistent multi-day operational outlier; externally unconfirmed |

## Traceable identities and supporting fields

### 2025-01-03 — MQ 3373

- Technical source identity: `868387dcedaef1b8d8392e608e642219fde50d594c3cf2094aec858167629ccf:502119`.
- Archive: `On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2025_1.zip`; CSV member: `On_Time_Reporting_Carrier_On_Time_Performance_(1987_present)_2025_1.csv`.
- Scheduled/actual departure HHMM: 530/713; scheduled/actual arrival: 713/828.0.
- Scheduled/actual elapsed minutes: 103/75.0; air time: 53.0; taxi-out/in: 10.0/12.0.
- First gate departure: nan; total/longest additional ground time: nan/nan; diversion landings: 0; cancellation reason: None.
- Elapsed identity residual: 0.0; departure/arrival clock residual modulo 1,440: 0.0/0.0; allocated-cause sum minus arrival delay: 0.0.
- Assessment: **Internally consistent multi-day operational outlier; externally unconfirmed**.

### 2025-01-15 — AA 1115

- Technical source identity: `868387dcedaef1b8d8392e608e642219fde50d594c3cf2094aec858167629ccf:25470`.
- Archive: `On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2025_1.zip`; CSV member: `On_Time_Reporting_Carrier_On_Time_Performance_(1987_present)_2025_1.csv`.
- Scheduled/actual departure HHMM: 700/1040; scheduled/actual arrival: 847/nan.
- Scheduled/actual elapsed minutes: 107/nan; air time: nan; taxi-out/in: nan/nan.
- First gate departure: 651.0; total/longest additional ground time: 90.0/61.0; diversion landings: 0; cancellation reason: A.
- Elapsed identity residual: nan; departure/arrival clock residual modulo 1,440: 0.0/nan; allocated-cause sum minus arrival delay: nan.
- Assessment: **Unresolved cancellation/gate-return anomaly; source follow-up required**.

### 2025-01-28 — AA 2420

- Technical source identity: `868387dcedaef1b8d8392e608e642219fde50d594c3cf2094aec858167629ccf:57435`.
- Archive: `On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2025_1.zip`; CSV member: `On_Time_Reporting_Carrier_On_Time_Performance_(1987_present)_2025_1.csv`.
- Scheduled/actual departure HHMM: 1001/1659; scheduled/actual arrival: 1139/1821.0.
- Scheduled/actual elapsed minutes: 98/82.0; air time: 43.0; taxi-out/in: 28.0/11.0.
- First gate departure: 950.0; total/longest additional ground time: 10.0/10.0; diversion landings: 0; cancellation reason: None.
- Elapsed identity residual: 0.0; departure/arrival clock residual modulo 1,440: 0.0/0.0; allocated-cause sum minus arrival delay: 0.0.
- Assessment: **Internally consistent multi-day operational outlier; externally unconfirmed**.

### 2025-02-21 — AA 1502

- Technical source identity: `12dc8dbdb3c8b3c20d4c00a8b188196ae202f781a8760871ae502a9c733d0ecd:55787`.
- Archive: `On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2025_2.zip`; CSV member: `On_Time_Reporting_Carrier_On_Time_Performance_(1987_present)_2025_2.csv`.
- Scheduled/actual departure HHMM: 500/832; scheduled/actual arrival: 640/1023.0.
- Scheduled/actual elapsed minutes: 100/111.0; air time: 68.0; taxi-out/in: 32.0/11.0.
- First gate departure: nan; total/longest additional ground time: nan/nan; diversion landings: 0; cancellation reason: None.
- Elapsed identity residual: 0.0; departure/arrival clock residual modulo 1,440: 0.0/0.0; allocated-cause sum minus arrival delay: 0.0.
- Assessment: **Internally consistent multi-day operational outlier; externally unconfirmed**.

### 2025-02-24 — AA 3063

- Technical source identity: `12dc8dbdb3c8b3c20d4c00a8b188196ae202f781a8760871ae502a9c733d0ecd:17371`.
- Archive: `On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2025_2.zip`; CSV member: `On_Time_Reporting_Carrier_On_Time_Performance_(1987_present)_2025_2.csv`.
- Scheduled/actual departure HHMM: 600/1443; scheduled/actual arrival: 910/1757.0.
- Scheduled/actual elapsed minutes: 250/254.0; air time: 237.0; taxi-out/in: 13.0/4.0.
- First gate departure: nan; total/longest additional ground time: nan/nan; diversion landings: 0; cancellation reason: None.
- Elapsed identity residual: 0.0; departure/arrival clock residual modulo 1,440: 0.0/0.0; allocated-cause sum minus arrival delay: 0.0.
- Assessment: **Internally consistent multi-day operational outlier; externally unconfirmed**.

### 2025-02-28 — AA 1361

- Technical source identity: `12dc8dbdb3c8b3c20d4c00a8b188196ae202f781a8760871ae502a9c733d0ecd:44259`.
- Archive: `On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2025_2.zip`; CSV member: `On_Time_Reporting_Carrier_On_Time_Performance_(1987_present)_2025_2.csv`.
- Scheduled/actual departure HHMM: 601/604; scheduled/actual arrival: 1130/1122.0.
- Scheduled/actual elapsed minutes: 209/198.0; air time: 167.0; taxi-out/in: 18.0/13.0.
- First gate departure: nan; total/longest additional ground time: nan/nan; diversion landings: 0; cancellation reason: None.
- Elapsed identity residual: 0.0; departure/arrival clock residual modulo 1,440: 0.0/0.0; allocated-cause sum minus arrival delay: 0.0.
- Assessment: **Internally consistent multi-day operational outlier; externally unconfirmed**.

### 2025-03-24 — AA 2241

- Technical source identity: `9c80fbc2112cdbf3f0613ec2001ba019b3ad75511cd69657080736e7eda9cef4:59770`.
- Archive: `On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2025_3.zip`; CSV member: `On_Time_Reporting_Carrier_On_Time_Performance_(1987_present)_2025_3.csv`.
- Scheduled/actual departure HHMM: 800/1448; scheduled/actual arrival: 1003/1638.0.
- Scheduled/actual elapsed minutes: 123/110.0; air time: 86.0; taxi-out/in: 16.0/8.0.
- First gate departure: nan; total/longest additional ground time: nan/nan; diversion landings: 0; cancellation reason: None.
- Elapsed identity residual: 0.0; departure/arrival clock residual modulo 1,440: 0.0/0.0; allocated-cause sum minus arrival delay: 0.0.
- Assessment: **Internally consistent multi-day operational outlier; externally unconfirmed**.

The six completed flights pass signed elapsed-time, local-clock modulo-day and cause-allocation consistency checks. These checks make the large delays internally plausible; they do not independently prove that a multi-day disruption occurred. No operational event is invented. The seventh flight is cancelled, so arrival/elapsed checks are unavailable. Gate-return fields provide context but cannot establish the cancellation timeline without dated event logs. Its classification remains unresolved, not a confirmed source error.

## Sensitivity (not canonical results)

| Scenario | Rows removed | Eligible arrivals | Mean arrival delay (min) | Mean late-arrival delay (min) | On-time % | Cancellation % |
|---|---:|---:|---:|---:|---:|---:|
| canonical_all | 0 | 1,611,046 | 4.984481 | 71.653984 | 80.306832 | 1.862045 |
| exclude_arrival_warning_only | 5 | 1,611,041 | 4.974551 | 71.604613 | 80.307081 | 1.862050 |
| exclude_any_arrival_or_departure_warning | 7 | 1,611,040 | 4.972772 | 71.595786 | 80.307131 | 1.861992 |

Excluding all flagged rows also removes one cancellation and changes the all-flight denominator. This is a sensitivity exercise only, not a proposed cleaning rule. Machine-readable metrics and exact differences are in `session2/extreme_sensitivity.csv`.

## Reporting guidance consulted

[BTS Technical Directive 39, effective January 1, 2025](https://www.bts.gov/explore-topics-and-geography/modes/aviation/number-39-technical-directive-reporting-time), sections 3.a, 5 and 7, accessed October 22, 2026: cancelled flights can retain departure fields after leaving the gate; on-time/diverted flights do not require delay-cause minutes, and reported cause allocations for late arrivals should reconcile to arrival delay. This supports the field checks, not independent confirmation of any event.
