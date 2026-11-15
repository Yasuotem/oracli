from typing import Annotated

import typer

from .commands import add_job, add_step, check, query, run
from .logging_config import config_logging

app = typer.Typer()


@app.callback()
def main(
    debug: Annotated[
        bool, typer.Option("--debug", "-d", help="DEBUGログを表示する")
    ] = False,
):
    config_logging(debug)


app.command()(run.run)
app.command()(query.query)
app.command()(check.check)
app.command()(add_job.add_job)
app.command()(add_step.add_step)


if __name＿_ == "__main__":
    app()
