
import logging
from enum import StrEnum
from typing import Annotated, ClassVar

import pyarrow as pa
from pyarrow import csv, parquet
from pydantic import BaseModel, ConfigDict, Field

log = logging.getLogger(__name__)


class Encoding(StrEnum):
    utf_8 = "utf-8"
    cp932 = "cp932"


type Output = Annotated[Csv | Parquet, Field(discriminator="type")]


class OutputKind(StrEnum):
    csv = "csv"
    parquet = "parquet"

class OutputError(Exception):
    """OutputError"""


class Csv(BaseModel):
    model_config = ConfigDict(extra="forbid")
    SUFFIX: ClassVar[str] = ".csv"
    path: Path
    file_name: str = "{step_name}_{date}"
    type: OutputKind = OutputKind.csv
    encoding: Encoding = Encoding.cp932

    def write(self, tbl: pa.Table, path: Path):
        options = csv.WriteOptions(encoding=self.encoding)
        csv.write_csv(tbl, path, options)


class Parquet(BaseModel):
    model_config = ConfigDict(extra="forbid")
    SUFFIX: ClassVar[str] = ".parquet"
    path: Path
    type: OutputKind = OutputKind.parquet
    file_name: str = "{step_name}_{date}"

    def write(self, tbl: pa.Table, path: Path):
        try:
            parquet.write_table(tbl, path)
        except (OSError, pa.ArrowException) as e:
           raise OutputError("OutputError") from e
