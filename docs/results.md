# Results

## Run Status

These results are from the authenticated-proxy run on 2026-06-08. LM Studio auth was enabled upstream, the benchmark harness used a dummy downstream key, and a loopback proxy injected the real upstream authorization locally. No model, judge, or utility calls were sent to a remote API.

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

The result JSONs reported zero execution-error cases across these 16 utility cases. The failures above are therefore treated as utility failures, not timeout or routing failures.

## Interpretation

The benchmark did not reach the attack-ASR phase. Both local models failed the benign utility control first.

This matters because low ASR from either model would be ambiguous: it could mean resistance to dormant prompt injection, or it could simply mean the model failed to use memory and tools well enough for the attack to execute. The lab therefore cannot support either planned hypothesis yet:

- H1, local is safer: not established
- H2, local is more poisonable: not established

The publishable finding from this run is narrower and cleaner: with the tested serving profiles, current local models were not sufficiently reliable as benchmark agents to make ASR meaningful.

## Notable Setup Findings

Routing needed explicit verification. The harness routes `gemini*` model ids to the Gemini client, but `qwen/qwen3.6-27b` and `google/gemma-4-12b` used the OpenAI-compatible path and honored the local base URL.

LM Studio's OpenAI-compatible API rejected `response_format: {"type":"json_object"}` with HTTP 400. A local proxy fixed this without sending data off-box by removing only that unsupported field.

Thinking mode had to be disabled at the serving layer. Qwen's first smoke run spent the generation budget on reasoning output and did not complete the gate. With thinking disabled, both models returned visible content quickly.

LM Studio upstream auth was enabled for this run. An unauthenticated `/v1/models` request returned HTTP 401, while the proxy returned HTTP 200 to the harness using a dummy downstream key.

The explicit memory backend does not require embeddings, but the benchmark email-search tool can attempt embeddings and fall back to keyword search when unavailable. During the proxy run, a small number of `/v1/embeddings` attempts returned HTTP 400 and did not surface as result-level execution errors. Local embedding wiring remains a prerequisite before any `mem0` or `rag` run.

The local semantic judge was fixed to `qwen/qwen3.6-27b` for both target-model utility runs. A hand-labeled judge-agreement set was not completed during this utility-gate run, so these results should be treated as gate evidence, not a final benchmark claim.

## Next Work

Do not run ASR sweeps until a local model clears the utility suites. Good next candidates:

- retry a stronger local model with reliable tool calling
- test an alternative serving stack that supports per-request thinking controls and JSON response formats
- hand-label a small judge agreement set before using a local judge for headline numbers
- wire and validate a local embedding endpoint before any `mem0` or `rag` backend sweep
