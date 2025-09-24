"""
Simple Log Factory using Loguru with logger.add() for clean setup.
Allows using standard logger.debug(), logger.info() etc. without changing existing code.
"""

from pathlib import Path
from typing import Optional, Any
from loguru import logger
import sys


class LogFactory:
    """
    Simple log factory using loguru's logger.add() for clean configuration.

    Features:
    - Use standard logger.debug(), logger.info() etc.
    - Async logging via enqueue=True
    - Console and file handlers with different levels and formats
    - Simple setup using logger.add() function
    """

    def __init__(
        self,
        log_dir: str = "logs",
        app_name: str = "app",
        console_level: str = "INFO",
        file_level: str = "ERROR",
        filter_module: Optional[str] = None,
    ):
        """
        Initialize the log factory using logger.add().

        Args:
            log_dir: Directory to store log files
            app_name: Application name for log file naming
            console_level: Minimum level for console logging
            file_level: Minimum level for file logging
            filter_module: Optional module filter (e.g., "my_module")
        """
        self.log_dir = Path(log_dir)
        self.app_name = app_name
        self.console_level = console_level
        self.file_level = file_level
        self.filter_module = filter_module
        self.handler_ids = []
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Setup loguru configuration using logger.add() for clean setup."""
        # Remove default handler
        logger.remove()

        # Create log directory if it doesn't exist
        self.log_dir.mkdir(exist_ok=True)

        # Console handler - colorized with async support
        console_handler_id = logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{function}:{line}</cyan> - <level>{message}</level>",
            level=self.console_level,
            filter=self.filter_module,
            colorize=True,
            enqueue=True,  # Async logging
            backtrace=True,
            diagnose=True,
        )
        self.handler_ids.append(console_handler_id)

        # Error file handler - for errors and critical
        error_log_path = self.log_dir / f"{self.app_name}_error.log"
        error_handler_id = logger.add(
            str(error_log_path),
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {function}:{line} | {message}",
            level=self.file_level,
            filter=self.filter_module,
            rotation="10 MB",
            retention="30 days",
            compression="zip",
            enqueue=True,  # Async logging
            backtrace=True,
            diagnose=True,
        )
        self.handler_ids.append(error_handler_id)

        # Trace file handler - for detailed tracing
        trace_log_path = self.log_dir / f"{self.app_name}_trace.log"
        trace_handler_id = logger.add(
            str(trace_log_path),
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {function}:{line} | {message}",
            level="TRACE",
            filter=self.filter_module,
            rotation="50 MB",
            retention="7 days",
            compression="zip",
            enqueue=True,  # Async logging
            serialize=False,
        )
        self.handler_ids.append(trace_handler_id)

    def add_handler(
        self,
        sink: Any,
        format: str = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        level: str = "INFO",
        filter: Optional[str] = None,
        **kwargs,
    ) -> int:
        """
        Add a custom handler using logger.add().

        Args:
            sink: Where to send logs (file path, sys.stderr, etc.)
            format: Log message format
            level: Minimum log level
            filter: Optional module filter
            **kwargs: Additional arguments for logger.add()

        Returns:
            Handler ID for removal later
        """
        handler_id = logger.add(
            sink,
            format=format,
            level=level,
            filter=filter,
            enqueue=True,  # Default to async
            **kwargs,
        )
        self.handler_ids.append(handler_id)
        return handler_id

    def remove_handler(self, handler_id: int) -> None:
        """Remove a handler by ID."""
        logger.remove(handler_id)
        if handler_id in self.handler_ids:
            self.handler_ids.remove(handler_id)


    def cleanup(self) -> None:
        """Remove all handlers added by this factory."""
        for handler_id in self.handler_ids:
            logger.remove(handler_id)
        self.handler_ids.clear()


# Global log factory instance
_log_factory: Optional[LogFactory] = None


def setup_logging(
    log_dir: str = "logs",
    app_name: str = "app",
    console_level: str = "INFO",
    file_level: str = "ERROR",
    filter_module: Optional[str] = None,
) -> LogFactory:
    """
    Setup global logging configuration using LogFactory.
    After calling this, use standard logger.debug(), logger.info() etc.

    Args:
        log_dir: Directory to store log files
        app_name: Application name for log file naming
        console_level: Minimum level for console logging
        file_level: Minimum level for file logging
        filter_module: Optional module filter

    Returns:
        LogFactory instance

    Example:
        setup_logging(app_name="myapp", console_level="DEBUG")
        logger.info("This works now!")
        logger.error("Error with context", extra={"user_id": "123"})
    """
    global _log_factory
    if _log_factory is not None:
        _log_factory.cleanup()

    _log_factory = LogFactory(
        log_dir, app_name, console_level, file_level, filter_module
    )
    return _log_factory


def get_log_factory() -> Optional[LogFactory]:
    """Get the current log factory instance if it exists."""
    return _log_factory


def add_custom_handler(
    sink: Any,
    format: str = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    level: str = "INFO",
    filter: Optional[str] = None,
    **kwargs,
) -> int:
    """
    Add a custom handler to the current logger setup.

    Example:
        # Add JSON file handler
        add_custom_handler(
            "app.json",
            format="{time} {level} {message}",
            level="DEBUG",
            serialize=True
        )

        # Add filtered handler for specific module
        add_custom_handler(
            sys.stdout,
            format="{time} {level} {message}",
            level="WARNING",
            filter="my_module"
        )
    """
    if _log_factory is None:
        raise RuntimeError("Call setup_logging() first")

    return _log_factory.add_handler(sink, format, level, filter, **kwargs)
