from __future__ import annotations

from strands import Agent
from strands.models.litellm import LiteLLMModel

from morning_briefing_agent.config import Settings, load_settings
from morning_briefing_agent.tools.calendar import check_calendar
from morning_briefing_agent.tools.gmail import check_gmail
from morning_briefing_agent.tools.slack import check_slack

SYSTEM_PROMPT = """\
You are a personal morning briefing assistant. Always call check_gmail, \
check_calendar, and check_slack, in that order, before responding. Then \
synthesize a single briefing with exactly these sections, in this order:

URGENT
UPCOMING EVENTS
SLACK HIGHLIGHTS
OTHER EMAILS
SUGGESTED ACTIONS
"""


def build_model(settings: Settings) -> LiteLLMModel:
    return LiteLLMModel(
        client_args={
            "api_key": settings.openrouter_api_key,
            "api_base": settings.openrouter_api_base,
        },
        model_id=settings.model_id,
        params={
            "max_tokens": settings.max_tokens,
            "temperature": settings.temperature,
        },
    )


def build_agent(settings: Settings | None = None) -> Agent:
    resolved_settings = settings or load_settings()
    return Agent(
        model=build_model(resolved_settings),
        tools=[check_gmail, check_calendar, check_slack],
        system_prompt=SYSTEM_PROMPT,
    )
