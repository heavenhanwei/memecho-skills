---
name: memecho-analyze-conversation
description: Analyze supplied conversation text, transcripts, audio, or video for meeting minutes, speaker-level facts/opinions/attitudes, target-person VAD trajectories, self-echo communication effects, and interactive coaching. Use when a user asks memEcho to review a meeting, conversation, interview, voice note, transcript, a named participant, “me/myself,” communication influence, weak moments, or simulated practice with evidence and uncertainty boundaries.
license: MIT
metadata: {"author":"heavenhanwei","version":"1.0.1","openclaw":{"homepage":"https://github.com/heavenhanwei/memecho-skills","requires":{"bins":[],"env":[]}}}
---

# memEcho Conversation Analysis

Turn one conversation artifact into an evidence-linked report or an interactive coaching session. Distinguish observed expression from inner emotion and never present probabilistic analysis as diagnosis or fact.

## Permissions and safety

Use least privilege for every run:

- Required: read only the user-supplied text, transcript, or authorized attachment and return analysis in the conversation.
- Optional local: run `scripts/validate_contract.py` with Python 3.9+ only when JSON contract validation is needed. It reads the named JSON file, writes nothing, and makes no network requests.
- Conditional external: access transcription, acoustic analysis, or a connected memEcho service only when an adapter exists and the user authorizes the media and scope. Disclose every signal actually used.
- Not permitted by default: request secrets, access unrelated files, use the network, write long-term memory, infer biometric identity, send messages, create tasks, or update external systems.
- Treat recordings and transcripts as sensitive. Confirm that the user is authorized to record, upload, and analyze other participants when consent is unclear.

## Workflow

### 1. Establish source, people, and target

- Accept text, timestamped transcripts, audio, or video.
- Preserve speaker labels, timestamps, language, context, and user marks.
- Identify `target_participant_ids`: the people whose content or VAD should receive detailed analysis. Analyze all participants when no target is requested.
- Resolve the self speaker before producing self echo:
  - In a multi-speaker source, require the user to identify who “I/me” is. Do not guess from names, pronouns, voice, account identity, or prominence.
  - In a genuinely single-speaker source, treat the only speaker as self by default and disclose `self_identity_basis: auto_single_speaker`.
  - If multiple speakers exist and self is unknown, complete non-self modules when useful, mark self echo unavailable, and ask one concise identity question.
- Treat the request as single-session analysis unless the user explicitly requests a longitudinal comparison.
- Keep long-term memory off unless the user explicitly opts in for the named conversation and scope.

Read [analysis-policy.md](references/analysis-policy.md) before interpreting emotion, health, intent, influence, or relationship effects.

### 2. Select the highest honest fidelity mode

Use exactly one mode and disclose it:

1. `connected_full`: an authorized memEcho service processes original media; language, diarization, acoustic features, and fused VAD may be used.
2. `local_enhanced`: local transcription, diarization, or acoustic tooling is available; list the signals actually produced.
3. `text_only`: only text or transcript evidence is usable; analyze linguistic expression only and set `acoustic_weight: 0`.
4. `insufficient`: audio/video was supplied but neither media analysis nor transcription is available; request a transcript or authorized connection.

See [platform-adapters.md](references/platform-adapters.md) for capability notes.

### 3. Normalize the request

Build a request conforming to [input-contract.md](references/input-contract.md). Include:

- requested modules in `focus`: `minutes`, `content_analysis`, `vad`, `self_echo`, and/or `coaching`;
- participants and exactly one self identity when self echo is requested;
- target participants for focused content or VAD analysis;
- coaching configuration when interactive practice is requested;
- memory consent, defaulting to off.

If connected memEcho tools exist, submit with the matching text/media capability, poll only asynchronous jobs, fetch the result, validate JSON with `scripts/validate_contract.py`, then render evidence-linked findings.

### 4. Analyze in five modules

