# Dark Matter

**Repository intelligence platform.** Converts any codebase into a verifiable, versioned knowledge graph. Designed for AI agents and the humans who command them.

```bash
pip install -e .
dm init .          # Scan project → build graph → find bugs
dm audit .         # Structural + regex bug detection
dm audit . -p      # Ponytail mode: regex-only, 6x faster
```

## One Shot

```bash
dm init /path/to/project && dm audit /path/to/project --severity high
```

That scans the project, builds a knowledge graph, and reports high-severity bugs — zero config.

## What It Finds

| Detector | Severity | What |
|----------|----------|------|
| Duplicate files | high | Same content hash across multiple paths |
| Hardcoded secrets | high | Passwords, API keys, tokens in source |
| SQL injection | high | String formatting in queries |
| Eval/exec usage | high | Dynamic code execution |
| Orphan files | medium | Code files never imported anywhere |
| Missing tests | medium | Source file without corresponding test |
| Empty catch blocks | medium | Silent exception swallowing |
| Bloated files | low | Files >500 lines |
| Console.log / print | low | Debug statements in production code |
| TODO without ticket | info | Markers without issue reference |

## Commands

| Command | Action |
|---------|--------|
| `dm init <path>` | Full scan, build graph, compile |
| `dm scan` | Incremental update (changed files only) |
| `dm scan -p` | Ponytail: skip infer/verify/compile, just collect + audit |
| `dm audit` | Run all 12 detectors |
| `dm audit -p` | Ponytail: 7 regex detectors, compact output |
| `dm audit --severity high` | Only critical + high findings |
| `dm compile` | Generate markdown report + .ai package |
| `dm verify` | Check facts against evidence |
| `dm search <q>` | Find files in knowledge graph |
| `dm context` | Full project context for AI agents (the ultimate prompt) |
| `dm report` | Deployability report for engineer handoff |
| `dm watch` | Watch repo for changes, auto-audit |
| `dm audit --fix` | Auto-fix console.log, empty catch, etc. |
| `dm audit --json` | Machine-readable output for AI agents |

## Demo

Scanning Dark Matter with itself:

```bash
$ dm audit -p
  1 high, 2 info

  src/dm/audit/detectors/regex.py:15  (high) Dynamic code execution: compile()
  src/dm/audit/detectors/__init__.py:7  (info) TODO without ticket reference

  3 findings
```

Auto-fix and watch:

```bash
$ dm audit -p --fix
  Auto-fixed: 1, failed: 0

$ dm watch
[dm] Watching dark-matter... (Ctrl+C to stop)
[14:23:45] 3 findings, 1 fixed, 0 failed
[14:23:48] 0 findings
```

Deployability report (for engineers):

```bash
$ dm report
  Report written to deployability-report.md
```

← One page. Verdict: ✅ DEPLOYABLE or ⛔ BLOCKED.

Audit any repo in one line:

```bash
git clone https://github.com/psf/black /tmp/black
dm init /tmp/black && dm audit /tmp/black --severity high
```

## Project Structure

```
AGENTS.md            ← Start here if you're an AI agent
VIBE-CODERS-GUIDE.md ← Start here if you're a human who vibes
src/dm/
  cli/main.py        Command routing (12 commands)
  pipeline.py        7-stage pipeline orchestrator
  graph/             Graph service + schema
  store/             JSON file store
  collectors/        File system walker
  inference/         Rule engine (keyword matching)
  verification/      3-factor confidence model
  audit/detectors/   5 structural + 7 regex detectors
  compiler/          Markdown + .ai output
```

## Philosophy

**Ponytail.** This project is built by a lazy senior developer. Every shortcut
is marked with a `# ponytail:` comment naming the ceiling and the upgrade path.

**No AI dependency for core.** Detection is pure heuristics + regex. An AI
model can be layered on top (Phase 5+), but the core loop works offline with
zero external calls.

**Everything traceable.** Every fact links to its evidence. Evidence links to
its source file. Confidence is computed mathematically from weight × freshness
× source trust.

## Dependencies

- Python ≥3.10
- PyYAML (for rule packs)

## Install

```bash
git clone <this-repo>
cd dark-matter
pip install -e .
```

Then from any project folder: `dm init .`

## Status

v0.2 — 12 detectors, auto-fix, pre-commit hook, CI gate, JSON output,
deployability report, watch mode, AI agent protocol. Everything automatic.
Next: semantic detectors, AI model layer, more advanced fix strategies.
