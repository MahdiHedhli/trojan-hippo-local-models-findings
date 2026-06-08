# Trojan Hippo, Local Models: The Utility Gate Closed First

DON'T PANIC // Threat Research

The motivating question was simple: are local agent models less vulnerable to Trojan Hippo-style dormant memory poisoning, or more vulnerable because they lack frontier-grade instruction hierarchy training?

This run does not answer that question yet. It found the control condition first.

Two self-hosted models were tested against the published Trojan Hippo benchmark harness:

- `qwen/qwen3.6-27b`
- `google/gemma-4-12b`

Both were served locally through LM Studio. The harness was not modified. A local proxy was used only to adapt LM Studio's OpenAI-compatible API to the harness semantic judge's `response_format` expectation.

Before running attack ASR, the lab required a utility floor. That is the right control: a model that fails benign memory tasks cannot be called secure when it also fails an attack. It may simply be broken as an agent.

## What Happened

Qwen failed the utility gate:

- `memory_only`: 6/20 steps
- `assistant_responses`: 5/20 steps

Gemma did better, but still failed the gate:

- `memory_only`: 16/20 steps
- `assistant_responses`: 11/20 steps

Because neither model cleared the utility suites, the attack sweep was not run. There is no local-model ASR headline from this run, and there should not be one.

## Why That Matters

The tempting story would be: "local models resisted Trojan Hippo."

That would be wrong.

The more careful story is: "under these serving profiles, the local models were not reliable enough agents for Trojan Hippo ASR to be meaningful."

This is still useful. It prevents a false security claim. It also gives a concrete next step: test a local model and serving stack that can pass the benign memory suites first, then rerun the static attack grid.

## Setup Notes

Three details mattered:

1. Routing had to be verified by watching the local serving logs. The model id passed to `--model` must be the id reported by the local endpoint.
2. LM Studio rejected `response_format: {"type":"json_object"}`. Without a local proxy, semantic-judge calls failed closed and made utility look worse than it was.
3. Thinking mode had to be disabled at the serving layer. Otherwise Qwen spent the gate window on reasoning output instead of completing the benchmark turn.

## Bottom Line

No ASR number is better than a misleading ASR number.

This run did not show that local models are safer. It did not show that local models are more poisonable. It showed that the utility control can fail first, and when it does, the only honest move is to stop.

