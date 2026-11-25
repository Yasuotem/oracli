import json
import logging
from pathlib import Path
from typing import Annotated

import pydantic
import sqlglot
import typer

from oracli.job import load_job
from oracli.prompt import prompt_path
from oracli.types import PathKind

log = logging.getLogger(__name__)


def check(
    job_file: Annotated[
        Path | None, typer.Argument(help="Jobが記載されたyamlファイル")
    ] = None,
):
    """Jobファイルに登録されているSQLの構文チェックを行う"""

    job_file = prompt_path(job_file, "Jobファイルを選択してください", PathKind.yaml)

    try:
        job = load_job(job_file)
    except pydantic.ValidationError as e:
        typer.echo(f"- {job_file}: ValidationError")
        typer.echo(e.errors())
        raise typer.Exit(1)

    for step in job.steps:
        try:
            sql = step.load_sql()
            sqlglot.parse_one(sql, dialect="oracle")
            typer.echo(f"{step.sql}: ok")

        except FileNotFoundError as e:
            typer.echo(e)
            continue
        except sqlglot.ParseError as e:
            typer.echo(f"{step.sql}: ParseError")
            typer.echo(json.dumps(e.errors, indent=2, ensure_ascii=False))
            continue

    typer.echo(f"{job.name}: All check finished.")
