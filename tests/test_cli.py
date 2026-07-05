from __future__ import annotations

from typing import Any

from morning_briefing_agent.cli import BRIEFING_PROMPT, main, run


def test_run_invokes_agent_with_briefing_prompt(mocker: Any) -> None:
    fake_agent = mocker.Mock(return_value="a briefing")
    mocker.patch("morning_briefing_agent.cli.build_agent", return_value=fake_agent)

    result = run()

    fake_agent.assert_called_once_with(BRIEFING_PROMPT)
    assert result == "a briefing"


def test_main_prints_run_result(mocker: Any, capsys: Any) -> None:
    mocker.patch("morning_briefing_agent.cli.run", return_value="briefing text")

    main()

    captured = capsys.readouterr()
    assert "briefing text" in captured.out
