# Strands Agents — Gotchas

1. **Tool docstrings matter.** They're sent to the LLM as the tool's description — vague docstrings produce worse tool-selection behavior.
2. **Type hints are required** on every tool parameter, not optional style preference — the framework relies on them.
3. **`@tool` only decorates plain Python functions.**
4. **Async vs. sync streaming don't mix.** Use `stream_async()` in async frameworks; callback handlers are synchronous. Set `callback_handler=None` when streaming to avoid duplicate output (see [`streaming-and-callbacks.md`](streaming-and-callbacks.md)).
5. **Default model is Amazon Bedrock Claude Sonnet 4** — if you don't explicitly configure a model provider, the agent will try to call Bedrock and fail without AWS credentials/model access enabled. This project uses LiteLLM instead (see [`model-providers/litellm.md`](model-providers/litellm.md) and [`../integration-patterns.md`](../integration-patterns.md)) — don't forget to pass `model=` explicitly.
6. **Missing extras cause `ModuleNotFoundError`.** Using `LiteLLMModel` without `pip install 'strands-agents[litellm]'` fails at import time with a module-not-found error, not a clear "install this extra" message.
7. **`strands-agents-tools` vs `strands.tools`** — the community tools package is `strands_tools` (a separate pip package, underscore import), easy to confuse with the core framework.
