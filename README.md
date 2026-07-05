# Morning Briefing Agent

An AI agent that checks Gmail, Google Calendar, and Slack, then synthesizes a prioritized
morning briefing: **URGENT**, **UPCOMING EVENTS**, **SLACK HIGHLIGHTS**, **OTHER EMAILS**,
and **SUGGESTED ACTIONS**.

Built with [Strands Agents](https://github.com/strands-agents/sdk-python) (agent loop),
[LiteLLM](https://github.com/BerriAI/litellm) (model provider), and
[OpenRouter](https://openrouter.ai) (free-tier LLM gateway).

## Prerequisites

- [uv](https://docs.astral.sh/uv/) installed.
- An OpenRouter account and API key.
- A Google Cloud project with the Gmail and Calendar APIs enabled, plus OAuth credentials.
- A Slack app with a **user token** (not a bot token).

Full step-by-step instructions for the Google Cloud and Slack setup are in
`20260423_Morning_briefing_agent_build_guide.docx` (sections 4–6). This README assumes
those credentials already exist.

## Setup

```bash
uv sync --all-groups
uv run pre-commit install
```

Create a `.env` file in the project root:

```
OPENROUTER_API_KEY=sk-or-your-key-here
SLACK_BOT_TOKEN=xoxp-your-token-here
```

Drop your downloaded `credentials.json` (Google OAuth client) in the project root.
`.env`, `credentials.json`, and `token.json` are all gitignored — never commit them.

## Running

```bash
uv run morning-briefing
```

The first run opens a browser window for Google OAuth login and writes `token.json`
after you approve access. Subsequent runs reuse that token silently until it expires.

## Development workflow

This project is built test-first: extend or add a test under `tests/` before touching
`src/`, run it red, then implement until green.

```bash
uv run pytest                    # run the test suite (coverage gate: 90%)
uv run mypy src                  # type-check
uv run ruff check .              # lint
uv run ruff format .             # format
uv run pre-commit run --all-files  # everything pre-commit enforces
uv run cz commit                 # interactive Conventional Commits helper
```

## Project layout

```
src/morning_briefing_agent/
  config.py       # Settings + load_settings() — reads .env
  time_utils.py   # single patchable time source (utcnow())
  models.py       # EmailSummary, EventSummary, ChannelDigest
  google_auth.py  # OAuth flow: cached token / refresh / interactive login
  clients.py      # live Gmail/Calendar/Slack client construction
  tools/
    gmail.py      # parse_email_message, fetch_recent_emails, check_gmail (@tool)
    calendar.py   # parse_calendar_event, fetch_upcoming_events, check_calendar (@tool)
    slack.py      # parse_channel_messages, fetch_recent_channel_activity, check_slack (@tool)
  agent.py        # SYSTEM_PROMPT, build_model(), build_agent()
  cli.py          # run(), main() — entry point
```

Each tool module separates pure data transforms (`parse_*`) and orchestration over an
injected client (`fetch_*`) from the live `@tool`-decorated wrapper that constructs real
credentials/clients. This is what makes the whole thing unit-testable without ever
touching the network or real credentials — see `CLAUDE.md` for the rationale.

## Secrets & security

- `.env`, `credentials.json`, and `token.json` are gitignored and must never be committed.
- The Slack token is a **personal user token** (`xoxp-`) — it authenticates as you, reads
  any channel you're already in. Do not share it or use it outside a personal, local tool.
- If any secret is ever accidentally committed, revoke and regenerate it immediately.

## Full build guide

`20260423_Morning_briefing_agent_build_guide.docx` in the repo root has the complete
narrative walkthrough, including Google Cloud Console and Slack app screenshots.
