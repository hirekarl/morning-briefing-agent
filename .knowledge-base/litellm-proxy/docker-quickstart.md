# LiteLLM Proxy — Docker Quickstart

## Fastest: interactive setup wizard (local/beginners, no Docker)

```bash
curl -fsSL https://raw.githubusercontent.com/BerriAI/litellm/main/scripts/install.sh | sh
litellm --setup
```

Walks through provider selection, API key entry, port/master key configuration, and auto-generates `litellm_config.yaml`.

## Docker: single container

```bash
docker run \
  -v $(pwd)/litellm_config.yaml:/app/config.yaml \
  -e AZURE_API_KEY=your_key \
  -e AZURE_API_BASE=https://your-deployment/ \
  -p 4000:4000 \
  docker.litellm.ai/berriai/litellm:latest \
  --config /app/config.yaml --detailed_debug
```

Swap the `-e` env vars and `config.yaml` model entries for whichever provider you're targeting (e.g. `OPENROUTER_API_KEY` — see [`../integration-patterns.md`](../integration-patterns.md)).

## Docker Compose (recommended for a team/production setup)

```bash
curl -O https://raw.githubusercontent.com/BerriAI/litellm/main/docker-compose.yml
echo 'LITELLM_MASTER_KEY="sk-1234"' > .env
echo 'LITELLM_SALT_KEY="sk-random-value"' >> .env
docker compose up
```

Fuller `.env` example:

```bash
LITELLM_MASTER_KEY="sk-1234"
LITELLM_SALT_KEY="generate-strong-random-value"
AZURE_API_BASE="https://openai-deployment/"
AZURE_API_KEY="your-azure-api-key"
DATABASE_URL="postgresql://llmproxy:dbpassword9090@db:5432/litellm"
```

The bundled `docker-compose.yml` expects a `prometheus.yml` file to exist alongside it:

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: "litellm"
    static_configs:
      - targets: ["litellm:4000"]
```

## Verify it's running

```bash
curl -X POST 'http://0.0.0.0:4000/chat/completions' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer sk-1234' \
  -d '{
    "model": "gpt-4o",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

## Gotcha — the one that will bite you

`prometheus.yml` **must exist as a real file before running `docker compose up`.** If it's missing, Docker Compose creates it as an **empty directory** instead of mounting a file, and the container fails to start. See [`troubleshooting.md`](troubleshooting.md) for the fix if this already happened to you.
