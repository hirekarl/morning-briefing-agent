from __future__ import annotations

from pathlib import Path
from typing import Any

from morning_briefing_agent.google_auth import GOOGLE_SCOPES, get_google_credentials


def test_get_google_credentials_loads_valid_cached_token(tmp_path: Path, mocker: Any) -> None:
    token_path = tmp_path / "token.json"
    token_path.write_text("{}")
    fake_credentials = mocker.Mock(valid=True, expired=False, refresh_token=None)
    mock_from_file = mocker.patch(
        "morning_briefing_agent.google_auth.Credentials.from_authorized_user_file",
        return_value=fake_credentials,
    )
    mock_flow = mocker.patch("morning_briefing_agent.google_auth.InstalledAppFlow")

    result = get_google_credentials(
        token_path=token_path, credentials_path=tmp_path / "credentials.json"
    )

    assert result is fake_credentials
    mock_from_file.assert_called_once_with(str(token_path), list(GOOGLE_SCOPES))
    mock_flow.from_client_secrets_file.assert_not_called()


def test_get_google_credentials_refreshes_expired_token(tmp_path: Path, mocker: Any) -> None:
    token_path = tmp_path / "token.json"
    token_path.write_text("{}")
    fake_credentials = mocker.Mock(valid=False, expired=True, refresh_token="r")
    fake_credentials.to_json.return_value = '{"refreshed": true}'
    mocker.patch(
        "morning_briefing_agent.google_auth.Credentials.from_authorized_user_file",
        return_value=fake_credentials,
    )
    mock_flow = mocker.patch("morning_briefing_agent.google_auth.InstalledAppFlow")

    result = get_google_credentials(
        token_path=token_path, credentials_path=tmp_path / "credentials.json"
    )

    fake_credentials.refresh.assert_called_once()
    mock_flow.from_client_secrets_file.assert_not_called()
    assert token_path.read_text() == '{"refreshed": true}'
    assert result is fake_credentials


def test_get_google_credentials_runs_oauth_flow_when_no_token(tmp_path: Path, mocker: Any) -> None:
    token_path = tmp_path / "token.json"
    credentials_path = tmp_path / "credentials.json"
    fake_credentials = mocker.Mock()
    fake_credentials.to_json.return_value = '{"new": true}'
    mock_flow_instance = mocker.Mock()
    mock_flow_instance.run_local_server.return_value = fake_credentials
    mock_flow_cls = mocker.patch("morning_briefing_agent.google_auth.InstalledAppFlow")
    mock_flow_cls.from_client_secrets_file.return_value = mock_flow_instance

    result = get_google_credentials(token_path=token_path, credentials_path=credentials_path)

    assert result is fake_credentials
    mock_flow_cls.from_client_secrets_file.assert_called_once_with(
        str(credentials_path), list(GOOGLE_SCOPES)
    )
    mock_flow_instance.run_local_server.assert_called_once_with(port=0)
    assert token_path.read_text() == '{"new": true}'
