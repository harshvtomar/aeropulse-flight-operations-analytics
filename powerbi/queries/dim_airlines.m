// Create a blank query named dim_airlines; paste this entire expression.
let
    Path = Text.TrimEnd(pDataFolder, {"/", "\"}) & "/dim_airlines.csv",
    Source = Table.PromoteHeaders(Csv.Document(File.Contents(Path), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]), [PromoteAllScalars=true]),
    Expected = {"airline_id", "airline_code"},
    Checked = if List.Count(List.Difference(Expected, Table.ColumnNames(Source))) = 0 and List.Count(List.Difference(Table.ColumnNames(Source), Expected)) = 0 then Source else error "Export schema differs from the Session 3 contract",
    Nulls = Table.ReplaceValue(Checked, "", null, Replacer.ReplaceValue, Table.ColumnNames(Checked)),
    Typed = Table.TransformColumnTypes(Nulls, {
        {"airline_id", Int64.Type},
        {"airline_code", type text}
    }, "en-US")
in
    Typed
