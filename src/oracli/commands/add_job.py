import logging
from datetime import time
from pathlib import Path
from typing import Annotated

import typer

from oracli.job import Job, save_job
from oracli.prompt import prompt_text
from oracli.types import TextKind

log = logging.getLogger(__name__)


def add_job(
    name: Annotated[str | None, typer.Argument(help="Job名")] = None,
    start: Annotated[
        time | None, typer.Option(help="作業日の開始時間を指定する")
    ] = None,
):
    """新規Jobファイルを作成"""
    name = prompt_text(name, "新規作成するジョブ名を入力してください", TextKind.str)

    start = prompt_text(start, "作業日の開始時間を入力してください", TextKind.time)

    job = Job(name=name, steps=[], business_day_start=start)
    filepath = Path(f"{name}.yaml")

    save_job(job, filepath)

    typer.echo(f"ジョブファイル: {filepath} が作成されました")
