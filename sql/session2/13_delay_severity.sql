-- How severe are delayed eligible arrivals? Keep a full severity denominator and late-arrival share.
WITH bands AS (
 SELECT CASE WHEN ArrDelay<15 THEN '0 under 15' WHEN ArrDelay<30 THEN '1 15-29' WHEN ArrDelay<60 THEN '2 30-59' WHEN ArrDelay<120 THEN '3 60-119' ELSE '4 120+' END AS severity,
 ArrDelay FROM fact_flights WHERE arrival_eligible), totals AS (SELECT count(*) AS eligible, count(*) FILTER (WHERE ArrDelay>=15) AS delayed FROM bands)
SELECT severity,count(*) AS flights,sum(ArrDelay) AS signed_arrival_minutes,avg(ArrDelay) AS avg_arrival_minutes,
100.0*count(*)/nullif(max(eligible),0) AS eligible_share_pct,
CASE WHEN severity='0 under 15' THEN NULL ELSE 100.0*count(*)/nullif(max(delayed),0) END AS delayed_share_pct
FROM bands CROSS JOIN totals GROUP BY severity ORDER BY severity;
