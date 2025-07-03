import logging

from .stream_formatter import StreamFormatter


# noinspection PyMissingOrEmptyDocstring
class StreamHandler(logging.StreamHandler):

    def __init__(self):
        """ """
        super().__init__()

        self.__log_level = logging.DEBUG
        self.__format_str = "[%(levelname)-8s] %(name)s, %(message)s"
        self.__formatter = StreamFormatter(fmt=self.__format_str)
        self.setFormatter(self.__formatter)
        self.setLevel(self.__log_level)
