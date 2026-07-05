# Strands Agents — Streaming & Callbacks

## Async iteration (recommended inside async frameworks, e.g. FastAPI)

```python
import asyncio
from strands import Agent
from strands_tools import calculator

agent = Agent(tools=[calculator], callback_handler=None)

async def process_streaming():
    prompt = "What is 25 * 48?"
    agent_stream = agent.stream_async(prompt)

    async for event in agent_stream:
        if "data" in event:
            print(event["data"], end="", flush=True)
        elif "current_tool_use" in event and event["current_tool_use"].get("name"):
            print(f"\n[Tool: {event['current_tool_use']['name']}]")

asyncio.run(process_streaming())
```

## Callback handlers (sync)

```python
import logging
from strands import Agent

logger = logging.getLogger("my_agent")
tool_use_ids = []

def callback_handler(**kwargs):
    if "data" in kwargs:
        logger.info(kwargs["data"], end="")
    elif "current_tool_use" in kwargs:
        tool = kwargs["current_tool_use"]
        if tool["toolUseId"] not in tool_use_ids:
            logger.info(f"\n[Using tool: {tool.get('name')}]")
            tool_use_ids.append(tool["toolUseId"])

agent = Agent(tools=[...], callback_handler=callback_handler)
result = agent("Your query")
print(result.message)
```

## Disabling default console output

```python
agent = Agent(tools=[...], callback_handler=None)
```

## Async invocation (non-streaming)

```python
result = await agent.invoke_async("Your prompt")
```

## Gotchas

- **Callback handlers and `stream_async` are mutually exclusive** in practice — pick one pattern per agent (sync callback for simple scripts, `stream_async` inside async frameworks). Set `callback_handler=None` when using `stream_async` to avoid double output.
- The default `callback_handler` prints reasoning/tool-use to the console — surprising in a server context (e.g. FastAPI) if you didn't explicitly disable it.
