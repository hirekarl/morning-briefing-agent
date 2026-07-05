# Strands Agents — Model Providers — Map

Strands supports pluggable model providers: Amazon Bedrock (default), Anthropic (direct), LiteLLM, OpenAI-compatible, Ollama, Mistral, Writer, Llama API, and community providers (Cohere, FireworksAI).

- [`litellm.md`](litellm.md) — the provider this project uses (routes to OpenRouter or a self-hosted LiteLLM proxy)
- [`bedrock.md`](bedrock.md) — the default provider, kept here for contrast/completeness

See [`../../integration-patterns.md`](../../integration-patterns.md) for the full end-to-end wiring to OpenRouter.

**Not fetched:** the general model-providers overview page (404 on the URL tried). The list of supported providers above is taken from the Strands Python quickstart page, not this overview.
