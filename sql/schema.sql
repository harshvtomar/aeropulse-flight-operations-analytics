-- One fact per source SHA-256 and 1-based CSV data row; no speculative deduplication.
CREATE TABLE dim_airlines AS
SELECT DISTINCT DOT_ID_Reporting_Airline, Reporting_Airline FROM fact_flights;
CREATE TABLE dim_airports AS
SELECT OriginAirportID AS airport_id, Origin AS airport_code FROM fact_flights
UNION SELECT DestAirportID, Dest FROM fact_flights;
CREATE TABLE dim_dates AS
SELECT DISTINCT CAST(FlightDate AS DATE) AS flight_date, Year, Month, DayOfWeek FROM fact_flights;
CREATE UNIQUE INDEX airline_key ON dim_airlines(DOT_ID_Reporting_Airline);
CREATE UNIQUE INDEX airport_key ON dim_airports(airport_id);
CREATE UNIQUE INDEX date_key ON dim_dates(flight_date);
CREATE UNIQUE INDEX flight_key ON fact_flights(flight_record_id);
CREATE VIEW v_arrival_eligible AS SELECT * FROM fact_flights WHERE arrival_eligible;
CREATE VIEW v_reliability AS
SELECT count(*) AS reported_flights,
 count(*) FILTER (WHERE arrival_eligible) AS eligible_flights,
 count(*) FILTER (WHERE on_time_arrival) AS on_time_flights,
 count(*) FILTER (WHERE late_arrival) AS late_flights,
 count(*) FILTER (WHERE Cancelled=1) AS cancelled_flights,
 count(*) FILTER (WHERE Diverted=1) AS diverted_flights,
 100.0*count(*) FILTER (WHERE on_time_arrival)/nullif(count(*) FILTER (WHERE arrival_eligible),0) AS on_time_pct,
 100.0*count(*) FILTER (WHERE late_arrival)/nullif(count(*) FILTER (WHERE arrival_eligible),0) AS late_pct,
 100.0*count(*) FILTER (WHERE Cancelled=1)/nullif(count(*),0) AS cancellation_pct,
 100.0*count(*) FILTER (WHERE Diverted=1)/nullif(count(*),0) AS diversion_pct,
 avg(ArrDelay) FILTER (WHERE arrival_eligible) AS avg_arrival_delay_minutes,
 avg(ArrDelay) FILTER (WHERE late_arrival) AS avg_late_arrival_delay_minutes
FROM fact_flights;
