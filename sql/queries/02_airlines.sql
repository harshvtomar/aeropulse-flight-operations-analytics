-- Compare reporting carriers; DOT ID avoids ambiguous carrier names.
SELECT a.DOT_ID_Reporting_Airline, a.Reporting_Airline, count(*) AS reported_flights,
 count(*) FILTER (WHERE arrival_eligible) AS eligible_flights,
 100.0*count(*) FILTER (WHERE on_time_arrival)/nullif(count(*) FILTER (WHERE arrival_eligible),0) AS on_time_pct,
 100.0*count(*) FILTER (WHERE Cancelled=1)/count(*) AS cancellation_pct,
 avg(ArrDelay) FILTER (WHERE arrival_eligible) AS avg_delay_minutes FROM fact_flights f JOIN dim_airlines a USING(DOT_ID_Reporting_Airline) GROUP BY ALL ORDER BY reported_flights DESC;
