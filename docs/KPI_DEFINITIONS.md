# KPI contract

All rates are percentages, not fractions. Zero denominators produce SQL NULL / Python None. Warehouse metrics describe accepted source records; quarantined counts must be disclosed alongside them. This run accepted every record.

| KPI | Numerator / measure | Denominator / population |
|---|---|---|
| Total reported flights | Source row count (accepted + quarantined) | Full monthly input; accepted count in `v_reliability` |
| Eligible completed flights | Cancelled=0 AND Diverted=0 AND ArrDelay nonmissing | Accepted facts |
| On-time arrival % | Eligible with ArrDelay <15, including negative delays | Eligible completed flights |
| Arrival delay rate | Eligible with ArrDelay >=15 | Eligible completed flights |
| Cancellation % | Cancelled=1 | All accepted reported flights |
| Diversion % | Diverted=1 | All accepted reported flights |
| Average arrival delay | Arithmetic mean of signed ArrDelay | Eligible completed flights |
| Average delay among delayed flights | Mean ArrDelay for delay >=15 | Eligible delayed flights |
| Airline reliability | Same arrival/cancellation metrics grouped by DOT ID | Group-specific denominators; display sample sizes |
| Airport reliability | Group by origin or destination ID | Group-specific denominators; origin means eventual arrival reliability of departures |
| Route reliability | Directed origin → destination | At least 1,000 eligible arrivals to enter ranking |
| Reported delay-cause minutes | Sum each reported minute field, ignoring NULL | Entire fact table; also report nonmissing-record counts |

Cancelled and diverted records are never counted as normal on-time arrivals. A diverted aircraft may ultimately reach its scheduled destination; BTS supplies separate diversion-specific delay fields, which are not used here. A cancellation/diversion overlap, if present, counts in both rates; never assume their sum is a disjoint partition. This quarter contains no overlap.

Missing normal-flight arrival delays are excluded from arrival-rate denominators and reported as warnings. ArrDel15 is cross-checked against signed ArrDelay; this project derives classification from ArrDelay, preserving any mismatch for review. Arrival time missingness is reported independently; eligibility follows the stated delay-based contract. No such normal-flight missingness or mismatches occurred in this quarter.

Cause minutes describe reported allocations. NULL is not overwritten with zero; absent reporting does not prove no delay cause. CarrierDelay is not monetary cost. Do not interpret weather attribution as all weather impacts, or sum causes as an independently established causal model.

Cancellation codes: A carrier, B weather, C National Air System, D security; missing/other codes remain visible as unknown. Departure times are local clock values, not comparable UTC instants. 2400 maps to hour 0 for hourly grouping only; no chronology is inferred from HHMM subtraction.
