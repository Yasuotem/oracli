import logging
from enum import StrEnum
from pathlib import Path
from typing import Annotated, ClassVar, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field

from oracli.db import DbKind

log = logging.getLogger(__name__)


class Encoding(StrEnum):
    utf_8 = "utf-8"
    cp932 = "cp932"


type Output = Annotated[Csv | Parquet, Field(discriminator="type")]


class OutputKind(StrEnum):
    csv = "csv"
    parquet = "parquet"


class Csv(BaseModel):
    model_config = ConfigDict(extra="forbid")
    SUFFIX: ClassVar[str] = ".csv"
    type: Literal[OutputKind.csv]
    encoding: Encoding = Encoding.cp932


class Parquet(BaseModel):
    model_config = ConfigDict(extra="forbid")
    SUFFIX: ClassVar[str] = ".parquet"
    type: Literal[OutputKind.parquet]


class Step(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    sql: Path
    output: Output
    output_path: Path
    file_name: str = "{step_name}_{date}"

    def load_sql(self) -> str:
        with self.sql.open("r", encoding="utf-8") as f:
            sql_text = f.read()

        return sql_text


class Job(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    db: DbKind
    steps: list[Step]


def load_job(path: Path) -> Job:
    log.debug("load job file %s", path)
    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    return Job.model_validate(raw)


def save_job(job: Job, path: Path):
    with path.open("w") as f:
        yamltext = yaml.safe_dump(
            job.model_dump(mode="json"), allow_unicode=False, sort_keys=False
        )
        log.debug("yaml dump text: %s", yamltext)
        f.write(yamltext)
