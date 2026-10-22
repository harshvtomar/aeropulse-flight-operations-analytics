-- Full calendar days per imported month, including zero-flight dates; monthly mean includes those dates.
WITH months AS (SELECT DISTINCT CAST(Year AS INTEGER) AS y,CAST(Month AS INTEGER) AS m FROM fact_flights),
calendar AS (SELECT CAST(d AS DATE) AS flight_date FROM months,LATERAL generate_series(make_date(y,m,1),last_day(make_date(y,m,1)),INTERVAL 1 DAY) AS t(d)),
g AS (SELECT CAST(FlightDate AS DATE) AS flight_date,count(*) AS reported_flights,count(*) FILTER (WHERE arrival_eligible) AS eligible_flights,count(*) FILTER (WHERE late_arrival) AS delayed_flights,count(*) FILTER (WHERE Cancelled=1) AS cancelled_flights FROM fact_flights GROUP BY 1),
daily AS (SELECT flight_date,year(flight_date) AS Year,month(flight_date) AS Month,coalesce(reported_flights,0) AS reported_flights,coalesce(eligible_flights,0) AS eligible_flights,coalesce(delayed_flights,0) AS delayed_flights,coalesce(cancelled_flights,0) AS cancelled_flights FROM calendar LEFT JOIN g USING(flight_date))
SELECT *,count(*) OVER (PARTITION BY Year,Month) AS calendar_days_in_month,
sum(reported_flights) OVER (PARTITION BY Year,Month) AS monthly_flights,
avg(reported_flights) OVER (PARTITION BY Year,Month) AS monthly_flights_per_day,
100.0*delayed_flights/nullif(eligible_flights,0) AS delay_rate_pct,
100.0*cancelled_flights/nullif(reported_flights,0) AS cancellation_pct
FROM daily ORDER BY flight_date;
