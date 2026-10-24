// Create a blank query named fact_flights; paste this entire expression.
let
    Path = Text.TrimEnd(pDataFolder, {"/", "\"}) & "/fact_flights.parquet",
    Source = Parquet.Document(File.Contents(Path)),
    Expected = {"flight_record_id", "date_key", "flight_date", "airline_id", "origin_airport_id", "destination_airport_id", "route_key", "scheduled_hour", "flight_number", "cancelled", "diverted", "cancellation_code", "eligible_arrival", "on_time_arrival", "late_arrival", "arrival_delay_minutes", "departure_delay_minutes", "eligible_delay_minutes", "late_delay_minutes", "distance_miles", "CarrierDelay", "WeatherDelay", "NASDelay", "SecurityDelay", "LateAircraftDelay", "source_sha256", "source_row"},
    Checked = if List.Count(List.Difference(Expected, Table.ColumnNames(Source))) = 0 and List.Count(List.Difference(Table.ColumnNames(Source), Expected)) = 0 then Source else error "Export schema differs from the Session 3 contract",
    Nulls = Table.ReplaceValue(Checked, "", null, Replacer.ReplaceValue, Table.ColumnNames(Checked)),
    Typed = Table.TransformColumnTypes(Nulls, {
        {"flight_record_id", type text},
        {"date_key", Int64.Type},
        {"flight_date", type date},
        {"airline_id", Int64.Type},
        {"origin_airport_id", Int64.Type},
        {"destination_airport_id", Int64.Type},
        {"route_key", type text},
        {"scheduled_hour", Int64.Type},
        {"flight_number", Int64.Type},
        {"cancelled", Int64.Type},
        {"diverted", Int64.Type},
        {"cancellation_code", type text},
        {"eligible_arrival", Int64.Type},
        {"on_time_arrival", Int64.Type},
        {"late_arrival", Int64.Type},
        {"arrival_delay_minutes", type number},
        {"departure_delay_minutes", type number},
        {"eligible_delay_minutes", type number},
        {"late_delay_minutes", type number},
        {"distance_miles", type number},
        {"CarrierDelay", type number},
        {"WeatherDelay", type number},
        {"NASDelay", type number},
        {"SecurityDelay", type number},
        {"LateAircraftDelay", type number},
        {"source_sha256", type text},
        {"source_row", Int64.Type}
    }, "en-US")
in
    Typed
