"""
organizer.py — Core file-sorting logic.

Moves (or copies) files in a target directory into categorized subfolders
based on their extension. Supports dry-run preview and undo logging.
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

from .config import EXTENSION_MAP, MISC_FOLDER, ORGANISED_FOLDERS


# ---------------------------------------------------------------------------
# Main organizer
# ---------------------------------------------------------------------------

def organize(
    target: Path,
    *,
    recursive: bool = False,
    copy: bool = False,
    dry_run: bool = False,
    undo_log_path: Path | None = None,
) -> dict:
    """
    Organise files in *target* into categorized subfolders.

    Returns a summary dict:
        {
            "moved": [...],   # list of (src, dst) tuples
            "skipped": [...], # list of paths skipped
            "errors": [...],  # list of (path, error_message)
        }
    """
    if not target.is_dir():
        raise NotADirectoryError(f"'{target}' is not a valid directory.")

    summary = {"moved": [], "skipped": [], "errors": []}
    undo_entries: list[dict] = []

    files = _collect_files(target, recursive=recursive)

    for src in files:
        # Skip files that live inside already-organised subfolders
        relative_parts = src.relative_to(target).parts
        if len(relative_parts) > 1 and relative_parts[0] in ORGANISED_FOLDERS:
            summary["skipped"].append(str(src))
            continue

        dest_folder_name = EXTENSION_MAP.get(src.suffix.lower(), MISC_FOLDER)
        dest_dir = target / dest_folder_name
        dest = _unique_path(dest_dir / src.name)

        if dry_run:
            print(f"[DRY-RUN] {'copy' if copy else 'move'}: {src} → {dest}")
            summary["moved"].append((str(src), str(dest)))
            continue

        try:
            dest_dir.mkdir(parents=True, exist_ok=True)
            if copy:
                shutil.copy2(src, dest)
            else:
                shutil.move(str(src), dest)

            summary["moved"].append((str(src), str(dest)))
            undo_entries.append({"src": str(src), "dst": str(dest), "copy": copy})
            print(f"  {'Copied' if copy else 'Moved'}: {src.name} → {dest_folder_name}/")

        except Exception as exc:  # noqa: BLE001
            summary["errors"].append((str(src), str(exc)))
            print(f"  [ERROR] {src.name}: {exc}")

    # Persist undo log
    if not dry_run and undo_entries:
        log_path = undo_log_path or (target / ".organizer_undo.json")
        _write_undo_log(log_path, undo_entries)

    return summary


# ---------------------------------------------------------------------------
# Undo
# ---------------------------------------------------------------------------

def undo(target: Path, undo_log_path: Path | None = None) -> dict:
    """
    Reverse the last organize run using the saved undo log.
    """
    log_path = undo_log_path or (target / ".organizer_undo.json")
    if not log_path.exists():
        raise FileNotFoundError(f"No undo log found at '{log_path}'.")

    with log_path.open() as f:
        data = json.load(f)

    entries: list[dict] = data.get("entries", [])
    summary = {"restored": [], "errors": []}

    for entry in reversed(entries):
        src = Path(entry["src"])
        dst = Path(entry["dst"])
        was_copy: bool = entry.get("copy", False)

        try:
            if was_copy:
                # Remove the copy we made; original is untouched
                if dst.exists():
                    dst.unlink()
                    print(f"  Removed copy: {dst}")
            else:
                if dst.exists():
                    src.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(dst), src)
                    print(f"  Restored: {dst.name} → {src.parent}/")

            summary["restored"].append(str(src))
        except Exception as exc:  # noqa: BLE001
            summary["errors"].append((str(dst), str(exc)))
            print(f"  [ERROR] restoring {dst}: {exc}")

    # Remove undo log after successful undo
    log_path.unlink(missing_ok=True)
    return summary


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _collect_files(directory: Path, *, recursive: bool) -> list[Path]:
    """Return a sorted list of files in *directory*."""
    if recursive:
        return sorted(p for p in directory.rglob("*") if p.is_file())
    return sorted(p for p in directory.iterdir() if p.is_file())


def _unique_path(path: Path) -> Path:
    """If *path* already exists, append a counter suffix to avoid collision."""
    if not path.exists():
        return path
    stem, suffix = path.stem, path.suffix
    counter = 1
    while True:
        candidate = path.parent / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def _write_undo_log(log_path: Path, entries: list[dict]) -> None:
    """Persist (or append to) the undo log file."""
    data = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "entries": entries,
    }
    with log_path.open("w") as f:
        json.dump(data, f, indent=2)


# ---------------------------------------------------------------------------
# Pretty summary printer
# ---------------------------------------------------------------------------

def print_summary(summary: dict, *, dry_run: bool = False) -> None:
    prefix = "[DRY-RUN] " if dry_run else ""
    moved = len(summary.get("moved", []))
    skipped = len(summary.get("skipped", []))
    errors = len(summary.get("errors", []))

    print()
    print("─" * 40)
    print(f"{prefix}Summary")
    print("─" * 40)
    print(f"  Files organised : {moved}")
    print(f"  Files skipped   : {skipped}")
    print(f"  Errors          : {errors}")
    if errors:
        for path, msg in summary["errors"]:
            print(f"    ✗ {path}: {msg}")
    print("─" * 40)
