from enum import StrEnum
from typing import Protocol, Self

import duckdb
import oracledb
import pyarrow as pa
import sqlglot


class DbError(Exception):
    """DBError"""


class DbKind(StrEnum):
    oracle = "oracle"
    duckdb = "duckdb"


class DbClient(Protocol):
    def __init__(self, connection_string: str): ...
    def query(self, sql: str) -> pa.Table: ...
    def close(self) -> None: ...
    def __enter__(self) -> Self: ...
    def __exit__(self, exc_type, exc_value, traceback) -> None: ...


def get_db(db_client: DbKind, dsn: str) -> DbClient:
    match db_client:
        case DbKind.oracle:
            return Oracle(dsn)
        case DbKind.duckdb:
            return Duckdb(dsn)


class Oracle:
    def __init__(self, dsn: str):
        try:
            self.conn = oracledb.connect(dsn)
        except oracledb.Error as e:
            raise DbError("oracledb接続失敗") from e

    def close(self):
        self.conn.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def query(self, sql: str) -> pa.Table:
        try:
            return pa.table(self.conn.fetch_df_all(sql))
        except oracledb.Error as e:
            raise DbError("oralcedbSQL実行失敗") from e


class Duckdb:
    def __init__(self, connection_string: str):
        try:
            self.conn = duckdb.connect(connection_string)
        except duckdb.Error as e:
            raise DbError("duckdb接続失敗") from e

    def close(self):
        self.conn.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def query(self, sql: str) -> pa.Table:
        try:
            duckdb_sql = sqlglot.transpile(sql, read="oracle", write="duckdb")
            return self.conn.sql(duckdb_sql[0]).to_arrow_table()
        except (duckdb.Error, sqlglot.ParseError) as e:
            raise DbError("duckdbSQL実行失敗") from e
