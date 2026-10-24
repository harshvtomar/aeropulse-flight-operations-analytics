-- Run against exported detail. These are independent reference populations for Session 4.
WITH scoped AS (
  SELECT 'all' AS scope, * FROM read_parquet('data/bi/fact_flights.parquet')
  UNION ALL
  SELECT 'january', * FROM read_parquet('data/bi/fact_flights.parquet') WHERE flight_date < DATE '2025-02-01'
  UNION ALL
  SELECT 'january_airline_19805_origin_10397_hour_8', * FROM read_parquet('data/bi/fact_flights.parquet')
  WHERE flight_date < DATE '2025-02-01' AND airline_id=19805 AND origin_airport_id=10397 AND scheduled_hour=8
)
SELECT scope, count(*) AS reported_flights,
 sum(eligible_arrival) AS eligible_arrivals,
 sum(on_time_arrival) AS on_time_arrivals, sum(late_arrival) AS late_arrivals,
 sum(cancelled) AS cancellations, sum(diverted) AS diversions,
 sum(on_time_arrival)::DOUBLE / nullif(sum(eligible_arrival),0) AS on_time_arrival_rate,
 sum(cancelled)::DOUBLE / nullif(count(*),0) AS cancellation_rate,
 sum(eligible_delay_minutes) / nullif(sum(eligible_arrival),0) AS mean_eligible_arrival_delay_minutes,
 sum(CarrierDelay) AS carrier_reported_minutes,
 count(*) FILTER (WHERE late_arrival=1 AND CarrierDelay IS NOT NULL)::DOUBLE / nullif(sum(late_arrival),0) AS carrier_cause_late_coverage
FROM scoped GROUP BY scope ORDER BY scope;
