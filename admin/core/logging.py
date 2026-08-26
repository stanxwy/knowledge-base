"""Logging bootstrap — mirrors ``app.utils.logger``.

Uses colorlog for stdout + TimedRotatingFileHandler for daily files.
"""
from __future__ import annotations

import logging
import os
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

import colorlog


_INITIALIZED = False


def setup_logging(level: str = "INFO") -> None:
    global _INITIALIZED
    if _INITIALIZED:
        return

    log_level = getattr(logging, level.upper(), logging.INFO)
    formatter = colorlog.LevelFormatter(
        fmt={
            logging.DEBUG: "%(log_color)s[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
            logging.INFO: "%(log_color)s[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
            logging.WARNING: "%(log_color)s[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
            logging.ERROR: "%(log_color)s[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
            logging.CRITICAL: "%(log_color)s[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
        },
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    )

    root = logging.getLogger()
    root.setLevel(log_level)
    for h in list(root.handlers):
        root.removeHandler(h)

    stream = logging.StreamHandler()
    stream.setFormatter(formatter)
    root.addHandler(stream)

    log_dir = Path(os.environ.get("KBMS_LOG_DIR", "logs"))
    log_dir.mkdir(parents=True, exist_ok=True)
    file_handler = TimedRotatingFileHandler(
        log_dir / "kbms-admin.log",
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8",
    )
    file_handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"))
    root.addHandler(file_handler)

    _INITIALIZED = True