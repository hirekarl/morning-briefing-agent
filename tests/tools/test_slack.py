from __future__ import annotations

from datetime import datetime
from typing import Any

from morning_briefing_agent.models import ChannelDigest, SlackMessage
from morning_briefing_agent.tools.slack import (
    check_slack,
    fetch_recent_channel_activity,
    parse_channel_messages,
)
from tests.conftest import FakeSlackClient, load_fixture


def test_parse_channel_messages_takes_up_to_five_messages() -> None:
    history = load_fixture("slack_conversation_history.json")

    digest = parse_channel_messages("general", history["messages"])

    assert digest == ChannelDigest(
        channel="general",
        messages=[
            SlackMessage(sender="U1", text="Deploy is done"),
            SlackMessage(sender="U2", text="Thanks, looks good!"),
        ],
    )


def test_parse_channel_messages_caps_at_five() -> None:
    messages = [{"user": f"U{i}", "text": f"msg {i}", "ts": str(i)} for i in range(8)]

    digest = parse_channel_messages("general", messages)

    assert len(digest.messages) == 5
    assert digest.messages == [SlackMessage(sender=f"U{i}", text=f"msg {i}") for i in range(5)]


def test_fetch_recent_channel_activity_returns_active_channels_only(
    patch_utcnow: datetime,
) -> None:
    channels = load_fixture("slack_channel_list.json")["channels"]
    history = load_fixture("slack_conversation_history.json")["messages"]
    client = FakeSlackClient(
        channels=channels,
        histories={"C001": history, "C002": [], "C003": []},
    )

    result = fetch_recent_channel_activity(client, hours_back=12, max_channels=5)

    assert result == [
        ChannelDigest(
            channel="general",
            messages=[
                SlackMessage(sender="U1", text="Deploy is done"),
                SlackMessage(sender="U2", text="Thanks, looks good!"),
            ],
        )
    ]


def test_fetch_recent_channel_activity_respects_max_channels(patch_utcnow: datetime) -> None:
    channels = load_fixture("slack_channel_list.json")["channels"]
    history = load_fixture("slack_conversation_history.json")["messages"]
    client = FakeSlackClient(
        channels=channels,
        histories={"C001": history, "C002": history, "C003": history},
    )

    result = fetch_recent_channel_activity(client, hours_back=12, max_channels=2)

    assert len(result) == 2


def test_check_slack_wires_client_and_fetch(mocker: Any) -> None:
    fake_client = object()
    expected = [ChannelDigest(channel="general", messages=[SlackMessage(sender="U1", text="hi")])]
    mock_build_client = mocker.patch(
        "morning_briefing_agent.tools.slack.build_slack_client", return_value=fake_client
    )
    mock_load_settings = mocker.patch(
        "morning_briefing_agent.tools.slack.load_settings",
        return_value=mocker.Mock(slack_bot_token="xoxp-test"),  # noqa: S106
    )
    mock_fetch = mocker.patch(
        "morning_briefing_agent.tools.slack.fetch_recent_channel_activity",
        return_value=expected,
    )

    result = check_slack(hours_back=6, max_channels=3)

    mock_load_settings.assert_called_once_with()
    mock_build_client.assert_called_once_with("xoxp-test")
    mock_fetch.assert_called_once_with(fake_client, hours_back=6, max_channels=3)
    assert result == [{"channel": "general", "messages": [{"sender": "U1", "text": "hi"}]}]


def test_check_slack_defaults_hours_back_and_max_channels_from_settings(mocker: Any) -> None:
    mocker.patch("morning_briefing_agent.tools.slack.build_slack_client")
    mock_fetch = mocker.patch(
        "morning_briefing_agent.tools.slack.fetch_recent_channel_activity", return_value=[]
    )
    mocker.patch(
        "morning_briefing_agent.tools.slack.load_settings",
        return_value=mocker.Mock(
            slack_bot_token="xoxp-test",  # noqa: S106
            slack_hours_back=6,
            slack_max_channels=2,
        ),
    )

    check_slack()

    mock_fetch.assert_called_once_with(mocker.ANY, hours_back=6, max_channels=2)
