# Non-Goals — Aether v1

> **Status:** Ratified
> **Purpose:** Define what Aether intentionally does not do. These boundaries protect the platform's scope and prevent feature creep.

---

Aether v1 is NOT:

| Area | Rationale |
|------|-----------|
| A documentation generator | Documentation is one output format, not the purpose |
| An IDE or code editor | Aether reads repositories; it does not edit code |
| A vector database | Aether's graph is structured, not semantic-embedding-based |
| A source control system | Git handles version control; Aether reads git history |
| An AI coding assistant | Aether provides knowledge; it does not generate code |
| A project management platform | No issue tracking, sprint planning, or task management |
| A code formatter or linter | Static analysis is a data source, not an output |
| A CI platform | CI integration is a trigger mechanism, not a pipeline engine |
| A replacement for documentation | Existing docs are evidence sources, not competitors |
| A runtime monitor or APM | Runtime data is a collector input, not an ongoing service |
| A search engine | Graph queries are structured; free-text search is a feature, not the product |
| A chat interface | AI interaction is one consumer; the graph is the product |

## Why These Boundaries

Every mature platform eventually faces feature requests that dilute its purpose.
Aether's core value is the graph + evidence + trust model. Everything else is
a view, a trigger, or an output.

If a feature request falls into any of the above categories, it should be
rejected at the RFC level unless it directly serves the core mission of
extracting, verifying, organizing, compiling, and distributing repository
knowledge.

## Future Reclassification

A non-goal is not permanent. If the platform's scope legitimately expands,
a non-goal may be reclassified via the RFC process. Reclassification requires:

1. Demonstrated demand from multiple implementations
2. A concrete design that does not compromise existing goals
3. A clear boundary between the new capability and the core mission
