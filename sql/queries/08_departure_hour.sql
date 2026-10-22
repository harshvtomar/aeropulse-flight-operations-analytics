-- Scheduled local departure hour; 2400 normalized to hour 0, not UTC.
SELECT CAST(floor(CRSDepTime/100)%24 AS INTEGER) AS scheduled_local_hour, count(*) AS reported_flights,
 count(*) FILTER (WHERE arrival_eligible) AS eligible_flights,
 100.0*count(*) FILTER (WHERE on_time_arrival)/nullif(count(*) FILTER (WHERE arrival_eligible),0) AS on_time_pct,
 100.0*count(*) FILTER (WHERE Cancelled=1)/count(*) AS cancellation_pct,
 avg(ArrDelay) FILTER (WHERE arrival_eligible) AS avg_delay_minutes FROM fact_flights GROUP BY scheduled_local_hour ORDER BY scheduled_local_hour;
