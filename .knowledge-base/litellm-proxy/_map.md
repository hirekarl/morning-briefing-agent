# LiteLLM Proxy — Map

LiteLLM Proxy is a self-hosted, Dockerized OpenAI-compatible server that fronts any provider (OpenRouter, Azure, Bedrock, local vLLM/Ollama, etc.) behind one consistent API. Source: `docs.litellm.ai/docs/proxy/docker_quick_start` and `docs.litellm.ai/docs/proxy/configs`.

- [`docker-quickstart.md`](docker-quickstart.md) — `docker run` / `docker compose`, `.env`, the `prometheus.yml` gotcha
- [`config-yaml-reference.md`](config-yaml-reference.md) — `model_list`, `router_settings`, `litellm_settings`, `general_settings`, credentials
- [`calling-from-python.md`](calling-from-python.md) — OpenAI SDK and LiteLLM SDK pointed at the running proxy
- [`virtual-keys-and-rate-limits.md`](virtual-keys-and-rate-limits.md) — `/key/generate`, `rpm_limit`, 429 behavior
- [`troubleshooting.md`](troubleshooting.md) — DB connection errors, SSL bypass, the `prometheus.yml`-as-directory bug

See [`../integration-patterns.md`](../integration-patterns.md) for routing this proxy to OpenRouter and calling it from a Strands agent.
