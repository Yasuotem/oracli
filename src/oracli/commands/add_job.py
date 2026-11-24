import logging
from datetime import time
from pathlib import Path
from typing import Annotated

import typer

from oracli.db import DbKind
from oracli.job import Job, save_job
from oracli.prompt import prompt_enum, prompt_text, prompt_time

log = logging.getLogger(__name__)


def add_job(
    name: Annotated[str | None, typer.Argument(help="Job名")] = None,
    db: Annotated[
        DbKind | None, typer.Option("--db", help="DBを指定 oracle | duckdb")
    ] = None,
    start: Annotated[
        time | None, typer.Option(help="作業日の開始時間を指定する")
    ] = None,
):
    name = prompt_text(name, "新規作成するジョブ名を入力してください")

    db = prompt_enum(db, "使用するDBを選択してください", DbKind)

    start = prompt_time(start, "作業日の開始時間を入力してください")

    job = Job(name=name, db=db, steps=[], business_day_start=start)
    filepath = Path(f"{name}.yaml")

    save_job(job, filepath)

    typer.echo(f"ジョブファイル: {filepath} が作成されました")
