#!/usr/bin/env python3
"""Build a deterministic, marketplace-ready memEcho Skill ZIP."""

import argparse
import hashlib
import re
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "memecho-analyze-conversation"
VERSION_FILE = ROOT / "VERSION"
FIXED_ZIP_TIME = (1980, 1, 1, 0, 0, 0)


def declared_version():
    version = VERSION_FILE.read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError(f"VERSION must contain semver, got {version!r}")
    return version


def archive_entry(archive, source, target):
    info = zipfile.ZipInfo(target.as_posix(), FIXED_ZIP_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    mode = 0o755 if source.suffix == ".py" else 0o644
    info.external_attr = (mode & 0xFFFF) << 16
    archive.writestr(info, source.read_bytes())


def build(output_dir):
    version = declared_version()
    skill_text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    if f'version: "{version}"' not in skill_text:
        raise ValueError("SKILL.md metadata.version does not match VERSION")

    output_dir.mkdir(parents=True, exist_ok=True)
    archive_path = output_dir / f"memecho-analyze-conversation-v{version}.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        sources = (
            path
            for path in SKILL.rglob("*")
            if path.is_file()
            and "__pycache__" not in path.parts
            and path.suffix not in {".pyc", ".pyo"}
        )
        for source in sorted(sources):
            archive_entry(archive, source, source.relative_to(SKILL))
        archive_entry(archive, ROOT / "LICENSE", Path("LICENSE"))

    digest = hashlib.sha256(archive_path.read_bytes()).hexdigest()
    checksum_path = output_dir / "SHA256SUMS.txt"
    checksum_path.write_bytes(f"{digest}  {archive_path.name}\n".encode("utf-8"))
    print(archive_path)
    print(checksum_path)
    return archive_path, checksum_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    build(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

