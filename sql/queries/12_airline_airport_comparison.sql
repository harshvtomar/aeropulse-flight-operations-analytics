-- Within-origin airline comparisons require 500 eligible flights per airline-origin; unadjusted for schedule/route mix.
WITH groups AS (SELECT Origin, Reporting_Airline, count(*) AS reported_flights,
 count(*) FILTER (WHERE arrival_eligible) AS eligible_flights,
 100.0*count(*) FILTER (WHERE on_time_arrival)/nullif(count(*) FILTER (WHERE arrival_eligible),0) AS on_time_pct,
 100.0*count(*) FILTER (WHERE Cancelled=1)/count(*) AS cancellation_pct,
 avg(ArrDelay) FILTER (WHERE arrival_eligible) AS avg_delay_minutes FROM fact_flights GROUP BY ALL),
qualified AS (SELECT *, dense_rank() OVER (PARTITION BY Origin ORDER BY on_time_pct DESC) AS origin_rank FROM groups WHERE eligible_flights>=500)
SELECT * FROM qualified ORDER BY Origin,origin_rank,Reporting_Airline;
