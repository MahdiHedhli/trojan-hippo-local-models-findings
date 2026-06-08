# Trojan Hippo, Local Models

Controlled local-model run of `debesheedas/trojan-hippo-benchmark` for DON'T PANIC // Threat Research.

## Result

The authenticated-proxy run on 2026-06-08 stopped at the Phase 1 utility gate. Neither local model cleared the utility control, so no ASR sweep was run and no ASR number should be quoted from this run.

| model | memory_only | assistant_responses | combined utility | gate |
| --- | ---: | ---: | ---: | --- |
| `qwen/qwen3.6-27b` | 6/20 steps, 0/4 tests | 5/20 steps, 0/4 tests | 11/40 steps, 0/8 tests | excluded |
| `google/gemma-4-12b` | 16/20 steps, 2/4 tests | 11/20 steps, 0/4 tests | 27/40 steps, 2/8 tests | excluded |

This is the main finding: for these local serving profiles, failed attacks would not be evidence of safety. The agents do not reliably perform the benign memory tasks that make ASR interpretable.

## What Was Controlled

- Harness repo: `debesheedas/trojan-hippo-benchmark`, commit `a67d3261338120c606fcf6afda2547f622809922`
- Harness source: unmodified
- Memory backend: `explicit`
- Defense: `none`
- Workers: `--num-workers 1`
- Judge: local `qwen/qwen3.6-27b` through the same local serving stack
- Network: local-only for model and judge calls
- LM Studio auth: enabled upstream; the harness used a dummy key against a loopback proxy

See `docs/run-manifest.md` for the reproducibility manifest, `docs/results.md` for the utility-gate notes, and `docs/proxy-evidence.md` for the OpenAI-compatibility evidence.

## Repo Contents

- `data/utility_scores.csv`: sanitized utility scores
- `data/proxy_compatibility.csv`: sanitized direct-vs-proxy API compatibility matrix
- `docs/run-manifest.md`: run configuration and gate decisions
- `docs/results.md`: findings and interpretation
- `docs/proxy-evidence.md`: evidence that the proxy kept authenticated LM Studio local while adapting `response_format`
- `scripts/lmstudio_openai_proxy.py`: local proxy used to keep the judge local while handling LM Studio's `response_format` compatibility gap
