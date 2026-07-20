# Portable input contract

The canonical request is JSON. A platform adapter may construct it from a prompt and attachments.

```json
{
  "schema_version": "1.1",
  "request_id": "req_01",
  "source": {"type": "transcript", "text": "[00:00] 阿青：我们先确认目标……", "path": null, "mime_type": "text/plain"},
  "session": {"title": "产品方案讨论", "occurred_at": "2026-07-20T10:00:00+08:00", "context": "工作"},
  "participants": [
    {"id": "speaker_1", "name": "阿青", "is_self": true},
    {"id": "speaker_2", "name": "小林", "is_self": false}
  ],
  "self_identity_basis": "user_confirmed",
  "target_participant_ids": ["speaker_1"],
  "language": "zh-CN",
  "focus": ["minutes", "content_analysis", "vad", "self_echo"],
  "coaching": {"enabled": false, "max_scenes": 1},
  "marks": [{"at_ms": 420000, "label": "关键分歧"}],
  "memory": {"mode": "off", "scope": []}
}
```

## Required fields

| Field | Meaning |
|---|---|
| `schema_version` | `1.0` or additive contract `1.1`; new callers should use `1.1`. |
| `request_id` | Caller-generated idempotency and trace identifier. |
| `source.type` | `text`, `transcript`, `audio`, or `video`. |
| `source.text` or `source.path` | Exactly one usable source locator. |
| `memory.mode` | `off`, `ask`, or `on`; omission behaves as `off`. |

## Person targeting and self identity

- `target_participant_ids` selects speakers for detailed content or VAD analysis. Omission means all known speakers.
- For multi-speaker self echo, exactly one participant must have `is_self: true`; the user must supply or confirm it.
- For a genuinely single-speaker source, the adapter may set the only participant to `is_self: true` and record `self_identity_basis: auto_single_speaker`.
- Allowed identity bases are `user_confirmed`, `auto_single_speaker`, and `unknown`.
- Never infer self from a person's name, pronouns, account identity, voice, or amount of speech.

## Focus modules

Allowed values are `minutes`, `content_analysis`, `vad`, `self_echo`, and `coaching`. Coaching is opt-in. When `coaching.enabled` is true, include `coaching` in `focus`.

## Source handling

- Do not embed binary media in this JSON.
- Do not claim acoustic access when only a transcript is available.
- Preserve segment time ranges, speaker, text, and ASR confidence when available.
- The caller is responsible for lawful recording and disclosure; remind the user when consent is unclear.
