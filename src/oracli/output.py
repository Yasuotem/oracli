import io
import logging
from pathlib import Path
from typing import Annotated, ClassVar, Literal

import pyarrow as pa
from pyarrow import csv, parquet
from pydantic import BaseModel, ConfigDict, Field

from oracli.types import EncodingKind, OutputKind

log = logging.getLogger(__name__)


type OutputType = Annotated[Csv | Parquet, Field(discriminator="type")]


class OutputError(Exception):
    """OutputError"""


class Output(BaseModel):
    model_config = ConfigDict(extra="forbid")

    def prepare_path(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)


class Csv(Output):
    SUFFIX: ClassVar[str] = ".csv"
    path: Path
    file_name: str = "{step_name}_{date}"
    type: Literal[OutputKind.csv]
    encoding: EncodingKind = EncodingKind.cp932

    def write(self, tbl: pa.Table, ctx: dict):
        try:
            file_path = (self.path / self.file_name.format(**ctx)).with_suffix(
                self.SUFFIX
            )

            buf = io.BytesIO()
            csv.write_csv(tbl, buf)

            self.prepare_path(file_path)

            with file_path.open("w", encoding=self.encoding, newline="") as f:
                f.write(buf.getvalue().decode("utf-8"))

        except (OSError, pa.ArrowException) as e:
            raise OutputError("OutputError") from e


class Parquet(Output):
    SUFFIX: ClassVar[str] = ".parquet"
    path: Path
    type: Literal[OutputKind.parquet]
    file_name: str = "{step_name}_{date}"

    def write(self, tbl: pa.Table, ctx: dict):
        try:
            file_path = (self.path / self.file_name.format(**ctx)).with_suffix(
                self.SUFFIX
            )
            self.prepare_path(file_path)
            parquet.write_table(tbl, file_path)
        except (OSError, pa.ArrowException) as e:
            raise OutputError("OutputError") from e
