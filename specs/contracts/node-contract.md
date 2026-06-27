# Node Contract v1

## Inputs
- `kind: str` — must match a registered node kind in the type registry
- `name: str` — human-readable identifier
- `properties: dict` — must satisfy the schema for the given kind
- `evidence_refs: str[]` — at least one reference to existing evidence

## Outputs
- `id: str` — stable identifier in format KIND-XXXXX
- `kind: str` — the node kind
- `name: str`
- `properties: dict` — validated against the kind's schema
- `evidence_refs: str[]`
- `timestamps: { created, modified, observed, verified, expired? }`
- `checksum: str` — hash of kind + properties + evidence_refs
- `confidence: float` — computed, not stored

## Invariants
1. `id` is immutable for the lifetime of the node
2. `kind` never changes
3. At least one evidence reference must exist
4. Properties must satisfy the kind's schema (required fields present, types match)
5. `modified` ≥ `created`
6. `expired` is null until explicit deprecation
7. `id` is globally unique across all node kinds
8. Every node is traceable to the event that created it

## Failure Modes
| Mode | Cause | Behavior |
|------|-------|----------|
| Unknown kind | Kind not in registry | Reject with schema error |
| Missing required field | Properties incomplete | Reject with validation error |
| No evidence | evidence_refs empty | Reject with provenance error |
| Duplicate ID | ID already exists | Reject with conflict error |
| Unique constraint violation | Duplicate name/path per kind | Reject with conflict error |
