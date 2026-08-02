# Exercise 0x25 — KV Cache Reuse (Latent Briefing Concept)

## Objective

Demonstrate how prompt caching enables KV cache reuse across multiple queries — the same core mechanism described in Ramp's "Latent Briefing" research.

## Background

**Paper:** https://labs.ramp.com/research/latent-briefing-kv-cache

In multi-agent systems, an orchestrator builds rich reasoning context over many calls. Passing this as raw text to worker agents causes token explosion. Latent Briefing solves this by operating directly on KV cache representations — pre-computing them once and sharing them across workers.

Anthropic's prompt caching is the production API for this: mark a context block with `cache_control`, and the KV cache is computed once then reused on subsequent calls.

### Concept Mapping

| Paper Concept | Exercise Equivalent |
|---|---|
| Orchestrator builds shared context | Large security policy in system prompt |
| KV cache pre-computation | `cache_control: {"type": "ephemeral"}` |
| Workers query shared representations | Multiple queries reuse cached context |
| Token reduction metrics | `cache_read_input_tokens` vs `cache_creation_input_tokens` |

## Instructions

### 1. Run the Demo

```sh
python extras/exercise-25/kv_cache_demo.py
```

### 2. Observe the Metrics

- **Query 1:** `cache_creation_input_tokens` > 0 (KV cache is computed)
- **Query 2 & 3:** `cache_read_input_tokens` > 0 (KV cache is reused)

Cached tokens are billed at 90% discount on reads, with a 25% write premium on creation.

### 3. Experiment (Optional)

- Remove the `cache_control` block and compare — all calls pay full input token cost
- Add more queries to observe continued cache hits within the 5-minute TTL
- Increase the policy size and observe how cache savings scale
- Try setting cache TTL to longer durations for persistent caching
