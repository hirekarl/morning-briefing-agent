# CLAUDE.md

Project-specific guidance for Claude Code sessions working in this repo.

## Project overview

An AI agent (Strands Agents + LiteLLM + OpenRouter free tier) that checks Gmail, Google
Calendar, and Slack, then synthesizes a prioritized morning briefing. See `README.md` for
setup/usage and `docs/20260423_Morning_briefing_agent_build_guide.docx` for the full
narrative build guide this project was scaffolded from. `.knowledge-base/` is authoritative
reference material for Strands Agents, LiteLLM, and OpenRouter — consult
`.knowledge-base/integration-patterns.md` and `.knowledge-base/strands-agents/gotchas.md`
before inventing API usage that isn't already established in `src/`.

## Commands

Always use `uv run ...` — never bare `python`, `pytest`, `ruff`, or `mypy`. This project's
interpreter and all dependencies are managed by uv.

| Command | Purpose |
|---|---|
| `uv sync --all-groups` | Install/update all dependencies (main + dev) |
| `uv run pytest` | Run the test suite (coverage gate: 90%, enforced by pytest config) |
| `uv run mypy src` | Type-check (strict mode) |
| `uv run ruff check .` | Lint |
| `uv run ruff format .` | Format |
| `uv run pre-commit run --all-files` | Everything pre-commit enforces, on demand |
| `uv run cz commit` | Interactive Conventional Commits helper |
| `uv run morning-briefing` | Run the agent for real (requires real credentials) |

## TDD expectations

This project is built test-first. Before changing or adding logic in `src/`, write or
extend a failing test under `tests/` in the mirrored path (e.g. changes to
`src/morning_briefing_agent/tools/gmail.py` get a test in `tests/tools/test_gmail.py`),
watch it fail, then implement until it passes.

No test may touch the real network or real OAuth. Every Gmail/Calendar/Slack client is
injected as a parameter, so tests pass fakes (`tests/conftest.py`: `FakeGmailService`,
`FakeCalendarService`, `FakeSlackClient`) instead of real API clients. `google_auth.py`'s
tests mock `Credentials.refresh` and `InstalledAppFlow.run_local_server` — never let a
test actually open a browser or hit `googleapis.com`/`slack.com`.

## Source layout rationale

The build guide's own suggested structure is a single `agent.py` that does OAuth, live
API calls, and agent wiring all in one file. That file is not unit-testable — importing
it would trigger network/OAuth side effects. This repo instead separates, per data
source, three layers:

1. **Pure transform** (`parse_email_message`, `parse_calendar_event`,
   `parse_channel_messages`) — raw API response dict in, dataclass out. No I/O.
2. **Orchestration over an injected client** (`fetch_recent_emails`,
   `fetch_upcoming_events`, `fetch_recent_channel_activity`) — takes a service/client as
   a parameter, so tests inject fakes.
3. **Live `@tool` wrapper** (`check_gmail`, `check_calendar`, `check_slack`) — the only
   place that constructs real credentials and real clients, calling layers 1–2.

`config.py`, `google_auth.py`, and `clients.py` are separated the same way: settings
loading, OAuth flow, and live client construction are each their own module so each can
be tested independently of the others. Do not collapse this back into one file to match
the build guide literally — the separation is what makes TDD possible here.

## Commit conventions

Conventional Commits, enforced by commitizen's `commit-msg` pre-commit hook (configured
in `.pre-commit-config.yaml` and `[tool.commitizen]` in `pyproject.toml`). Use
`uv run cz commit` for the interactive prompt, or hand-write messages in that format
(`type(scope): subject`).

### Hard constraint: no Claude/Anthropic attribution

`.claude/hooks/block-claude-coauthor.py` (wired via a `PreToolUse` hook on `Bash` in
`.claude/settings.json`) blocks any `git commit` command whose message contains "claude"
or "anthropic" (case-insensitive). Never add a `Co-Authored-By` trailer or a
"Generated with Claude" line to a commit message — commitizen's config does not add one
either, and none should be added manually.

## Pre-commit

`uv run pre-commit install` (run once per clone) installs both the `pre-commit` and
`commit-msg` hook types — this repo's `.pre-commit-config.yaml` sets
`default_install_hook_types: [pre-commit, commit-msg]` so a bare `pre-commit install`
without that key would silently skip the commitizen commit-msg check. Every commit runs
ruff (lint + format), mypy, and the standard hygiene hooks (trailing whitespace, EOF
fixer, large-file check, private-key detection, LF line-ending enforcement matching
`.gitattributes`).

## Secrets handling

`.env`, `credentials.json`, and `token.json` are gitignored. Never read their contents
aloud, print them, log them, or stage/commit them — if `git status` ever shows one of
these as tracked or about to be committed, stop and flag it rather than proceeding.
