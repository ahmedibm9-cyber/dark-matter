# RFC 0003: Confidence Formula

**Status:** Accepted  
**Date:** 2026-06-26  
**Author:** Architecture specification  

## Summary

Define how confidence scores are computed for nodes, edges, and facts.
Confidence is always computed, never stored. Every confidence score is
decomposable into its contributing factors.

## Motivation

Without explainable confidence:
- AI models appear to hallucinate (they may just have low confidence)
- Users cannot distinguish verified facts from inferences
- Stale knowledge persists without detection
- There is no mechanism for knowledge quality improvement

## Design

Confidence is a float in [0.0, 1.0] computed as:

```
Final = 1 - Π(1 - wi × fi × ti × ai) × v
```

Where:
- wi = evidence confidence_weight (how definitive the evidence type is)
- fi = freshness factor (decays over time per evidence kind)
- ti = source trust factor (trustworthiness of the collector)
- ai = agreement factor (consensus among evidence sources)
- v = verification multiplier (independently verified boosts or contradicts)

### Tiers
| Range | Label |
|-------|-------|
| 0.95+ | Verified |
| 0.85-0.94 | High Confidence |
| 0.70-0.84 | Medium Confidence |
| 0.50-0.69 | Low Confidence |
| 0.25-0.49 | Speculative |
| 0.00-0.24 | Unknown |

### Key Rules
- Confidence is never stored — always computed on query
- Every confidence score must be explainable (decomposable into factors)
- A fact with zero supporting evidence has confidence 0.0
- Freshness decay is evidence-kind-specific

## Alternatives Considered
- **Static confidence**: Rejected — cannot account for staleness
- **Simple average**: Rejected — loses information about evidence quality
- **Binary (true/false)**: Rejected — loses nuance needed for AI context

## Consequences
- Confidence is always current (reflects latest evidence)
- Computational cost on query (mitigated by caching)
- Users trust what they can decompose

## Status
This design is implemented in PIPELINE.md §4.
