-- Track monthly volume and reliability; absolute counts reflect month length.
WITH monthly AS (SELECT Year, Month, count(*) AS reported_flights,
 count(*) FILTER (WHERE arrival_eligible) AS eligible_flights,
 100.0*count(*) FILTER (WHERE on_time_arrival)/nullif(count(*) FILTER (WHERE arrival_eligible),0) AS on_time_pct,
 100.0*count(*) FILTER (WHERE Cancelled=1)/count(*) AS cancellation_pct,
 avg(ArrDelay) FILTER (WHERE arrival_eligible) AS avg_delay_minutes FROM fact_flights GROUP BY ALL)
SELECT *, reported_flights-lag(reported_flights) OVER (ORDER BY Year, Month) AS flight_change_from_prior_month FROM monthly ORDER BY Year,Month;
