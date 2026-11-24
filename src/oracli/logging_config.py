import logging


def config_logging(debug: bool = False) -> None:
    root = logging.getLogger("oracli")
    root.handlers.clear()

    root.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(name)-24s %(message)s")

    file_handler = logging.FileHandler("oracli.log", encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    if debug:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        root.addHandler(console_handler)
