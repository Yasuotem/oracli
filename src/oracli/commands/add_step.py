import logging
from pathlib import Path
from typing import Annotated

import typer

from oracli.job import Step, load_job, save_job
from oracli.output import Csv, OutputKind, Parquet
from oracli.prompt import PathKind, prompt_enum, prompt_path, prompt_text
from oracli.types import EncodingKind, TextKind

log = logging.getLogger(__name__)


def add_step(
    jobfile: Annotated[
        Path | None, typer.Argument(help="Jobファイルのファイルパス")
    ] = None,
    name: Annotated[str | None, typer.Option(help="Step名")] = None,
    sql: Annotated[Path | None, typer.Option(help="Sqlファイルのファイルパス")] = None,
    out_type: Annotated[
        OutputKind | None, typer.Option(help="出力するファイルの種類")
    ] = None,
    out_path: Annotated[Path | None, typer.Option(help="出力先のパス")] = None,
    encording: Annotated[
        EncodingKind | None, typer.Option(help="出力するcsvファイルのエンコードを指定")
    ] = None,
):
    """JobファイルにStepを追加します"""

    jobfile = prompt_path(jobfile, "Jobファイルを指定してください", PathKind.yaml)

    job = load_job(jobfile)
    log.debug("Job: %s", job)

    name = prompt_text(name, "追加するステップ名を入力してください", TextKind.str)

    sql = prompt_path(sql, "Sqlファイルのファイルパスを指定してください", PathKind.sql)

    out_type = prompt_enum(
        out_type, "出力するファイルの種類を指定してください", OutputKind
    )

    out_path = prompt_path(out_path, "出力先のパスを指定してください", PathKind.path)

    match out_type:
        case OutputKind.csv:
            encording = prompt_enum(
                encording, "csvファイルのエンコードを指定してください", EncodingKind
            )
            output = Csv(type=OutputKind.csv, path=out_path, encoding=encording)
        case OutputKind.parquet:
            output = Parquet(type=OutputKind.parquet, path=out_path)

    step = Step(
        name=name,
        sql=sql,
        output=output,
    )

    job.steps.append(step)

    save_job(job, jobfile)

    typer.echo(f"step: {step.name}の追加が完了しました")
