#!/usr/bin/env python3
"""Validate the portable memEcho request or result contract using stdlib only."""

import json
import sys
from pathlib import Path

VERSIONS = {"1.0", "1.1"}
MODES = {"connected_full", "local_enhanced", "text_only", "insufficient"}
SOURCE_TYPES = {"text", "transcript", "audio", "video"}
MEMORY_MODES = {"off", "ask", "on"}
CLAIM_LEVELS = {"observed", "computed", "interpreted"}
FOCUS_VALUES = {"minutes", "content_analysis", "vad", "self_echo", "coaching", "self_perspective"}
IDENTITY_BASES = {"user_confirmed", "auto_single_speaker", "unknown"}
COACHING_STATUSES = {"not_requested", "awaiting_user", "scored", "complete"}


def require(condition, message, errors):
    if not condition:
        errors.append(message)


def validate_request(data):
    errors = []
    require(data.get("schema_version") in VERSIONS, "schema_version must be '1.0' or '1.1'", errors)
    require(isinstance(data.get("request_id"), str) and bool(data.get("request_id")), "request_id is required", errors)
    source = data.get("source")
    require(isinstance(source, dict), "source must be an object", errors)
    if isinstance(source, dict):
        require(source.get("type") in SOURCE_TYPES, "source.type is invalid", errors)
        require(bool(source.get("text")) ^ bool(source.get("path")), "provide exactly one of source.text or source.path", errors)

    memory = data.get("memory", {"mode": "off"})
    require(isinstance(memory, dict), "memory must be an object", errors)
    if isinstance(memory, dict):
        require(memory.get("mode", "off") in MEMORY_MODES, "memory.mode is invalid", errors)

    participants = data.get("participants", [])
    require(isinstance(participants, list), "participants must be an array", errors)
    participant_ids = set()
    self_ids = []
    if isinstance(participants, list):
        for index, participant in enumerate(participants):
            require(isinstance(participant, dict), f"participants[{index}] must be an object", errors)
            if isinstance(participant, dict):
                participant_id = participant.get("id")
                require(isinstance(participant_id, str) and bool(participant_id), f"participants[{index}].id is required", errors)
                if isinstance(participant_id, str):
                    require(participant_id not in participant_ids, f"duplicate participant id '{participant_id}'", errors)
                    participant_ids.add(participant_id)
                if participant.get("is_self") is True:
                    self_ids.append(participant_id)

    focus = data.get("focus", [])
    require(isinstance(focus, list), "focus must be an array", errors)
    if isinstance(focus, list):
        for value in focus:
            require(value in FOCUS_VALUES, f"focus value '{value}' is invalid", errors)

    targets = data.get("target_participant_ids", [])
    require(isinstance(targets, list), "target_participant_ids must be an array", errors)
    if isinstance(targets, list):
        for target in targets:
            require(target in participant_ids, f"target participant '{target}' is missing", errors)

    needs_self = isinstance(focus, list) and bool({"self_echo", "self_perspective"}.intersection(focus))
    if needs_self:
        require(len(self_ids) == 1, "self echo requires exactly one participant with is_self=true", errors)
        basis = data.get("self_identity_basis")
        require(basis in IDENTITY_BASES - {"unknown"}, "self_identity_basis must resolve self identity", errors)
        if basis == "auto_single_speaker":
            require(len(participants) == 1, "auto_single_speaker is valid only for one participant", errors)

    coaching = data.get("coaching", {})
    require(isinstance(coaching, dict), "coaching must be an object", errors)
    if isinstance(coaching, dict) and coaching.get("enabled") is True:
        require("coaching" in focus, "enabled coaching requires 'coaching' in focus", errors)
    return errors


def validate_action_list(items, expected_origin, expected_status, field, evidence_ids, errors):
    require(isinstance(items, list), f"{field} must be an array", errors)
    for index, item in enumerate(items or []):
        if not isinstance(item, dict):
            errors.append(f"{field}[{index}] must be an object")
            continue
        require(item.get("origin") == expected_origin, f"{field}[{index}].origin must be '{expected_origin}'", errors)
        require(item.get("status") == expected_status, f"{field}[{index}].status must be '{expected_status}'", errors)
        for ref in item.get("evidence_refs", []):
            require(ref in evidence_ids, f"{field}[{index}] references missing evidence '{ref}'", errors)


def validate_result(data):
    errors = []
    require(data.get("schema_version") in VERSIONS, "schema_version must be '1.0' or '1.1'", errors)
    require(isinstance(data.get("request_id"), str) and bool(data.get("request_id")), "request_id is required", errors)
    require(data.get("analysis_mode") in MODES, "analysis_mode is invalid", errors)
    evidence = data.get("evidence")
    insights = data.get("insights")
    require(isinstance(evidence, list), "evidence must be an array", errors)
    require(isinstance(insights, list), "insights must be an array", errors)
    evidence_ids = {item.get("id") for item in evidence or [] if isinstance(item, dict)}

    for index, insight in enumerate(insights or []):
        if not isinstance(insight, dict):
            errors.append(f"insights[{index}] must be an object")
            continue
        require(insight.get("claim_level") in CLAIM_LEVELS, f"insights[{index}].claim_level is invalid", errors)
        confidence = insight.get("confidence")
        require(isinstance(confidence, (int, float)) and 0 <= confidence <= 1, f"insights[{index}].confidence must be in [0,1]", errors)
        refs = insight.get("evidence_refs", [])
        require(isinstance(refs, list) and bool(refs), f"insights[{index}] needs evidence_refs", errors)
        for ref in refs if isinstance(refs, list) else []:
            require(ref in evidence_ids, f"insights[{index}] references missing evidence '{ref}'", errors)

    if data.get("schema_version") == "1.1":
        minutes = data.get("minutes", {})
        require(isinstance(minutes, dict), "minutes must be an object", errors)
        if isinstance(minutes, dict):
            validate_action_list(minutes.get("explicit_actions", []), "discussed", "confirmed", "minutes.explicit_actions", evidence_ids, errors)
            validate_action_list(minutes.get("recommendations", []), "suggested", "proposed", "minutes.recommendations", evidence_ids, errors)
        require(isinstance(data.get("content_analysis", []), list), "content_analysis must be an array", errors)
        for index, point in enumerate(data.get("vad_series", [])):
            if isinstance(point, dict) and data.get("analysis_mode") == "text_only":
                require(point.get("acoustic_weight") == 0, f"vad_series[{index}].acoustic_weight must be 0 in text_only", errors)
        coaching = data.get("coaching", {"enabled": False, "status": "not_requested", "scenes": []})
        require(isinstance(coaching, dict), "coaching must be an object", errors)
        if isinstance(coaching, dict):
            require(coaching.get("status") in COACHING_STATUSES, "coaching.status is invalid", errors)
            if coaching.get("status") == "awaiting_user":
                for index, scene in enumerate(coaching.get("scenes", [])):
                    if isinstance(scene, dict):
                        require(not scene.get("scores"), f"coaching.scenes[{index}] cannot be scored while awaiting_user", errors)

    memory = data.get("memory")
    require(isinstance(memory, dict) and isinstance(memory.get("written"), bool), "memory.written must be boolean", errors)
    return errors


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in {"request", "result"}:
        print("usage: validate_contract.py request|result path.json", file=sys.stderr)
        return 2
    try:
        data = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"invalid JSON input: {exc}", file=sys.stderr)
        return 2
    if not isinstance(data, dict):
        print("top-level JSON must be an object", file=sys.stderr)
        return 1
    errors = validate_request(data) if sys.argv[1] == "request" else validate_result(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"OK: valid memEcho {sys.argv[1]} contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
