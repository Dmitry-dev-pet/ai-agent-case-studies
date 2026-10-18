"""Pure-Python tests; GGUF, llama.cpp and network not needed."""
import importlib.util
import json
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "examples" / "qwen_structured_output.py"
spec = importlib.util.spec_from_file_location("qwen_structured_output", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class StructuredOutputValidation(unittest.TestCase):
    good = {"action": "mesh", "teeth_driver": 12, "teeth_driven": 60, "rpm_driver": 120}

    def test_valid_object(self):
        self.assertEqual(module.validate(dict(self.good)), self.good)

    def test_rejects_extra_field(self):
        with self.assertRaises(ValueError):
            module.validate({**self.good, "shell": "echo unwanted"})

    def test_rejects_unexpected_action(self):
        with self.assertRaises(ValueError):
            module.validate({**self.good, "action": "execute"})

    def test_rejects_boolean_number(self):
        with self.assertRaises(ValueError):
            module.validate({**self.good, "teeth_driver": True})

    def test_rejects_equal_counts(self):
        with self.assertRaises(ValueError):
            module.validate({**self.good, "teeth_driven": 12})

    def test_rejects_bad_rpm(self):
        with self.assertRaises(ValueError):
            module.validate({**self.good, "rpm_driver": 121})

    def test_rejects_bad_json(self):
        with self.assertRaises(ValueError):
            module.parse_cli_response("banner...not a JSON object")

    def test_extracts_json_from_cli_banner(self):
        text = "> instruction\n" + json.dumps(self.good) + "\n[ Prompt: 100 t/s | Generation: 20 t/s ]"
        self.assertEqual(module.parse_cli_response(text), self.good)


if __name__ == "__main__":
    unittest.main()
