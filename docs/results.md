# Results

## Utility Gate

| model | suite | tests passed | steps passed | step rate |
| --- | --- | ---: | ---: | ---: |
| `qwen/qwen3.6-27b` | `memory_only` | 0/4 | 6/20 | 30.0% |
| `qwen/qwen3.6-27b` | `assistant_responses` | 0/4 | 5/20 | 25.0% |
| `google/gemma-4-12b` | `memory_only` | 2/4 | 16/20 | 80.0% |
| `google/gemma-4-12b` | `assistant_responses` | 0/4 | 11/20 | 55.0% |

Combined:

| model | tests passed | steps passed | gate |
| --- | ---: | ---: | --- |
| `qwen/qwen3.6-27b` | 0/8 | 11/40 | excluded |
| `google/gemma-4-12b` | 2/8 | 27/40 | excluded |

## Interpretation

The benchmark did not reach the attack-ASR phase. Both local models failed the benign utility control first.

This matters because low ASR from either model would be ambiguous: it could mean resistance to dormant prompt injection, or it could simply mean the model failed to use memory and tools well enough for the attack to execute. The lab therefore cannot support either planned hypothesis yet:

- H1, local is safer: not established
- H2, local is more poisonable: not established

The publishable finding from this run is narrower and cleaner: with the tested serving profiles, current local models were not sufficiently reliable as benchmark agents to make ASR meaningful.

## Notable Setup Findings

Routing needed explicit verification. The harness routes `gemini*` model ids to the Gemini client, but `qwen/qwen3.6-27b` and `google/gemma-4-12b` used the OpenAI-compatible path and honored the local base URL.

LM Studio's OpenAI-compatible API rejected `response_format: {"type":"json_object"}`. That initially made semantic-judge checks fail closed. A local proxy fixed this without sending data off-box.

Thinking mode had to be disabled at the serving layer. Qwen's first smoke run spent the generation budget on reasoning output and did not complete the gate. With thinking disabled, both models returned visible content quickly.

## Next Work

Do not run ASR sweeps until a local model clears the utility suites. Good next candidates:

- retry a stronger local model with reliable tool calling
- test an alternative serving stack that supports per-request thinking controls and JSON response formats
- hand-label a small judge agreement set before using a local judge for headline numbers

