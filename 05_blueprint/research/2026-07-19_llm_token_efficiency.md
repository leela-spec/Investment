# Research Archive — Token-Efficient LLM Patterns for Weekly Jobs (mid-2026)

**Date:** 2026-07-19 · **Method:** web research agent (pricing/doc pages cited) · **Question:** cheapest, most robust AI layer for a weekly snapshot-first report · **Feeds:** decision A8; meso plan C6.

## Key findings

1. **Prompt caching does NOT help weekly jobs.** All providers discount cached prefixes (Anthropic ~10% read cost; OpenAI 90% off, TTL up to 24h; Gemini ~10%), but every TTL expires between weekly runs → **never engineer for cache hits here**. Keep cache-correct hygiene anyway (frozen prefix, volatile data last) because it makes runs diffable.
2. **The levers that matter: Batch API (−50%, all three providers, ≤24h turnaround — perfect for weekly) + structured outputs (JSON-schema-enforced everywhere incl. Ollama `format`) which eliminate retry/parse waste.**
3. **Cost reality (8k in + 2k out per week ≈ 4.3 runs/month), mid-2026 prices per MTok:**
   | Model | $/MTok in/out | ≈/month |
   |---|---|---|
   | GPT-5 nano | 0.05 / 0.40 | ~0.5¢ |
   | GPT-5 mini | 0.25 / 2.00 | ~2.6¢ |
   | Gemini 3.1 Flash-Lite | 0.25 / 1.50 | ~2.2¢ |
   | Gemini 3 Flash | 0.50 / 3.00 | ~4.3¢ |
   | Claude Haiku 4.5 | 1.00 / 5.00 | ~7.8¢ (~4¢ batched) |
   Even Sonnet-class synthesis ≈ 5¢/run. **At <10¢/month: choose on quality, not price.**
4. **$0 options:** Gemini free tier (≈250–1,500 req/day depending on model; one weekly call trivial; caveat: free-tier prompts may train Google products — MVP snapshot contains no personal data), local Ollama (Qwen-class 8–14B narrates pre-computed JSON well at temp 0 with schema; interpretive nuance weaker), or manual paste into a Claude Project / ChatGPT (frontier quality, ~2 min/week).
5. **"Code computes, LLM narrates" is a recognized best practice** — deterministic data-to-text decomposition / "generative last mile"; validated by recent papers on partitioning deterministic vs neural computation and by practitioner guidance ("use LLMs only where judgment is required"). Snapshot-first without RAG is correct at this scale — 60 indicators + selected modules fit any context window; embeddings add infra for zero benefit.
6. **Stable recurring-prompt hygiene:** frozen versioned system prompt (never interpolate dates/values), stable→volatile ordering, explicit per-section output budgets enforced via JSON schema, temperature 0 where supported, pinned model versions, `prompt_version` recorded in every output.

Key URLs: developers.openai.com/api/docs/pricing · developers.openai.com/api/docs/guides/prompt-caching · ai.google.dev/gemini-api/docs/pricing · ai.google.dev/gemini-api/docs/rate-limits · platform.claude.com/docs/en/about-claude/pricing · glukhov.org/llm-performance/ollama (structured output) · arxiv.org/pdf/2605.29652 (partitioning deterministic/neural) · collinwilkins.com/articles/structured-output
