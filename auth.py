"""
auth.py
-------
Lightweight username/password authentication for farmers, backed by a local
JSON file (data/users.json). This is a demo-grade auth system suitable for a
single-instance Streamlit deployment - it is NOT intended as a production
identity system (no email verification, password reset, or rate limiting).
For production use, replace this with a proper identity provider.

Passwords are stored as salted SHA-256 hashes, never in plain text.
"""

import json
import os
import hashlib
import secrets

USERS_FILE = os.path.join(os.path.dirname(__file__), "data", "users.json")


def _ensure_store():
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump({}, f)


def _load_users() -> dict:
    _ensure_store()
    with open(USERS_FILE, "r") as f:
        return json.load(f)


def _save_users(users: dict):
    _ensure_store()
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


def _hash_password(password: str, salt: str) -> str:
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()


def register_user(username: str, password: str, full_name: str = "", district: str = "") -> tuple:
    """Returns (success: bool, message_key: str)."""
    username = username.strip().lower()
    if not username or not password:
        return False, "invalid_input"

    users = _load_users()
    if username in users:
        return False, "user_exists"

    salt = secrets.token_hex(16)
    users[username] = {
        "salt": salt,
        "password_hash": _hash_password(password, salt),
        "full_name": full_name,
        "district": district,
    }
    _save_users(users)
    return True, "register_success"


def authenticate(username: str, password: str) -> tuple:
    """Returns (success: bool, user_record: dict | None)."""
    username = username.strip().lower()
    users = _load_users()
    record = users.get(username)
    if not record:
        return False, None

    expected_hash = _hash_password(password, record["salt"])
    if secrets.compare_digest(expected_hash, record["password_hash"]):
        return True, {"username": username, **record}
    return False, None
