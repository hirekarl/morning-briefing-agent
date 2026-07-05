from __future__ import annotations

from typing import Any

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from slack_sdk import WebClient

GMAIL_SERVICE_NAME = "gmail"
GMAIL_API_VERSION = "v1"
CALENDAR_SERVICE_NAME = "calendar"
CALENDAR_API_VERSION = "v3"


def build_gmail_service(credentials: Credentials) -> Any:
    return build(GMAIL_SERVICE_NAME, GMAIL_API_VERSION, credentials=credentials)


def build_calendar_service(credentials: Credentials) -> Any:
    return build(CALENDAR_SERVICE_NAME, CALENDAR_API_VERSION, credentials=credentials)


def build_slack_client(token: str) -> WebClient:
    return WebClient(token=token)
