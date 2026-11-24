import logging
from datetime import datetime, time
from pathlib import Path
from typing import Annotated

import typer

from oracli.db import DbClient, DbError, get_db
from oracli.job import Step, load_job
from oracli.settings import Settings
from oracli.template_variables import get_filename_ctx, get_sql_ctx

log = logging.getLogger(__name__)


def run(
    job_file: Annotated[Path, typer.Argument(help="Jobが記載されたyamlファイル")],
    dt: Annotated[datetime | None, typer.Option(help="作業日を指定する")] = None,
):
    """Jobを実行する"""
    settings = Settings()
    log.debug("Settings: %s", settings)

    try:
        job = load_job(job_file)
        log.debug("job: %s", job)

    except Exception:
        log.exception("Job file load failed", extra={"job_file": job_file})
        raise typer.Exit(1)

    try:
        with get_db(settings) as db:
            if dt is None:
                dt = datetime.now()
            log.debug("dt: %s", dt)

            for step in job.steps:
                try:
                    do_step(db, step, dt, job.business_day_start)
                except (FileNotFoundError, DbError, KeyError) as e:
                    log.error(f"Step [{step.name}] execution failed:  {e}")
                    continue

    except Exception:
        log.exception("Job execution failed", extra={"job": job.name})
        raise typer.Exit(1)


def do_step(db: DbClient, step: Step, dt: datetime, bussiness_day_start: time):
    """Stepを順番に実行する"""

    sql = step.load_sql()
    log.debug("sql: %s", sql)

    sql_ctx = get_sql_ctx(dt, bussiness_day_start)

    tbl = db.query(sql, sql_ctx)

    filename_ctx = get_filename_ctx(step.name, dt)

    step.output.write(tbl, filename_ctx)
