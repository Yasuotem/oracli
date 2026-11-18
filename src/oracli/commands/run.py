import logging
from datetime import datetime
from pathlib import Path
from typing import Annotated

import typer

from oracli.db import DbClient, DbError, get_db
from oracli.job import Step, load_job
from oracli.template_variables import get_filename_ctx

log = logging.getLogger(__name__)


def run(
    job_file: Annotated[Path, typer.Argument(help="Jobが記載されたyamlファイル")],
    dsn: Annotated[str, typer.Argument(help="DBの接続文字列")],
):
    """Jobを実行する"""
    try:
        job = load_job(job_file)
    except Exception:
        log.exception("Jobの読み込みに失敗しました", extra={"job_file": job_file})
        raise typer.Exit(1)

    try:
        with get_db(job.db, dsn) as db:
            do_steps(db, job.steps)

    except Exception:
        log.exception("Jobの実行に失敗しました", extra={"job": job.name})
        raise typer.Exit(1)


def do_steps(db: DbClient, steps: list[Step]):
    """Stepを順番に実行する"""

    dt = datetime.now()

    for step in steps:

        try:
            sql = step.load_sql()

            tbl = db.query(sql)

            try:
                ctx = get_filename_ctx(step.name, dt)
            except KeyError as e:
                log.error(f"不明なテンプレート変数: {e}")
                continue

            step.output.write(tbl, ctx)

        except (FileNotFoundError, DbError) as e:
            log.error(f"Step:{step.name} {e}")
            continue
