__all__ = ["Logger"]

try:
    from .logger import Logger
except ImportError:
    from logger import Logger
