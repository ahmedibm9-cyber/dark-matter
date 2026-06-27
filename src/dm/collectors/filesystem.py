import os
import hashlib
from datetime import datetime
from pathlib import Path

CONFIDENCE_WEIGHTS = {
    ".md": 0.60,
    ".json": 0.80,
    ".py": 0.85,
    ".js": 0.85,
    ".ts": 0.85,
    ".yaml": 0.80,
    ".yml": 0.80,
    ".toml": 0.80,
}

# ponytail: hardcoded skip dirs, no .dmignore file support yet
SKIP_DIRS = {".darkmatter", ".git", "__pycache__", "node_modules",
             ".venv", "venv", "env", ".tox", ".eggs", "dist", "build",
             ".idea", ".vscode", ".next", ".nuxt", ".svelte-kit",
             "bin", "obj", "vendor", "packages", "target", "out",
             "output", ".npm", ".cache", ".config", ".local",
             ".openclaw", ".claude", ".opencode", ".mavis",
             ".cursor", ".vscode-server", ".ssh", ".docker",
             "AppData", "Application Data",
             "Desktop", "Downloads", "Pictures", "Photos",
             "Videos", "Music", "Movies", " recordings",
             "Documents", "OneDrive", "iCloud Drive",
             "Dropbox", "Google Drive", "Library"}

# ponytail: safety limit, prevents OOM on massive home-dir scans
MAX_FILES = 5000

BINARY_EXTS = {".exe", ".dll", ".so", ".dylib", ".bin", ".dat",
               ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".svg",
               ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
               ".zip", ".tar", ".gz", ".bz2", ".xz", ".7z", ".rar",
               ".mp3", ".mp4", ".avi", ".mov", ".wav", ".flac", ".ogg",
               ".woff", ".woff2", ".ttf", ".eot",
               ".pyc", ".pyo", ".pyd", ".obj", ".o", ".a", ".lib",
               ".class", ".jar", ".war", ".nar",
               ".pak", ".unity", ".asset", ".resx"}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

def _walk_files(root: Path):
    """Walk files, skipping inaccessible dirs silently."""
    try:
        for entry in sorted(root.iterdir()):
            try:
                if entry.is_dir():
                    if entry.name.startswith(".") or entry.name in SKIP_DIRS:
                        continue
                    yield from _walk_files(entry)
                elif entry.is_file():
                    yield entry
            except (PermissionError, OSError, FileNotFoundError):
                continue
    except (PermissionError, OSError, FileNotFoundError):
        pass

def collect(repo_path: str, progress_cb=None) -> list:
    evidence = []
    root = Path(repo_path)
    total = 0
    skipped = 0
    for f in _walk_files(root):
        total += 1
        if total > MAX_FILES:
            break
        ext = f.suffix.lower()
        if ext in BINARY_EXTS:
            skipped += 1
            continue
        size = f.stat().st_size
        if size > MAX_FILE_SIZE:
            skipped += 1
            continue
        try:
            content = f.read_text(encoding="utf-8", errors="replace")
        except Exception:
            skipped += 1
            continue
        payload = {
            "path": str(f.absolute()),
            "relative_path": str(f.relative_to(root)),
            "extension": ext,
            "size_bytes": size,
            "line_count": len(content.splitlines()),
            # ponytail: 500-char preview is enough for regex/keyword detection
    "content_preview": content[:500],
            "hash": hashlib.sha256(content.encode()).hexdigest(),
        }
        evidence.append({
            "kind": "file",
            "source": "filesystem",
            "source_version": "1.0.0",
            "payload": payload,
            "confidence_weight": CONFIDENCE_WEIGHTS.get(ext, 0.50),
            "tags": ["file", ext.lstrip(".")],
            "collected_at": datetime.utcnow().isoformat(),
        })
        if progress_cb and total % 50 == 0:
            progress_cb(len(evidence), total, skipped)
    if progress_cb:
        progress_cb(len(evidence), total, skipped)
    return evidence
