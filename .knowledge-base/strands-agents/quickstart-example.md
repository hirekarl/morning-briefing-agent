# Strands Agents — Quickstart Example

## Full working example

```python
from strands import Agent, tool
from strands_tools import calculator, current_time

@tool
def letter_counter(word: str, letter: str) -> int:
    """Count occurrences of a specific letter in a word."""
    if not isinstance(word, str) or not isinstance(letter, str):
        return 0
    if len(letter) != 1:
        raise ValueError("The 'letter' parameter must be a single character")
    return word.lower().count(letter.lower())

agent = Agent(tools=[calculator, current_time, letter_counter])

message = """I have 4 requests:
1. What is the time right now?
2. Calculate 3111696 / 740883. Tell me how many letter R's are in the word "strawberry" 🍓"""

agent(message)
```

Run it: `python my_agent/agent.py`

## What's happening

1. `calculator` and `current_time` are pre-built tools from `strands_tools`.
2. `letter_counter` is a custom tool — any Python function decorated with `@tool` becomes callable by the agent.
3. Calling `agent(message)` runs the full reasoning loop: the LLM reads the message, decides which tool(s) to call, executes them, and produces a final response. By default this prints reasoning/tool calls to the console as it goes (see [`streaming-and-callbacks.md`](streaming-and-callbacks.md) to change that).

## Default model

Out of the box, with no `model=` argument, the agent uses **Amazon Bedrock with Claude Sonnet 4** — see [`model-providers/_map.md`](model-providers/_map.md) to swap in a different provider (this project uses LiteLLM → OpenRouter instead; see [`../integration-patterns.md`](../integration-patterns.md)).
