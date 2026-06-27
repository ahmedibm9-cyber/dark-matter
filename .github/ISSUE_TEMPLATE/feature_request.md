---
name: Feature request
about: New detector, collector, command, or capability
title: ''
labels: enhancement
assignees: ''
---

**Problem**

What's missing or what could be better.

**Solution**

What should dm do.

**Detector checklist** (if adding a detector)

- [ ] Function written with `(graph, evidence) -> list[Finding]` signature
- [ ] Registered in `audit/detectors/__init__.py`
- [ ] CLI handles `--detector` filter
- [ ] Test covers at least one true positive
