"""
Structured Logger Utility
Multi-Agent AI Customer Support Assistant
Provides structured, performance-instrumented logging with timestamps,
module origins, latency metrics, and error traces suitable for cloud log streaming (Render / Docker).
"""

import sys
import time
import logging
from typing import Any, Dict, Optional
from loguru import logger as loguru_logger

# Configure Loguru format for clear cloud / terminal log streaming
LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>"
)

# Reset and reconfigure loguru handlers
loguru_logger.remove()
loguru_logger.add(
    sys.stdout,
    format=LOG_FORMAT,
    level="INFO",
    colorize=True,
    enqueue=True,
    backtrace=True,
    diagnose=True,
)


class StructuredLogger:
    """
    Wrapper providing structured logging helper methods for multi-agent workflows.
    """

    def __init__(self, context: str):
        self.context = context
        self._logger = loguru_logger.bind(context=context)

    def info(self, message: str, **kwargs: Any) -> None:
        if kwargs:
            extra_str = " | " + " ".join(f"{k}={v}" for k, v in kwargs.items())
            self._logger.info(f"[{self.context}] {message}{extra_str}")
        else:
            self._logger.info(f"[{self.context}] {message}")

    def warning(self, message: str, **kwargs: Any) -> None:
        if kwargs:
            extra_str = " | " + " ".join(f"{k}={v}" for k, v in kwargs.items())
            self._logger.warning(f"[{self.context}] {message}{extra_str}")
        else:
            self._logger.warning(f"[{self.context}] {message}")

    def error(self, message: str, **kwargs: Any) -> None:
        if kwargs:
            extra_str = " | " + " ".join(f"{k}={v}" for k, v in kwargs.items())
            self._logger.error(f"[{self.context}] {message}{extra_str}")
        else:
            self._logger.error(f"[{self.context}] {message}")

    def debug(self, message: str, **kwargs: Any) -> None:
        if kwargs:
            extra_str = " | " + " ".join(f"{k}={v}" for k, v in kwargs.items())
            self._logger.debug(f"[{self.context}] {message}{extra_str}")
        else:
            self._logger.debug(f"[{self.context}] {message}")

    def log_agent_execution(
        self,
        agent_name: str,
        query: str,
        duration_ms: float,
        chunks_count: int,
        sources: list,
        status: str = "success",
    ) -> None:
        """Log granular agent RAG and generation metrics."""
        self._logger.info(
            f"⚡ [Agent: {agent_name.upper()}] status={status} | "
            f"duration={duration_ms:.2f}ms | chunks_retrieved={chunks_count} | "
            f"sources={len(sources)} | query_preview='{query[:50]}...'"
        )

    def log_pipeline_summary(
        self,
        session_id: str,
        intents: list,
        agents_invoked: list,
        total_duration_ms: float,
        response_length: int,
    ) -> None:
        """Log end-to-end multi-agent orchestration summary."""
        self._logger.info(
            f"🎯 [Orchestration Summary] session={session_id} | "
            f"intents={intents} | agents={agents_invoked} | "
            f"total_time={total_duration_ms:.2f}ms | output_chars={response_length}"
        )


def get_logger(name: str) -> StructuredLogger:
    """Factory function to get a structured logger with context name."""
    return StructuredLogger(context=name)


# Intercept standard library logging to pipe through loguru
class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = loguru_logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        loguru_logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_root_logging() -> None:
    """Redirect standard library logging to Loguru and suppress noisy third-party HTTP logs."""
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    # Keep application servers routed to Loguru
    for name in ["uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"]:
        log = logging.getLogger(name)
        log.handlers = [InterceptHandler()]
        log.propagate = False

    # Suppress harmless internal HEAD/GET probe logs from HuggingFace & HTTP libraries
    for noisy_lib in ["urllib3", "httpx", "httpcore", "huggingface_hub", "transformers", "sentence_transformers"]:
        logging.getLogger(noisy_lib).setLevel(logging.WARNING)
