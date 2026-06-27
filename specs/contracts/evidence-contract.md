# Evidence Contract v1

## Inputs
- `kind: str` — evidence type (file, test, config, log, runtime, git, document, claim)
- `source: str` — collector or method that produced it
- `source_version: str` — version of the collector
- `payload: dict` — the collected data
- `confidence_weight: float` — [0.0, 1.0] how definitive this evidence type is
- `tags: str[]` — optional classification

## Outputs
- `id: str` — EVID-XXXXX
- `hash: str` — SHA-256 of (kind + source + payload)
- `collected_at: timestamp`
- `ingested_at: timestamp`
- `deduplicated: bool` — true if hash already existed

## Invariants
1. Evidence is immutable once committed
2. Evidence is never deleted
3. Evidence hash uniquely identifies content (same payload = same hash)
4. Evidence does not reference nodes or edges (nodes reference evidence)
5. Evidence kind must be registered
6. `confidence_weight` is in [0.0, 1.0]
7. Evidence is content-addressed (same hash produces same ID)
8. Evidence `expires` is null unless the evidence type is inherently temporary

## Failure Modes
| Mode | Cause | Behavior |
|------|-------|----------|
| Invalid weight | confidence_weight outside [0,1] | Clamp to valid range |
| Missing payload | payload empty or null | Reject with validation error |
| Unknown kind | Evidence kind not registered | Accept with warning |
| Hash collision | Two different payloads, same hash | Theoretical only (SHA-256) |
| Oversized payload | Payload > 1MB | Reject with size limit error |
