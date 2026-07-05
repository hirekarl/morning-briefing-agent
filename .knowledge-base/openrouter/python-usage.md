# OpenRouter — Python Usage

Three ways to call OpenRouter from Python. All are OpenAI-compatible under the hood.

## Option 1 — Official Python SDK

```bash
pip install openrouter
```

```python
from openrouter import OpenRouter
import os

with OpenRouter(api_key=os.getenv("OPENROUTER_API_KEY")) as client:
    response = client.chat.send(
        model="~openai/gpt-latest",
        messages=[
            {"role": "user", "content": "What is the meaning of life?"}
        ],
    )

    print(response.choices[0].message.content)
```

## Option 2 — OpenAI SDK pointed at OpenRouter (drop-in replacement)

Useful if the codebase already standardizes on the `openai` package.

```python
from openai import OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="<OPENROUTER_API_KEY>",
)

completion = client.chat.completions.create(
  extra_headers={
    "HTTP-Referer": "<YOUR_SITE_URL>",
    "X-OpenRouter-Title": "<YOUR_SITE_NAME>",
  },
  model="~openai/gpt-latest",
  messages=[
    {"role": "user", "content": "What is the meaning of life?"}
  ]
)

print(completion.choices[0].message.content)
```

## Option 3 — Raw HTTP via `requests`

See [`authentication.md`](authentication.md) for the full snippet — plain POST to `https://openrouter.ai/api/v1/chat/completions` with a JSON body.

## Which to use

- **Official SDK** — cleanest if you want typed responses and don't already have `openai` as a dependency.
- **OpenAI SDK** — best choice if the backend (or a framework like Strands' LiteLLM provider) already expects an OpenAI-compatible client — this is exactly the shape LiteLLM/Strands talk to (see [`../integration-patterns.md`](../integration-patterns.md)).
- **Raw `requests`** — only when you need to avoid all SDK dependencies.

## Gotchas

- `~openai/gpt-latest`-style aliases auto-update to the newest model version — fine for prototyping, but pin an exact model slug (e.g. `openai/gpt-4o`) for anything you want reproducible.
- Response shape matches OpenAI's `chat.completions` format (`response.choices[0].message.content`) regardless of which upstream model actually served the request.
