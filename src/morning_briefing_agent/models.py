"""Data shapes returned by each tool's parsing/orchestration layer."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EmailSummary:
    sender: str
    subject: str
    date: str
    snippet: str


@dataclass(frozen=True, slots=True)
class EventSummary:
    title: str
    start: str
    end: str
    location: str
    attendees: list[str]


@dataclass(frozen=True, slots=True)
class SlackMessage:
    sender: str
    text: str


@dataclass(frozen=True, slots=True)
class ChannelDigest:
    channel: str
    messages: list[SlackMessage]
