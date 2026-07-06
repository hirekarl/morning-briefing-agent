from __future__ import annotations

from typing import Any

from morning_briefing_agent.agent import SYSTEM_PROMPT, build_agent, build_model
from morning_briefing_agent.config import Settings
from morning_briefing_agent.tools.calendar import check_calendar
from morning_briefing_agent.tools.gmail import check_gmail
from morning_briefing_agent.tools.slack import check_slack

SECTION_HEADERS = (
    "URGENT",
    "UPCOMING EVENTS",
    "SLACK HIGHLIGHTS",
    "OTHER EMAILS",
    "SUGGESTED ACTIONS",
)


def test_system_prompt_contains_all_five_sections_in_order() -> None:
    positions = [SYSTEM_PROMPT.index(section) for section in SECTION_HEADERS]

    assert positions == sorted(positions)


def test_system_prompt_instructs_calling_all_three_tools() -> None:
    for tool_name in ("check_gmail", "check_calendar", "check_slack"):
        assert tool_name in SYSTEM_PROMPT


def test_build_model_passes_client_args_model_id_and_params(mocker: Any) -> None:
    mock_litellm_model = mocker.patch("morning_briefing_agent.agent.LiteLLMModel")
    settings = Settings(openrouter_api_key="sk-or-test", slack_bot_token="xoxp-test")  # noqa: S106

    build_model(settings)

    mock_litellm_model.assert_called_once_with(
        client_args={
            "api_key": "sk-or-test",
            "api_base": "https://openrouter.ai/api/v1",
        },
        model_id="openrouter/openrouter/free",
        params={"max_tokens": 4096, "temperature": 0.7},
    )


def test_build_agent_passes_model_and_all_three_tools(mocker: Any) -> None:
    fake_model = object()
    mocker.patch("morning_briefing_agent.agent.build_model", return_value=fake_model)
    mock_agent_cls = mocker.patch("morning_briefing_agent.agent.Agent")
    settings = Settings(openrouter_api_key="sk-or-test", slack_bot_token="xoxp-test")  # noqa: S106

    build_agent(settings)

    _, kwargs = mock_agent_cls.call_args
    assert kwargs["model"] is fake_model
    assert kwargs["tools"] == [check_gmail, check_calendar, check_slack]
    assert kwargs["system_prompt"] == SYSTEM_PROMPT
    assert kwargs["callback_handler"] is None


def test_build_agent_loads_settings_when_none_given(mocker: Any) -> None:
    fake_settings = object()
    mock_load_settings = mocker.patch(
        "morning_briefing_agent.agent.load_settings", return_value=fake_settings
    )
    mock_build_model = mocker.patch("morning_briefing_agent.agent.build_model")
    mocker.patch("morning_briefing_agent.agent.Agent")

    build_agent()

    mock_load_settings.assert_called_once_with()
    mock_build_model.assert_called_once_with(fake_settings)
