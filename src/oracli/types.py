from enum import StrEnum


class DbKind(StrEnum):
    oracle = "oracle"
    duckdb = "duckdb"


class Encoding(StrEnum):
    utf_8 = "utf-8"
    cp932 = "cp932"


class OutputKind(StrEnum):
    csv = "csv"
    parquet = "parquet"


class PathKind(StrEnum):
    file = "file"
    dir = "dir"
    csv_or_parquet = "csv_or_parquet"
    sql = "sql"
    yaml = "yaml"
