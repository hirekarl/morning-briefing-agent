from __future__ import annotations

from morning_briefing_agent.agent import build_agent

BRIEFING_PROMPT = "What did I miss? Give me my morning briefing."


def run() -> str:
    agent = build_agent()
    result = agent(BRIEFING_PROMPT)
    return str(result)


def main() -> None:
    print(run())


if __name__ == "__main__":
    main()
