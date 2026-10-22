-- Compare weekdays/weekends within month; calendar counts normalize unequal exposure days.
WITH calendar AS (SELECT Year,Month,CASE WHEN isodow(d)>=6 THEN 'weekend' ELSE 'weekday' END AS day_type,count(*) AS calendar_days
FROM (SELECT DISTINCT CAST(Year AS INTEGER) AS Year,CAST(Month AS INTEGER) AS Month FROM fact_flights) m,
LATERAL generate_series(make_date(Year,Month,1),last_day(make_date(Year,Month,1)),INTERVAL 1 DAY) AS t(d) GROUP BY ALL),
g AS (SELECT Year,Month,CASE WHEN DayOfWeek>=6 THEN 'weekend' ELSE 'weekday' END AS day_type,count(*) AS reported_flights,
count(*) FILTER (WHERE arrival_eligible) AS eligible_flights,
count(*) FILTER (WHERE late_arrival) AS delayed_flights,
count(*) FILTER (WHERE on_time_arrival) AS on_time_flights,
count(*) FILTER (WHERE Cancelled=1) AS cancelled_flights,
100.0*count(*) FILTER (WHERE late_arrival)/nullif(count(*) FILTER (WHERE arrival_eligible),0) AS delay_rate_pct,
100.0*count(*) FILTER (WHERE Cancelled=1)/count(*) AS cancellation_pct FROM fact_flights GROUP BY ALL)
SELECT g.*,calendar_days,reported_flights*1.0/calendar_days AS flights_per_calendar_day FROM g JOIN calendar USING(Year,Month,day_type) ORDER BY Year,Month,day_type;
