---
name: factory-taste
description: Capture and apply the user's technical and design preferences across projects and within a product. Use after explicit feedback or when relevant preferences inform a decision.
---

# Maintain taste

1. Read the project taste index and relevant decisions. For user-wide preferences, read the harness preference index. The default path is `~/.pi/agent/preferences/index.md`. If the harness stores them elsewhere, use its documented location and state which one you used. Load only records needed for this task.
2. Keep user-wide preferences separate from project-specific choices. Project rules and the current request take precedence.
3. Capture the choice, its context, the reason, and a source or example. Record rejected alternatives when useful.
4. Label explicit user preferences as confirmed. Label agent inferences as hypotheses. Ask before promoting a hypothesis to a general preference or creating user-wide storage.
5. Apply confirmed preferences only when relevant. Report conflicts and ask when they affect a consequential choice.
6. Keep indexes short. Link to detailed records and examples. Let the user correct or delete records. Do not store secrets.

Do not infer a permanent preference from one choice. A preference is not permission to spend, install, delegate, merge, or deploy. Send a new or changed record to `audit-taste`. Apply it as a general preference only after `PASS: evidence`.
