import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memecho_cli.cli import main
from memecho_cli.rendering import ascii_axis, render_html, render_markdown


class ReportRenderingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads((ROOT / "examples" / "result-text-only.json").read_text(encoding="utf-8"))

    def test_ascii_axis_is_ascii_only_and_marks_zero(self):
        chart = ascii_axis(0.35)
        self.assertIn("|", chart)
        self.assertIn("*", chart)
        self.assertTrue(chart.isascii())

    def test_markdown_contains_visuals_and_semantic_boundaries(self):
        report = render_markdown(self.result)
        self.assertIn("REPORT CONFIDENCE", report)
        self.assertIn("```text", report)
        self.assertIn("V [", report)
        self.assertIn("状态：confirmed", report)
        self.assertIn("建议（未确认）", report)
        self.assertIn("不是心理诊断", report)

    def test_html_is_standalone_responsive_and_escaped(self):
        result = json.loads(json.dumps(self.result, ensure_ascii=False))
        result["minutes"]["summary"] = '<script>alert("x")</script>'
        result["vad_series"][0]["linguistic_weight"] = '<script>weight()</script>'
        result["scope"]["quality"] = "not-a-number"
        report = render_html(result)
        self.assertTrue(report.startswith("<!doctype html>"))
        self.assertIn('<meta charset="utf-8">', report)
        self.assertIn("@media(max-width:760px)", report)
        self.assertIn("&lt;script&gt;", report)
        self.assertNotIn('<script>alert("x")</script>', report)
        self.assertNotIn('<script>weight()</script>', report)
        self.assertNotIn("https://", report)
        self.assertIn("未解决分歧", report)
        self.assertIn("VAD 走向", report)

    def test_cli_renders_both_files(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp) / "conversation-report"
            stream = io.StringIO()
            with redirect_stdout(stream):
                code = main(["render", str(ROOT / "examples" / "result-text-only.json"), "--format", "both", "--output", str(base)])
            self.assertEqual(0, code)
            self.assertTrue(base.with_suffix(".md").exists())
            self.assertTrue(base.with_suffix(".html").exists())
            self.assertIn("REPORT CONFIDENCE", base.with_suffix(".md").read_text(encoding="utf-8"))
            self.assertIn("<!doctype html>", base.with_suffix(".html").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
