-- Does scheduled local-hour reliability recur by month? Local hour is not UTC; 2400 maps to 0.
SELECT Year,Month,CAST(floor(CRSDepTime/100)%24 AS INTEGER) AS departure_hour,count(*) AS reported_flights,
count(*) FILTER (WHERE arrival_eligible) AS eligible_flights,
count(*) FILTER (WHERE late_arrival) AS delayed_flights,
count(*) FILTER (WHERE on_time_arrival) AS on_time_flights,
count(*) FILTER (WHERE Cancelled=1) AS cancelled_flights,
100.0*count(*) FILTER (WHERE late_arrival)/nullif(count(*) FILTER (WHERE arrival_eligible),0) AS delay_rate_pct,
100.0*count(*) FILTER (WHERE Cancelled=1)/count(*) AS cancellation_pct,
count(*) FILTER (WHERE arrival_eligible AND ArrDelay>=120) AS severe_delayed_flights
FROM fact_flights GROUP BY ALL ORDER BY Year,Month,departure_hour;
