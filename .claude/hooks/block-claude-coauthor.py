#!/usr/bin/env python3
"""PreToolUse(Bash) hook: block any git commit whose message mentions Claude/Anthropic."""
import json
import re
import sys

data = json.load(sys.stdin)
cmd = data.get("tool_input", {}).get("command", "") or ""

if re.search(r"git\s+commit", cmd, re.I) and re.search(r"claude|anthropic", cmd, re.I):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                "Blocked: commit message references 'Claude' or 'Anthropic'. "
                "This repo forbids attributing Claude/Anthropic as commit co-author "
                "(e.g. a Co-Authored-By line). Remove the reference and retry."
            ),
        }
    }))
