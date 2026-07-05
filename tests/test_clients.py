from __future__ import annotations

from typing import Any

from morning_briefing_agent.clients import (
    build_calendar_service,
    build_gmail_service,
    build_slack_client,
)


def test_build_gmail_service_calls_discovery_build(mocker: Any) -> None:
    fake_credentials = mocker.Mock()
    fake_service = mocker.Mock()
    mock_build = mocker.patch("morning_briefing_agent.clients.build", return_value=fake_service)

    result = build_gmail_service(fake_credentials)

    mock_build.assert_called_once_with("gmail", "v1", credentials=fake_credentials)
    assert result is fake_service


def test_build_calendar_service_calls_discovery_build(mocker: Any) -> None:
    fake_credentials = mocker.Mock()
    fake_service = mocker.Mock()
    mock_build = mocker.patch("morning_briefing_agent.clients.build", return_value=fake_service)

    result = build_calendar_service(fake_credentials)

    mock_build.assert_called_once_with("calendar", "v3", credentials=fake_credentials)
    assert result is fake_service


def test_build_slack_client_constructs_webclient_with_token(mocker: Any) -> None:
    mock_webclient_cls = mocker.patch("morning_briefing_agent.clients.WebClient")

    result = build_slack_client("xoxp-test")

    mock_webclient_cls.assert_called_once_with(token="xoxp-test")
    assert result is mock_webclient_cls.return_value
