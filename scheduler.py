"""
scheduler.py — Run the organizer on a recurring schedule.

Uses only Python's standard library (time, threading) — no third-party packages
required.
"""

from __future__ import annotations

import time
from pathlib import Path


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

_UNIT_TO_SECONDS: dict[str, int] = {
    "minutes": 60,
    "hours":   3_600,
    "days":    86_400,
    "weeks":   604_800,
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
            if unit in _UNIT_TO_SECONDS:
                return (unit, amount)

    raise ValueError(
        f"Cannot parse interval '{interval}'. "
        "Try: 'hourly', 'daily', 'weekly', 'every 30 minutes', 'every 2 hours', etc."
    )


def _interval_seconds(unit: str, amount: int) -> int:
    """Convert (unit, amount) to a total number of seconds."""
    return _UNIT_TO_SECONDS[unit] * amount


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
    from .organizer import organize, print_summary  # local import to avoid circularity

    unit, amount = parse_interval(interval)
    sleep_secs = _interval_seconds(unit, amount)

    print(f"  Scheduler started — organising '{target}' every {amount} {unit}.")
    print("  Press Ctrl-C to stop.\n")

    def _job() -> None:
        print(f"\n[SCHEDULER] Running organizer on '{target}' …")
        summary = organize(target, recursive=recursive, copy=copy)
        print_summary(summary)

    # Run immediately on first invocation
    _job()

    try:
        while True:
            time.sleep(sleep_secs)
            _job()
    except KeyboardInterrupt:
        print("\n  Scheduler stopped.")
