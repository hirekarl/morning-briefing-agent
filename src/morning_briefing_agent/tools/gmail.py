from __future__ import annotations

from dataclasses import asdict
from datetime import timedelta
from email.utils import parsedate_to_datetime
from typing import Any, Protocol

from strands import tool

from morning_briefing_agent import time_utils
from morning_briefing_agent.clients import build_gmail_service
from morning_briefing_agent.google_auth import get_google_credentials
from morning_briefing_agent.models import EmailSummary

SNIPPET_MAX_LENGTH = 200
GMAIL_UNREAD_QUERY = "is:unread"
GMAIL_MAX_RESULTS = 50


class _Executable(Protocol):
    def execute(self) -> dict[str, Any]: ...


class _GmailMessagesProtocol(Protocol):
    def list(self, *, userId: str, q: str, maxResults: int) -> _Executable: ...
    def get(self, *, userId: str, id: str, format: str) -> _Executable: ...


class _GmailUsersProtocol(Protocol):
    def messages(self) -> _GmailMessagesProtocol: ...


class GmailServiceProtocol(Protocol):
    def users(self) -> _GmailUsersProtocol: ...


def _header_value(headers: list[dict[str, str]], name: str) -> str:
    for header in headers:
        if header.get("name", "").lower() == name.lower():
            return header.get("value", "")
    return ""


def parse_email_message(raw: dict[str, Any]) -> EmailSummary:
    headers = raw.get("payload", {}).get("headers", [])
    snippet = raw.get("snippet", "")
    return EmailSummary(
        sender=_header_value(headers, "From"),
        subject=_header_value(headers, "Subject"),
        date=_header_value(headers, "Date"),
        snippet=snippet[:SNIPPET_MAX_LENGTH],
    )


def fetch_recent_emails(service: GmailServiceProtocol, hours_back: int = 12) -> list[EmailSummary]:
    cutoff = time_utils.utcnow() - timedelta(hours=hours_back)
    list_response = (
        service.users()
        .messages()
        .list(userId="me", q=GMAIL_UNREAD_QUERY, maxResults=GMAIL_MAX_RESULTS)
        .execute()
    )
    message_ids = [item["id"] for item in list_response.get("messages", [])]

    summaries: list[EmailSummary] = []
    for message_id in message_ids:
        raw = service.users().messages().get(userId="me", id=message_id, format="full").execute()
        summary = parse_email_message(raw)
        try:
            sent_at = parsedate_to_datetime(summary.date)
        except (TypeError, ValueError):
            continue
        if sent_at >= cutoff:
            summaries.append(summary)
    return summaries


@tool
def check_gmail(hours_back: int = 12) -> list[dict[str, str]]:
    """Check for unread Gmail messages from the last `hours_back` hours.

    Returns a list of dicts with sender, subject, date, and a snippet (max 200
    characters) for each unread email received within the time window.
    """
    credentials = get_google_credentials()
    service = build_gmail_service(credentials)
    emails = fetch_recent_emails(service, hours_back=hours_back)
    return [asdict(email) for email in emails]
