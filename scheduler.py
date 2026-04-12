"""
scheduler.py — Run the organizer on a recurring schedule.

Uses the lightweight `schedule` library (pip install schedule).
Falls back gracefully if the library is missing.
"""

from __future__ import annotations

import time
from pathlib import Path

try:
    import schedule
    HAS_SCHEDULE = True
except ImportError:
    HAS_SCHEDULE = False


# ---------------------------------------------------------------------------
# Interval parser
# ---------------------------------------------------------------------------

_ALIASES: dict[str, tuple[str, int]] = {
    "hourly":      ("hours", 1),
    "daily":       ("days", 1),
    "weekly":      ("weeks", 1),
    # human-friendly shortcuts
    "every hour":  ("hours", 1),
    "every day":   ("days", 1),
    "every week":  ("weeks", 1),
}


def parse_interval(interval: str) -> tuple[str, int]:
    """
    Parse a human-readable *interval* string into (unit, amount).

    Supported formats:
      - "hourly" / "daily" / "weekly"
      - "every N minutes" / "every N hours" / "every N days"
      - "N minutes" / "N hours" / "N days"

    Returns (unit, amount) e.g. ("minutes", 30).
    Raises ValueError on unknown format.
    """
    key = interval.strip().lower()

    if key in _ALIASES:
        return _ALIASES[key]

    # "every N unit" or "N unit"
    parts = key.split()
    if parts[0] == "every":
        parts = parts[1:]

    if len(parts) == 2:
        try:
            amount = int(parts[0])
        except ValueError:
            pass
        else:
            unit = parts[1].rstrip("s") + "s"  # normalise to plural
            if unit in ("minutes", "hours", "days", "weeks"):
                return (unit, amount)

    raise ValueError(
        f"Cannot parse interval '{interval}'. "
        "Try: 'hourly', 'daily', 'weekly', 'every 30 minutes', 'every 2 hours', etc."
    )


# ---------------------------------------------------------------------------
# Scheduler entry point
# ---------------------------------------------------------------------------

def run_scheduled(
    target: Path,
    interval: str,
    *,
    recursive: bool = False,
    copy: bool = False,
) -> None:
    """
    Run the organizer on *target* repeatedly according to *interval*.
    Blocks the calling thread (Ctrl-C to stop).
    """
    if not HAS_SCHEDULE:
        raise ImportError(
            "The 'schedule' package is required for scheduling. "
            "Install it with:  pip install schedule"
        )

    from .organizer import organize, print_summary  # local import to avoid circularity

    unit, amount = parse_interval(interval)
    print(f"  Scheduler started — organising '{target}' every {amount} {unit}.")
    print("  Press Ctrl-C to stop.\n")

    def _job() -> None:
        print(f"\n[SCHEDULER] Running organizer on '{target}' …")
        summary = organize(target, recursive=recursive, copy=copy)
        print_summary(summary)

    # Wire up the schedule
    job_fn = getattr(schedule.every(amount), unit)
    job_fn.do(_job)

    # Run immediately on first invocation
    _job()

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n  Scheduler stopped.")
