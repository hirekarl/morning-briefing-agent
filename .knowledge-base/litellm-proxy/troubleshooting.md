# LiteLLM Proxy — Troubleshooting

## Database connection failed

```
httpx.ConnectError: All connection attempts failed
```

**Fix:** verify PostgreSQL permissions:

```sql
GRANT ALL PRIVILEGES ON DATABASE litellm TO your_username;
```

## `prometheus.yml` mounted as a directory

```
Error: cannot create subdirectories in ".../prometheus.yml": not a directory
```

**Cause:** the file didn't exist before `docker compose up`, so Docker created it as an empty directory instead of mounting a file into it.

**Fix:**

```bash
rm -rf prometheus.yml
# recreate it as a real file (see docker-quickstart.md for contents)
docker compose up
```

## SSL certificate verification error

**Fix (development only — do not use in production):**

```yaml
litellm_settings:
  ssl_verify: false
```

## Rate limit errors (429) that seem too aggressive

Check whether the virtual key in use has a low `rpm_limit`/`tpm_limit` set — see [`virtual-keys-and-rate-limits.md`](virtual-keys-and-rate-limits.md). This is enforced per-key, so a shared team key with a low limit will 429 quickly under concurrent use.

## Model not found / wrong model called

Confirm the `model` string sent in the request matches a `model_name` alias in `config.yaml` exactly (see [`config-yaml-reference.md`](config-yaml-reference.md)) — not the underlying provider's model ID.
