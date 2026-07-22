# memEcho command interface

Treat a user message beginning with `memecho` as an explicit invocation of this skill. Route the first token after `memecho` to the matching focus module.

## Commands

| Command | Focus |
|---|---|
| `memecho analyze` | General analysis: minutes when applicable, content analysis, VAD, and self echo when self is resolved |
| `memecho minutes` | Meeting summary, consensus, disagreements, focus, explicit actions, and suggestions |
| `memecho content` | Per-speaker fact claims, opinions, attitudes, and interaction influence |
| `memecho vad` | Whole-conversation or target-person VAD trajectory |
| `memecho echo` | Self echo from a confirmed self speaker |
| `memecho coach` | Interactive coaching; present one exercise and wait for the user |
| `memecho help` | Show command help without analyzing content |

For a completed result contract, the repository CLI also supports `memecho render result.json --format markdown|html|both`. This is a renderer, not a new analysis module.

If no subcommand is provided, treat `memecho` as `memecho analyze`.

## Common arguments

```text
--input <attached-file|local-path|->
--self <speaker-name-or-id>
--target <speaker-name-or-id>[,<speaker-name-or-id>...]
--context <meeting|interview|conversation|monologue|custom-text>
--format <markdown|html|both|json>
--memory <off|ask|on>
```

Natural-language arguments after the command are also valid. Do not require terminal-style flags when the user's intent is clear.

## Identity rules

- For a single-speaker source, automatically resolve the only speaker as self.
- For multi-speaker `echo` or `coach`, require `--self` or an equivalent natural-language statement.
- For `minutes`, `content`, and general VAD, self identity is optional.
- `--target` narrows detailed content or VAD analysis; omission means all reliably identified speakers.

## Examples

```text
memecho minutes --input meeting.txt
memecho content --input transcript.md --target 阿青,小林
memecho vad --input interview.txt --target 小林
memecho echo --input meeting.txt --self 阿青 --target 小林
memecho coach --input meeting.txt --self 阿青
memecho analyze 下面是一段单人独白：……
```

## Error behavior

- Unknown command: show the supported commands and do not guess a destructive or unrelated action.
- Missing input: request text or an attached media file.
- Missing self in multi-speaker `echo` or `coach`: ask only who the self speaker is.
- Unusable audio/video: select `insufficient` and request a transcript or authorized media connection.

This is a conversational command protocol. Do not claim that an operating-system `memecho` executable is installed unless an actual wrapper has been created and verified.
