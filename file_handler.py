import os
import logging
from datetime import datetime
from .file_formatter import FileFormatter


class FileHandler(logging.FileHandler):
    """
    Handle writes to file.
    """
    def __init__(
        self,
        mode: str = "a",
        encoding: str | None = None,
        delay: bool = False,
        errors: str | None = None,
    ) -> None:
        """ """
        self.__filename = "App_{}-{}-{}_{}-{}.log".format(
            str(datetime.now().year),
            str(datetime.now().month),
            str(datetime.now().day),
            str(datetime.now().hour),
            str(datetime.now().minute),
        )
        os.makedirs("logs", exist_ok=True)
        self.__file_path = os.path.join("logs", self.__filename)

        super().__init__(self.__file_path, mode, encoding, delay, errors)

        self.__log_level = logging.DEBUG
        self.__format_str = "%(levelname)-8s, %(name)s, %(message)s"
        self.__formatter = FileFormatter(fmt=self.__format_str)
        self.setFormatter(self.__formatter)
        self.setLevel(self.__log_level)
