# Live end-to-end run

## Scope
The author ran the coordinator with the current default model. The model audits are separate processes, but they are not independent human review.

## Planning

- **idea**: PASS: §1 ties the single offline user and problem to the goal; §2 marks A1–A7 unverified; §3–4 compare D1/D2/D3 and select D1 with reversible defaults and expli — `docs/factory/idea.md`
- **spec**: PASS: §1 and §6 state the single offline user, add/complete/delete scope, and explicit exclusions; §2–§4 map flows UF-1–UF-6 to prioritized F1–F14 and testable  — `docs/factory/spec.md`
- **design**: PASS: §2 reports the missing taste index and marks its baseline as an instructed default; §3 labels Apple Reminders/Microsoft To Do/Todoist as unverified non-le — `docs/factory/design.md`
- **architecture**: PASS: §2 lists scale targets with UNK2–UNK6 marked unknown and 12 KB/quota as unmeasured estimates; §6 compares A/B/C with rejection reasons; §7 covers storage- — `docs/factory/architecture.md`
- **plan**: PASS: Plan rev 2 closes the prior PL-D2/WU-7/AS-15 defect — §4's rule table forbids any boot-time write to checklist.v1, gates resumption on a successful backup — `docs/factory/plan.md`

## Build

- Structural checks: passed.
- Browser probe: passed. Repair attempted: False.
- Prototype: `artifacts/live-run/.factory-build/index.html`.
- Probe scope: page load, uncaught JavaScript errors, and horizontal overflow at two viewport sizes. No checklist-specific acceptance contract was supplied.

## Fixes found by the live run

- The model emitted tool-call markup instead of a verdict. The parser now accepts one verdict line, rejects markup, and makes one corrective call.
- A valid `REVISE` blocked the run. The coordinator now regenerates the stage once with the audit finding, then re-audits.
- Stage outputs were not durable. Each passed stage is written once to `docs/factory/<stage>.md` and never overwrites an existing file.
- Stage history overflowed the old excerpt budget. The newest stages now get the full text up to a total budget.
- Long outputs exceeded the old limits and the 120-second timeout. Limits and the planning timeout were raised.

## Limits

- The audits are model judgments. They are not independent proof.
- Browser verification is generic. Functional checklist behavior, accessibility, and screen-reader use remain unverified.
- The run did not deploy. No production target is configured.
- Model calls can incur subscription overages. No dollar cap is enforced.
