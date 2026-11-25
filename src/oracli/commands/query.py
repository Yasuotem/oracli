import logging
from datetime import datetime, time
from pathlib import Path
from typing import Annotated

import typer

from oracli.commands.run import do_step
from oracli.db import get_db
from oracli.job import Step
from oracli.output import Csv, Parquet
from oracli.prompt import prompt_enum, prompt_path
from oracli.settings import Settings
from oracli.types import EncodingKind, OutputKind, PathKind

log = logging.getLogger(__name__)


def query(
    sql: Annotated[Path | None, typer.Option(help="sql")] = None,
    output: Annotated[Path | None, typer.Option(help="出力先のファイルパス")] = None,
    dt: Annotated[datetime | None, typer.Option(help="作業日を指定する")] = None,
    encording: Annotated[
        EncodingKind | None, typer.Option(help="出力するcsvファイルのエンコードを指定")
    ] = None,
):
    """SQLを実行してファイル出力を行う"""

    settings = Settings()

    sql = prompt_path(sql, "sqlファイルのファイルパスを指定してください", PathKind.sql)

    output = prompt_path(
        output, "出力先のファイルパスを指定してください", PathKind.output
    )

    if dt is None:
        dt = datetime.now()

    start = time(9, 0)

    match output.suffix:
        case ".csv":
            encording = prompt_enum(
                encording, "csvファイルのエンコードを選択してください", EncodingKind
            )
            out = Csv(
                path=output, file_name="", type=OutputKind.csv, encoding=encording
            )
        case ".parquet":
            out = Parquet(path=output, file_name="", type=OutputKind.parquet)
        case _:
            raise ValueError()

    step = Step(name="", sql=sql, output=out)

    with get_db(settings) as db:
        do_step(db, step, dt, start)
