from datetime import datetime
from typing import Optional

def format_datetime(
        iso_str: Optional[str],
        default: str = "Not yet"
    ) -> str:
    if iso_str is None:
        return default
    try:
        dt = datetime.fromisoformat(iso_str)
        local_dt = dt.astimezone()
        return local_dt.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return iso_str

def normalize_task_id(raw: str) -> str:
    """Normalize a user-provided task ID to canonical ``TASK-XXXX`` form.

    Accepts a bare decimal integer (e.g. ``"1"``, ``"42"``) and converts
    it to the canonical zero-padded format.  Full ``TASK-XXXX`` IDs and
    any other non-numeric strings pass through unchanged::

        normalize_task_id("1")     → "TASK-0001"
        normalize_task_id("42")    → "TASK-0042"
        normalize_task_id("TASK-0001") → "TASK-0001"
        normalize_task_id("CUSTOM-001") → "CUSTOM-001"
        normalize_task_id("")      → ""
    """
    if raw.isdigit():
        return f"TASK-{int(raw):04d}"
    return raw