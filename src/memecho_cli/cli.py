"""Build and validate portable memEcho requests; no analysis backend is bundled."""

import argparse
import json
import sys
import uuid
from pathlib import Path

from .rendering import render_html, render_markdown
from .validation import validate_request, validate_result


COMMAND_FOCUS = {
    "minutes": ["minutes"],
    "content": ["content_analysis"],
    "vad": ["vad"],
    "echo": ["self_echo"],
    "coach": ["coaching"],
}
MEDIA_EXTENSIONS = {
    ".wav": "audio", ".mp3": "audio", ".m4a": "audio", ".aac": "audio", ".flac": "audio",
    ".mp4": "video", ".mov": "video", ".mkv": "video", ".webm": "video",
}


def comma_list(value):
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def add_common_arguments(parser):
    parser.add_argument("--input", required=True, help="Text file, media path, or - for stdin")
    parser.add_argument("--source-type", choices=["auto", "text", "transcript", "audio", "video"], default="auto")
    parser.add_argument("--participants", help="Comma-separated speaker names")
    parser.add_argument("--self", dest="self_name", help="Speaker representing the user's viewpoint")
    parser.add_argument("--target", help="Comma-separated target speakers")
    parser.add_argument("--context", default="conversation", help="meeting, interview, conversation, or monologue")
    parser.add_argument("--memory", choices=["off", "ask", "on"], default="off")
    parser.add_argument("--output", help="Write JSON to this path instead of stdout")


def parser_for_cli():
    parser = argparse.ArgumentParser(
        prog="memecho",
        description="Build or validate memEcho 1.1 contracts (analysis backend not included).",
    )
    subparsers = parser.add_subparsers(dest="command")
    for command in ("analyze", "minutes", "content", "vad", "echo", "coach"):
        subparser = subparsers.add_parser(command)
        add_common_arguments(subparser)
    validate = subparsers.add_parser("validate", help="Validate a request or result JSON file")
    validate.add_argument("kind", choices=["request", "result"])
    validate.add_argument("path")
    render = subparsers.add_parser("render", help="Render result JSON as Markdown or standalone HTML")
    render.add_argument("path", help="Validated memEcho result JSON")
    render.add_argument("--format", choices=["markdown", "html", "both"], default="markdown")
    render.add_argument("--output", help="Output path, or basename for --format both")
    render.add_argument("--title", help="Optional report title")
    return parser


def infer_source(input_value, requested_type):
    if input_value == "-":
        return {"type": "text" if requested_type == "auto" else requested_type, "text": sys.stdin.read(), "path": None, "mime_type": "text/plain"}
    path = Path(input_value)
    source_type = requested_type
    if source_type == "auto":
        source_type = MEDIA_EXTENSIONS.get(path.suffix.lower(), "text")
    if source_type in {"audio", "video"}:
        return {"type": source_type, "text": None, "path": str(path), "mime_type": None}
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"cannot read input: {exc}") from exc
    return {"type": source_type, "text": text, "path": None, "mime_type": "text/plain"}


def resolve_people(names, self_name, target_names, context):
    ordered = list(dict.fromkeys(names))
    if self_name and self_name not in ordered:
        ordered.append(self_name)
    if not ordered and context == "monologue":
        ordered = [self_name or "我"]
    participants = []
    basis = "unknown"
    for index, name in enumerate(ordered, start=1):
        participants.append({"id": f"speaker_{index}", "name": name, "is_self": False})
    by_name = {item["name"]: item for item in participants}
    by_id = {item["id"]: item for item in participants}
    if self_name:
        person = by_name.get(self_name) or by_id.get(self_name)
        if not person:
            raise ValueError(f"self speaker '{self_name}' is not in participants")
        person["is_self"] = True
        basis = "user_confirmed"
    elif len(participants) == 1:
        participants[0]["is_self"] = True
        basis = "auto_single_speaker"
    targets = []
    for target in target_names:
        person = by_name.get(target) or by_id.get(target)
        if not person:
            raise ValueError(f"target speaker '{target}' is not in participants")
        targets.append(person["id"])
    return participants, basis, targets


def build_request(args):
    source = infer_source(args.input, args.source_type)
    participants, basis, targets = resolve_people(
        comma_list(args.participants), args.self_name, comma_list(args.target), args.context
    )
    self_resolved = any(person["is_self"] for person in participants)
    if args.command == "analyze":
        focus = ["minutes", "content_analysis", "vad"]
        if self_resolved:
            focus.append("self_echo")
    else:
        focus = list(COMMAND_FOCUS[args.command])
    if args.command in {"echo", "coach"} and not self_resolved:
        raise ValueError(f"{args.command} requires --self for a multi-speaker source")
    request = {
        "schema_version": "1.1",
        "request_id": f"req_{uuid.uuid4().hex[:12]}",
        "source": source,
        "session": {"title": Path(args.input).stem if args.input != "-" else "stdin", "occurred_at": None, "context": args.context},
        "participants": participants,
        "self_identity_basis": basis,
        "target_participant_ids": targets,
        "language": "zh-CN",
        "focus": focus,
        "coaching": {"enabled": args.command == "coach", "max_scenes": 1},
        "marks": [],
        "memory": {"mode": args.memory, "scope": []},
    }
    errors = validate_request(request)
    if errors:
        raise ValueError("; ".join(errors))
    return request


def validate_file(kind, path):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: invalid JSON input: {exc}", file=sys.stderr)
        return 2
    errors = validate_request(data) if kind == "request" else validate_result(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"OK: valid memEcho {kind} contract")
    return 0


def render_file(path, report_format, output=None, title=None):
    try:
        source = Path(path)
        data = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: invalid JSON input: {exc}", file=sys.stderr)
        return 2
    errors = validate_result(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    renderers = {"markdown": render_markdown, "html": render_html}
    if report_format != "both":
        rendered = renderers[report_format](data, title)
        if output:
            Path(output).write_text(rendered, encoding="utf-8")
            print(f"Wrote {output}")
        else:
            sys.stdout.write(rendered + ("" if rendered.endswith("\n") else "\n"))
        return 0
    base = Path(output) if output else source.with_suffix("").with_name(source.stem + ".report")
    if base.suffix in {".md", ".html"}:
        base = base.with_suffix("")
    for kind, suffix in (("markdown", ".md"), ("html", ".html")):
        target = base.with_suffix(suffix)
        target.write_text(renderers[kind](data, title), encoding="utf-8")
        print(f"Wrote {target}")
    return 0


def main(argv=None):
    parser = parser_for_cli()
    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 0
    if args.command == "validate":
        return validate_file(args.kind, args.path)
    if args.command == "render":
        return render_file(args.path, args.format, args.output, args.title)
    try:
        request = build_request(args)
    except ValueError as exc:
        parser.error(str(exc))
    rendered = json.dumps(request, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
        print(f"Wrote {args.output}")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
