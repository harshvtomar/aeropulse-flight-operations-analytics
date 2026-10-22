-- Does airline reliability change across consecutive months? Missing intervening months yield NULL change.
WITH g AS (SELECT Year,Month,DOT_ID_Reporting_Airline,Reporting_Airline,count(*) AS reported_flights,
count(*) FILTER (WHERE arrival_eligible) AS eligible_flights,
count(*) FILTER (WHERE late_arrival) AS delayed_flights,
count(*) FILTER (WHERE on_time_arrival) AS on_time_flights,
count(*) FILTER (WHERE Cancelled=1) AS cancelled_flights,
100.0*count(*) FILTER (WHERE late_arrival)/nullif(count(*) FILTER (WHERE arrival_eligible),0) AS delay_rate_pct,
100.0*count(*) FILTER (WHERE Cancelled=1)/count(*) AS cancellation_pct FROM fact_flights GROUP BY ALL)
SELECT *, CASE WHEN date_diff('month',
lag(make_date(CAST(Year AS INTEGER),CAST(Month AS INTEGER),1)) OVER (PARTITION BY DOT_ID_Reporting_Airline ORDER BY Year,Month),
make_date(CAST(Year AS INTEGER),CAST(Month AS INTEGER),1))=1
THEN delay_rate_pct-lag(delay_rate_pct) OVER (PARTITION BY DOT_ID_Reporting_Airline ORDER BY Year,Month)
ELSE NULL END AS prior_month_change_pp
FROM g ORDER BY DOT_ID_Reporting_Airline,Year,Month;
