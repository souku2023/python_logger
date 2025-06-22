import logging


class StreamFormatter(logging.Formatter):

    def formatException(self, exc_info):
        result = f"{exc_info[1].__class__.__qualname__}: {exc_info[1]}"
        return result

    # Ignoring stack info in sys.stdout
    def formatStack(self, stack_info: str) -> str:
        return ""

    def formatMessage(self, record: logging.LogRecord) -> str:
        """Custom message formatting: for console only the last child is
        printed"""
        if "__main__" not in record.name:
            split_name = record.name.split(".")
            record.name = split_name[-1].upper()

        return super().formatMessage(record)

    def format(self, record):
        s = super(StreamFormatter, self).format(record)
        if record.exc_text:
            s = s.replace("\n", ", ").strip()
        s = s.replace("\nNoneType: None", "")
        return s
