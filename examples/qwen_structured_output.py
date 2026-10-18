#!/usr/bin/env python3
"""Reproduce a single, validated Qwen3.5-0.8B GBNF JSON sample offline.

Requires a locally available, trusted llama.cpp CLI and the Q4_K_M GGUF.
No download/API calls are made by this script. The model does not execute tools.
"""
import argparse
import hashlib
import json
import re
import subprocess
import time
from pathlib import Path

GRAMMAR = Path(__file__).with_name("qwen_mesh.gbnf")
FIELDS = {"action", "teeth_driver", "teeth_driven", "rpm_driver"}
PROMPT = (
    "Выбери шестерни для одного расчета. A=12 зубьев, B=60 зубьев, "
    "скорость A=120 об/мин. Выдай только объект JSON action mesh "
    "с полями action, teeth_driver, teeth_driven, rpm_driver."
)


def validate(obj):
    """Reject malformed, extra fields, invalid type/ranges and equal tooth counts."""
    if not isinstance(obj, dict) or set(obj) != FIELDS:
        raise ValueError("unexpected JSON fields")
    if obj["action"] != "mesh":
        raise ValueError("unexpected action")
    a, b, rpm = (obj[k] for k in ("teeth_driver", "teeth_driven", "rpm_driver"))
    if not (type(a) is int and type(b) is int and 12 <= a <= 60 and 12 <= b <= 60 and a != b):
        raise ValueError("invalid or equal gear tooth counts")
    if type(rpm) is not int or rpm != 120:
        raise ValueError("invalid input rotation speed")
    return obj


def parse_cli_response(stdout):
    """llama-cli may print a startup banner and prompt echo before the response."""
    decoder = json.JSONDecoder()
    objects = []
    for match in re.finditer(r"\{", stdout):
        try:
            data, _ = decoder.raw_decode(stdout[match.start():])
            if isinstance(data, dict) and data.get("action") == "mesh":
                objects.append(data)
        except ValueError:
            continue
    if not objects:
        raise ValueError("no generated JSON action in CLI output")
    return validate(objects[-1])


def sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def run(cli, model, timeout):
    if not cli.is_file() or not model.is_file():
        raise FileNotFoundError("provide an existing llama-cli and GGUF model")
    if model.open("rb").read(4) != b"GGUF":
        raise ValueError("not a GGUF file")
    cmd = [str(cli), "--model", str(model), "--threads", "4", "--ctx-size", "1024",
           "--predict", "96", "--temp", "0", "--reasoning", "off", "--seed", "45",
           "--single-turn", "--no-display-prompt", "--simple-io", "--grammar-file",
           str(GRAMMAR), "--prompt", PROMPT]
    start = time.monotonic()
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
    elapsed = round(time.monotonic() - start, 2)
    if proc.returncode:
        raise RuntimeError(f"llama-cli failed (exit={proc.returncode})")
    obj = parse_cli_response(proc.stdout)
    timing = re.search(r"\[ Prompt: ([0-9.]+) t/s \| Generation: ([0-9.]+) t/s \]", proc.stdout)
    return {
        "model": "Qwen3.5-0.8B-Q4_K_M",
        "model_bytes": model.stat().st_size,
        "model_sha256": sha256_file(model),
        "engine_sha256": sha256_file(cli),
        "device": "CPU",
        "threads": 4,
        "ctx_size": 1024,
        "sampling": {"temperature": 0, "seed": 45},
        "output_constraint": "GBNF grammar (qwen_mesh.gbnf) + Python semantic validation",
        "output": obj,
        "verified": True,
        "elapsed_seconds": elapsed,
        "prompt_tokens_per_second": float(timing.group(1)) if timing else None,
        "generated_tokens_per_second": float(timing.group(2)) if timing else None,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--cli", type=Path, required=True)
    p.add_argument("--model", type=Path, required=True)
    p.add_argument("--evidence", type=Path, help="optional JSON evidence output path")
    p.add_argument("--timeout", type=int, default=120)
    args = p.parse_args()
    result = run(args.cli, args.model, args.timeout)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    print(rendered, end="")
    if args.evidence:
        args.evidence.write_text(rendered, encoding="utf-8")


if __name__ == "__main__":
    main()
