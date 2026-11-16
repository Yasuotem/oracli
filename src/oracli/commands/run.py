import logging
from datetime import datetime
from pathlib import Path
from typing import Annotated

import pyarrow
import typer
from pyarrow import csv, parquet

from oracli.db import DbClient, DbError, get_db
from oracli.job import Csv, Output, Parquet, Step, load_job
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
        ctx = get_filename_ctx(step.name, dt)

        try:
            sql = step.load_sql()

            tbl = db.query(sql)
            try:
                path = (step.output_path / step.file_name.format(**ctx)).with_suffix(
                    step.output.SUFFIX
                )
            except KeyError as e:
                log.error(f"不明なテンプレート変数: {e}")
                continue

            do_output(tbl, step.output, path)

        except (FileNotFoundError, DbError) as e:
            log.error(f"Step:{step.name} {e}")
            continue


def do_output(tbl: pyarrow.Table, output: Output, path: Path):
    """テーブルを出力する"""

    match output:
        case Csv(encoding=encoding):
            options = csv.WriteOptions(encoding=encoding)
            csv.write_csv(tbl, path, options)

        case Parquet():
            parquet.write_table(tbl, path)
