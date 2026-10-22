-- Reported allocated minutes; null means unreported, not evidence of zero causes.
SELECT 'CarrierDelay' AS reported_cause,sum(CarrierDelay) AS reported_minutes,count(CarrierDelay) AS records_with_value FROM fact_flights
UNION ALL
SELECT 'WeatherDelay' AS reported_cause,sum(WeatherDelay) AS reported_minutes,count(WeatherDelay) AS records_with_value FROM fact_flights
UNION ALL
SELECT 'NASDelay' AS reported_cause,sum(NASDelay) AS reported_minutes,count(NASDelay) AS records_with_value FROM fact_flights
UNION ALL
SELECT 'SecurityDelay' AS reported_cause,sum(SecurityDelay) AS reported_minutes,count(SecurityDelay) AS records_with_value FROM fact_flights
UNION ALL
SELECT 'LateAircraftDelay' AS reported_cause,sum(LateAircraftDelay) AS reported_minutes,count(LateAircraftDelay) AS records_with_value FROM fact_flights;
