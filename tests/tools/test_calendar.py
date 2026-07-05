from __future__ import annotations

from datetime import datetime
from typing import Any

from morning_briefing_agent.models import EventSummary
from morning_briefing_agent.tools.calendar import (
    check_calendar,
    fetch_upcoming_events,
    parse_calendar_event,
)
from tests.conftest import FakeCalendarService, load_fixture


def test_parse_calendar_event_extracts_fields_with_attendees() -> None:
    raw = load_fixture("calendar_event_with_attendees.json")

    event = parse_calendar_event(raw)

    assert event == EventSummary(
        title="Sprint planning",
        start="2026-07-05T10:00:00-04:00",
        end="2026-07-05T11:00:00-04:00",
        location="Zoom",
        attendees=["alice@example.com", "bob@example.com"],
    )


def test_parse_calendar_event_handles_all_day_event_with_no_attendees() -> None:
    raw = load_fixture("calendar_event_all_day.json")

    event = parse_calendar_event(raw)

    assert event == EventSummary(
        title="Company holiday",
        start="2026-07-06",
        end="2026-07-07",
        location="",
        attendees=[],
    )


def test_fetch_upcoming_events_returns_parsed_events(patch_utcnow: datetime) -> None:
    raw = load_fixture("calendar_event_with_attendees.json")
    service = FakeCalendarService(items=[raw])

    result = fetch_upcoming_events(service, hours_ahead=24)

    assert result == [parse_calendar_event(raw)]


def test_fetch_upcoming_events_returns_empty_for_no_items(patch_utcnow: datetime) -> None:
    service = FakeCalendarService(items=[])

    assert fetch_upcoming_events(service) == []


def test_check_calendar_wires_credentials_service_and_fetch(mocker: Any) -> None:
    fake_creds = object()
    fake_service = object()
    expected = [
        EventSummary(title="t", start="s", end="e", location="l", attendees=["a"]),
    ]
    mock_get_creds = mocker.patch(
        "morning_briefing_agent.tools.calendar.get_google_credentials", return_value=fake_creds
    )
    mock_build_service = mocker.patch(
        "morning_briefing_agent.tools.calendar.build_calendar_service",
        return_value=fake_service,
    )
    mock_fetch = mocker.patch(
        "morning_briefing_agent.tools.calendar.fetch_upcoming_events", return_value=expected
    )

    result = check_calendar(hours_ahead=48)

    mock_get_creds.assert_called_once_with()
    mock_build_service.assert_called_once_with(fake_creds)
    mock_fetch.assert_called_once_with(fake_service, hours_ahead=48)
    assert result == [{"title": "t", "start": "s", "end": "e", "location": "l", "attendees": ["a"]}]
