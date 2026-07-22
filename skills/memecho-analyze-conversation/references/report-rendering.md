# Report rendering

Use this reference when producing a human-readable report. Keep the analysis semantics in `output-contract.md`; presentation must never change the evidence, confidence, action status, or uncertainty.

## Format selection

- Default to `markdown` when the user does not specify a format.
- Accept `--format markdown`, `--format html`, `--format both`, or an equivalent natural-language request.
- Keep JSON separate. JSON is the machine contract; Markdown and HTML are views of the same result.
- When returning HTML, create or attach a `.html` file instead of flooding the conversation with source code, unless the user explicitly asks to inspect the source.
- For `both`, produce matching `.md` and `.html` files from the same analysis result.

## Markdown view

Keep the required report headings from `SKILL.md`. Add compact ASCII visualization inside fenced `text` blocks for numerical summaries.

### Confidence

Use ten cells, `#` for filled and `.` for remaining:

```text
REPORT CONFIDENCE
[########..] 78%
```

### VAD

Use 21 cells over `-1..1`, `|` for zero and `*` for the current value. Include the signed number so the chart remains accessible without visual alignment.

```text
-1.0       0.0       +1.0
seg_03
  V [......*...|..........] -0.42
  A [..........|.....*....] +0.58
  D [........*.|..........] -0.18
  C [#######...] 72%
```

Rules:

- Use ASCII characters only inside the chart; do not use emoji or Unicode block elements.
- Put charts after the relevant explanation, not before the report scope.
- Render at most the most relevant 12 VAD points per participant. Summarize longer series and link to evidence.
- Do not imply precision beyond the source. Keep confidence visually separate from VAD magnitude.
- Text-only analysis must still state `acoustic_weight: 0`; a visual chart does not make acoustic evidence available.
- Use `[x]` only for explicit confirmed actions and `[ ]` for proposed recommendations.

## HTML view

Generate one offline, self-contained HTML5 file with UTF-8 metadata and embedded CSS. Do not load remote scripts, fonts, analytics, images, or stylesheets.

Required sections:

1. Hero: title, single-session summary, analysis mode, used/missing signals, report confidence.
2. Minutes: focus, consensus, unresolved disagreements, confirmed actions, proposed suggestions.
3. Per-participant fact claims, opinions, attitudes, and observable influence.
4. VAD meters for relevant participants and segments, with signed values, confidence, and signal weights.
5. Self echo when self identity is resolved.
6. Evidence-linked insights with alternative explanations.
7. Evidence index and uncertainties.
8. Safety footer stating that VAD is expression-level inference, not diagnosis or hidden intent.

Visual and accessibility requirements:

- Use semantic headings, lists, tables, and meaningful text; do not encode conclusions only by color.
- Distinguish `confirmed` actions from `proposed` suggestions with both visible text and style.
- Use a responsive layout that remains readable at 320 px width.
- Escape every user-derived string before inserting it into HTML.
- Keep evidence excerpts concise and preserve speaker/segment labels.
- Prefer CSS meters and cards; do not add JavaScript unless the user asks for interaction.
- Include print-friendly defaults and avoid animations in the report artifact.

## Deterministic repository renderer

When the `memecho` repository CLI is installed, render a validated result contract with:

```text
memecho render result.json --format markdown --output report.md
memecho render result.json --format html --output report.html
memecho render result.json --format both --output report
```

If the renderer is unavailable, follow the same rules directly. Never claim a file was created unless it was actually written and verified.
