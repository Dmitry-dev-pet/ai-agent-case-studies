# Qwen3.5-0.8B on an ephemeral ChatGPT CPU: reproducible experiment

**Date:** 2026-10-18. **Status:** Local generation, private model recovery, one bounded tool call, and GBNF-constrained JSON are verified. Reliable multi-step autonomous planning is **not** demonstrated.

This is a narrow, evidence-backed case study. It is **not** a continuously running model endpoint, a ChatGPT feature claim, a multi-run performance benchmark, or a change to any existing Alfred/MCP access rules.

## Setup and provenance

| Component | Verified configuration |
|---|---|
| Execution | Ephemeral ChatGPT Linux x86-64 container; 4 vCPU, 4 GiB RAM limit, CPU-only, 4 inference threads |
| Model | `notschmee/Qwen3.5-0.8B-GGUF`, `Qwen3.5-0.8B-Q4_K_M.gguf` |
| Hugging Face source revision | `1870603ac8ab59c7ddb9d94cccf3b297e379538f` |
| GGUF bytes | `590880672` |
| GGUF SHA-256 | `be5b3cb8c2f3ebd791349c9c775ea38950f23a2b9e792ca2f0411597dd172988` |
| Inference engine | `llama.cpp` CPU CLI, source pinned at `5aeac37a35b44fde4bdffaec9159f2fcb253b622`, Release build with `GGML_NATIVE=OFF`, AVX2 and FMA |
| CPU executable SHA-256 | `a93a982329e4ca22083cabfa7c0e8cc7c8bb5b3825c9f27f8979d54fd93d89df` |

Neither model weights nor the compiled executable are committed to this public GitHub repository. The model and engine are backed up in a **private** Google Drive folder; GGUF is split into eight individually checksummed, <=75 MB parts. A fresh read-back of those parts was concatenated and verified against the full GGUF digest above. The CPU engine ZIP was also read back from Drive and verified. The restoration recipe remains in that private storage.

## Verified observations

1. **Local inference:** the Qwen GGUF was loaded by `llama.cpp` and generated Russian-language text directly on the ChatGPT container's CPU; no external inference provider was queried. Initial single-run measurements were approximately **47.9 generated tokens/s** and **124.9 prompt tokens/s** with four threads and 1024 context tokens. Treat these as single observations, not guaranteed speed.
2. **Large-file transport and cleanup:** one ordinary GitHub-hosted Ubuntu runner downloaded and fingerprinted the GGUF from Hugging Face; it was delivered as two temporary GitHub Actions artifacts below the GitHub connector's **512 MiB** retrieval limit. ChatGPT's Google Drive upload path also imposed a smaller limit (~100 MiB), so the locally verified GGUF was split again into eight Drive parts. Both Qwen artifacts and the one-time CPU engine artifact were deleted after successful verification. **No Mac runner, Cloudflare worker, Colab, GitHub release binary, or persistent inference server was used.**
3. **Bounded autonomy:** when given only a deterministic `mesh` calculator (`rpm_out = -rpm_in * teeth_driver / teeth_driven`), the model selected A=12 teeth, B=60 teeth, and +120 rpm; one real tool invocation returned **-24 rpm**. It carried that number into its final JSON, but incorrectly described the speed as *increased*. In more involved three-gear trials, it repeated the first tool call or produced premature reports. These are observed failures, not successes to conceal.
4. **Strictly constrained JSON (GBNF):** the pinned CLI successfully generated a `mesh` object under `--grammar-file` control; a separate Python validator enforced exact fields, primitive types, bounds, and unequal tooth counts. A new reproducible run (temperature 0, seed 45, 4 threads, context 1024) returned the example below and measured **3.59 s end-to-end**, **36.7 generated tokens/s**, **137.4 prompt tokens/s**. The engine emits a normal stdout banner in addition to the JSON; the harness isolates the JSON action before validation. See [`examples/qwen_mesh.gbnf`](../examples/qwen_mesh.gbnf), [`examples/qwen_structured_output.py`](../examples/qwen_structured_output.py) and [`evidence/qwen-structured-2026-10-18.json`](../evidence/qwen-structured-2026-10-18.json).

```json
{
  "action": "mesh",
  "teeth_driver": 12,
  "teeth_driven": 60,
  "rpm_driver": 120
}
```

### Limits of the structured-output result

GBNF restricts the output's syntax and the allowed command shape. Python independently checks `12 <= teeth <= 60`, different tooth counts, and a fixed +120 rpm input. This does **not** prove correct action selection, correct physical reasoning, or successful multi-step autonomy. In a previous attempt, `llama.cpp --json-schema` returned a grammar initialization error in this environment; the reproducible success uses `--grammar-file` instead. The JSON Schema issue was not isolated to a root cause and should not be generalized to all versions.

### Autonomous tool experiments (full logs kept privately)

| Experiment | Actual calculator calls | Outcome |
|---|---:|---|
| Free-form, three gears | 0 | Premature invented report, incorrect claim about idler effect |
| Tool-first, three gears | 1 | A=12 / B=24 -> -60 rpm; then premature report |
| Bounded stateful, three gears | 5 attempted | One valid A=30 / B=25 -> -144 rpm result; repeated A→B instead of progressing |
| Simplified one-mesh challenge | 1 | Successful validated call for A=12 / B=60 -> -24 rpm; subsequent prose mistake |

One further interrupted retry (5 attempts with repeated requests despite duplicate errors) is excluded from complete-run counts. There was no unrestricted shell, browsing, external file access, or persistent tool authority granted to the model.

**Physics reference (checked outside Qwen):** for two external gear meshes, `omega_C = omega_A * z_A / z_C`, so the final gear turns in the same direction as A, and changing only B's tooth count does not change C's ideal angular speed. The model did not reliably derive this in its autonomous three-gear experiment.

## Reproduce the structured-output sample

After obtaining and verifying **your own local GGUF and trusted llama-cli binary**, run the following offline. Neither is fetched automatically:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 examples/qwen_structured_output.py \
  --cli /path/to/llama-cli \
  --model /path/to/Qwen3.5-0.8B-Q4_K_M.gguf \
  --evidence /tmp/qwen-structured-evidence.json
```

The script enforces one fixed GBNF grammar, runs one single-turn local CPU generation, parses the model's JSON action, rejects unexpected fields or invalid values, and prints a compact record with elapsed time and hashes. The eight Python unit tests do not need a model or network connection.

## Public GitHub evidence

- [Initial one-shot GGUF transfer workflow — successful run](https://github.com/Dmitry-dev-pet/ai-agent-case-studies/actions/runs/39119325556); one artifact was oversized for connector retrieval, subsequently removed.
- [Two-part GGUF handoff — successful run](https://github.com/Dmitry-dev-pet/ai-agent-case-studies/actions/runs/39120108933) and [workflow PR #3](https://github.com/Dmitry-dev-pet/ai-agent-case-studies/pull/3).
- [Pinned Linux CPU engine build — successful run](https://github.com/Dmitry-dev-pet/ai-agent-case-studies/actions/runs/39120931734) and [workflow PR #6](https://github.com/Dmitry-dev-pet/ai-agent-case-studies/pull/6).
- [Verified artifact deletion workflows](https://github.com/Dmitry-dev-pet/ai-agent-case-studies/actions/workflows/qwen-gguf-cleanup.yml); all three resulting large/transient model/engine artifacts were removed.

**Interpretation:** useful small-model *local inference* and *constrained output* are demonstrated. A general-purpose autonomous agent, correct multi-step physics research, state persistence of a live process, or unrestricted tool access are **not**.
