import sys
from datetime import datetime

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

_log_view = None  # Optional Gtk.TextView for GUI logging

def _now():
    return datetime.now().strftime("%H:%M:%S")

def _should_log(level: str) -> bool:
    return _levels[level] >= _levels.get(LOG_LEVEL, 20)

def _write(msg: str, level: str, tag: str = "core"):
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
# Public API
def debug(msg: str, tag: str = "core"):
    if _should_log("DEBUG"):
        _write(msg, "DEBUG", tag)
def info(msg: str, tag: str = "core"):
    if _should_log("INFO"):
        _write(msg, "INFO", tag)
def warn(msg: str, tag: str = "core"):
    if _should_log("WARN"):
        _write(msg, "WARN", tag)
def err(msg: str, tag: str = "core"):
    if _should_log("ERROR"):
        _write(msg, "ERROR", tag)

log = info  # Alias

def utils_log_attach_textview(view):
    global _log_view
    _log_view = view

def utils_log_get_logger(tag: str):
    return {
        "debug": lambda msg: debug(msg, tag),
        "info": lambda msg: info(msg, tag),
        "warn": lambda msg: warn(msg, tag),
        "err": lambda msg: err(msg, tag),
    }
# ********************************************************************************************