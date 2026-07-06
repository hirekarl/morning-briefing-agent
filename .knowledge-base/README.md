# Knowledge Base: Agent Stack (OpenRouter + Strands Agents + LiteLLM Proxy)

This is a map-and-leaf knowledge base for the three pieces of the Python agent backend built this week at Pursuit:

| Tool               | Role                                                                     | Section                                            |
| ------------------ | ------------------------------------------------------------------------ | -------------------------------------------------- |
| **OpenRouter**     | Unified API for hundreds of LLMs behind one OpenAI-compatible endpoint   | [`openrouter/_map.md`](openrouter/_map.md)         |
| **Strands Agents** | Python agent framework (agent loop, tools, model providers)              | [`strands-agents/_map.md`](strands-agents/_map.md) |
| **LiteLLM Proxy**  | Self-hosted, Dockerized OpenAI-compatible proxy in front of any provider | [`litellm-proxy/_map.md`](litellm-proxy/_map.md)   |

Each section folder has a `_map.md` (orientation + links) and one leaf file per topic. Leaf files hold the actual config tables, gotchas, and full code snippets — the maps never duplicate that content, they just point to it.

## How the three pieces compose

**[`integration-patterns.md`](integration-patterns.md) is the payoff doc** — it shows the concrete Python wiring for the two realistic architectures:

1. `Strands Agent` → `LiteLLMModel` → **directly to OpenRouter** (OpenRouter's endpoint is OpenAI-compatible, so LiteLLM can call it like any other provider)
2. `Strands Agent` → `LiteLLMModel` → **self-hosted LiteLLM proxy** (Docker) → OpenRouter or any other provider configured in `config.yaml`

Start there if you already know you're wiring an agent end-to-end. Start in a tool's `_map.md` if you need the details on one piece.

## Source coverage

All content here was pulled from:

- OpenRouter: `docs/quickstart`
- Strands Agents: `docs/user-guide/quickstart/python/`, `docs/user-guide/concepts/model-providers/litellm/`
- LiteLLM: `docs/proxy/docker_quick_start`, `docs/proxy/configs`

Two pages referenced by the docs (Strands' general model-providers overview page, OpenRouter's provider-routing guide) returned 404s on the URLs tried and were **not** fetched — they are not included here rather than guessed at. If you need them, search the docs sites directly.
