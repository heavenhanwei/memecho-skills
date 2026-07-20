# Analysis policy

## Claim ladder

Use the weakest claim the evidence supports:

1. **Observed**: a word, timestamp, pause, interruption, acoustic measurement, or explicit statement is present.
2. **Computed**: a reproducible statistic or model score was derived from observed evidence.
3. **Interpreted**: an expression or interaction pattern is a plausible reading with confidence and alternatives.
4. **Not allowed**: diagnosis, stable personality judgment, hidden intent, deception, mental state as fact, or causality inferred from timing alone.

VAD describes expressed affect in context. It does not reveal how a person “really feels.” Do not compare raw scores across speakers as if voices, microphones, languages, and cultural norms were calibrated identically.

## Fact, opinion, and attitude

- `fact_claim`: a statement framed as externally checkable. Classification does not verify it.
- `opinion`: a judgment, inference, preference, prediction, or recommendation.
- `attitude`: stance toward a person, proposal, event, or outcome, including support, resistance, uncertainty, concern, or commitment.

Mixed statements may contain multiple spans. Preserve ambiguity rather than forcing one label.

## Evidence rules

- Material conclusions require an evidence reference and confidence.
- Acoustic conclusions require original audio and an acoustic-capable mode.
- In `text_only`, say “linguistic expression suggests” and omit acoustic attributes.
- Low ASR confidence, overlap, noise, short duration, code-switching, or missing identity must lower confidence.
- Quote minimally and point to timestamps or segment IDs.
- For interaction effects, use neutral language: “X was followed within 20 seconds by Y.”

## Self-perspective rules

Prioritize the user's observable choices and outcomes. Do not coach manipulation. Recommendations should be specific, low-pressure, and testable, such as separating a fact claim from a preference or checking shared understanding after a high-arousal segment.

## Privacy and memory

- Default long-term memory to off.
- Do not infer or store sensitive traits, diagnoses, protected characteristics, or biometric identity.
- Store provenance, validity interval, confidence, and deletion linkage for every retained observation.
- A deleted source invalidates or recomputes derived memories.
- Sharing a report does not imply permission to share raw media, private notes, or longitudinal memory.

## High-risk contexts

For medical, mental-health, employment, education, insurance, legal, or safety decisions, frame output as non-diagnostic communication reflection. Do not rank or take consequential action against people based on inferred emotion. Encourage qualified human review when decisions affect rights, care, or safety.
