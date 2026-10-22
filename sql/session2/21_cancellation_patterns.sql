-- Locate cancellation concentrations by carrier, origin and month; display all denominators.
SELECT Year,Month,DOT_ID_Reporting_Airline,Reporting_Airline,OriginAirportID,Origin,count(*) AS reported_flights,
count(*) FILTER (WHERE arrival_eligible) AS eligible_flights,
count(*) FILTER (WHERE late_arrival) AS delayed_flights,
count(*) FILTER (WHERE on_time_arrival) AS on_time_flights,
count(*) FILTER (WHERE Cancelled=1) AS cancelled_flights,
100.0*count(*) FILTER (WHERE late_arrival)/nullif(count(*) FILTER (WHERE arrival_eligible),0) AS delay_rate_pct,
100.0*count(*) FILTER (WHERE Cancelled=1)/count(*) AS cancellation_pct,
count(*) FILTER(WHERE Cancelled=1 AND CancellationCode='A') AS carrier_cancellations,
count(*) FILTER(WHERE Cancelled=1 AND CancellationCode='B') AS weather_cancellations,
count(*) FILTER(WHERE Cancelled=1 AND CancellationCode='C') AS nas_cancellations,
count(*) FILTER(WHERE Cancelled=1 AND CancellationCode='D') AS security_cancellations,
count(*) FILTER(WHERE Cancelled=1 AND (CancellationCode IS NULL OR CancellationCode NOT IN ('A','B','C','D'))) AS unknown_cancellations,
count(*)>=100 AS cancellation_rate_comparison_eligible
FROM fact_flights GROUP BY ALL ORDER BY Year,Month,DOT_ID_Reporting_Airline,OriginAirportID;
