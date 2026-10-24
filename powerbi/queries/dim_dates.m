// Create a blank query named dim_dates; paste this entire expression.
let
    Path = Text.TrimEnd(pDataFolder, {"/", "\"}) & "/dim_dates.csv",
    Source = Table.PromoteHeaders(Csv.Document(File.Contents(Path), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]), [PromoteAllScalars=true]),
    Expected = {"date_key", "flight_date", "year", "month", "day_of_week", "is_weekend"},
    Checked = if List.Count(List.Difference(Expected, Table.ColumnNames(Source))) = 0 and List.Count(List.Difference(Table.ColumnNames(Source), Expected)) = 0 then Source else error "Export schema differs from the Session 3 contract",
    Nulls = Table.ReplaceValue(Checked, "", null, Replacer.ReplaceValue, Table.ColumnNames(Checked)),
    Typed = Table.TransformColumnTypes(Nulls, {
        {"date_key", Int64.Type},
        {"flight_date", type date},
        {"year", Int64.Type},
        {"month", Int64.Type},
        {"day_of_week", Int64.Type},
        {"is_weekend", type logical}
    }, "en-US")
in
    Typed
