from enum import StrEnum
from pathlib import Path

import questionary


class PathKind(StrEnum):
    file = "file"
    dir = "dir"


validators = {
    PathKind.file: lambda x: Path(x).is_file(),
    PathKind.dir: lambda x: Path(x).is_dir(),
}


def prompt_path(msg: str, kind: PathKind) -> Path:

    value = questionary.path(msg, validate=validators[kind]).ask()

    assert value is not None
    return Path(value)


def prompt_enum[T: StrEnum](msg: str, enum_type: type[T]) -> T:

    choices = [questionary.Choice(title=e.value, value=e) for e in enum_type]
    value = questionary.select(msg, choices=choices).ask()

    assert value is not None
    return value


def prompt_text(msg: str) -> str:

    value = questionary.text(msg).ask()

    assert value is not None
    return value
