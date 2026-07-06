# Morning Briefing Agent

An AI agent that checks Gmail, Google Calendar, and Slack, then synthesizes a prioritized morning briefing: **URGENT**, **UPCOMING EVENTS**, **SLACK HIGHLIGHTS**, **OTHER EMAILS**, and **SUGGESTED ACTIONS**.

Built with [Strands Agents](https://github.com/strands-agents/sdk-python) (agent loop), [LiteLLM](https://github.com/BerriAI/litellm) (model provider), and [OpenRouter](https://openrouter.ai) (free-tier LLM gateway).

## About this repo

This is one student's build of the Pursuit AI-native program's morning-briefing-agent assignment, following `docs/20260423_Morning_briefing_agent_build_guide.docx`. If you're a classmate working through the same guide: this repo intentionally diverges from it in places (see "Design decisions" below) rather than being a template to copy, and it was built together with an AI coding agent under a specific set of engineering practices — see `docs/working-with-claude-code.md` for the full story on how and why.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) installed.
- An OpenRouter account and API key.
- A Google Cloud project with the Gmail and Calendar APIs enabled, plus OAuth credentials.
- A Slack app with a **user token** (not a bot token) — the `.env` variable that holds it is still named `SLACK_BOT_TOKEN` regardless; don't be misled by that name into generating a bot token (`xoxb-`) instead.

Full step-by-step instructions for the Google Cloud and Slack setup are in `docs/20260423_Morning_briefing_agent_build_guide.docx` (sections 4–6). This README assumes those credentials already exist.

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

Everything else in `Settings` (`src/morning_briefing_agent/config.py`) is optional and falls back to a sensible default if unset — override any of them in `.env` if needed:

```
MODEL_ID=openrouter/openrouter/free
OPENROUTER_API_BASE=https://openrouter.ai/api/v1
MAX_TOKENS=4096
TEMPERATURE=0.7
GMAIL_HOURS_BACK=12
CALENDAR_HOURS_AHEAD=24
SLACK_HOURS_BACK=12
SLACK_MAX_CHANNELS=5
```

Drop your downloaded `credentials.json` (Google OAuth client) in the project root. `.env`, `credentials.json`, and `token.json` are all gitignored — never commit them.

## Running

```bash
uv run morning-briefing
```

The first run opens a browser window for Google OAuth login and writes `token.json` after you approve access. Subsequent runs reuse that token, silently refreshing it as needed — you'll only see the browser again if the refresh token itself is revoked or invalid.

## Development workflow

This project is built test-first: extend or add a test under `tests/` before touching `src/`, run it red, then implement until green.

```bash
uv run pytest                    # run the test suite (coverage gate: 90%)
uv run mypy src                  # type-check
uv run ruff check .              # lint
uv run ruff format .             # format
uv run mdformat --wrap no --number .  # format Markdown (no hard-wrapping)
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

Each tool module separates pure data transforms (`parse_*`) and orchestration over an injected client (`fetch_*`) from the live `@tool`-decorated wrapper that constructs real credentials/clients. This is what makes the whole thing unit-testable without ever touching the network or real credentials — see `CLAUDE.md` for the rationale.

`.knowledge-base/` (not shown above) is a separate, curated reference on OpenRouter, Strands Agents, and LiteLLM Proxy, built from real docs pages before any agent code was written — see `docs/working-with-claude-code.md` for what it is and how it was put together.

## Design decisions

Places where this repo deviates from a literal reading of the build guide, and why:

- **Layered tool architecture instead of one `agent.py`.** The guide's own suggested structure does OAuth, live API calls, and agent wiring in a single file. This repo splits each data source into a pure transform, an orchestration layer over an injected client, and a live `@tool` wrapper — see `CLAUDE.md`'s "Source layout rationale" for the full reasoning.
- **Auto-router model (`openrouter/openrouter/free`) instead of a pinned free model.** `openai/gpt-oss-120b`, `gpt-oss-20b`, and `meta-llama/llama-3.3-70b-instruct` were each tried live as pins, to avoid the auto-router landing on a model without tool-calling support. All three hit their own reliability problem instead: the `gpt-oss-*` models are reasoning models whose chain-of-thought content breaks multi-turn tool calling (observed live as empty final responses), and two of the three hit persistent upstream 429s. The auto-router succeeded cleanly by trying whichever backend currently has capacity. Override via `MODEL_ID` if you want to pin to a specific model anyway. See the comment above `DEFAULT_MODEL_ID` in `config.py` for the full writeup.
- **Cancelled and self-declined calendar events are filtered out, not just displayed.** `parse_calendar_event` didn't originally read `status` or `attendees[].responseStatus`, so a cancelled event or one you'd declined showed up in `UPCOMING EVENTS` identically to a real meeting. `fetch_upcoming_events` now filters those out before parsing, rather than leaving it to the LLM to notice.
- **Slack highlights are attributed to a sender.** `parse_channel_messages` originally kept only message text, discarding who sent it, so the briefing could never say who posted anything. Messages now carry a `SlackMessage(sender, text)` shape through to the prompt.
- **Every optional `.env` setting actually takes effect.** `load_settings()` originally read only the two required secrets from the environment — `model_id`, `max_tokens`, `temperature`, and the per-tool hours-back/hours-ahead/max-channels fields always resolved to hardcoded defaults regardless of `.env`. `check_gmail`/`check_calendar`/`check_slack` now resolve their defaults from `Settings` when the caller doesn't pass one, so the knobs listed in Setup above are real.
- **The default Strands callback handler is disabled.** It streams the assistant's response straight to the console as it's generated; `cli.py` then prints the returned result again, so every run printed the briefing twice until this was turned off.

## Secrets & security

- `.env`, `credentials.json`, and `token.json` are gitignored and must never be committed.
- The Slack token is a **personal user token** (`xoxp-`) — it authenticates as you, reads any channel you're already in. Do not share it or use it outside a personal, local tool.
- If any secret is ever accidentally committed, revoke and regenerate it immediately.

## Full build guide

`docs/20260423_Morning_briefing_agent_build_guide.docx` has the complete narrative walkthrough, including Google Cloud Console and Slack app screenshots.

If you're new to `uv`, pre-commit hooks, TDD, or working with an AI coding agent, `docs/working-with-claude-code.md` explains all of that from scratch, plus the reasoning behind how this repo was built with Claude Code.
