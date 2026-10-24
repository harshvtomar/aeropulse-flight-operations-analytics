// Create a blank query named dim_hours; paste this entire expression.
let
    Path = Text.TrimEnd(pDataFolder, {"/", "\"}) & "/dim_hours.csv",
    Source = Table.PromoteHeaders(Csv.Document(File.Contents(Path), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]), [PromoteAllScalars=true]),
    Expected = {"scheduled_hour", "hour_label"},
    Checked = if List.Count(List.Difference(Expected, Table.ColumnNames(Source))) = 0 and List.Count(List.Difference(Table.ColumnNames(Source), Expected)) = 0 then Source else error "Export schema differs from the Session 3 contract",
    Nulls = Table.ReplaceValue(Checked, "", null, Replacer.ReplaceValue, Table.ColumnNames(Checked)),
    Typed = Table.TransformColumnTypes(Nulls, {
        {"scheduled_hour", Int64.Type},
        {"hour_label", type text}
    }, "en-US")
in
    Typed
