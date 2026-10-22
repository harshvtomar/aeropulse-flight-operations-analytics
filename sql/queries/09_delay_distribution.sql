-- Partition eligible arrival delays into exhaustive disjoint minute bands.
WITH bands AS (SELECT CASE WHEN ArrDelay<0 THEN '1 Early (<0)' WHEN ArrDelay<15 THEN '2 0–<15' WHEN ArrDelay<30 THEN '3 15–<30' WHEN ArrDelay<60 THEN '4 30–<60' WHEN ArrDelay<120 THEN '5 60–<120' ELSE '6 120+' END AS delay_band FROM v_arrival_eligible)
SELECT delay_band,count(*) AS flights,100.0*count(*)/sum(count(*)) OVER () AS eligible_share_pct FROM bands GROUP BY delay_band ORDER BY delay_band;
