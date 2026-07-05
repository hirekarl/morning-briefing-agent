# Strands Agents — Installation

**Requirement:** Python 3.10+

```bash
python -m venv .venv
source .venv/bin/activate          # macOS/Linux
# .venv\Scripts\activate.bat       # Windows CMD
# .venv\Scripts\Activate.ps1       # Windows PowerShell

pip install strands-agents
pip install strands-agents-tools   # community tools package (calculator, current_time, etc.)
```

## Optional extras

For the LiteLLM model provider specifically (see [`model-providers/litellm.md`](model-providers/litellm.md)):

```bash
pip install 'strands-agents[litellm]' strands-agents-tools
```

## Gotchas

- `strands-agents-tools` is a **separate package** from `strands-agents` — the quickstart example imports from `strands_tools` (underscore), not `strands.tools`.
- Model-provider-specific extras (like `[litellm]`) are opt-in — a bare `pip install strands-agents` will raise `ModuleNotFoundError` for `litellm` until you install the extra (see [`gotchas.md`](gotchas.md)).
