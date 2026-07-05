# OpenRouter — Gotchas

- **Auth goes in the header, not the body.** `Authorization: Bearer <key>` — a common first-integration mistake is putting the key in the JSON payload.
- **`~openai/gpt-latest` aliases move under you.** Great for quickstart demos, risky for anything you need reproducible — pin exact slugs in real code.
- **Rate limits vary by key/model tier**, including free-tier models with their own limits — see the FAQ (`/faq#how-are-rate-limits-calculated`) rather than assuming a flat global limit.
- **Response shape is OpenAI's shape**, even though the request may be served by Anthropic, Google, or another upstream provider — don't special-case parsing per-provider.
- **App attribution headers (`HTTP-Referer`, `X-OpenRouter-Title`) are optional** — omitting them doesn't break requests, it just excludes the app from OpenRouter's leaderboards.
- **This KB did not fetch OpenRouter's provider-routing guide** (404 on the URL tried) — if fine-grained control over which upstream provider serves a request is needed (`order`, `allow_fallbacks`, `ignore`, `quantizations`), look it up directly on `openrouter.ai/docs` rather than trusting an assumed shape.
