-- Concentration by destination; threshold screens rate comparisons, not volume contribution.
WITH g AS (SELECT DestAirportID,Dest,count(*) AS reported_flights,
count(*) FILTER (WHERE arrival_eligible) AS eligible_flights,
count(*) FILTER (WHERE late_arrival) AS delayed_flights,
count(*) FILTER (WHERE on_time_arrival) AS on_time_flights,
count(*) FILTER (WHERE Cancelled=1) AS cancelled_flights,
100.0*count(*) FILTER (WHERE late_arrival)/nullif(count(*) FILTER (WHERE arrival_eligible),0) AS delay_rate_pct,
100.0*count(*) FILTER (WHERE Cancelled=1)/count(*) AS cancellation_pct FROM fact_flights GROUP BY ALL)
SELECT *,100.0*delayed_flights/nullif(sum(delayed_flights) OVER (),0) AS network_delayed_share_pct,
row_number() OVER (ORDER BY delayed_flights DESC,DestAirportID) AS contribution_rank,
eligible_flights>=1000 AS rate_comparison_eligible FROM g ORDER BY contribution_rank;
