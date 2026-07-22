# Changelog

All notable changes to this project are documented here.

## 1.0.2 — 2026-07-22

Report readability release.

- Added ASCII-only confidence and VAD visualizations to Markdown reports.
- Added responsive, self-contained HTML reports with no external assets or network calls.
- Added `memecho render` for Markdown, HTML, or paired output.
- Added report examples and tests for rendering, escaping, responsive layout, and CLI output.

## 1.0.1 — 2026-07-20

Marketplace compatibility patch.

- Added explicit permissions and safety boundaries.
- Added `metadata.openclaw` in the single-line JSON format required by OpenClaw.
- Declared zero required binaries, environment variables, and network access for the core text workflow.
- Improved Python 3.9 and cross-platform release-building compatibility.

## 1.0.0 — 2026-07-20

First stable community release.

- Added the `memecho-analyze-conversation` Agent Skill.
- Added meeting minutes, fact/opinion/attitude, VAD, self-echo, and coaching workflows.
- Added explicit identity, evidence, uncertainty, acoustic, memory, and high-risk-use boundaries.
- Added the portable request/result contract and dependency-free validator.
- Added the `memecho` request-construction CLI.
- Added community documentation, examples, tests, and release automation.

