"""
config.py — File-type → destination folder mapping.
Extend EXTENSION_MAP to support new file types without touching any logic.
"""

EXTENSION_MAP: dict[str, str] = {
    # Images
    ".jpg": "Images",
    ".jpeg": "Images",
    ".png": "Images",
    ".gif": "Images",
    ".bmp": "Images",
    ".svg": "Images",
    ".webp": "Images",
    ".tiff": "Images",
    ".ico": "Images",
    ".heic": "Images",
    ".raw": "Images",
    # Documents
    ".pdf": "Documents",
    ".doc": "Documents",
    ".docx": "Documents",
    ".xls": "Documents",
    ".xlsx": "Documents",
    ".ppt": "Documents",
    ".pptx": "Documents",
    ".odt": "Documents",
    ".ods": "Documents",
    ".odp": "Documents",
    ".txt": "Documents",
    ".md": "Documents",
    ".rtf": "Documents",
    ".csv": "Documents",
    # Videos
    ".mp4": "Videos",
    ".mkv": "Videos",
    ".avi": "Videos",
    ".mov": "Videos",
    ".wmv": "Videos",
    ".flv": "Videos",
    ".webm": "Videos",
    ".m4v": "Videos",
    ".3gp": "Videos",
    # Audio
    ".mp3": "Audio",
    ".wav": "Audio",
    ".flac": "Audio",
    ".aac": "Audio",
    ".ogg": "Audio",
    ".wma": "Audio",
    ".m4a": "Audio",
    # Archives
    ".zip": "Archives",
    ".tar": "Archives",
    ".gz": "Archives",
    ".bz2": "Archives",
    ".xz": "Archives",
    ".rar": "Archives",
    ".7z": "Archives",
    # Code
    ".py": "Code",
    ".js": "Code",
    ".ts": "Code",
    ".java": "Code",
    ".c": "Code",
    ".cpp": "Code",
    ".h": "Code",
    ".rs": "Code",
    ".go": "Code",
    ".rb": "Code",
    ".php": "Code",
    ".html": "Code",
    ".css": "Code",
    ".sh": "Code",
    ".json": "Code",
    ".yaml": "Code",
    ".yml": "Code",
    ".toml": "Code",
    ".xml": "Code",
    # Executables / Disk images
    ".exe": "Executables",
    ".dmg": "Executables",
    ".iso": "Executables",
    ".apk": "Executables",
    ".deb": "Executables",
    ".rpm": "Executables",
    # Fonts
    ".ttf": "Fonts",
    ".otf": "Fonts",
    ".woff": "Fonts",
    ".woff2": "Fonts",
}

# Files that belong to already-organised destination folders are skipped
ORGANISED_FOLDERS: set[str] = set(EXTENSION_MAP.values()) | {"Misc"}

# Fallback folder for unrecognised extensions
MISC_FOLDER = "Misc"
