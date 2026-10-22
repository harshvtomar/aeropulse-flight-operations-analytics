-- Coverage and allocated minutes by source category/month; NULL remains unreported.
-- 'late eligible' = normal completed arrival delayed >=15, an analytical population, not a certification of reporting compliance.
WITH base AS (SELECT *,(CarrierDelay IS NOT NULL AND WeatherDelay IS NOT NULL AND NASDelay IS NOT NULL AND SecurityDelay IS NOT NULL AND LateAircraftDelay IS NOT NULL) AS all_causes_reported,(CarrierDelay+WeatherDelay+NASDelay+SecurityDelay+LateAircraftDelay) AS complete_allocated_minutes FROM fact_flights),
coverage AS (SELECT Year,Month,count(*) AS reported_flights,count(*) FILTER (WHERE late_arrival) AS late_eligible_flights,
count(*) FILTER (WHERE late_arrival AND all_causes_reported) AS late_complete_cause_records,
count(*) FILTER (WHERE late_arrival AND NOT all_causes_reported) AS late_incomplete_cause_records,
count(*) FILTER (WHERE NOT late_arrival AND (CarrierDelay IS NOT NULL OR WeatherDelay IS NOT NULL OR NASDelay IS NOT NULL OR SecurityDelay IS NOT NULL OR LateAircraftDelay IS NOT NULL)) AS outside_late_any_cause_records,
count(*) FILTER (WHERE late_arrival AND all_causes_reported AND abs(complete_allocated_minutes-ArrDelay)>0.000001) AS complete_allocation_mismatch_records,
sum(complete_allocated_minutes) FILTER (WHERE late_arrival AND all_causes_reported) AS complete_allocated_minutes,
sum(ArrDelay) FILTER (WHERE late_arrival AND all_causes_reported) AS complete_arrival_delay_minutes
FROM base GROUP BY Year,Month),
categories AS (
SELECT Year,Month,'CarrierDelay' AS cause,count(CarrierDelay) AS records_with_value,count(*) FILTER (WHERE late_arrival AND CarrierDelay IS NOT NULL) AS late_records_with_value,sum(CarrierDelay) AS reported_minutes,sum(CarrierDelay) FILTER (WHERE late_arrival) AS late_reported_minutes FROM base GROUP BY Year,Month
UNION ALL
SELECT Year,Month,'WeatherDelay' AS cause,count(WeatherDelay) AS records_with_value,count(*) FILTER (WHERE late_arrival AND WeatherDelay IS NOT NULL) AS late_records_with_value,sum(WeatherDelay) AS reported_minutes,sum(WeatherDelay) FILTER (WHERE late_arrival) AS late_reported_minutes FROM base GROUP BY Year,Month
UNION ALL
SELECT Year,Month,'NASDelay' AS cause,count(NASDelay) AS records_with_value,count(*) FILTER (WHERE late_arrival AND NASDelay IS NOT NULL) AS late_records_with_value,sum(NASDelay) AS reported_minutes,sum(NASDelay) FILTER (WHERE late_arrival) AS late_reported_minutes FROM base GROUP BY Year,Month
UNION ALL
SELECT Year,Month,'SecurityDelay' AS cause,count(SecurityDelay) AS records_with_value,count(*) FILTER (WHERE late_arrival AND SecurityDelay IS NOT NULL) AS late_records_with_value,sum(SecurityDelay) AS reported_minutes,sum(SecurityDelay) FILTER (WHERE late_arrival) AS late_reported_minutes FROM base GROUP BY Year,Month
UNION ALL
SELECT Year,Month,'LateAircraftDelay' AS cause,count(LateAircraftDelay) AS records_with_value,count(*) FILTER (WHERE late_arrival AND LateAircraftDelay IS NOT NULL) AS late_records_with_value,sum(LateAircraftDelay) AS reported_minutes,sum(LateAircraftDelay) FILTER (WHERE late_arrival) AS late_reported_minutes FROM base GROUP BY Year,Month
)
SELECT categories.*,coverage.* EXCLUDE(Year,Month),
100.0*late_records_with_value/nullif(late_eligible_flights,0) AS late_coverage_pct,
100.0*reported_minutes/nullif(sum(reported_minutes) OVER(PARTITION BY categories.Year,categories.Month),0) AS allocated_minute_share_pct
FROM categories JOIN coverage USING(Year,Month) ORDER BY Year,Month,cause;
