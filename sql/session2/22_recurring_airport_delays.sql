-- Which destinations repeatedly exceed the same-month network arrival-delay rate?
-- Screen at >=1,000 eligible arrivals in EACH observed month; recurrence requires every month (three in Q1).
WITH months AS (SELECT Year,Month,100.0*count(*) FILTER(WHERE late_arrival)/nullif(count(*) FILTER(WHERE arrival_eligible),0) AS network_delay_pct FROM fact_flights GROUP BY Year,Month),
g AS (SELECT DestAirportID,Dest,Year,Month,count(*) AS reported_flights,count(*) FILTER(WHERE arrival_eligible) AS eligible_flights,count(*) FILTER(WHERE late_arrival) AS delayed_flights,
100.0*count(*) FILTER(WHERE late_arrival)/nullif(count(*) FILTER(WHERE arrival_eligible),0) AS airport_delay_pct FROM fact_flights GROUP BY ALL),
j AS (SELECT *,airport_delay_pct-network_delay_pct AS excess_delay_pp FROM g JOIN months USING(Year,Month)),
s AS (SELECT DestAirportID,Dest,count(*) AS observed_months,count(*) FILTER(WHERE eligible_flights>=1000) AS screened_months,
count(*) FILTER(WHERE eligible_flights>=1000 AND excess_delay_pp>0) AS above_network_months,
sum(reported_flights) AS reported_flights,sum(eligible_flights) AS eligible_flights,sum(delayed_flights) AS delayed_flights,
min(eligible_flights) AS min_month_eligible,min(excess_delay_pp) AS min_excess_pp,max(excess_delay_pp) AS max_excess_pp FROM j GROUP BY DestAirportID,Dest)
SELECT *, (SELECT count(*) FROM months) AS required_months,
screened_months=(SELECT count(*) FROM months) AND above_network_months=(SELECT count(*) FROM months) AS recurring_above_network
FROM s ORDER BY recurring_above_network DESC,delayed_flights DESC,DestAirportID;
