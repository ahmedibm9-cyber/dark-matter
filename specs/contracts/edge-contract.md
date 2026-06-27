# Edge Contract v1

## Inputs
- `source_id: str` — must reference existing node
- `target_id: str` — must reference existing node
- `kind: str` — must match a registered edge kind
- `properties: dict` — optional, schema-validated per kind
- `evidence_refs: str[]` — at least one reference

## Outputs
- Composite key: `(source_id, target_id, kind)`
- `properties: dict`
- `evidence_refs: str[]`
- `confidence: float` — computed
- `created: timestamp`
- `modified: timestamp`

## Invariants
1. Source and target nodes must exist before edge creation
2. Edge kind must be registered
3. Properties must satisfy the edge kind's schema
4. `(source_id, target_id, kind)` is unique
5. If either endpoint is deprecated, the edge is candidates for removal
6. Every edge is traceable to its creating evidence

## Failure Modes
| Mode | Cause | Behavior |
|------|-------|----------|
| Missing source | source_id not in graph | Reject with reference error |
| Missing target | target_id not in graph | Reject with reference error |
| Duplicate edge | Same composite key exists | Reject with conflict error |
| Unknown kind | Edge kind not registered | Reject with schema error |
| Self-loop | source_id == target_id | Reject (unless explicitly allowed by kind) |
