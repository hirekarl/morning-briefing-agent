from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Pinning to a single named free model was tried (openai/gpt-oss-120b, gpt-oss-20b, then
# meta-llama/llama-3.3-70b-instruct) to avoid the auto-router landing on a model without tool
# calling support. In practice every pinned model hit its own reliability problem instead: the
# gpt-oss-* models are reasoning models whose chain-of-thought content breaks multi-turn tool
# calling over the Chat Completions API (observed live: empty final responses), and both
# gpt-oss-120b and llama-3.3-70b-instruct hit persistent upstream 429s from their specific
# backend. The auto-router succeeded immediately and cleanly in the same live test by trying
# whichever backend currently has capacity. Override via MODEL_ID in .env if you want to pin
# to a specific model anyway (e.g. once a particular free model's availability stabilizes).
DEFAULT_MODEL_ID = "openrouter/openrouter/free"
DEFAULT_OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"
DEFAULT_MAX_TOKENS = 4096
DEFAULT_TEMPERATURE = 0.7
DEFAULT_GMAIL_HOURS_BACK = 12
DEFAULT_CALENDAR_HOURS_AHEAD = 24
DEFAULT_SLACK_HOURS_BACK = 12
DEFAULT_SLACK_MAX_CHANNELS = 5

REQUIRED_ENV_VARS = ("OPENROUTER_API_KEY", "SLACK_BOT_TOKEN")


class MissingConfigError(OSError):
    """Raised when a required environment variable is not set."""


@dataclass(frozen=True, slots=True)
class Settings:
    openrouter_api_key: str
    slack_bot_token: str
    model_id: str = DEFAULT_MODEL_ID
    openrouter_api_base: str = DEFAULT_OPENROUTER_API_BASE
    max_tokens: int = DEFAULT_MAX_TOKENS
    temperature: float = DEFAULT_TEMPERATURE
    gmail_hours_back: int = DEFAULT_GMAIL_HOURS_BACK
    calendar_hours_ahead: int = DEFAULT_CALENDAR_HOURS_AHEAD
    slack_hours_back: int = DEFAULT_SLACK_HOURS_BACK
    slack_max_channels: int = DEFAULT_SLACK_MAX_CHANNELS


def load_settings() -> Settings:
    load_dotenv()
    missing = [name for name in REQUIRED_ENV_VARS if not os.getenv(name)]
    if missing:
        raise MissingConfigError(f"Missing required environment variable(s): {', '.join(missing)}")
    return Settings(
        openrouter_api_key=os.environ["OPENROUTER_API_KEY"],
        slack_bot_token=os.environ["SLACK_BOT_TOKEN"],
        model_id=os.getenv("MODEL_ID", DEFAULT_MODEL_ID),
        openrouter_api_base=os.getenv("OPENROUTER_API_BASE", DEFAULT_OPENROUTER_API_BASE),
        max_tokens=int(os.getenv("MAX_TOKENS", DEFAULT_MAX_TOKENS)),
        temperature=float(os.getenv("TEMPERATURE", DEFAULT_TEMPERATURE)),
        gmail_hours_back=int(os.getenv("GMAIL_HOURS_BACK", DEFAULT_GMAIL_HOURS_BACK)),
        calendar_hours_ahead=int(os.getenv("CALENDAR_HOURS_AHEAD", DEFAULT_CALENDAR_HOURS_AHEAD)),
        slack_hours_back=int(os.getenv("SLACK_HOURS_BACK", DEFAULT_SLACK_HOURS_BACK)),
        slack_max_channels=int(os.getenv("SLACK_MAX_CHANNELS", DEFAULT_SLACK_MAX_CHANNELS)),
    )
