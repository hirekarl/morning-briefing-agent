# OpenRouter — Authentication

All requests require bearer token authentication via the `Authorization` header.

## Required and optional headers

| Header | Required | Purpose |
|---|---|---|
| `Authorization` | Yes | `Bearer <OPENROUTER_API_KEY>` |
| `HTTP-Referer` | No | Enables app attribution on OpenRouter leaderboards |
| `X-OpenRouter-Title` | No | App name shown in attribution |

## Raw request example

```python
import requests
import json

response = requests.post(
  url="https://openrouter.ai/api/v1/chat/completions",
  headers={
    "Authorization": "Bearer <OPENROUTER_API_KEY>",
    "HTTP-Referer": "<YOUR_SITE_URL>",       # Optional
    "X-OpenRouter-Title": "<YOUR_SITE_NAME>", # Optional
  },
  data=json.dumps({
    "model": "~openai/gpt-latest",
    "messages": [
      {"role": "user", "content": "What is the meaning of life?"}
    ]
  })
)
```

## Gotchas

- The API key goes in the `Authorization` header as a bearer token — not a query param, not `X-API-Key`.
- The attribution headers are optional but harmless to always send if you want your app to show up in OpenRouter's usage leaderboards.
- Store the key in an environment variable (`OPENROUTER_API_KEY`); every code example in this KB reads it via `os.getenv(...)` rather than hardcoding it.
