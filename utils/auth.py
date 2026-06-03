"""
auth.py — Minimal file-based user authentication using bcrypt password hashing.

User credentials are stored in a JSON file inside the logs/ directory.
No plain-text passwords are ever written to disk.
"""

import json
import os

import bcrypt


_USERS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "users.json")
os.makedirs(os.path.dirname(_USERS_FILE), exist_ok=True)


def _load_users() -> dict:
    if not os.path.exists(_USERS_FILE):
        return {}
    try:
        with open(_USERS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def _save_users(users: dict) -> None:
    with open(_USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


def register_user(username: str, password: str) -> tuple[bool, str]:
    """
    Register a new user.

    Returns (True, "success message") or (False, "error message").
    """
    if not username or not password:
        return False, "Username and password cannot be empty."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."

    users = _load_users()
    if username in users:
        return False, "Username already exists. Please choose another."

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    users[username] = hashed
    _save_users(users)
    return True, "Account created successfully! You can now log in."


def verify_user(username: str, password: str) -> tuple[bool, str]:
    """
    Verify login credentials.

    Returns (True, "welcome message") or (False, "error message").
    """
    users = _load_users()
    if username not in users:
        return False, "Username not found."

    if bcrypt.checkpw(password.encode(), users[username].encode()):
        return True, f"Welcome back, {username}!"
    return False, "Incorrect password."
