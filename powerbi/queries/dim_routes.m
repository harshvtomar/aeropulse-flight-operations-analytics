// Create a blank query named dim_routes; paste this entire expression.
let
    Path = Text.TrimEnd(pDataFolder, {"/", "\"}) & "/dim_routes.csv",
    Source = Table.PromoteHeaders(Csv.Document(File.Contents(Path), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]), [PromoteAllScalars=true]),
    Expected = {"route_key", "origin_airport_id", "destination_airport_id"},
    Checked = if List.Count(List.Difference(Expected, Table.ColumnNames(Source))) = 0 and List.Count(List.Difference(Table.ColumnNames(Source), Expected)) = 0 then Source else error "Export schema differs from the Session 3 contract",
    Nulls = Table.ReplaceValue(Checked, "", null, Replacer.ReplaceValue, Table.ColumnNames(Checked)),
    Typed = Table.TransformColumnTypes(Nulls, {
        {"route_key", type text},
        {"origin_airport_id", Int64.Type},
        {"destination_airport_id", Int64.Type}
    }, "en-US")
in
    Typed
