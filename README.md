# Smart File Organizer

A Python CLI tool that **automatically sorts files into categorized folders**, detects duplicates, and supports scheduled auto-cleanup.

## Features

| Feature | Description |
|---|---|
| 📁 Auto-Sort | Moves/copies files into `Images/`, `Documents/`, `Videos/`, `Audio/`, `Archives/`, `Code/`, `Misc/`, etc. |
| 🔍 Dry-Run | Preview changes without touching any files |
| ♻️ Undo | Reverse the last organize operation |
| 🔁 Duplicate Detection | SHA-256 content hashing to find exact duplicate files |
| 🗑️ Duplicate Deletion | Delete duplicates, keeping the oldest copy |
| ⏱️ Scheduler | Run automatically on a schedule (`hourly`, `daily`, `every 30 minutes`, …) |
| 🔄 Recursive | Optionally organise subdirectories too |
| 📋 Summary | Clear report of files moved, skipped, and errors |

## Installation

```bash
cd NewProject
pip install -r file_organizer/requirements.txt
```

## Usage

```bash
# Organise current directory
python -m file_organizer .

# Organise a specific folder
python -m file_organizer ~/Downloads

# Preview without making changes
python -m file_organizer ~/Downloads --dry-run

# Organise recursively (including subdirectories)
python -m file_organizer ~/Downloads --recursive

# Copy instead of move
python -m file_organizer ~/Downloads --copy

# Undo last organize
python -m file_organizer ~/Downloads --undo

# Find duplicate files
python -m file_organizer ~/Downloads --detect-dupes

# Find AND delete duplicates (with confirmation)
python -m file_organizer ~/Downloads --delete-dupes

# Schedule: organise every day automatically
python -m file_organizer ~/Downloads --schedule daily

# Schedule: every 30 minutes
python -m file_organizer ~/Downloads --schedule "every 30 minutes"
```

## File Type Mappings

| Category | Extensions |
|---|---|
| **Images** | `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.svg`, `.webp`, `.tiff`, `.ico`, `.heic`, `.raw` |
| **Documents** | `.pdf`, `.doc(x)`, `.xls(x)`, `.ppt(x)`, `.odt`, `.txt`, `.md`, `.csv`, `.rtf` |
| **Videos** | `.mp4`, `.mkv`, `.avi`, `.mov`, `.wmv`, `.flv`, `.webm`, `.m4v` |
| **Audio** | `.mp3`, `.wav`, `.flac`, `.aac`, `.ogg`, `.wma`, `.m4a` |
| **Archives** | `.zip`, `.tar`, `.gz`, `.bz2`, `.xz`, `.rar`, `.7z` |
| **Code** | `.py`, `.js`, `.ts`, `.java`, `.c`, `.cpp`, `.rs`, `.go`, `.html`, `.css`, `.sh`, `.json`, `.yaml` |
| **Executables** | `.exe`, `.dmg`, `.iso`, `.apk`, `.deb`, `.rpm` |
| **Fonts** | `.ttf`, `.otf`, `.woff`, `.woff2` |
| **Misc** | Everything else |

> **Extending:** Add new mappings in `file_organizer/config.py` — no logic changes needed.

## Project Structure

```
file_organizer/
├── __init__.py            # Public API
├── __main__.py            # CLI entry point
├── config.py              # Extension → folder mapping
├── organizer.py           # Core sort, move/copy, undo
├── duplicate_detector.py  # SHA-256 duplicate detection
├── scheduler.py           # Recurring schedule support
└── requirements.txt       # schedule (only external dep)
tests/
├── test_organizer.py
└── test_duplicate_detector.py
```

## Running Tests

```bash
pip install pytest
pytest tests/ -v
```

## How Undo Works

Every organize run writes a `.organizer_undo.json` log inside the target directory. When you run `--undo`, it reads this log and moves files back to their original locations, then removes the log.
