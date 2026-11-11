---
name: factory-preferences
description: Read or maintain user preferences across projects. Use when preferences affect a task or the user asks to remember, change, or delete one.
---

# Maintain user preferences

1. Read the user preference index at `~/.pi/agent/preferences/index.md` if it exists. Load only entries relevant to the task.
2. Keep user-wide preferences separate from project decisions. Project rules and the current request take precedence.
3. Record a general preference only when the user confirms it. Include its context and source. Mark inferences as hypotheses.
4. Ask before creating or changing user-wide storage. Let the user inspect, correct, or delete entries. Do not store secrets.
5. Do not treat a preference as permission to spend, install, delegate, merge, or deploy.

If no index exists, report the gap when relevant. Do not assume this skill automatically loads in every session.
