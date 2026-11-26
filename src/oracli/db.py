import logging
from typing import Protocol, Self

import duckdb
import oracledb
import pyarrow as pa
import sqlglot

from oracli.settings import Settings
from oracli.types import DbKind

log = logging.getLogger(__name__)


class DbError(Exception):
    """DBError"""


class DbClient(Protocol):
    def query(self, sql: str, params: dict) -> pa.Table: ...
    def close(self) -> None: ...
    def __enter__(self) -> Self: ...
    def __exit__(self, exc_type, exc_value, traceback) -> None: ...


def get_db(settings: Settings) -> DbClient:
    match settings.db:
        case DbKind.oracle:
            return Oracle(settings)
        case DbKind.duckdb:
            return Duckdb(settings)


class Oracle:
    def __init__(self, settings: Settings):
        try:
            self.conn = oracledb.connect(
                user=settings.user, dsn=settings.dsn, password=settings.password
            )
        except oracledb.Error as e:
            raise DbError("oracledb　connection failed") from e

    def close(self):
        self.conn.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def query(self, sql: str, params: dict) -> pa.Table:
        """sqlを実行してarrow tableを返す"""
        try:
            return pa.table(self.conn.fetch_df_all(sql, params))
        except oracledb.Error as e:
            raise DbError("oralcedb SQL execution failed") from e


class Duckdb:
    def __init__(self, settings: Settings):
        if settings.path is None:
            raise DbError("path is undefined")
        try:
            self.conn = duckdb.connect(settings.path)
        except duckdb.Error as e:
            raise DbError("duckdb connection failed") from e

    def close(self):
        self.conn.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def query(self, sql: str, params: dict) -> pa.Table:
        """sqlをduckdbのsqlに変換して実行してarrow tableを返す"""
        try:
            duckdb_sql = sqlglot.transpile(sql, read="oracle", write="duckdb")
            log.debug("duckdbSQL: %s", duckdb_sql)
            return self.conn.sql(duckdb_sql[0], params=params).to_arrow_table()
        except (duckdb.Error, sqlglot.ParseError) as e:
            raise DbError("duckdb SQL execution failed") from e
