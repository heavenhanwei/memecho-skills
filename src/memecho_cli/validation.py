"""Small, dependency-free validators for the public memEcho 1.1 contract."""

VERSIONS = {"1.0", "1.1"}
MODES = {"connected_full", "local_enhanced", "text_only", "insufficient"}
SOURCE_TYPES = {"text", "transcript", "audio", "video"}
FOCUS_VALUES = {"minutes", "content_analysis", "vad", "self_echo", "coaching"}


def validate_request(data):
    errors = []
    if data.get("schema_version") not in VERSIONS:
        errors.append("schema_version must be '1.0' or '1.1'")
    if not isinstance(data.get("request_id"), str) or not data.get("request_id"):
        errors.append("request_id is required")
    source = data.get("source")
    if not isinstance(source, dict):
        errors.append("source must be an object")
    else:
        if source.get("type") not in SOURCE_TYPES:
            errors.append("source.type is invalid")
        if bool(source.get("text")) == bool(source.get("path")):
            errors.append("provide exactly one of source.text or source.path")
    memory = data.get("memory", {"mode": "off"})
    if not isinstance(memory, dict) or memory.get("mode", "off") not in {"off", "ask", "on"}:
        errors.append("memory.mode is invalid")

    participants = data.get("participants", [])
    ids = set()
    self_ids = []
    if not isinstance(participants, list):
        errors.append("participants must be an array")
        participants = []
    for index, participant in enumerate(participants):
        if not isinstance(participant, dict) or not participant.get("id"):
            errors.append(f"participants[{index}].id is required")
            continue
        participant_id = participant["id"]
        if participant_id in ids:
            errors.append(f"duplicate participant id '{participant_id}'")
        ids.add(participant_id)
        if participant.get("is_self") is True:
            self_ids.append(participant_id)

    focus = data.get("focus", [])
    if not isinstance(focus, list):
        errors.append("focus must be an array")
        focus = []
    for value in focus:
        if value not in FOCUS_VALUES:
            errors.append(f"focus value '{value}' is invalid")
    for target in data.get("target_participant_ids", []):
        if target not in ids:
            errors.append(f"target participant '{target}' is missing")
    if "self_echo" in focus:
        if len(self_ids) != 1:
            errors.append("self echo requires exactly one participant with is_self=true")
        if data.get("self_identity_basis") not in {"user_confirmed", "auto_single_speaker"}:
            errors.append("self_identity_basis must resolve self identity")
    coaching = data.get("coaching", {})
    if isinstance(coaching, dict) and coaching.get("enabled") and "coaching" not in focus:
        errors.append("enabled coaching requires 'coaching' in focus")
    return errors


def validate_result(data):
    errors = []
    if data.get("schema_version") not in VERSIONS:
        errors.append("schema_version must be '1.0' or '1.1'")
    if not data.get("request_id"):
        errors.append("request_id is required")
    if data.get("analysis_mode") not in MODES:
        errors.append("analysis_mode is invalid")
    evidence = data.get("evidence")
    insights = data.get("insights")
    if not isinstance(evidence, list):
        errors.append("evidence must be an array")
        evidence = []
    if not isinstance(insights, list):
        errors.append("insights must be an array")
        insights = []
    evidence_ids = {item.get("id") for item in evidence if isinstance(item, dict)}
    for index, insight in enumerate(insights):
        if insight.get("claim_level") not in {"observed", "computed", "interpreted"}:
            errors.append(f"insights[{index}].claim_level is invalid")
        confidence = insight.get("confidence")
        if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
            errors.append(f"insights[{index}].confidence must be in [0,1]")
        for ref in insight.get("evidence_refs", []):
            if ref not in evidence_ids:
                errors.append(f"insights[{index}] references missing evidence '{ref}'")
    if data.get("analysis_mode") == "text_only":
        for index, point in enumerate(data.get("vad_series", [])):
            if point.get("acoustic_weight") != 0:
                errors.append(f"vad_series[{index}].acoustic_weight must be 0 in text_only")
    for field, origin, status in (
        ("explicit_actions", "discussed", "confirmed"),
        ("recommendations", "suggested", "proposed"),
    ):
        for index, item in enumerate(data.get("minutes", {}).get(field, [])):
            if item.get("origin") != origin or item.get("status") != status:
                errors.append(f"minutes.{field}[{index}] must be {origin}/{status}")
    memory = data.get("memory")
    if not isinstance(memory, dict) or not isinstance(memory.get("written"), bool):
        errors.append("memory.written must be boolean")
    return errors

