-- Cancellation shares among cancelled flights; total cancellation rate is in query 01.
SELECT coalesce(CancellationCode,'UNKNOWN') AS cancellation_code,
CASE CancellationCode WHEN 'A' THEN 'Carrier' WHEN 'B' THEN 'Weather' WHEN 'C' THEN 'National Air System' WHEN 'D' THEN 'Security' ELSE 'Unknown' END AS reported_reason,
count(*) AS cancelled_flights,100.0*count(*)/sum(count(*)) OVER () AS cancelled_share_pct
FROM fact_flights WHERE Cancelled=1 GROUP BY ALL ORDER BY cancelled_flights DESC;
