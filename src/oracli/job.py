import logging
from datetime import time
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict

from oracli.output import OutputType

log = logging.getLogger(__name__)


class Step(BaseModel):
    """SQLを実行するジョブステップの定義
    SQLファイルの読み込みを担当する"""

    model_config = ConfigDict(extra="forbid")
    name: str
    sql: Path
    output: OutputType

    def load_sql(self) -> str:
        with self.sql.open("r", encoding="utf-8") as f:
            sql_text = f.read()

        return sql_text


class Job(BaseModel):
    """ジョブの定義"""

    model_config = ConfigDict(extra="forbid")
    name: str
    steps: list[Step]
    business_day_start: time


def load_job(path: Path) -> Job:
    """Jobファイルを読み込む"""
    log.debug("load job file %s", path)
    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    return Job.model_validate(raw)


def save_job(job: Job, path: Path):
    """Jobファイルを保存する"""
    with path.open("w", encoding="utf-8") as f:
        yamltext = yaml.safe_dump(
            job.model_dump(mode="json"), allow_unicode=True, sort_keys=False
        )
        log.debug("yaml dump text: %s", yamltext)
        f.write(yamltext)
