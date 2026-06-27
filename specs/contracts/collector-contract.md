# Collector Contract v1

## Inputs
- `repo_path: Path` — target repository root
- `scope: str` — "all" | "paths" | "commit_range"
- `paths: str[]` — if scope is "paths"
- `commit_range: (str, str)` — if scope is "commit_range"
- `config: dict` — collector-specific configuration

## Outputs
- `list[RawEvidence]` — zero or more evidence items
- `collector_name: str`
- `collector_version: str`

## Invariants
1. Collectors are side-effect free: they never modify the repository
2. Collectors are resource-bounded (max files, max depth, timeout)
3. One collector failure never blocks other collectors
4. Collectors are independently versioned
5. Empty output (zero evidence) is valid — means nothing to collect
6. `collect()` is reentrant and idempotent
7. Evidence timestamps reflect observation time, not collection time

## Failure Modes
| Mode | Cause | Behavior |
|------|-------|----------|
| Path not found | repo_path doesn't exist | Return empty list, log warning |
| Timeout | Collector exceeds time limit | Kill collector, return partial results |
| Permission denied | Cannot read target path | Return empty list, log warning |
| Resource limit | Files/depth/size exceeded | Return partial results, log warning |
| Collector crash | Unhandled exception | Return empty list, log error |
| Invalid scope | Unrecognized scope value | Default to "all" |
