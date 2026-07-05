# Strands Agents (Python) — Map

Strands Agents is the agent framework for this project: an `Agent` runs a reasoning loop (LLM → tool selection → tool execution → response) over a configurable model provider. Source: `strandsagents.com/docs/user-guide/quickstart/python/` and the LiteLLM model-provider page.

- [`installation.md`](installation.md) — venv, pip install, Python version requirement
- [`quickstart-example.md`](quickstart-example.md) — full working `agent.py`, `@tool` decorator
- [`agent-and-tools.md`](agent-and-tools.md) — `Agent` constructor params, tool authoring rules
- [`model-providers/_map.md`](model-providers/_map.md) — configuring which LLM backend the agent uses
- [`streaming-and-callbacks.md`](streaming-and-callbacks.md) — `stream_async`, `callback_handler`
- [`observability.md`](observability.md) — `AgentResult`, metrics, debug logging
- [`gotchas.md`](gotchas.md) — pitfalls specific to Strands

See also [`../integration-patterns.md`](../integration-patterns.md) for wiring the `LiteLLMModel` provider to OpenRouter/LiteLLM proxy.

**Not fetched (404 on the URL tried):** the general model-providers overview page. The LiteLLM-specific provider page (linked above) was fetched successfully and covers everything needed for this project.
