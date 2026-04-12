"""
duplicate_detector.py — SHA-256 hash-based duplicate file detection.
"""

from __future__ import annotations

import hashlib
from pathlib import Path


CHUNK_SIZE = 65_536  # 64 KB read chunks for memory efficiency


def compute_hash(path: Path) -> str:
    """Return the SHA-256 hex digest of *path*'s content."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
            h.update(chunk)
    return h.hexdigest()


def find_duplicates(target: Path, *, recursive: bool = True) -> dict[str, list[Path]]:
    """
    Walk *target* and group files by content hash.

    Returns a dict mapping hash → list of Paths **only** for hashes
    that have more than one file (i.e., actual duplicates).
    """
    if not target.is_dir():
        raise NotADirectoryError(f"'{target}' is not a valid directory.")

    hash_map: dict[str, list[Path]] = {}

    files = (
        (p for p in target.rglob("*") if p.is_file())
        if recursive
        else (p for p in target.iterdir() if p.is_file())
    )

    for path in files:
        try:
            digest = compute_hash(path)
            hash_map.setdefault(digest, []).append(path)
        except OSError as exc:
            print(f"  [WARN] Cannot read '{path}': {exc}")

    return {h: paths for h, paths in hash_map.items() if len(paths) > 1}


def report_duplicates(duplicates: dict[str, list[Path]]) -> None:
    """Print a human-readable duplicate report."""
    if not duplicates:
        print("  No duplicate files found.")
        return

    total_dupes = sum(len(v) - 1 for v in duplicates.values())
    print(f"\n  Found {len(duplicates)} duplicate group(s) — {total_dupes} redundant file(s):\n")

    for i, (digest, paths) in enumerate(duplicates.items(), start=1):
        print(f"  Group {i}  [{digest[:12]}...]")
        for j, p in enumerate(paths):
            marker = "  KEEP " if j == 0 else "  DUPE "
            size_kb = p.stat().st_size / 1024
            print(f"    {marker} {p}  ({size_kb:.1f} KB)")
        print()


def delete_duplicates(
    duplicates: dict[str, list[Path]],
    *,
    dry_run: bool = False,
    confirm: bool = True,
) -> dict:
    """
    Delete all but the first (oldest by mtime) file in each duplicate group.

    Returns: {"deleted": [...], "errors": [...]}
    """
    summary: dict[str, list] = {"deleted": [], "errors": []}

    if not duplicates:
        print("  Nothing to delete.")
        return summary

    if confirm and not dry_run:
        total = sum(len(v) - 1 for v in duplicates.values())
        answer = input(f"\n  Delete {total} duplicate file(s)? [y/N] ").strip().lower()
        if answer != "y":
            print("  Aborted.")
            return summary

    for digest, paths in duplicates.items():
        # Sort by modification time and keep the earliest file
        sorted_paths = sorted(paths, key=lambda p: p.stat().st_mtime)
        to_delete = sorted_paths[1:]  # everything after the oldest

        for p in to_delete:
            if dry_run:
                print(f"  [DRY-RUN] Would delete: {p}")
                summary["deleted"].append(str(p))
                continue
            try:
                p.unlink()
                print(f"  Deleted: {p}")
                summary["deleted"].append(str(p))
            except OSError as exc:
                summary["errors"].append((str(p), str(exc)))
                print(f"  [ERROR] {p}: {exc}")

    return summary
