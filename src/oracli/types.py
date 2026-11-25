from enum import StrEnum


class DbKind(StrEnum):
    oracle = "oracle"
    duckdb = "duckdb"


class EncodingKind(StrEnum):
    utf_8 = "utf-8"
    cp932 = "cp932"


class OutputKind(StrEnum):
    csv = "csv"
    parquet = "parquet"


class PathKind(StrEnum):
    file = "file"
    dir = "dir"
    path = "path"
    output = "output"
    sql = "sql"
    yaml = "yaml"


class TextKind(StrEnum):
    datetime = "datetime"
    date = "date"
    time = "time"
    str = "str"
