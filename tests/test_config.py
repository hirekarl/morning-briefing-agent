from __future__ import annotations

import pytest

from morning_briefing_agent.config import MissingConfigError, Settings, load_settings


def test_load_settings_raises_when_required_vars_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("SLACK_BOT_TOKEN", raising=False)
    monkeypatch.setattr("morning_briefing_agent.config.load_dotenv", lambda: None)

    with pytest.raises(MissingConfigError, match="OPENROUTER_API_KEY"):
        load_settings()


def test_load_settings_returns_settings_with_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-test")
    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxp-test")  # noqa: S105
    monkeypatch.setattr("morning_briefing_agent.config.load_dotenv", lambda: None)

    settings = load_settings()

    assert settings == Settings(
        openrouter_api_key="sk-or-test",
        slack_bot_token="xoxp-test",
    )
    assert settings.model_id == "openrouter/openrouter/free"
    assert settings.max_tokens == 4096


def test_load_settings_reads_optional_overrides_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-test")
    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxp-test")  # noqa: S105
    monkeypatch.setenv("MODEL_ID", "openrouter/openai/gpt-oss-120b:free")
    monkeypatch.setenv("OPENROUTER_API_BASE", "https://example.com/api/v1")
    monkeypatch.setenv("MAX_TOKENS", "2048")
    monkeypatch.setenv("TEMPERATURE", "0.2")
    monkeypatch.setenv("GMAIL_HOURS_BACK", "6")
    monkeypatch.setenv("CALENDAR_HOURS_AHEAD", "48")
    monkeypatch.setenv("SLACK_HOURS_BACK", "3")
    monkeypatch.setenv("SLACK_MAX_CHANNELS", "10")
    monkeypatch.setattr("morning_briefing_agent.config.load_dotenv", lambda: None)

    settings = load_settings()

    assert settings.model_id == "openrouter/openai/gpt-oss-120b:free"
    assert settings.openrouter_api_base == "https://example.com/api/v1"
    assert settings.max_tokens == 2048
    assert settings.temperature == 0.2
    assert settings.gmail_hours_back == 6
    assert settings.calendar_hours_ahead == 48
    assert settings.slack_hours_back == 3
    assert settings.slack_max_channels == 10
