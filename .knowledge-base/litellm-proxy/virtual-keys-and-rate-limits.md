# LiteLLM Proxy — Virtual Keys & Rate Limits

Use virtual keys instead of handing out the `master_key` to every teammate/service — each virtual key can carry its own rate limits.

## Generate a key with an RPM limit

```bash
curl -L -X POST 'http://0.0.0.0:4000/key/generate' \
  -H 'Authorization: Bearer sk-1234' \
  -H 'Content-Type: application/json' \
  -d '{
    "rpm_limit": 1
  }'
```

Response:
```json
{"key": "sk-12..."}
```

## What happens when the limit is hit

First request within the window succeeds; a second request within the same minute returns HTTP 429:

```json
{
  "error": {
    "message": "LiteLLM Rate Limit Handler... Crossed TPM/RPM limit",
    "code": "429"
  }
}
```

## Why this matters for a team project

If the whole team shares one upstream OpenRouter key behind the proxy, generate one virtual key per teammate/service with its own `rpm_limit`/`tpm_limit` — this isolates a runaway script or bug in one person's code from starving everyone else's rate limit budget. See [`../integration-patterns.md`](../integration-patterns.md).

## Gotcha

- `rpm_limit` is enforced **per virtual key**, not per model or globally — plan limits accordingly if multiple keys hit the same underlying model deployment.
