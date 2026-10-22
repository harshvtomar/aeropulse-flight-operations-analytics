-- Which directed routes contribute most delayed flights? Contribution is not a ranking of intrinsic quality.
WITH g AS (SELECT OriginAirportID,DestAirportID,Origin,Dest,count(*) AS reported_flights,
count(*) FILTER (WHERE arrival_eligible) AS eligible_flights,
count(*) FILTER (WHERE late_arrival) AS delayed_flights,
count(*) FILTER (WHERE on_time_arrival) AS on_time_flights,
count(*) FILTER (WHERE Cancelled=1) AS cancelled_flights,
100.0*count(*) FILTER (WHERE late_arrival)/nullif(count(*) FILTER (WHERE arrival_eligible),0) AS delay_rate_pct,
100.0*count(*) FILTER (WHERE Cancelled=1)/count(*) AS cancellation_pct FROM fact_flights GROUP BY ALL),
r AS (SELECT *,100.0*delayed_flights/nullif(sum(delayed_flights) OVER (),0) AS network_delayed_share_pct,
100.0*sum(delayed_flights) OVER (ORDER BY delayed_flights DESC,OriginAirportID,DestAirportID ROWS UNBOUNDED PRECEDING)/nullif(sum(delayed_flights) OVER (),0) AS cumulative_delayed_share_pct,
row_number() OVER (ORDER BY delayed_flights DESC,OriginAirportID,DestAirportID) AS contribution_rank FROM g)
SELECT *,eligible_flights>=1000 AS rate_comparison_eligible FROM r ORDER BY contribution_rank;
