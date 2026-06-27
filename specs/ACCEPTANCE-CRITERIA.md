# Acceptance Criteria — Aether v0.1 Vertical Slice

> **Status:** Draft
> **Purpose:** Definition of done for the minimal end-to-end pipeline

## Success Criteria

The vertical slice succeeds when all of the following pass:

### Collection
- [ ] `Input/README.md` is discovered by the filesystem collector
- [ ] `Input/package.json` is discovered by the filesystem collector
- [ ] Each file produces one evidence record
- [ ] Evidence records include source path, content hash, and timestamp

### Evidence
- [ ] Evidence is stored immutably
- [ ] Evidence ID is assigned (EVID-XXXX format)
- [ ] Evidence hash is computed and unique
- [ ] Running the collector twice produces a deduplicated copy

### Graph
- [ ] A REPO node exists for the repository
- [ ] FILE nodes exist for README.md and package.json
- [ ] CONTAINS edges connect REPO → each FILE
- [ ] Every node references its creating evidence
- [ ] Every edge references its creating evidence

### Inference
- [ ] At least one rule fires on the evidence
- [ ] A framework detection rule produces a fact (e.g., "uses Node.js")
- [ ] Confidence is computed for the inferred fact
- [ ] The fact is traceable to evidence and rule

### Verification
- [ ] Every fact passes verification against evidence
- [ ] A verification record is created (VERIFY-XXXX)
- [ ] Confidence incorporates evidence weight, freshness, and source trust

### Compilation
- [ ] `repository.ai` is generated and contains the graph
- [ ] Markdown is generated with FileMap and discovered facts
- [ ] Both outputs are deterministic (same graph → same output)
- [ ] Outputs include graph version and timestamp

### Integrity
- [ ] All provenance is traceable: claim → verification → evidence → collector
- [ ] Zero manual edits to the graph or compiled outputs
- [ ] Running the full pipeline twice produces identical graph state
- [ ] Running the full pipeline twice does not duplicate nodes or evidence

## v0.1 Is Complete When

All checkboxes above are checked.

Nothing more.
Nothing less.
