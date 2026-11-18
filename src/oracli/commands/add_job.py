import logging
from pathlib import Path
from typing import Annotated

import typer

from oracli.db import DbKind
from oracli.job import Job, save_job
from oracli.prompt import prompt_enum, prompt_text

log = logging.getLogger(__name__)


def add_job(
    name: Annotated[str | None, typer.Argument(help="Job名")] = None,
    db: Annotated[
        DbKind | None, typer.Option("--db", help="DBを指定 oracle | duckdb")
    ] = None,
):
    name = prompt_text(name, "新規作成するジョブ名を入力してください")

    db = prompt_enum(db, "使用するDBを選択してください", DbKind)

    job = Job(name=name, db=db, steps=[])
    filepath = Path(f"{name}.yaml")

    save_job(job, filepath)

    typer.echo(f"ジョブファイル: {filepath} が作成されました")
