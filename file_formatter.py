import logging
from typing import override


# noinspection PyMissingOrEmptyDocstring
class FileFormatter(logging.Formatter):
    @override
    def formatException(self, exc_info):
        result = super().formatException(exc_info)
        result = "\n\t".join(result.splitlines())
        return result

    @override
    def formatStack(self, stack_info: str) -> str:
        return "\t" + "\n\t".join(super().formatStack(stack_info).split("\n"))

    @override
    def formatMessage(self, record: logging.LogRecord) -> str:
        if "__main__" not in record.name:
            split_name = record.name.split(".")
            record.name = split_name[-1].upper()

        return super().formatMessage(record)

    @override
    def format(self, record):
        s = super().format(record)
        if record.exc_text:
            s = s.replace("\nNoneType: None", "")
            s = s.replace("\n", "\n\t").strip()
        return s
