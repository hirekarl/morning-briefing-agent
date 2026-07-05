from __future__ import annotations

from datetime import datetime

from morning_briefing_agent.models import EmailSummary
from morning_briefing_agent.tools.gmail import (
    SNIPPET_MAX_LENGTH,
    check_gmail,
    fetch_recent_emails,
    parse_email_message,
)
from tests.conftest import FakeGmailService, load_fixture


def test_parse_email_message_extracts_headers_and_snippet() -> None:
    raw = load_fixture("gmail_message_unread.json")

    summary = parse_email_message(raw)

    assert summary == EmailSummary(
        sender="Alice Smith <alice@example.com>",
        subject="Action required: deadline approaching",
        date="Sun, 05 Jul 2026 08:15:00 -0400",
        snippet=raw["snippet"],
    )


def test_parse_email_message_truncates_snippet_to_200_chars() -> None:
    raw = load_fixture("gmail_message_long_body.json")
    assert len(raw["snippet"]) > SNIPPET_MAX_LENGTH

    summary = parse_email_message(raw)

    assert len(summary.snippet) == SNIPPET_MAX_LENGTH
    assert summary.snippet == raw["snippet"][:SNIPPET_MAX_LENGTH]


def test_fetch_recent_emails_filters_by_window(patch_utcnow: datetime) -> None:
    recent = load_fixture("gmail_message_unread.json")  # 2026-07-05 08:15 -0400 -> within 12h
    stale = load_fixture("gmail_message_long_body.json")  # 2026-07-05 07:00 -0400 -> still within
    stale = {**stale, "id": "stale-id"}
    stale["payload"] = {
        "headers": [
            {"name": "From", "value": "Old <old@example.com>"},
            {"name": "Subject", "value": "Old news"},
            {"name": "Date", "value": "Fri, 03 Jul 2026 08:00:00 -0400"},
        ]
    }
    service = FakeGmailService(
        message_ids=[recent["id"], stale["id"]],
        messages_by_id={recent["id"]: recent, stale["id"]: stale},
    )

    result = fetch_recent_emails(service, hours_back=12)

    assert len(result) == 1
    assert result[0].subject == "Action required: deadline approaching"


def test_fetch_recent_emails_returns_empty_for_no_messages(patch_utcnow: datetime) -> None:
    service = FakeGmailService(message_ids=[], messages_by_id={})

    assert fetch_recent_emails(service) == []


def test_check_gmail_wires_credentials_service_and_fetch(mocker) -> None:  # type: ignore[no-untyped-def]
    fake_creds = object()
    fake_service = object()
    expected = [
        EmailSummary(sender="a", subject="b", date="c", snippet="d"),
    ]
    mock_get_creds = mocker.patch(
        "morning_briefing_agent.tools.gmail.get_google_credentials", return_value=fake_creds
    )
    mock_build_service = mocker.patch(
        "morning_briefing_agent.tools.gmail.build_gmail_service", return_value=fake_service
    )
    mock_fetch = mocker.patch(
        "morning_briefing_agent.tools.gmail.fetch_recent_emails", return_value=expected
    )

    result = check_gmail(hours_back=24)

    mock_get_creds.assert_called_once_with()
    mock_build_service.assert_called_once_with(fake_creds)
    mock_fetch.assert_called_once_with(fake_service, hours_back=24)
    assert result == [{"sender": "a", "subject": "b", "date": "c", "snippet": "d"}]
