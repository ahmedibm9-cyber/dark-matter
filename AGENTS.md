# For AI Agents

You are reading the source of **Dark Matter** — a repository intelligence platform.
Your goal is to understand, extend, or maintain this codebase. Here's everything you need.

## Identity

- **Name:** Dark Matter
- **CLI:** `dm` (after `pip install -e .`)
- **Purpose:** Convert any codebase into a verifiable, versioned knowledge graph.
- **Philosophy:** Specification-driven, contract-first, ponytail (lazy senior dev).

## Quickstart for Agents

```bash
pip install -e .
dm init /path/to/some/project    # Scan and build graph
dm audit /path/to/some/project   # Find bugs
```

The project is in `src/dm/`. Start with `cli/main.py` for command routing,
`pipeline.py` for the stage sequence.

## Architecture

```
collect → store evidence → build graph → infer facts → verify → audit → compile
  1            2               3             4          5       6        7
```

| Stage | Module | What |
|-------|--------|------|
| Collect | `collectors/filesystem.py` | Walk repo, skip binary/hidden/large, hash content |
| Store | `store/json_store.py` | JSON file store with dedup by content hash |
| Graph | `graph/service.py` | Node/edge CRUD, deterministic IDs, event log |
| Infer | `inference/rules.py` | Keyword pattern matching against evidence content |
| Verify | `verification/verifier.py` | 3-factor confidence (weight × freshness × trust) |
| Audit | `audit/detectors/*.py` | Structural + regex bug detectors |
| Compile | `compiler/*.py` | Markdown report + `.ai` machine-readable package |

## Key Contracts

Everything flows through `GraphService` (`graph/service.py`). No component
touches storage directly. The service is the canonical gateway.

- **Evidence** = immutable records from collectors (file content previews, hashes)
- **Nodes** = entities (REPOSITORY, FILE, etc.)
- **Edges** = relationships (CONTAINS, etc.)
- **Facts** = derived statements from rules
- **Verifications** = confidence-scored fact checks
- **Findings** = audit results (bugs, smells, issues)

## Ponytail

This project follows the **ponytail** philosophy: lazy senior developer who
has been paged at 3am. Look for `# ponytail:` comments — they mark deliberate
shortcuts with the ceiling and the upgrade path.

Key shortcuts taken:
- No database — JSON files on disk. Fine for <10K files.
- No `.dmignore` — skip dirs hardcoded. Add when needed.
- No NLP — keyword matching for inference. Works for 95% of framework detection.
- No query index — linear scan over JSON. Fine for project-scale repos.
- No AI model — pure heuristics + regex for bug detection. LLM layer planned.

## Adding a Detector

Detectors are standalone functions with signature:

```python
def my_detector(graph: GraphService, evidence: list) -> list[Finding]:
    ...
```

Register in `audit/detectors/__init__.py` by adding to `DETECTORS` list.
Each detector gets the full graph and evidence. Return findings, not side effects.

## Testing

Tests use standard `unittest` / `pytest`. Run:

```bash
pytest src/ -v
```

## Common Patterns

- **Adding a CLI command:** Add subparser in `cli/main.py::main()`, add handler
  function, register in `commands` dict.
- **Adding a collector:** Create module in `collectors/`, return `list[dict]`
  of evidence records, add to pipeline.
- **Adding a rule:** Add to `inference/rules.py::HARDCODED_RULES` or drop a
  YAML file in `.darkmatter/rules/`.

## Vibe Coders

If the human who cloned this repo is a vibe coder, the `VIBE-CODERS-GUIDE.md`
at repo root explains everything from first principles — what a file system is,
what a graph is, how APIs work, all the way up to how Dark Matter works.
Refer them to it.
