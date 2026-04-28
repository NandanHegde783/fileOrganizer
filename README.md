# Smart File Organizer

A Python CLI tool that **automatically sorts files into categorized folders**, detects duplicates, and supports scheduled auto-cleanup. Runs natively or inside Docker — no external dependencies required.

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
| 🐳 Docker | Fully containerised — stdlib only, no pip install needed |

---

## Quick Start (Docker) — Recommended

### 1. Prerequisites

Make sure your user can run Docker without `sudo`:

```bash
sudo usermod -aG docker $USER
newgrp docker   # apply without logging out
```

### 2. Build the image

```bash
cd NewProject/fileOrganizer
./build.sh
```

### 3. Run

```bash
# Preview changes (dry-run)
./run.sh ~/Downloads --dry-run

# Organise your Downloads folder
./run.sh ~/Downloads

# Recursive + copy mode
./run.sh ~/Downloads --recursive --copy

# Detect duplicates
./run.sh ~/Downloads --detect-dupes

# Delete duplicates (keeps oldest, asks for confirmation)
./run.sh ~/Downloads --delete-dupes

# Undo the last run
./run.sh ~/Downloads --undo

# Run on a schedule (blocks; Ctrl-C to stop)
./run.sh ~/Downloads --schedule daily
./run.sh ~/Downloads --schedule "every 30 minutes"
```

> The container mounts your host directory as `/data` and is removed automatically after each run (`--rm`).

---

## Local (No Docker)

No external packages needed — stdlib only.

```bash
cd NewProject/fileOrganizer

# Organise current directory
python -m fileOrganizer .

# Organise a specific folder
python -m fileOrganizer ~/Downloads

# Preview without making changes
python -m fileOrganizer ~/Downloads --dry-run

# Organise recursively
python -m fileOrganizer ~/Downloads --recursive

# Copy instead of move
python -m fileOrganizer ~/Downloads --copy

# Undo last organize
python -m fileOrganizer ~/Downloads --undo

# Find duplicate files
python -m fileOrganizer ~/Downloads --detect-dupes

# Find AND delete duplicates
python -m fileOrganizer ~/Downloads --delete-dupes

# Schedule: organise every day
python -m fileOrganizer ~/Downloads --schedule daily

# Schedule: every 30 minutes
python -m fileOrganizer ~/Downloads --schedule "every 30 minutes"
```

---

## CLI Reference

```
usage: fileOrganizer [TARGET_DIR] [OPTIONS]

positional arguments:
  TARGET_DIR            Directory to organise (default: current directory)

Organisation:
  --recursive, -r       Also organise files in subdirectories
  --copy, -c            Copy files instead of moving them
  --dry-run, -n         Preview what would happen without making any changes
  --undo                Reverse the last organize operation

Duplicates:
  --detect-dupes        Scan for duplicate files and print a report
  --delete-dupes        Delete duplicate files (keeps oldest). Implies --detect-dupes

Scheduler:
  --schedule INTERVAL   Run organizer repeatedly on an interval.
                        E.g. 'hourly', 'daily', 'weekly',
                             'every 30 minutes', 'every 2 hours'
```

---

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

> **Extending:** Add new mappings in `config.py` — no logic changes needed.

---

## Project Structure

```
fileOrganizer/
├── __init__.py            # Public API
├── __main__.py            # CLI entry point
├── config.py              # Extension → folder mapping
├── organizer.py           # Core sort, move/copy, undo logic
├── duplicate_detector.py  # SHA-256 duplicate detection
├── scheduler.py           # Recurring schedule (stdlib time.sleep)
├── requirements.txt       # No external dependencies
├── Dockerfile             # Single-stage, no pip install
├── build.sh               # Build the Docker image
└── run.sh                 # Run the container against a host directory
```

---

## How Undo Works

Every organize run writes a `.organizer_undo.json` log inside the target directory. Running `--undo` reads that log and moves every file back to its original location, then removes the log.

---

## How Duplicate Detection Works

Files are fingerprinted with **SHA-256** (content hash). Two files are duplicates only if their content is byte-for-byte identical — file names are irrelevant. When deleting, the **oldest** file (by creation/modification time) is kept and all newer copies are removed.

> Large files are hashed in 64 KB chunks to keep memory usage flat regardless of file size.