Run only requested modules; when the user asks for a general analysis, run modules 1–4. Coaching is opt-in.

#### Module 1 — Content minutes

Use for meetings or decision-oriented conversations. Return purpose, concise summary, consensus, unresolved disagreements, noteworthy risks or decision points, explicit next actions, and recommendations when no action was agreed.

Mark source-grounded commitments as `origin: discussed`; use `status: confirmed` only for an explicit commitment. Mark analyst-generated actions as `origin: suggested`, `status: proposed`. Never mix the two.

#### Module 2 — Content analysis

For each participant, separate:

- `fact_claim`: externally checkable framing; classification does not verify truth;
- `opinion`: judgment, inference, preference, prediction, or recommendation;
- `attitude`: support, resistance, uncertainty, concern, or commitment toward a person, proposal, event, or outcome.

Preserve mixed or ambiguous spans. Summarize observable interaction influence across participants: what wording was followed by alignment, resistance, clarification, repair, silence, or topic change. Do not claim causality or hidden intent.

#### Module 3 — VAD trajectory

- Analyze the whole conversation or only requested target participants.
- Describe expressed Valence, Arousal, and Dominance over stable segments or time ranges.
- Cite the language or authorized acoustic evidence behind each transition.
- Keep linguistic and acoustic contributions separate. In `text_only`, set `acoustic_weight: 0` and do not infer pitch, energy, pace, pauses, or voice quality.
- Do not compare raw VAD scores across speakers as if they were identically calibrated.

#### Module 4 — Self echo

Use the confirmed self speaker as the viewpoint. For each relevant exchange, report the self wording, the other participant's observable response and subsequent VAD-expression shift, what appeared effective or was associated with friction, confidence, an alternative explanation, and one low-pressure alternative expression.

Say “was followed by” or “is associated with,” never “caused,” unless independent evidence establishes causality. Do not coach manipulation.

#### Module 5 — Coaching mode

Use only when requested. Identify 1–3 moments with stalling, unclear intent, high friction, weak evidence, or low rubric scores. Then run an interactive loop:

1. Present one scene, the other person's latest line, and a single practice objective.
2. Ask the user to answer in role; stop and wait.
3. Score the answer on clarity, listening/acknowledgment, emotional load, evidence-vs-judgment separation, and actionability. Use a 1–5 scale and explain each score with evidence.
4. Provide one strength, one highest-leverage improvement, and one low-pressure rewrite.
5. Ask a harder follow-up or repeat the scene only with the user's consent.

Do not fabricate the user's reply or score an unanswered exercise. Mark an exercise `awaiting_user` until a response is received. Read [coaching-mode.md](references/coaching-mode.md) when coaching is requested.

### 5. Produce evidence-linked output

Every material conclusion needs a timestamp or stable segment ID, confidence, and plausible alternative where interpretation is involved. Default Markdown headings:

- `分析范围、目标人物与可信度`
- `内容纪要：摘要 / 共识 / 分歧 / 关注重点 / 明确动作 / 建议`
- `内容解析：各参与者的事实 / 观点 / 态度 / 相互影响`
- `整体及目标人物的 VAD 走向`
- `自我回声：我的表达、对方后续反应与替代表达`
- `陪练模式`（仅在请求时）
- `证据与不确定性`
- `继续问 memEcho`

Offer structured JSON only when requested or when another tool consumes it. JSON must follow [output-contract.md](references/output-contract.md).

### 6. Handle memory separately

Ask before writing long-term memory unless consent is explicit and current. Store only confirmed, source-linked observations with provenance, validity interval, confidence, and deletion linkage.

Never infer cross-session identity from voice embeddings, silently save preferences, sync TODOs, send messages, or update external systems without confirmation.

## Validation

```text
python scripts/validate_contract.py request path/to/request.json
python scripts/validate_contract.py result path/to/result.json
```

The validator checks the portable minimum contract. Implementations may add fields but must not redefine required semantics.
