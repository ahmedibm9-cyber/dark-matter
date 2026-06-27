import os
import sys
import time
from datetime import datetime
from pathlib import Path


def _walk_files(root: Path):
    for entry in root.rglob("*"):
        if entry.is_file() and ".darkmatter" not in entry.parts and ".git" not in entry.parts:
            yield entry


def _latest_mtime(root: Path) -> float:
    latest = 0.0
    for f in _walk_files(root):
        try:
            mtime = os.path.getmtime(f)
            if mtime > latest:
                latest = mtime
        except OSError:
            pass
    return latest


def watch(repo_path: str, interval: int = 3, fix: bool = False):
    repo = Path(repo_path).resolve()
    dm_dir = repo / ".darkmatter"
    if not dm_dir.exists():
        print(f"[dm] Not initialized: {repo}")
        print(f"[dm] Run: dm init {repo}")
        sys.exit(1)

    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from dm.store.json_store import JSONStore
    from dm.audit import run_detectors_ponytail
    from dm.audit.fixer import apply_all

    store = JSONStore(str(dm_dir))
    last_mtime = _latest_mtime(repo)

    print(f"[dm] Watching {repo.name}... (Ctrl+C to stop)")
    try:
        while True:
            time.sleep(interval)
            current = _latest_mtime(repo)
            if current <= last_mtime:
                continue
            last_mtime = current
            evidence = store.find_evidence()
            if not evidence:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] No evidence yet, run dm init first")
                continue
            results = run_detectors_ponytail(evidence)
            total = sum(len(v) for v in results.values())
            if fix:
                all_f = [f for fs in results.values() for f in fs]
                fixed, failed = apply_all(all_f, str(repo))
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {total} findings, {fixed} fixed, {failed} failed")
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {total} findings")
    except KeyboardInterrupt:
        print(f"\n[dm] Stopped.")
