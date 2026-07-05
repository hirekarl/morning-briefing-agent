# Strands Agents — Model Provider: Amazon Bedrock (default)

Kept here for contrast — this project uses LiteLLM (see [`litellm.md`](litellm.md)), not Bedrock, but the framework defaults to Bedrock if no `model=` is passed.

## Credentials

Configure AWS credentials via one of:
- Environment variables: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`
- AWS credentials file (`aws configure`)
- IAM roles (EC2, ECS, Lambda)
- Bedrock API key: `AWS_BEARER_TOKEN_BEDROCK`

## Explicit configuration

```python
from strands.models import BedrockModel

bedrock_model = BedrockModel(
    model_id="anthropic.claude-sonnet-4-20250514-v1:0",
    region_name="us-west-2",
    temperature=0.3,
)
agent = Agent(model=bedrock_model)
```

## Gotcha

- **Model access must be explicitly enabled in the AWS Bedrock console** before a model ID is usable — a valid IAM credential alone isn't sufficient. This is the most common reason the quickstart example fails "out of the box" for a new AWS account.
