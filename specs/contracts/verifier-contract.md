# Verifier Contract v1

## Inputs
- `claim: str` — the assertion to verify
- `claim_type: str` — fact, relationship, property value, node existence
- `supporting_evidence: list[Evidence]` — evidence backing the claim
- `confidence_threshold: float` — minimum confidence to accept (default 0.7)

## Outputs
- `result: str` — "verified", "rejected", "inconclusive"
- `confidence: float` — computed from evidence
- `reason: str` — explanation of the result
- `evidence_used: str[]` — IDs of evidence evaluated
- `evidence_missing: str[]` — expected evidence not found
- `verification_id: str` — VERIFY-XXXXX

## Invariants
1. Verifiers never modify the graph
2. Verification is deterministic for identical input evidence
3. Every verification produces a traceable record
4. A claim with zero supporting evidence → "inconclusive" (not "rejected")
5. A claim with contradictory evidence → "rejected" with explanation
6. Verification records are immutable
7. The verifier does not trust the source of the claim — only the evidence

## Failure Modes
| Mode | Cause | Behavior |
|------|-------|----------|
| No evidence | zero evidence provided | Return "inconclusive" with confidence 0.0 |
| Confidence below threshold | computed < threshold | Return "rejected" with computed confidence |
| Conflicting evidence | Evidence both supports and contradicts | Return "rejected", document both sides |
| Stale evidence | All evidence past freshness threshold | Return "inconclusive", flag staleness |
| Verifier crash | Unexpected error | Retry up to 3 times, then error |
