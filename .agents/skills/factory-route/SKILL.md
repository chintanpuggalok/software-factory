---
name: factory-route
description: Select a bounded workflow for a factory task. Use when a new idea, feature, bug, refactor, verification, or release enters the factory, or when earlier work resumes.
---

# Route the task

1. Read the goal, authorized scope, project state, and relevant constraints.
2. If earlier state or a blocked stage exists, start with `factory-recover`. Do not restart completed work.
3. Select the entry point. Use `factory-idea` or `factory-spec` for product shaping, `factory-design` or `factory-architecture` for a direction, `factory-plan` before complex work, and `factory-build` for an authorized change. Use `factory-verify`, `factory-visual-review`, `factory-security`, or `factory-release` when that evidence is needed. Do not run every stage for a small change.
4. For a bug, feature, or refactor, read the matching file in `references/`. Use only the selected playbook.
5. Name the next skill, its audit, required evidence, and dependencies. Record the reason and the next action.
6. Load only the selected skill and the context it needs.

This skill recommends a route. It does not enforce execution or grant permission to spend, install, delegate, or deploy.
