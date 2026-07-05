# OpenRouter — Models & Parameters

## Endpoint

```
POST https://openrouter.ai/api/v1/chat/completions
```

## Model identifiers

- Standard slugs: `openai/gpt-4-turbo`, `anthropic/claude-3-opus`, etc. (`<provider>/<model>` format)
- "Latest" aliases: `~openai/gpt-latest` — auto-updates to the newest version of that model family
- Full catalog: `openrouter.ai/models`, or programmatically via `GET /api/v1/models`

## Request parameters

Standard OpenAI-compatible parameters are supported:

| Parameter | Purpose |
|---|---|
| `model` | Model identifier/slug |
| `messages` | Conversation history array |
| `temperature` | Response randomness |
| `max_tokens` | Output length limit |
| `tools` | Function-calling definitions |

## Advanced features

- **Streaming** — supported for real-time responses (standard OpenAI-style SSE streaming).
- **Tool calling** — built into OpenRouter's Agent SDK with automatic execution loops (not the focus here since Strands is the agent framework being used instead — see [`../strands-agents/_map.md`](../strands-agents/_map.md)).
- **Fallback models** — automatic failover via the unified API.
- **Provider routing** — control which upstream provider serves a model (doc page 404'd, see [`_map.md`](_map.md) note).

## Gotchas

- Because every model is routed through the same endpoint, per-model quirks (context window, supported params) still apply — OpenRouter surfaces this via `require_parameters`-style behavior on the (unfetched) provider-routing page. Check `openrouter.ai/models` for a given model's actual limits before assuming full OpenAI-parameter parity.
- `tools` param works for models that support function calling upstream; not all routed models do.
