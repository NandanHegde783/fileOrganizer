"""
__main__.py — CLI entry point.

Usage:
    python -m file_organizer [TARGET_DIR] [OPTIONS]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="file_organizer",
        description="Smart File Organizer — automatically sort, deduplicate, and schedule your files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m file_organizer ~/Downloads
  python -m file_organizer ~/Downloads --dry-run
  python -m file_organizer ~/Downloads --recursive --copy
  python -m file_organizer ~/Downloads --detect-dupes
  python -m file_organizer ~/Downloads --delete-dupes
  python -m file_organizer ~/Downloads --schedule daily
  python -m file_organizer ~/Downloads --schedule "every 30 minutes"
  python -m file_organizer ~/Downloads --undo
        """,
    )

    parser.add_argument(
        "target",
        nargs="?",
        default=".",
        metavar="TARGET_DIR",
        help="Directory to organise (default: current directory).",
    )

    # ── Organise flags ──────────────────────────────────────────────────────
    org_group = parser.add_argument_group("Organisation")
    org_group.add_argument(
        "--recursive", "-r",
        action="store_true",
        help="Also organise files in subdirectories.",
    )
    org_group.add_argument(
        "--copy", "-c",
        action="store_true",
        help="Copy files instead of moving them.",
    )
    org_group.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Preview what would happen without making any changes.",
    )
    org_group.add_argument(
        "--undo",
        action="store_true",
        help="Reverse the last organize operation.",
    )

    # ── Duplicate flags ─────────────────────────────────────────────────────
    dupe_group = parser.add_argument_group("Duplicates")
    dupe_group.add_argument(
        "--detect-dupes",
        action="store_true",
        help="Scan for duplicate files and print a report.",
    )
    dupe_group.add_argument(
        "--delete-dupes",
        action="store_true",
        help="Delete duplicate files (keeps the oldest copy). Implies --detect-dupes.",
    )

    # ── Scheduler flags ─────────────────────────────────────────────────────
    sched_group = parser.add_argument_group("Scheduler")
    sched_group.add_argument(
        "--schedule",
        metavar="INTERVAL",
        help=(
            "Run organizer repeatedly on an interval. "
            "E.g. 'hourly', 'daily', 'weekly', 'every 30 minutes', 'every 2 hours'."
        ),
    )

    return parser


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    target = Path(args.target).expanduser().resolve()

    if not target.exists():
        print(f"[ERROR] Path does not exist: {target}", file=sys.stderr)
        return 1
    if not target.is_dir():
        print(f"[ERROR] Not a directory: {target}", file=sys.stderr)
        return 1

    # ── Undo ────────────────────────────────────────────────────────────────
    if args.undo:
        from .organizer import undo
        print(f"Undoing last organize run in '{target}' …")
        summary = undo(target)
        restored = len(summary["restored"])
        errors = len(summary["errors"])
        print(f"\n  Restored : {restored} file(s)")
        if errors:
            print(f"  Errors   : {errors}")
        return 0 if not errors else 1

    # ── Scheduler ───────────────────────────────────────────────────────────
    if args.schedule:
        from .scheduler import run_scheduled
        run_scheduled(
            target,
            args.schedule,
            recursive=args.recursive,
            copy=args.copy,
        )
        return 0

    # ── Duplicate detection / deletion ──────────────────────────────────────
    if args.detect_dupes or args.delete_dupes:
        from .duplicate_detector import (
            delete_duplicates,
            find_duplicates,
            report_duplicates,
        )
        print(f"Scanning '{target}' for duplicates …")
        duplicates = find_duplicates(target, recursive=True)
        report_duplicates(duplicates)

        if args.delete_dupes and duplicates:
            summary = delete_duplicates(
                duplicates,
                dry_run=args.dry_run,
                confirm=True,
            )
            deleted = len(summary["deleted"])
            errors = len(summary["errors"])
            print(f"\n  Deleted  : {deleted} duplicate(s)")
            if errors:
                print(f"  Errors   : {errors}")
        return 0

    # ── Standard organise ───────────────────────────────────────────────────
    from .organizer import organize, print_summary

    action = "Previewing" if args.dry_run else "Organising"
    print(f"{action} '{target}' …\n")

    summary = organize(
        target,
        recursive=args.recursive,
        copy=args.copy,
        dry_run=args.dry_run,
    )
    print_summary(summary, dry_run=args.dry_run)
    return 1 if summary["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
