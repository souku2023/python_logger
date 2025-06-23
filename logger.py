"""
A simple Python logger configuration
"""
import atexit
import inspect
import logging
import queue
import threading
import traceback
from functools import partial
from types import FrameType
from typing import Any

from traceback import format_exception

# Import Custom Handlers
from .file_handler import FileHandler
from .stream_handler import StreamHandler


def format_traceback(e: Exception) -> str:
    """
    Format e.__traceback__ for Log message.
    """
    return "\nTraceback:" + "\n\t".join(
        traceback.format_tb(e.__traceback__) + ["Exception Info:"] \
            + format_exception(e)
    )


def __get_caller_info(frame: FrameType) -> str:
    """
    Get caller class and method name from the call stack.

    :parameter frame: The frame at the time the logger method was called
    """
    try:
        # Traverse back through the call stack frames
        while True:
            if frame is None:
                break
            class_name = "module"
            if "self" in frame.f_locals:
                class_name = frame.f_locals["self"].__class__.__name__
            elif "cls" in frame.f_locals:
                class_name = frame.f_locals["cls"].__name__
            else:
                # Use module name if no class found
                class_name = frame.f_globals.get("__name__", "module")
            frame = frame.f_back
            if "Logger" in class_name:
                break

        if frame is None:
            return "unknown.unknown"

        # Try to get class name from frame context
        class_name = "module"
        if "self" in frame.f_locals:
            class_name = frame.f_locals["self"].__class__.__name__
        elif "cls" in frame.f_locals:
            class_name = frame.f_locals["cls"].__name__
        else:
            # Use module name if no class found
            class_name = frame.f_globals.get("__name__", "module")

        method_name = frame.f_code.co_name
        return f"{class_name}.{method_name}"
    except Exception as e:
        print("Error getting caller info: ", format_traceback(e))
        return "unknown.unknown"
    finally:
        # Avoid reference cycles
        del frame


def format_message(frame, msg: Any) -> str:
    """Format message with caller tag"""
    caller_tag = __get_caller_info(frame)
    return f"{caller_tag}: {msg}"


class Logger(logging.Logger):
    """
    Logger class.
    """

    __log_queue = queue.Queue(-1)  # Unlimited size queue
    __background_thread = None
    __running = False

    def __init__(self, name: str, level: int | str = 0) -> None:
        """Class for Logging service for this app."""
        super().__init__(name, level)

        if Logger.__background_thread is None and Logger.__running is False:
            Logger.__start_background_logging()

        # Create handlers
        self.__stream_handler = StreamHandler()
        self.__file_handler = FileHandler()

        # Add handlers directly to logger
        self.addHandler(self.__stream_handler)
        self.addHandler(self.__file_handler)

    @staticmethod
    def __start_background_logging():
        """Start the background logging thread"""
        print("Logger.__start_background_logging, Starting logger thread")
        Logger.__running = True
        Logger.__background_thread = threading.Thread(
            target=Logger.__process_log_queue, daemon=True
        )
        Logger.__background_thread.start()
        atexit.register(Logger.shutdown)

    @staticmethod
    def __process_log_queue():
        """Process log records from the queue"""
        print("Logger.__process_log_queue, Starting Log processing thread")
        while Logger.__running or not Logger.__log_queue.empty():
            try:
                c = Logger.__log_queue.get(timeout=0.1)
                c()
            except queue.Empty:
                continue
            except Exception as e:
                # Fallback to stderr if logging fails
                print(f"Logger error: {e}")

    @staticmethod
    def shutdown():
        """Shutdown the logger and background thread"""
        Logger.__running = False
        if Logger.__background_thread and Logger.__background_thread.is_alive():
            Logger.__background_thread.join(timeout=1.0)
        Logger.__background_thread = None
        print("Logger.shutdown, Shutting down logger")

    def __add_log(self, level: int, msg, frame, *args, **kwargs):
        if self.isEnabledFor(level):
            formatted_msg = format_message(frame, msg)
            self._log(level, formatted_msg, args, **kwargs)

    def __enqueue_log_record(self, level: int, msg, frame, *args, **kwargs):
        Logger.__log_queue.put(partial(self.__add_log, level, msg, frame, *args, **kwargs))

    def d(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'DEBUG'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.
        """
        self.__enqueue_log_record(logging.DEBUG, msg, inspect.currentframe(), *args, **kwargs)

    def i(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'INFO'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.
        """
        self.__enqueue_log_record(logging.INFO, msg, inspect.currentframe(), *args, **kwargs)

    def w(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'WARNING'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.
        """
        self.__enqueue_log_record(logging.WARNING, msg, inspect.currentframe(), *args, **kwargs)

    def e(self, e: Exception, *args, **kwargs):
        """
        Convenience method for logging an Exception.
        """
        msg = "Stack Trace:"
        msg += format_traceback(e)
        self.__enqueue_log_record(logging.ERROR, msg, inspect.currentframe(), *args, **kwargs)

    def c(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'CRITICAL'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.
        """
        self.__enqueue_log_record(logging.CRITICAL, msg, inspect.currentframe(), *args, **kwargs)
