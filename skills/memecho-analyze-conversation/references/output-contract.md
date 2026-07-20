# Portable output contract

The result keeps observations, interpretations, evidence, and uncertainty separable.

```json
{
  "schema_version": "1.1",
  "request_id": "req_01",
  "analysis_mode": "text_only",
  "scope": {"single_session": true, "signals_used": ["transcript", "linguistic"], "signals_missing": ["acoustic"], "quality": 0.78, "target_participant_ids": ["speaker_1"], "self_participant_id": "speaker_1", "self_identity_basis": "user_confirmed"},
  "minutes": {
    "summary": "…",
    "focus": ["…"],
    "consensus": ["…"],
    "disagreements": ["…"],
    "explicit_actions": [{"text": "…", "owner": "speaker_1", "due_at": null, "origin": "discussed", "status": "confirmed", "evidence_refs": ["ev_01"]}],
    "recommendations": [{"text": "…", "owner": null, "due_at": null, "origin": "suggested", "status": "proposed", "evidence_refs": ["ev_01"]}]
  },
  "content_analysis": [{"participant_id": "speaker_1", "fact_claims": [], "opinions": [], "attitudes": [], "influence_summary": []}],
  "participants": [],
  "vad_series": [{"participant_id": "speaker_1", "segment_id": "seg_01", "v": 0.1, "a": 0.4, "d": 0.2, "scale": "-1..1", "confidence": 0.72, "linguistic_weight": 1, "acoustic_weight": 0, "evidence_refs": ["ev_01"]}],
  "interaction_events": [],
  "self_echo": {"participant_id": "speaker_1", "identity_basis": "user_confirmed", "effects": [], "alternatives": []},
  "coaching": {"enabled": false, "status": "not_requested", "scenes": []},
  "insights": [{"id": "in_01", "claim": "…", "claim_level": "interpreted", "confidence": 0.72, "evidence_refs": ["ev_01"], "alternatives": ["…"]}],
  "evidence": [{"id": "ev_01", "source_type": "transcript", "speaker_id": "speaker_1", "start_ms": 12000, "end_ms": 18000, "segment_id": "seg_03", "excerpt": "…", "quality_flags": []}],
  "uncertainties": ["缺少原始音频，未分析声学特征"],
  "provenance": {"skill_version": "1.0.0", "service_version": null, "model_manifest": []},
  "memory": {"written": false, "consent_basis": null}
}
```

## Required semantics

- `analysis_mode`: `connected_full`, `local_enhanced`, `text_only`, or `insufficient`.
- `scope.signals_used`: actual evidence channels, never aspirational capabilities.
- `minutes.explicit_actions`: only actions explicitly agreed in the source; `origin: discussed`.
- `minutes.recommendations`: analyst suggestions not agreed in the source; `origin: suggested`, `status: proposed`.
- `content_analysis`: separate fact claims, opinions, and attitudes for each relevant participant.
- `insights[].claim_level`: `observed`, `computed`, or `interpreted`.
- `confidence` is in `[0,1]` and means analysis confidence, not emotion intensity.
- Evidence references resolve within `evidence` or an authorized evidence service.
- Each VAD point includes participant, range/segment, V/A/D, scale, confidence, and linguistic/acoustic weights. Text-only points must set `acoustic_weight: 0`.
- `self_echo` requires a resolved self participant. Do not populate it when identity is unknown.
- Coaching statuses are `not_requested`, `awaiting_user`, `scored`, or `complete`. Never score an unanswered scene.
- `memory.written` is false unless a separate authorized write succeeded.

Consumers must ignore unknown fields and reject changed meanings. Additive changes may remain in `1.x`; breaking changes require a new major version.
