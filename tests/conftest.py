from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> dict[str, Any]:
    return json.loads((FIXTURES_DIR / name).read_text())


@pytest.fixture
def frozen_now() -> datetime:
    return datetime(2026, 7, 5, 12, 0, 0, tzinfo=UTC)


@pytest.fixture
def patch_utcnow(monkeypatch: pytest.MonkeyPatch, frozen_now: datetime) -> datetime:
    from morning_briefing_agent import time_utils

    monkeypatch.setattr(time_utils, "utcnow", lambda: frozen_now)
    return frozen_now


class _Executable:
    def __init__(self, payload: dict[str, Any]) -> None:
        self._payload = payload

    def execute(self) -> dict[str, Any]:
        return self._payload


class FakeGmailService:
    """Implements only the .users().messages().list()/.get() chain check_gmail uses."""

    def __init__(self, message_ids: list[str], messages_by_id: dict[str, dict[str, Any]]) -> None:
        self._message_ids = message_ids
        self._messages_by_id = messages_by_id

    def users(self) -> FakeGmailService:
        return self

    def messages(self) -> FakeGmailService:
        return self

    def list(self, **_: Any) -> _Executable:
        return _Executable({"messages": [{"id": mid} for mid in self._message_ids]})

    def get(self, *, id: str, **_: Any) -> _Executable:
        return _Executable(self._messages_by_id[id])


class FakeCalendarService:
    """Implements only the .events().list() chain check_calendar uses."""

    def __init__(self, items: list[dict[str, Any]]) -> None:
        self._items = items

    def events(self) -> FakeCalendarService:
        return self

    def list(self, **_: Any) -> _Executable:
        return _Executable({"items": self._items})


class FakeSlackClient:
    """Implements only the conversations_list/conversations_history calls check_slack uses."""

    def __init__(
        self, channels: list[dict[str, Any]], histories: dict[str, list[dict[str, Any]]]
    ) -> None:
        self._channels = channels
        self._histories = histories

    def conversations_list(self, **_: Any) -> dict[str, Any]:
        return {"ok": True, "channels": self._channels}

    def conversations_history(self, *, channel: str, **_: Any) -> dict[str, Any]:
        return {"ok": True, "messages": self._histories.get(channel, [])}


@pytest.fixture
def fake_credentials() -> Any:
    from google.oauth2.credentials import Credentials

    return Credentials(token="fake-token")  # noqa: S106
