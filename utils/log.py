"""
utils_log.py - Simple logging utility with optional GTK TextView integration.

Features:
    - Supports four log levels: DEBUG, INFO, WARN, ERROR
    - Colored output to the terminal for easier readability
    - Optional attachment to a Gtk.TextView for GUI logging
    - Tagging support to identify log sources (modules/components)

Usage:
    from utils.log import utils_log_get_logger

    LOG = utils_log_get_logger("network")
    LOG["debug"]("Connecting to server...")
    LOG["info"]("Connection established")
    LOG["warn"]("Slow response detected")
    LOG["err"]("Connection failed")

Author: Khuong Nguyen (ntkhuong.coder@gmail.com)
"""

import sys
from datetime import datetime

# ********************************************************************************************
# [Configuration]
LOG_LEVEL = "DEBUG"

_levels = {
    "DEBUG": 10,
    "INFO": 20,
    "WARN": 30,
    "ERROR": 40,
}

_colors = {
    "DEBUG": "\033[36m",  # Cyan
    "INFO": "\033[32m",   # Green
    "WARN": "\033[33m",   # Yellow
    "ERROR": "\033[31m",  # Red
}

_RESET = "\033[0m"

# Optional Gtk.TextView for GUI logging
_log_view = None
# ********************************************************************************************


# ********************************************************************************************
# [Helpers]
def _now() -> str:
    """Return current time as HH:MM:SS string."""
    return datetime.now().strftime("%H:%M:%S")


def _should_log(level: str) -> bool:
    """Return True if the given level should be logged under current LOG_LEVEL."""
    return _levels[level] >= _levels.get(LOG_LEVEL, 20)


def _write(msg: str, level: str, tag: str = "core"):
    """
    Write a formatted log message to stdout/stderr and optionally a Gtk.TextView.

    Args:
        msg (str): The log message to display.
        level (str): Log level (DEBUG, INFO, WARN, ERROR).
        tag (str, optional): Tag to identify log source (default = "core").
    """
    formatted = f"[{_now()}] [{level:<5}] [{tag}] {msg}"

    # Colorize output for terminal
    color = _colors.get(level, "")
    colored_msg = f"{color}{formatted}{_RESET}"

    # Print to terminal
    if level in ["ERROR", "WARN"]:
        print(colored_msg, file=sys.stderr)
    else:
        print(colored_msg, file=sys.stdout)

    # Also print to GUI TextView if available (without color codes)
    if _log_view:
        buf = _log_view.get_buffer()
        buf.insert(buf.get_end_iter(), formatted + "\n")
# ********************************************************************************************


# ********************************************************************************************
# [Public API]
def debug(msg: str, tag: str = "core"):
    """Log a debug-level message (cyan)."""
    if _should_log("DEBUG"):
        _write(msg, "DEBUG", tag)


def info(msg: str, tag: str = "core"):
    """Log an info-level message (green)."""
    if _should_log("INFO"):
        _write(msg, "INFO", tag)


def warn(msg: str, tag: str = "core"):
    """Log a warning-level message (yellow)."""
    if _should_log("WARN"):
        _write(msg, "WARN", tag)


def err(msg: str, tag: str = "core"):
    """Log an error-level message (red)."""
    if _should_log("ERROR"):
        _write(msg, "ERROR", tag)


# Convenience alias
log = info


def utils_log_attach_textview(view):
    """
    Attach a Gtk.TextView to receive log messages.

    Args:
        view (Gtk.TextView): TextView widget where logs will be appended.
    """
    global _log_view
    _log_view = view


def utils_log_get_logger(tag: str):
    """
    Return a tagged logger as a dict of logging functions.

    Args:
        tag (str): Identifier for the logger (e.g., module name).

    Returns:
        dict: Mapping of {"debug", "info", "warn", "err"} to log functions.

    Example:
        >>> LOG = utils_log_get_logger("auth")
        >>> LOG["info"]("User logged in")
    """
    return {
        "debug": lambda msg: debug(msg, tag),
        "info": lambda msg: info(msg, tag),
        "warn": lambda msg: warn(msg, tag),
        "err": lambda msg: err(msg, tag),
    }
# ********************************************************************************************
