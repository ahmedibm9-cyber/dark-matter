# Contributing

This guide is for AI agents and humans who want to extend Dark Matter.

## Design Rules

1. **Everything goes through `GraphService`.** No component touches storage directly.
2. **Detectors return findings, not side effects.** Pure function in, list of findings out.
3. **Ponytail first.** Add the lazy solution. Mark its ceiling with `# ponytail:`.
4. **Test your addition.** One test that exercises the happy path.

## Adding a Detector

```python
# 1. Create function in audit/detectors/structural.py
def my_new_detector(graph: GraphService, evidence: list[dict]) -> list[Finding]:
    findings = []
    for ev in evidence:
        if some_condition(ev):
            findings.append(Finding(
                rule_id="DM-STRUCT-006",
                severity="medium",
                file=ev["payload"]["relative_path"],
                line=ev["payload"].get("line", None),
                description="Found a thing",
                confidence=0.8,
                suggested_fix="Do something about it",
            ))
    return findings

# 2. Register in audit/detectors/__init__.py
from .structural import my_new_detector
DETECTORS.append(("Structural: My New Detector", my_new_detector))

# 3. Done. dm audit will now run your detector.
```

## Adding a CLI Command

```python
# 1. Add subparser in cli/main.py::main()
sub = subparsers.add_parser("mycmd", help="Does something")
sub.add_argument("--path", default=".", help="Repository path")

# 2. Write handler
def cmd_mycmd(args):
    repo = _check_aether(args.path)
    ...

# 3. Register handler
commands["mycmd"] = cmd_mycmd
```

## Code Standards

- **Type hints on every function signature.** No `def foo(args)` — always
  `def foo(args: argparse.Namespace) -> None`.
- **No comments except `# ponytail:`** — let types and function names speak.
- **One export per line** in `__init__.py`.
- **Tests go next to the module** they test: `tests/audit/test_structural.py`.
- **Run before pushing:** `make all` (installs, tests, lints, typechecks).

## Commit Messages

```
<area>: <short description>

Longer explanation if needed.
```

Areas: audit, cli, collectors, compiler, graph, inference, store,
verification, pipeline, infra, docs.

## Release Process

1. Update `CHANGELOG.md` with new version and changes.
2. Update version in `pyproject.toml`.
3. Tag: `git tag v0.2.0 && git push --tags`.
4. CI will auto-publish to PyPI (if configured).
