import logging
from pathlib import Path
from typing import Annotated

import typer
from pyarrow import csv, parquet

from oracli.db import DbKind, get_db

log = logging.getLogger(__name__)


def query(
    db_client: Annotated[DbKind, typer.Argument(help="db名")],
    dsn: Annotated[str, typer.Argument(help="dbの接続文字列")],
    sql: Annotated[str, typer.Argument(help="sql")],
    output: Annotated[Path, typer.Argument(help="出力先のファイルパス")],
):
    """DBを指定してクエリとファイル出力を行う"""
    if output is None or not output.suffix in (".csv", ".parquet"):
        typer.echo("outputはcsvかparquetのファイルパスを指定してください")
        raise typer.Exit(1)

    with get_db(db_client, dsn) as db:
        tbl = db.query(sql)

        output.parent.mkdir(parents=True, exist_ok=True)
        if output.suffix == ".csv":
            csv.write_csv(tbl, output)
        elif output.suffix == ".parquet":
            parquet.write_table(tbl, output)
