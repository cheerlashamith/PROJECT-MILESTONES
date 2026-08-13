"""
Application Logger – Structured Logging
========================================
Configures Python logging with file + console handlers.
Logs user prompts, AI responses, response times, errors, and session info.
"""

import os
import logging
from datetime import datetime
from backend.config import Config


class AppLogger:
    """Structured logging for the CIH application."""

    def __init__(self, config: Config = None):
        self.config = config or Config()
        self._setup_logger()

    def _setup_logger(self):
        """Configure logging with file and console handlers."""
        # Create logs directory
        os.makedirs(self.config.LOG_DIR, exist_ok=True)

        # Create logger
        self.logger = logging.getLogger("CIH")
        self.logger.setLevel(getattr(logging, self.config.LOG_LEVEL, logging.INFO))

        # Prevent duplicate handlers on re-init
        if self.logger.handlers:
            return

        # File handler (daily log file)
        log_file = os.path.join(
            self.config.LOG_DIR,
            f"cih_{datetime.now().strftime('%Y-%m-%d')}.log",
        )
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    # ── Logging Methods ──────────────────────────────────────────────

    def log_user_prompt(self, prompt: str):
        """Log a user prompt (truncated for privacy)."""
        truncated = prompt[:200] + "..." if len(prompt) > 200 else prompt
        self.logger.info(f"USER_PROMPT: {truncated}")

    def log_ai_response(self, response_time: float, token_count: int = 0):
        """Log an AI response with timing."""
        self.logger.info(
            f"AI_RESPONSE: time={response_time:.2f}s tokens={token_count}"
        )

    def log_error(self, error: str, context: str = ""):
        """Log an error with optional context."""
        self.logger.error(f"ERROR [{context}]: {error}")

    def log_service_status(self, service: str, status: str):
        """Log service status changes."""
        self.logger.info(f"SERVICE: {service} → {status}")

    def log_calculation(self, calc_type: str, params: dict):
        """Log a calculation event."""
        self.logger.info(f"CALC: {calc_type} params={params}")

    def info(self, message: str):
        """General info log."""
        self.logger.info(message)

    def warning(self, message: str):
        """General warning log."""
        self.logger.warning(message)

    def error(self, message: str):
        """General error log."""
        self.logger.error(message)
