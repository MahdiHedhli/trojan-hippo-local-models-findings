# Proxy Evidence

Date: 2026-06-08

Purpose: keep the benchmark and semantic judge local while adapting one LM Studio OpenAI-compatibility gap.

## Auth Boundary

LM Studio upstream auth was enabled.

| check | result |
| --- | --- |
| Direct unauthenticated upstream `/v1/models` | HTTP 401 |
| Proxy `/v1/models` with dummy downstream key | HTTP 200 |
| Proxy model ids observed | `qwen/qwen3.6-27b`, `google/gemma-4-12b`, `google/gemma-4-31b`, `text-embedding-nomic-embed-text-v1.5` |

The harness used the proxy endpoint with a dummy non-empty API key. The proxy read the real LM Studio Authorization value from local environment and forwarded it upstream. No credential value is logged or stored in this repo.

## `response_format` Compatibility

LM Studio rejected OpenAI's legacy `response_format: {"type":"json_object"}` value. The proxy removed only that unsupported field before forwarding the request upstream.

| model | direct LM Studio | proxy |
| --- | --- | --- |
| `qwen/qwen3.6-27b` | HTTP 400, `'response_format.type' must be 'json_schema' or 'text'` | HTTP 200, returned `{"ok": true}`, `reasoning_len=0` |
| `google/gemma-4-12b` | HTTP 400, `'response_format.type' must be 'json_schema' or 'text'` | HTTP 200, returned `{"ok": true}`, `reasoning_len=0` |

The proxy log showed harness-issued `POST /v1/chat/completions` calls and `rewrote unsupported json_object response_format` notices during the utility suites. Request bodies were not logged.

## Scope

This proxy is not a harness modification. It sits between the unmodified benchmark and the local OpenAI-compatible server.

The proxy does not implement model behavior, retries, scoring, validators, memory, or tool logic. It forwards requests locally and strips one unsupported request field when needed.
