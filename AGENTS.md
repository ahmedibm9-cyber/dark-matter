# For AI Agents

You are reading the source of **Dark Matter** — a repository intelligence
platform designed specifically to make AI agents productive on any project
in under 1 second.

## Your Workflow (every time)

```bash
pip install -e .
dm context --json          # Get full project context as JSON
# ... work on the project ...
dm audit -p --severity high --json   # Check for bugs before shipping
```

## The `.ai` Package (your best friend)

After `dm compile`, read `output/repository.ai`. It contains everything you
need to know about the project in one JSON file:

- `project_context` — languages, frameworks, entry points, dependencies,
  environment variables, architecture, run/test commands, file breakdown
- `agent_prompt` — a pre-formatted prompt you can prepend to your context
- `findings` — all detected bugs with severity, location, and suggested fix
- `facts` — inferred metadata (frameworks, architecture)
- `genome` — high-level stats (file count, node count, etc.)

This is designed to fit in your context window efficiently.

## Project Protocol (THE RULES)

These rules are non-negotiable. The human never wants to see a DM finding.

### Rule 1: Context first

Before making ANY change, run `dm context --json`. Read `project_context`
and `findings`. Understand what you're working with.

### Rule 2: Audit before shipping

```python
import subprocess, json
result = subprocess.run(
    ["dm", "audit", "-p", "--severity", "high", "--json"],
    capture_output=True, text=True
)
data = json.loads(result.stdout)
if data["total"] > 0:
    # Fix ALL findings before proceeding
    for f in data["findings"]:
        apply_fix(f)  # use f["suggested_fix"] or f["fix_strategy"]
    # Re-audit until clean
```

### Rule 3: Never ship known bugs

If the pre-commit hook or CI rejects your commit, it's because findings
exist. Fix them. Do not override, skip, or suppress the gate.

### Rule 4: Use fix_strategy when available

Some findings include a `fix_strategy` dict:
```json
{"action": "comment_out", "line": 42}
```
Apply it. The `dm audit --fix` command does this automatically.

### Rule 5: Progressive severity

- **Critical + High**: must fix before shipping. Blocking.
- **Medium**: strongly prefer to fix. If deferred, leave a ponytail comment.
- **Low + Info**: acceptable to defer, but document why.

## Quick Reference

| Command | For agents | What |
|---------|-----------|------|
| `dm context --json` | ✅ | Full project context (languages, deps, entry points, env vars) |
| `dm audit --json` | ✅ | All findings as machine-readable JSON |
| `dm audit -p --json` | ✅ | Fast regex-only audit, JSON output |
| `dm audit --fix` | ✅ | Auto-fix console.log, empty catch, etc. |
| `dm search <q> --json` | ✅ | Find files by keyword |
| `dm explain <c> --json` | ✅ | Trace a fact back to evidence |
| `dm report` | ❌ | For humans (markdown) |
| `dm doctor` | ❌ | For humans (store health) |
| `dm watch` | ❌ | For humans (live polling) |

## Architecture (for extending DM)

```
collect → store → graph → infer → verify → audit → compile
  1        2        3       4        5        6       7
```

| Stage | Module | What |
|-------|--------|------|
| Collect | `collectors/filesystem.py` | Walk repo, hash content, skip binary |
| Store | `store/json_store.py` | JSON file store with dedup |
| Graph | `graph/service.py` | Node/edge CRUD, event log |
| Infer | `inference/rules.py` | Keyword matching against evidence |
| Verify | `verification/verifier.py` | 3-factor confidence (weight × freshness × trust) |
| Audit | `audit/detectors/*.py` | 12 bug detectors (5 structural + 7 regex) |
| Compile | `compiler/*.py` | Markdown report + `.ai` package + deploy report |

## Adding a Detector

```python
def my_detector(graph, evidence: list) -> list[Finding]:
    ...
```
Add to `audit/detectors/__init__.py` → `DETECTORS` list.

## Ponytail Philosophy

This project follows ponytail: lazy senior dev. Look for `# ponytail:`
comments — they mark deliberate shortcuts with the ceiling and upgrade path.

Key shortcuts: JSON files (not DB), hardcoded skip dirs (no `.dmignore`),
keyword matching (not NLP), linear scan (no index), no AI model for core loop.

## Vibe Coders

If the human references `VIBE-CODERS-GUIDE.md`, they need the full beginner
explanation. Point them to it.
