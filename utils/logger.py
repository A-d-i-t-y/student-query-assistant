"""
logger.py — Handles saving and loading conversation logs as JSON files.
"""

import json
import os
from datetime import datetime


LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)


def _log_path(username: str) -> str:
    """Return the log file path for a given user."""
    safe = "".join(c for c in username if c.isalnum() or c in "_-")
    return os.path.join(LOG_DIR, f"{safe}_history.json")


def load_history(username: str) -> list[dict]:
    """
    Load saved conversation history for a user.

    Returns an empty list if no history file exists.
    """
    path = _log_path(username)
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_history(username: str, history: list[dict]) -> None:
    """
    Persist the full conversation history to disk.

    Each entry is expected to be a dict with keys:
      role  : "user" | "assistant"
      content : str
      timestamp : ISO-format string (added here if missing)
    """
    stamped = []
    for msg in history:
        entry = dict(msg)
        entry.setdefault("timestamp", datetime.now().isoformat())
        stamped.append(entry)

    path = _log_path(username)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(stamped, f, ensure_ascii=False, indent=2)
    except IOError as exc:
        print(f"[logger] Could not save history: {exc}")


def append_turn(username: str, role: str, content: str) -> None:
    """
    Append a single message turn to the user's log file.

    Useful for incremental saves without holding the full list in memory.
    """
    history = load_history(username)
    history.append({"role": role, "content": content, "timestamp": datetime.now().isoformat()})
    save_history(username, history)
