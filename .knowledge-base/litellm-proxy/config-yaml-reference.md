# LiteLLM Proxy — `config.yaml` Reference

## Top-level sections

| Section | Purpose |
|---|---|
| `model_list` | Available models and their deployment configs |
| `router_settings` | Routing behavior, load balancing, retries/timeouts |
| `litellm_settings` | Module-level LiteLLM config (fallbacks, verbosity, logging) |
| `general_settings` | Server/database/admin-auth config |
| `environment_variables` | Optional: external env config block |
| `credential_list` | Reusable named credentials, referenced from `model_list` |

## `model_list`

```yaml
model_list:
  - model_name: gpt-4o                    # client-facing alias
    litellm_params:                       # passed to litellm.completion()
      model: azure/gpt-4o-eu              # <provider>/<model-id>
      api_base: https://my-endpoint.openai.azure.com/
      api_key: "os.environ/AZURE_API_KEY" # env var reference syntax
      api_version: "2023-05-15"
      temperature: 0.2
      max_tokens: 20
      rpm: 6                              # requests/minute limit
      tpm: 1000                           # tokens/minute limit
    model_info:
      supported_environments: ["production", "staging"]
```

**Env var syntax:** `"os.environ/<VAR_NAME>"` executes `os.getenv("VAR_NAME")` — this only works inside `config.yaml`, not in Python `client_args` (see [`../strands-agents/model-providers/litellm.md`](../strands-agents/model-providers/litellm.md)).

### Provider examples

```yaml
model_list:
  # Azure
  - model_name: gpt-4
    litellm_params:
      model: azure/gpt-4-deployment
      api_base: https://my-azure.openai.azure.com

  # OpenAI
  - model_name: gpt-4
    litellm_params:
      model: openai/gpt-4
      api_key: os.environ/OPENAI_API_KEY

  # Custom OpenAI-compatible (vLLM, Ollama, OpenRouter)
  - model_name: my-llama
    litellm_params:
      model: openai/meta/llama-3-8b
      api_base: http://my-vllm-server:8000/v1
      api_key: "optional-key"

  # Bedrock
  - model_name: claude-3
    litellm_params:
      model: bedrock/anthropic.claude-3-sonnet-20240229-v1:0
      aws_region_name: us-east-1
```

For routing to OpenRouter specifically, see [`../integration-patterns.md`](../integration-patterns.md).

### Wildcard/default model

```yaml
model_list:
  - model_name: "*"
    litellm_params:
      model: "*"
```
Allows requests to any model without an explicit entry, provided credentials exist in the environment.

### Load balancing (same `model_name`, multiple deployments)

```yaml
model_list:
  - model_name: zephyr-beta
    litellm_params:
      model: huggingface/HuggingFaceH4/zephyr-7b-beta
      api_base: http://0.0.0.0:8001
      rpm: 60
  - model_name: zephyr-beta
    litellm_params:
      model: huggingface/HuggingFaceH4/zephyr-7b-beta
      api_base: http://0.0.0.0:8002
      rpm: 600

router_settings:
  routing_strategy: "simple-shuffle"
  redis_host: <redis-host>
```
Weighted picks are based on established tpm/rpm across the deployments sharing a `model_name`.

## `router_settings`

```yaml
router_settings:
  routing_strategy: "simple-shuffle"      # simple-shuffle | least-busy | usage-based-routing | latency-based-routing
  num_retries: 2
  timeout: 30                             # seconds
  model_group_alias:
    gpt-4: "gpt-4o"                       # route requests to alias target
  redis_host: <redis-host>                # for multi-instance deployments
  redis_password: <password>
  redis_port: 1992
```

## `litellm_settings`

```yaml
litellm_settings:
  drop_params: true                       # remove unsupported params before sending upstream
  set_verbose: true
  num_retries: 3                          # retries per model
  request_timeout: 10                     # seconds
  fallbacks:
    - zephyr-beta: ["gpt-4o"]             # primary → fallback model
  context_window_fallbacks:
    - zephyr-beta: ["gpt-3.5-turbo-16k"]  # use fallback if context window exceeded
  allowed_fails: 3                        # cool down after N failures per minute
  success_callback: ["langfuse"]          # requires provider-specific env keys
  ssl_verify: false                       # dev-only: bypass TLS verification
```

## `general_settings`

```yaml
general_settings:
  master_key: "sk-1234"                   # authorizes all requests; must start with sk-
  alerting: ["slack"]                     # requires SLACK_WEBHOOK_URL env var
  database_url: "postgresql://user:password@host:5432/litellm"
  database_connection_pool_limit: 10      # per worker process
  database_connection_timeout: 60
  database_socket_timeout: 300            # close idle connections after 5 min
  database_connect_timeout: 15
  database_disable_prepared_statements: true  # needed with PgBouncer
  database_extra_connection_params:
    pgbouncer: "true"
    sslmode: "require"
    statement_cache_size: 0
```

Pool sizing: `pool_limit = MAX_DB_CONNECTIONS ÷ (instances × workers_per_instance)`. E.g. 100 max connections, 1 instance, 8 workers → 100 ÷ 8 = 12.5 → set to **10**.

## `credential_list` (centralized credential reuse)

```yaml
credential_list:
  - credential_name: default_azure_credential
    credential_values:
      api_key: os.environ/AZURE_API_KEY
      api_base: os.environ/AZURE_API_BASE
      api_version: "2023-05-15"
    credential_info:
      description: "Production credentials for EU region"
      custom_llm_provider: "azure"

model_list:
  - model_name: gpt-4o
    litellm_params:
      model: azure/gpt-4o
      litellm_credential_name: default_azure_credential
```

## Gotchas

- **Env var syntax is exact**: `os.environ/VAR_NAME` — no other form works.
- **`rpm`/`tpm` limits interact with `routing_strategy: simple-shuffle`** to do weighted load balancing, not hard caps alone.
- **Fallbacks only trigger after retries are exhausted**, not on the first failure.
- **Database pool limits are per worker**, not per instance — multiply by worker count for the real total.
- **PgBouncer users must set `database_disable_prepared_statements: true`** to avoid cached-plan errors under transaction pooling mode.
- **`master_key` must start with `sk-`.**
