# Query Contract v1

## Inputs
- `query_type: str` — one of: get_node, get_neighbors, find_path, subgraph, search, time_travel
- `parameters: dict` — query-specific parameters
- `timestamp: timestamp?` — for point-in-time queries (optional)

## Outputs
- `results: list[Node | Edge | Path | Subgraph]` — matching entities
- `total_count: int` — total matches (ignoring pagination)
- `returned_count: int` — matches in this page
- `query_duration_ms: int`

## Invariants
1. Queries never modify the graph
2. Queries are deterministic for a given graph state
3. Default max traversal depth is 5 hops
4. Default max results is 1000
5. Confidence filtering respects computed confidence (never stored)
6. Point-in-time queries return state as it existed at the given timestamp

## Failure Modes
| Mode | Cause | Behavior |
|------|-------|----------|
| Unknown query type | query_type not in registry | Reject with error |
| Nonexistent node | node_id not found | Return empty (no error) |
| Max depth exceeded | Traversal exceeds limit | Truncate at limit, flag in result |
| Timeout | Query exceeds time limit | Return partial results with warning |
| Invalid timestamp | Timestamp format or before first event | Return empty state |
