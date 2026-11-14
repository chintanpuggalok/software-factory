---
name: factory-state-gate
description: Surface implicit state machines and select UX, DX, and AX gains without behavior change. Use before release.
---

# Review implicit states

1. List implicit state machines in the change and touched flows. Include UI, data load, auth, form, and retry states. Record each state, event, and transition.
2. Identify unreachable states, missing transitions, and conflicting indicators. Cite file paths and line ranges.
3. Select the smallest change that improves UX (user clarity), DX (code clarity), and AX (agent clarity) together. Reject any change that breaks a test or changes approved behavior.
4. Apply only the selected change. Keep data shapes and public interfaces unchanged unless the plan authorizes it. Record results and risks.
5. Send the evidence to `audit-verify` or `audit-release`. Advance only after `PASS: evidence`.

Do not invent states absent from the code. Do not bypass a failed gate.
