import logging
from pathlib import Path
from typing import Annotated

import typer

from oracli.job import Csv, OutputKind, Parquet, Step, load_job, save_job
from oracli.prompt import PathKind, prompt_enum, prompt_path, prompt_text

log = logging.getLogger(__name__)


def add_step(
    jobfile: Annotated[Path, typer.Argument(help="Jobファイルのファイルパス")],
    name: Annotated[str | None, typer.Option("--name", help="Step名")] = None,
    sql: Annotated[
        Path | None, typer.Option("--sql", help="Sqlファイルのファイルパス")
    ] = None,
    out_type: Annotated[
        OutputKind | None, typer.Option("--out-type", help="出力するファイルの種類")
    ] = None,
    out_path: Annotated[
        Path | None, typer.Option("--out-path", help="出力先のパス")
    ] = None,
):
    job = load_job(jobfile)

    if name is None:
        name = prompt_text("追加するステップ名を入力してください")

    if sql is None:
        sql = prompt_path("Sqlファイルのファイルパスを指定してください", PathKind.file)

    if out_type is None:
        out_type = prompt_enum("出力するファイルの種類を指定してください", OutputKind)

    if out_path is None:
        out_path = prompt_path("出力先のパスを指定してください", PathKind.dir)

    match out_type:
        case OutputKind.csv:
            output = Csv(type=OutputKind.csv)
        case OutputKind.parquet:
            output = Parquet(type=OutputKind.parquet)

    step = Step(
        name=name,
        sql=sql,
        output=output,
        output_path=out_path,
    )

    job.steps.append(step)

    save_job(job, jobfile)

    typer.echo(f"step: {step.name}の追加が完了しました")
