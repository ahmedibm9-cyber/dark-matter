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

v0.1 — Core loop complete. 12 bug detectors. Ponytail mode. Ready to use.
Next: AI model layer, semantic detectors, auto-fix.
