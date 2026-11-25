import logging
from collections.abc import Callable
from datetime import time
from enum import StrEnum
from pathlib import Path

import questionary

from oracli.types import PathKind

log = logging.getLogger(__name__)

type PathValidator = Callable[[str], bool]


validators: dict[PathKind, PathValidator] = {
    PathKind.file: lambda x: Path(x).is_file(),
    PathKind.dir: lambda x: Path(x).is_dir(),
    PathKind.path: lambda x: Path(x).parent.exists(),
    PathKind.output: lambda x: Path(x).parent.exists() and Path(x).suffix in (".csv", ".parquet"),
    PathKind.sql: lambda x: Path(x).is_file() and Path(x).suffix in (".sql"),
    PathKind.yaml: lambda x: Path(x).is_file() and Path(x).suffix in (".yaml"),
}


def prompt_path(value: Path | None, msg: str, kind: PathKind) -> Path:
    """valueがバリデーションに適合しない場合入力プロンプトを表示する"""
    if value is not None and validators[kind](str(value)):
        return value

    text = questionary.path(msg, validate=validators[kind]).ask()

    assert text is not None
    return Path(text)


def prompt_enum[T: StrEnum](value: T | None, msg: str, enum_type: type[T]) -> T:
    """valueがNoneの場合入力プロンプトを表示する"""
    if value is not None:
        return value

    choices = [questionary.Choice(title=e.value, value=e) for e in enum_type]
    enum = questionary.select(msg, choices=choices).ask()

    assert enum is not None
    return enum


def prompt_text(value: str | None, msg: str) -> str:
    """valueがNoneの場合入力プロンプトを表示する"""
    if value is not None:
        return value
    text = questionary.text(msg).ask()

    assert text is not None
    return text


def prompt_time(value: time | None, msg: str) -> time:
    def validator(value: str):
        try:
            time.fromisoformat(value)
            return True
        except ValueError:
            return False

    if value is not None:
        return value

    text = questionary.text(msg, validate=validator).ask()

    assert text is not None
    return time.fromisoformat(text)
