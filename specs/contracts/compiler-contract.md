# Compiler Contract v1

## Inputs
- `graph: KnowledgeGraph` — current graph state
- `target: str` — compiler target kind (markdown, ai_package, json, dashboard)
- `output_path: Path` — where to write
- `config: dict` — target-specific options

## Outputs
- `path: Path` — where the artifact was written
- `size_bytes: int`
- `checksum: str` — SHA-256 of output content
- `generated_at: timestamp`
- `graph_version: str`

## Invariants
1. Compilers are deterministic: same graph + same config → identical output
2. Compilers never modify the graph or evidence store
3. Compilers are independently versioned
4. One compiler failure never blocks other compilers
5. Compilers MUST NOT introduce new facts or relationships
6. Every compiled artifact includes the graph version that produced it
7. Compilers are side-effect free beyond writing to the output path

## Failure Modes
| Mode | Cause | Behavior |
|------|-------|----------|
| Target not found | Unrecognized compiler target | Reject with error |
| Output path unwritable | Permission denied | Reject with error |
| Graph empty | No nodes in graph | Write empty/minimal output |
| Large output | Output exceeds reasonable size | Continue (size limit is target-specific) |
| Missing template | Template-based compiler can't find template | Fall back to default template |
