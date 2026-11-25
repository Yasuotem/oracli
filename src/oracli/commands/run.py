import logging
from datetime import datetime
from pathlib import Path
from typing import Annotated

import typer

from oracli.db import DbError, get_db
from oracli.job import load_job
from oracli.settings import Settings
from oracli.template_variables import extract_sql_params, get_filename_ctx, get_sql_ctx

log = logging.getLogger(__name__)


def run(
    job_file: Annotated[Path, typer.Argument(help="Jobが記載されたyamlファイル")],
    dt: Annotated[datetime | None, typer.Option(help="作業日を指定する")] = None,
):
    """Jobを実行する"""
    log.info("Start and loading Settings, Job")
    settings = Settings()
    log.debug("Settings: %s", settings)

    try:
        job = load_job(job_file)
        log.debug("job: %s", job)

    except Exception:
        log.exception("Job file load failed", extra={"job_file": job_file})
        raise typer.Exit(1)

    log.info("Executing Job: %s", job.name)
    log.info("Connecting %s", settings.db)
    try:
        with get_db(settings) as db:
            log.info("Connected %s", settings.db)

            if dt is None:
                dt = datetime.now()
            log.debug("dt: %s", dt)

            for step in job.steps:
                log.info("Executing Step: %s", step.name)
                try:
                    sql = step.load_sql()
                    sql_ctx = get_sql_ctx(dt, job.business_day_start)

                    params, rest = extract_sql_params(sql, sql_ctx)
                    log.debug("params: %s keys: %s", params, rest)

                    filename_ctx = get_filename_ctx(step.name, dt)

                    tbl = db.query(sql, params)

                    step.output.write(tbl, filename_ctx)

                except (FileNotFoundError, DbError, KeyError) as e:
                    log.error(f"Step [{step.name}] execution failed:  {e}")
                    continue

    except Exception:
        log.exception("Job execution failed", extra={"job": job.name})
        raise typer.Exit(1)

    log.info("Job: %s finished", job.name)
