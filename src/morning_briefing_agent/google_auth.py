from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

GOOGLE_SCOPES = (
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.readonly",
)

DEFAULT_TOKEN_PATH = Path("token.json")
DEFAULT_CREDENTIALS_PATH = Path("credentials.json")


def _load_cached_token(token_path: Path, scopes: Sequence[str]) -> Credentials | None:
    if not token_path.exists():
        return None
    credentials: Credentials = Credentials.from_authorized_user_file(str(token_path), list(scopes))
    return credentials


def _refresh(credentials: Credentials) -> Credentials:
    credentials.refresh(Request())
    return credentials


def _run_oauth_flow(credentials_path: Path, scopes: Sequence[str]) -> Credentials:
    flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), list(scopes))
    credentials: Credentials = flow.run_local_server(port=0)
    return credentials


def get_google_credentials(
    token_path: Path = DEFAULT_TOKEN_PATH,
    credentials_path: Path = DEFAULT_CREDENTIALS_PATH,
    scopes: Sequence[str] = GOOGLE_SCOPES,
) -> Credentials:
    """Load cached OAuth credentials, refreshing or re-authenticating as needed.

    Reads `token_path` if present. If the cached token is still valid, returns
    it as-is. If it is expired but has a refresh token, refreshes it. Otherwise
    runs the interactive OAuth flow via `credentials_path`. Any newly obtained
    or refreshed credentials are written back to `token_path`.
    """
    credentials = _load_cached_token(token_path, scopes)

    if credentials and credentials.valid:
        return credentials

    if credentials and credentials.expired and credentials.refresh_token:
        credentials = _refresh(credentials)
    else:
        credentials = _run_oauth_flow(credentials_path, scopes)

    token_path.write_text(credentials.to_json())
    return credentials
