from __future__ import annotations

from dataclasses import asdict
from datetime import timedelta
from typing import Any, Protocol

from strands import tool

from morning_briefing_agent import time_utils
from morning_briefing_agent.clients import build_slack_client
from morning_briefing_agent.config import load_settings
from morning_briefing_agent.models import ChannelDigest

MAX_MESSAGES_PER_CHANNEL = 5
CHANNEL_TYPES = "public_channel,private_channel"


class _SlackResponseLike(Protocol):
    """Matches slack_sdk's SlackResponse structurally without depending on it."""

    def get(self, key: str, default: Any = ...) -> Any: ...


class SlackClientProtocol(Protocol):
    def conversations_list(self, **kwargs: Any) -> _SlackResponseLike: ...
    def conversations_history(self, *, channel: str, **kwargs: Any) -> _SlackResponseLike: ...


def parse_channel_messages(channel_name: str, messages: list[dict[str, Any]]) -> ChannelDigest:
    texts = [message.get("text", "") for message in messages[:MAX_MESSAGES_PER_CHANNEL]]
    return ChannelDigest(channel=channel_name, messages=texts)


def fetch_recent_channel_activity(
    client: SlackClientProtocol, hours_back: int = 12, max_channels: int = 5
) -> list[ChannelDigest]:
    cutoff_ts = (time_utils.utcnow() - timedelta(hours=hours_back)).timestamp()
    channels = client.conversations_list(types=CHANNEL_TYPES, exclude_archived=True).get(
        "channels", []
    )

    active: list[tuple[float, ChannelDigest]] = []
    for channel in channels:
        history = client.conversations_history(
            channel=channel["id"], oldest=str(cutoff_ts), limit=MAX_MESSAGES_PER_CHANNEL
        ).get("messages", [])
        if not history:
            continue
        latest_ts = float(history[0].get("ts", 0))
        active.append((latest_ts, parse_channel_messages(channel["name"], history)))

    active.sort(key=lambda entry: entry[0], reverse=True)
    return [digest for _, digest in active[:max_channels]]


@tool
def check_slack(hours_back: int = 12, max_channels: int = 5) -> list[dict[str, Any]]:
    """Check recent Slack activity in the `max_channels` most recently active channels.

    Returns a list of dicts with channel name and up to 5 recent messages per
    channel, for channels with activity in the last `hours_back` hours.
    """
    settings = load_settings()
    client = build_slack_client(settings.slack_bot_token)
    digests = fetch_recent_channel_activity(
        client, hours_back=hours_back, max_channels=max_channels
    )
    return [asdict(digest) for digest in digests]
