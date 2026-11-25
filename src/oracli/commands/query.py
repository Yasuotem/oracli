import logging
from datetime import datetime, time
from pathlib import Path
from typing import Annotated

import typer

from oracli.db import get_db
from oracli.job import Step
from oracli.output import Csv, Parquet
from oracli.prompt import prompt_enum, prompt_path, prompt_text
from oracli.settings import Settings
from oracli.template_variables import extract_sql_params, get_filename_ctx, get_sql_ctx
from oracli.types import EncodingKind, OutputKind, PathKind, TextKind

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
        sql_text = step.load_sql()
        sql_ctx = get_sql_ctx(dt, start)

        params, rest = extract_sql_params(sql_text, sql_ctx)
        log.debug("params: %s keys: %s", params, rest)

        for key in rest:
            typer.echo(f"SQLのバインド変数{key}が未定義です")
            param_type = prompt_enum(None, f"{key}のTypeを選択してください", TextKind)
            params[key] = prompt_text(None, f"{key}の値を入力してください", param_type)

        filename_ctx = get_filename_ctx(step.name, dt)

        tbl = db.query(sql_text, params)

        step.output.write(tbl, filename_ctx)
