# OpenRouter — Map

OpenRouter is a unified API giving access to hundreds of AI models through a single OpenAI-compatible endpoint, with automatic fallback and cost-aware routing. Source: `openrouter.ai/docs/quickstart`.

- [`authentication.md`](authentication.md) — API key, required/optional headers, bearer auth
- [`python-usage.md`](python-usage.md) — official `openrouter` SDK and OpenAI-SDK-compatible calls, full snippets
- [`models-and-parameters.md`](models-and-parameters.md) — model slugs/aliases, request parameters, streaming/tools
- [`gotchas.md`](gotchas.md) — pitfalls specific to OpenRouter

See also [`../integration-patterns.md`](../integration-patterns.md) for how OpenRouter fits behind Strands + LiteLLM.

**Not fetched (404 on the URL tried, not guessed further):** OpenRouter's provider-routing guide (`provider` object with `order`/`allow_fallbacks`/`sort` etc.). If you need fine-grained provider routing config, check `openrouter.ai/docs` directly for the current path.
