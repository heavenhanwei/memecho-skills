import hashlib
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.build_release import build, declared_version


class ReleasePackageTest(unittest.TestCase):
    def test_versions_are_aligned(self):
        version = declared_version()
        self.assertEqual("1.0.0", version)
        self.assertIn(f'version = "{version}"', (ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertIn(f'__version__ = "{version}"', (ROOT / "src" / "memecho_cli" / "__init__.py").read_text(encoding="utf-8"))

    def test_release_archive_is_flat_and_verified(self):
        with tempfile.TemporaryDirectory() as temp:
            archive, checksums = build(Path(temp))
            with zipfile.ZipFile(archive) as package:
                names = package.namelist()
                self.assertIn("SKILL.md", names)
                self.assertIn("LICENSE", names)
                self.assertIn("agents/openai.yaml", names)
                self.assertFalse(any(name.startswith("memecho-analyze-conversation/") for name in names))
                self.assertFalse(any("__pycache__" in name for name in names))
                self.assertTrue(all(info.create_system == 3 for info in package.infolist()))
            digest = hashlib.sha256(archive.read_bytes()).hexdigest()
            self.assertEqual(f"{digest}  {archive.name}\n", checksums.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

