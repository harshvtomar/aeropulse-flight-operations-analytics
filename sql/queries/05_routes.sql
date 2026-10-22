-- Directed routes; rank only routes with at least 1,000 eligible arrivals in this coverage.
WITH routes AS (SELECT Origin, Dest, count(*) AS reported_flights,
 count(*) FILTER (WHERE arrival_eligible) AS eligible_flights,
 100.0*count(*) FILTER (WHERE on_time_arrival)/nullif(count(*) FILTER (WHERE arrival_eligible),0) AS on_time_pct,
 100.0*count(*) FILTER (WHERE Cancelled=1)/count(*) AS cancellation_pct,
 avg(ArrDelay) FILTER (WHERE arrival_eligible) AS avg_delay_minutes FROM fact_flights GROUP BY ALL)
SELECT *, dense_rank() OVER (ORDER BY on_time_pct ASC) AS poor_reliability_rank
FROM routes WHERE eligible_flights >= 1000 ORDER BY poor_reliability_rank, reported_flights DESC, Origin, Dest;
