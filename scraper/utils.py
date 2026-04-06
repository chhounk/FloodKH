"""
FloodKH Utilities — Shared helper functions used across the scraper package.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Time helpers
# ---------------------------------------------------------------------------

def get_utc_now() -> datetime:
    """Return the current UTC time as an aware datetime."""
    return datetime.now(timezone.utc)


def get_utc_now_str() -> str:
    """Return the current UTC time as an ISO-8601 string."""
    return get_utc_now().isoformat()


# ---------------------------------------------------------------------------
# Numeric helpers
# ---------------------------------------------------------------------------

def safe_round(val: float | None, decimals: int = 2) -> float | None:
    """Round *val* to *decimals* places, returning None when val is None."""
    if val is None:
        return None
    return round(val, decimals)


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp *value* to the closed interval [min_val, max_val]."""
    return max(min_val, min(value, max_val))


def score_from_thresholds(value: float | None, thresholds: list[tuple[float, int]]) -> int:
    """Look up a score from a sorted list of (upper_bound, score) tuples.

    The first entry whose *upper_bound* is **strictly greater than** *value*
    determines the returned score.  If *value* is None the score is 0.

    Example::

        thresholds = [(30, 0), (80, 5), (150, 12), (float('inf'), 25)]
        score_from_thresholds(45, thresholds)  # -> 5

    Parameters
    ----------
    value:
        The observed measurement to classify.
    thresholds:
        Ascending list of ``(upper_bound, score)`` pairs.  The last entry
        should normally use ``float('inf')`` as its upper bound.

    Returns
    -------
    int
        The score corresponding to the matched threshold bucket.
    """
    if value is None:
        return 0
    for upper_bound, score in thresholds:
        if value <= upper_bound:
            return score
    # Fallback: return the last score if nothing matched (shouldn't happen
    # when the list ends with inf).
    return thresholds[-1][1] if thresholds else 0


# ---------------------------------------------------------------------------
# JSON I/O helpers
# ---------------------------------------------------------------------------

def load_json(filepath: str | Path) -> dict[str, Any]:
    """Load a JSON file and return its contents as a dict.

    Returns an empty dict if the file does not exist, is unreadable, or
    contains invalid JSON.  Errors are logged rather than raised so that
    callers can degrade gracefully.
    """
    path = Path(filepath)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        logger.warning("JSON file not found: %s", path)
        return {}
    except (json.JSONDecodeError, OSError) as exc:
        logger.error("Failed to load JSON from %s: %s", path, exc)
        return {}


def save_json(filepath: str | Path, data: Any) -> None:
    """Write *data* as pretty-printed JSON to *filepath*.

    Parent directories are created automatically if they do not exist.
    """
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )
