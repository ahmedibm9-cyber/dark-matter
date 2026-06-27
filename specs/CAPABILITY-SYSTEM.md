# Capability System Specification v1

> **Status:** Draft
> **Part of:** Aether Intelligence Platform
> **Scope:** Plugin discovery, registration, execution, lifecycle, sandboxing

---

## 1. Rationale

Without a formal capability system, every new feature becomes a hard-coded branch
inside the pipeline. Collectors, rules, compilers, verifiers, and eventually
reasoners all follow the same pattern: they are plug-in capabilities that need
discovery, versioning, permissions, and lifecycle management.

A capability system prevents Aether from becoming a monolith by enforcing that
every extension point is a first-class plugin with a contract.

---

## 2. Capability Model

```python
@dataclass
class Capability:
    id: str                  # e.g. "collector.filesystem", "rule.framework.detect"
    version: str             # semver
    name: str
    description: str
    type: CapabilityType     # COLLECTOR, RULE, COMPILER, VERIFIER, REASONER, EXPORTER
    entrypoint: str          # module path or executable
    permissions: list[Permission]
    contracts: list[str]     # contract versions this capability satisfies
    dependencies: list[str]  # capability IDs this depends on
    config_schema: dict      # JSON Schema for configuration
    resource_limits: ResourceLimits
    languages: list[str]     # supported programming languages (empty = any)
    tags: list[str]
    lifecycle: CapabilityLifecycle  # active, deprecated, removed
```

### 2.1 Capability Types

| Type | Produces | Consumes | Side Effects |
|------|----------|----------|--------------|
| `COLLECTOR` | Evidence | Repository path | Read-only filesystem |
| `RULE` | Facts, Unknowns | Evidence, GraphState | None |
| `REASONER` | DerivedInsights | GraphState, Facts | None |
| `VERIFIER` | Verifications | Claims, Evidence | None |
| `COMPILER` | Artifacts | GraphState | Write output files |
| `EXPORTER` | Serialized data | GraphState | Write output files |

### 2.2 Permission Model

```python
@dataclass
class Permission:
    resource: str        # "filesystem.read", "filesystem.write",
                         # "graph.read", "graph.write",
                         # "network", "process", "environment"
    scope: str           # "all", "path:/specific/dir", "kind:file"
    reason: str          # why this permission is needed
```

Every capability declares its required permissions. At registration time,
the system validates that the permission set is appropriate for the
capability type (e.g., a RULE must never request `filesystem.write`).

### 2.3 Resource Limits

```python
@dataclass
class ResourceLimits:
    max_files: int = 10000
    max_depth: int = 20
    max_size_mb: int = 100
    timeout_seconds: int = 300
    max_memory_mb: int = 512
    max_evidence: int = 50000
```

---

## 3. Capability Registry

The registry is the single source of truth for what Aether can do.

```python
class CapabilityRegistry:
    def register(self, capability: Capability) -> RegistrationResult: ...
    def unregister(self, capability_id: str) -> None: ...
    def get(self, capability_id: str) -> Optional[Capability]: ...
    def find(self, query: CapabilityQuery) -> list[Capability]: ...
    def resolve(self, dependencies: list[str]) -> ResolutionGraph: ...
    def validate(self, capability: Capability) -> ValidationResult: ...
```

### 3.1 Discovery Sources

Capabilities are discovered in order:

1. **Built-in** — Registered in `aether.capabilities.builtin` at startup
2. **Project-local** — From `.aether/capabilities/` in the repository
3. **User-global** — From `~/.config/aether/capabilities/`
4. **System-global** — From installed packages via entry points
5. **Remote** — From registries (future: `aether install capability-name`)

### 3.2 CapabilityQuery

```python
@dataclass
class CapabilityQuery:
    type: Optional[CapabilityType] = None
    language: Optional[str] = None
    tag: Optional[str] = None
    contract: Optional[str] = None
    version_constraint: Optional[str] = None  # semver range
```

### 3.3 Registration Validation

Before a capability is accepted, the registry validates:

1. **ID uniqueness** — No duplicate capability IDs
2. **Dependency resolution** — All dependencies exist and are compatible
3. **Permission appropriateness** — Permissions match capability type
4. **Contract compliance** — Capability claims contracts that exist
5. **Entrypoint reachable** — The module or binary can be loaded
6. **Config schema valid** — JSON Schema is well-formed

### 3.4 Resolution

When the pipeline needs a set of capabilities (e.g., "all collectors for
this repository"), the registry returns a resolution graph:

```python
@dataclass
class ResolutionGraph:
    capabilities: list[Capability]
    execution_order: list[str]        # topological order
    missing_dependencies: list[str]   # unmet dependencies
    conflicts: list[Conflict]         # incompatible versions
```

---

## 4. Capability Lifecycle

```
Registered
    │
    ▼
Validated
    │
    ├──→ Active (available for use)
    │
    ├──→ Deprecated (still works, but warns)
    │       │
    │       └──→ Removed (no longer available)
    │
    └──→ Disabled (installed but not active)
            │
            └──→ Active
```

Capabilities transition between states explicitly:

| Transition | Trigger |
|------------|---------|
| Registered → Validated | Registry validates the capability |
| Validated → Active | Validation passes, no dependency conflicts |
| Active → Deprecated | Developer marks as deprecated with replacement ID |
| Deprecated → Removed | After deprecation period expires |
| Active → Disabled | User explicitly disables |
| Disabled → Active | User explicitly enables |

---

## 5. Capability Packs

A capability pack is a distributable set of related capabilities.

```yaml
# Example: .aether/capabilities/nextjs/v1/pack.yaml
id: pack.nextjs
version: 1.2.0
name: Next.js Intelligence
description: Collectors, rules, and compilers for Next.js repositories
capabilities:
  - collector.nextjs.config
  - collector.nextjs.routes
  - rule.nextjs.app-router
  - rule.nextjs.server-components
  - rule.nextjs.data-fetching
  - compiler.nextjs.architecture-report
dependencies:
  - pack.javascript
  - pack.react
```

### 5.1 Pack Directory Layout

```
.aether/capabilities/<pack-name>/<version>/
    pack.yaml              # Pack metadata
    capabilities/
        collector.yaml     # Individual capability definitions
        rule.yaml
        compiler.yaml
    schemas/               # Config schemas
    resources/             # Static resources (templates, etc.)
```

---

## 6. Execution Context

Every capability executes within a bounded context.

```python
@dataclass
class ExecutionContext:
    capability: Capability
    input: dict
    output: dict
    logger: Logger
    metrics: MetricsCollector
    resource_monitor: ResourceMonitor
    abort_signal: threading.Event
    temp_dir: Path
```

The context provides:
- **Isolation:** Each capability gets its own temp directory
- **Monitoring:** Resource usage is tracked and limited
- **Abort:** Pipeline can signal mid-execution termination
- **Logging:** Structured, prefixed by capability ID
- **Metrics:** Execution time, memory, evidence count, errors

---

## 7. Sandboxing

### 7.1 In-Process Sandbox

For trusted Python capabilities (built-in, project-local):
- Sub-interpreter or isolated module execution
- Resource monitoring via `resource` module
- Timeout via `signal.SIGALRM` or threading timer

### 7.2 Process Sandbox

For untrusted or non-Python capabilities:
- Subprocess with cgroups/Windows job objects
- Memory limit, CPU limit, filesystem access restricted
- Communication via stdin/stdout JSON protocol
- Timeout enforced by parent process kill

### 7.3 Container Sandbox (Future)

For remote or high-risk capabilities:
- Docker/Podman container with read-only filesystem mount
- Network access restricted (if not explicitly permitted)
- Volume mounts limited to specific paths

---

## 8. Built-in Capabilities

Aether ships with these built-in capabilities:

### 8.1 Collectors
| ID | Version | Languages |
|----|---------|-----------|
| `collector.filesystem` | 1.0.0 | any |
| `collector.git` | 1.0.0 | any |
| `collector.package-json` | 1.0.0 | javascript |

### 8.2 Rules
| ID | Version | Description |
|----|---------|-------------|
| `rule.framework.detect` | 1.0.0 | Detect frameworks from package manifests |
| `rule.architecture.detect` | 1.0.0 | Infer architecture from directory layout |

### 8.3 Compilers
| ID | Version | Output |
|----|---------|--------|
| `compiler.markdown` | 1.0.0 | Human-readable reports |
| `compiler.ai-package` | 1.0.0 | repository.ai binary |

### 8.4 Verifiers
| ID | Version | Method |
|----|---------|--------|
| `verifier.evidence-based` | 1.0.0 | Confidence from evidence chain |

---

## 9. Capability Contract

Every capability must satisfy this contract:

```yaml
# Required fields in every capability definition
capability:
  id: str                        # unique identifier
  version: str                   # semver
  type: str                      # one of the CapabilityType values
  entrypoint: str                # module path

  # Optional but recommended
  name: str
  description: str
  permissions:
    - resource: str
      scope: str
      reason: str
  dependencies: [str]
  config_schema: {}
  resource_limits: {}
  languages: [str]
  tags: [str]
```

Capabilities that fail to provide required fields are rejected at registration.

---

## 10. Pipeline Integration

The pipeline resolves capabilities at initialization:

```python
# Pseudocode
capabilities = registry.find(type=COLLECTOR, language=repo.primary_language)
resolution = registry.resolve([c.id for c in capabilities])

if resolution.missing_dependencies:
    warn(f"Missing collectors: {resolution.missing_dependencies}")

for cap_id in resolution.execution_order:
    capability = registry.get(cap_id)
    context = ExecutionContext(capability=capability, ...)
    evidence = capability.execute(context)
    store.store_evidence(evidence)
```

This means adding a new collector, rule, or compiler never requires
changing the pipeline code — only registering a new capability.
