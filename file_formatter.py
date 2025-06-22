import logging


class FileFormatter(logging.Formatter):
    def formatException(self, exc_info):
        result = super().formatException(exc_info)
        result = "\n\t".join(result.splitlines())
        return result

    def formatStack(self, stack_info: str) -> str:
        return "\t" + "\n\t".join(super().formatStack(stack_info).split("\n"))

    def formatMessage(self, record: logging.LogRecord) -> str:
        """Custom message formatting: for console only the last child is
        printed"""
        if "__main__" not in record.name:
            split_name = record.name.split(".")
            record.name = split_name[-1].upper()

        return super().formatMessage(record)

    def format(self, record):
        s = super().format(record)
        if record.exc_text:
            s = s.replace("\nNoneType: None", "")
            s = s.replace("\n", "\n\t").strip()
        return s
