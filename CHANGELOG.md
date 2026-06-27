# Changelog

## 0.1.0 (2024-06-27)

- **Initial release.** Vertical slice of the Dark Matter platform.
- 7-stage pipeline: collect → store → graph → infer → verify → audit → compile
- 12 bug detectors (5 structural, 7 regex)
- Ponytail mode (`-p`) for ~6x faster audits
- JSON file store with content-addressable dedup
- 3-factor confidence model (weight × freshness × trust)
- Markdown report + .ai machine-readable package outputs
- 12 CLI commands (`dm init`, `dm scan`, `dm audit`, etc.)
- VIBE-CODERS-GUIDE.md — 6 chapters from first principles
- AGENTS.md — AI agent onboarding
