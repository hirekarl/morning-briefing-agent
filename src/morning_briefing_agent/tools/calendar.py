from __future__ import annotations

from dataclasses import asdict
from datetime import timedelta
from typing import Any, Protocol

from strands import tool

from morning_briefing_agent import time_utils
from morning_briefing_agent.clients import build_calendar_service
from morning_briefing_agent.config import load_settings
from morning_briefing_agent.google_auth import get_google_credentials
from morning_briefing_agent.models import EventSummary

CALENDAR_ID = "primary"


class _Executable(Protocol):
    def execute(self) -> dict[str, Any]: ...


class CalendarServiceProtocol(Protocol):
    def events(self) -> _CalendarEventsProtocol: ...


class _CalendarEventsProtocol(Protocol):
    def list(
        self,
        *,
        calendarId: str,
        timeMin: str,
        timeMax: str,
        singleEvents: bool,
        orderBy: str,
    ) -> _Executable: ...


def _extract_time(time_block: dict[str, str]) -> str:
    return time_block.get("dateTime") or time_block.get("date") or ""


def _is_relevant_event(raw: dict[str, Any]) -> bool:
    if raw.get("status") == "cancelled":
        return False
    return not any(
        attendee.get("self") and attendee.get("responseStatus") == "declined"
        for attendee in raw.get("attendees", [])
    )


def parse_calendar_event(raw: dict[str, Any]) -> EventSummary:
    return EventSummary(
        title=raw.get("summary", ""),
        start=_extract_time(raw.get("start", {})),
        end=_extract_time(raw.get("end", {})),
        location=raw.get("location", ""),
        attendees=[attendee["email"] for attendee in raw.get("attendees", [])],
    )


def fetch_upcoming_events(
    service: CalendarServiceProtocol, hours_ahead: int = 24
) -> list[EventSummary]:
    now = time_utils.utcnow()
    time_min = now.isoformat()
    time_max = (now + timedelta(hours=hours_ahead)).isoformat()
    response = (
        service.events()
        .list(
            calendarId=CALENDAR_ID,
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    return [
        parse_calendar_event(item) for item in response.get("items", []) if _is_relevant_event(item)
    ]


@tool
def check_calendar(hours_ahead: int | None = None) -> list[dict[str, Any]]:
    """Check for upcoming Google Calendar events in the next `hours_ahead` hours.

    Defaults to the configured `CALENDAR_HOURS_AHEAD` setting when not given.
    Returns a list of dicts with title, start, end, location, and attendees
    for each event starting within the time window.
    """
    if hours_ahead is None:
        hours_ahead = load_settings().calendar_hours_ahead
    credentials = get_google_credentials()
    service = build_calendar_service(credentials)
    events = fetch_upcoming_events(service, hours_ahead=hours_ahead)
    return [asdict(event) for event in events]
