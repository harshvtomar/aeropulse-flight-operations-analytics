"""Generate reviewable Power Query imports; does not create or validate a PBIX."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TYPE_MAP = {"VARCHAR": "type text", "INTEGER": "Int64.Type", "BIGINT": "Int64.Type", "DOUBLE": "type number", "DATE": "type date", "BOOLEAN": "type logical"}
KEYS = {"dim_airlines": "airline_id", "dim_origin_airports": "origin_airport_id", "dim_destination_airports": "destination_airport_id", "dim_dates": "date_key", "dim_routes": "route_key", "dim_hours": "scheduled_hour"}


def generate(manifest, output):
    output = Path(output)
    (output / "queries").mkdir(parents=True, exist_ok=True)
    tables = []
    for entry in manifest["inventory"]:
        name = Path(entry["file"]).stem
        if name != "fact_flights" and name not in KEYS:
            continue
        columns = entry["columns"]
        types = ",\n        ".join('{"' + c["name"] + '", ' + TYPE_MAP[c["type"]] + '}' for c in columns)
        names = ", ".join(json.dumps(c["name"]) for c in columns)
        source = 'Parquet.Document(File.Contents(Path))' if name == 'fact_flights' else 'Table.PromoteHeaders(Csv.Document(File.Contents(Path), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]), [PromoteAllScalars=true])'
        script = f'''// Create a blank query named {name}; paste this entire expression.
let
    Path = Text.TrimEnd(pDataFolder, {{"/", "\\"}}) & "/{entry['file']}",
    Source = {source},
    Expected = {{{names}}},
    Checked = if List.Count(List.Difference(Expected, Table.ColumnNames(Source))) = 0 and List.Count(List.Difference(Table.ColumnNames(Source), Expected)) = 0 then Source else error "Export schema differs from the Session 3 contract",
    Nulls = Table.ReplaceValue(Checked, "", null, Replacer.ReplaceValue, Table.ColumnNames(Checked)),
    Typed = Table.TransformColumnTypes(Nulls, {{
        {types}
    }}, "en-US")
in
    Typed
'''
        (output / 'queries' / f'{name}.m').write_text(script)
        tables.append({"name": name, "file": entry["file"], "columns": columns})
    relationships = [{"one_table": t, "one_column": k, "many_table": "fact_flights", "many_column": k, "active": True, "cross_filter": "Single"} for t, k in KEYS.items()]
    (output / 'model_contract.json').write_text(json.dumps({"artifact_type": "manual-build-contract-not-native-powerbi", "tables": tables, "relationships": relationships, "date_table": {"table": "dim_dates", "column": "flight_date"}}, indent=2) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, default=ROOT / 'reports/session2/BI_EXPORT_VALIDATION.json')
    parser.add_argument('--output', type=Path, default=ROOT / 'powerbi')
    args = parser.parse_args()
    generate(json.loads(args.manifest.read_text()), args.output)
