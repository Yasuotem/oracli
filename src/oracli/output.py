
import logging
from enum import StrEnum
from pathlib import Path
from typing import Annotated, ClassVar, Literal

import pyarrow as pa
from pyarrow import csv, parquet
from pydantic import BaseModel, ConfigDict, Field

log = logging.getLogger(__name__)


class Encoding(StrEnum):
    utf_8 = "utf-8"
    cp932 = "cp932"


type OutputType = Annotated[Csv | Parquet, Field(discriminator="type")]


class OutputKind(StrEnum):
    csv = "csv"
    parquet = "parquet"


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
    encoding: Encoding = Encoding.cp932

    def write(self, tbl: pa.Table, ctx: dict):
        try:
            file_path = (self.path / self.file_name.format(**ctx)).with_suffix(self.SUFFIX)
            self.prepare_path(file_path)
            options = csv.WriteOptions(encoding=self.encoding)
            csv.write_csv(tbl, file_path, options)
        except (OSError, pa.ArrowException) as e:
            raise OutputError("OutputError") from e


class Parquet(Output):
    SUFFIX: ClassVar[str] = ".parquet"
    path: Path
    type: Literal[OutputKind.parquet]
    file_name: str = "{step_name}_{date}"

    def write(self, tbl: pa.Table, ctx: dict):
        try:
            file_path = (self.path / self.file_name.format(**ctx)).with_suffix(self.SUFFIX)
            self.prepare_path(file_path)
            parquet.write_table(tbl, self.path)
        except (OSError, pa.ArrowException) as e:
           raise OutputError("OutputError") from e
