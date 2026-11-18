import logging
from pathlib import Path
from typing import Annotated

import typer

from oracli.db import DbKind, get_db
from oracli.job import Step
from oracli.output import Csv, OutputKind, Parquet
from oracli.prompt import PathKind, prompt_enum, prompt_path, prompt_text

from .run import do_steps

log = logging.getLogger(__name__)


def query(
    dsn: Annotated[str | None, typer.Argument(help="dbの接続文字列")] = None,
    db_client: Annotated[DbKind | None, typer.Option(help="db名")] = None,
    sql: Annotated[Path | None, typer.Option(help="sql")] = None,
    output: Annotated[Path | None, typer.Option(help="出力先のファイルパス")] = None,
):
    """DBを指定してクエリとファイル出力を行う"""

    dsn = prompt_text(dsn, "DBの接続文字列を入力してください")

    db_client = prompt_enum(db_client, "DBを選択してください", DbKind)

    sql = prompt_path(sql, "sqlファイルのファイルパスを指定してください", PathKind.sql)

    output = prompt_path(output, "出力先のファイルパスを指定してください", PathKind.csv_or_parquet)
    match output.suffix:
        case ".csv":
            # encording
            out = Csv(path=output, file_name="", type=OutputKind.csv)
        case ".parquet":
            out = Parquet(path=output, file_name="", type=OutputKind.parquet)
        case _:
            raise ValueError()

    step = Step(name="", sql=sql, output=out)

    with get_db(db_client, dsn) as db:
        do_steps(db, [step])
