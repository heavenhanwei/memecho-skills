# memEcho Skills 1.0.2

This release improves report readability while preserving the evidence and safety semantics of the 1.1 result contract.

## Highlights

- Markdown reports now include ASCII-only confidence and VAD visualizations that remain readable in terminals, GitHub, and SkillHub.
- Added a responsive, self-contained HTML report with embedded CSS, evidence cards, VAD meters, action status, uncertainties, and no external network dependencies.
- Added `memecho render` for converting validated result JSON to Markdown, HTML, or both.
- Added generated Markdown and HTML examples plus rendering, HTML escaping, responsive-layout, and CLI tests.

## Commands

```text
memecho render examples/result-text-only.json --format markdown --output report.md
memecho render examples/result-text-only.json --format html --output report.html
memecho render examples/result-text-only.json --format both --output report
```

The HTML renderer escapes user-derived content and does not load remote scripts, fonts, stylesheets, analytics, or images.
