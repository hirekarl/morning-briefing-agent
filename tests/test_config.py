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
