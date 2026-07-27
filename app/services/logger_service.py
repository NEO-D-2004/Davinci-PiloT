"""
Loguru Logging Service with PySide6 Signal integration.
Routes application logs to app/logs/app.log and emits signals for UI log widgets.
"""

import sys
from pathlib import Path
from loguru import logger
from PySide6.QtCore import QObject, Signal


class LogSignalEmitter(QObject):
    """Qt Signal Emitter for live UI logging."""
    log_emitted = Signal(str, str)  # (level, message)


class QtLogSink:
    """Custom Loguru sink that dispatches log messages to PySide6 signals."""

    def __init__(self, emitter: LogSignalEmitter) -> None:
        self.emitter = emitter

    def write(self, message: str) -> None:
        record = getattr(message, "record", None)
        if record:
            level = record["level"].name
            text = record["message"]
            self.emitter.log_emitted.emit(level, text)
        else:
            self.emitter.log_emitted.emit("INFO", str(message))


class LoggerService:
    """Central Logging Service managing Loguru sinks."""

    def __init__(self) -> None:
        self.signal_emitter = LogSignalEmitter()
        self._qt_sink = QtLogSink(self.signal_emitter)
        self.log_dir = Path(__file__).resolve().parent.parent / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "app.log"
        self._setup_logger()

    def _setup_logger(self) -> None:
        """Configure Loguru sinks."""
        logger.remove()

        # Console sink
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level="DEBUG",
            colorize=True,
        )

        # File sink with rotation & retention
        logger.add(
            str(self.log_file),
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="DEBUG",
            rotation="10 MB",
            retention="30 days",
            compression="zip",
            encoding="utf-8",
        )

        # Qt Signal sink
        logger.add(
            self._qt_sink.write,
            format="{message}",
            level="INFO",
        )

    def get_logger(self):
        return logger


# Global singleton logger service
logger_service = LoggerService()
app_logger = logger_service.get_logger()
