import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memecho_cli.cli import build_request, parser_for_cli
from memecho_cli.validation import validate_request, validate_result


def load_skill_validator():
    path = ROOT / "skills" / "memecho-analyze-conversation" / "scripts" / "validate_contract.py"
    spec = importlib.util.spec_from_file_location("skill_validator", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ContractExamplesTest(unittest.TestCase):
    def test_request_example_passes_both_validators(self):
        data = json.loads((ROOT / "examples" / "request-meeting.json").read_text(encoding="utf-8"))
        self.assertEqual([], validate_request(data))
        self.assertEqual([], load_skill_validator().validate_request(data))

    def test_result_example_passes_both_validators(self):
        data = json.loads((ROOT / "examples" / "result-text-only.json").read_text(encoding="utf-8"))
        self.assertEqual([], validate_result(data))
        self.assertEqual([], load_skill_validator().validate_result(data))

    def test_monologue_auto_resolves_self(self):
        args = parser_for_cli().parse_args([
            "analyze", "--input", str(ROOT / "examples" / "monologue.txt"), "--context", "monologue"
        ])
        request = build_request(args)
        self.assertEqual("auto_single_speaker", request["self_identity_basis"])
        self.assertEqual(["minutes", "content_analysis", "vad", "self_echo"], request["focus"])
        self.assertTrue(request["participants"][0]["is_self"])

    def test_multispeaker_echo_requires_self(self):
        args = parser_for_cli().parse_args([
            "echo", "--input", str(ROOT / "examples" / "meeting-transcript.txt"),
            "--participants", "阿青,小林"
        ])
        with self.assertRaisesRegex(ValueError, "requires --self"):
            build_request(args)

    def test_text_only_rejects_acoustic_weight(self):
        data = json.loads((ROOT / "examples" / "result-text-only.json").read_text(encoding="utf-8"))
        data["vad_series"][0]["acoustic_weight"] = 0.5
        self.assertTrue(any("acoustic_weight" in error for error in validate_result(data)))


if __name__ == "__main__":
    unittest.main()

