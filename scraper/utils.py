"""
FloodKH -- Utility helpers.
"""

import json
import os
from datetime import datetime, timezone


def get_current_utc_time() -> str:
    """Return current UTC time as an ISO-8601 string."""
    return datetime.now(timezone.utc).isoformat()


def safe_round(value, decimals: int = 2):
    """Round a numeric value, returning None if the input is None."""
    if value is None:
        return None
    try:
        return round(float(value), decimals)
    except (TypeError, ValueError):
        return None


def load_json(filepath: str) -> dict | list | None:
    """Load and return JSON from *filepath*, or None on failure."""
    try:
        with open(filepath, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError, OSError) as exc:
        print(f"[utils] could not load {filepath}: {exc}")
        return None


def save_json(filepath: str, data) -> bool:
    """Write *data* as pretty-printed JSON to *filepath*.

    Creates parent directories if they do not exist.
    Returns True on success, False on failure.
    """
    try:
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
        return True
    except OSError as exc:
        print(f"[utils] could not save {filepath}: {exc}")
        return False
