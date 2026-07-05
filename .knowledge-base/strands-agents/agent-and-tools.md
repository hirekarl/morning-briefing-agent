# Strands Agents — Agent & Tools

## Agent loop

```
Input → [LLM Reasoning → Tool Selection → Tool Execution] → Response
```

The agent iterates through reasoning cycles, automatically selecting tools based on context, until it produces a final answer.

## `Agent` constructor

```python
Agent(
    model="model_id_or_instance",      # string or model instance; default: Bedrock Claude Sonnet 4
    tools=[tool1, tool2, ...],         # list of tools (functions or instances)
    callback_handler=function_or_None, # streaming callback; default prints to console
    # additional: session_id, state, hooks, prompts, etc. — see full API docs
)
```

## Defining custom tools

```python
from strands import tool

@tool
def my_tool(param1: str, param2: int) -> str:
    """Tool description for the agent."""
    return f"Result: {param1} x {param2}"
```

Rules:
- **Type hints are required** on every parameter — the agent uses them to validate/construct tool calls.
- **The docstring is not just documentation** — it's sent to the LLM as part of the tool's definition, so write it as you would a description for the model, not just for a human reader.
- `@tool` only works on plain Python functions.

## Checking the active model config

```python
from strands import Agent
agent = Agent()
print(agent.model.config)
# {'model_id': 'global.anthropic.claude-sonnet-4-6'}
```

## Simplest model override (string form)

```python
agent = Agent(model="anthropic.claude-sonnet-4-20250514-v1:0")
```

For anything beyond a plain string (custom `api_base`, provider-specific params), construct a model instance instead — see [`model-providers/_map.md`](model-providers/_map.md).
