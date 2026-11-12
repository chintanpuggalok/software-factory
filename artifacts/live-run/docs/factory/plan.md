# factory-plan

Verdict: PASS: Plan rev 2 closes the prior PL-D2/WU-7/AS-15 defect — §4's rule table forbids any boot-time write to checklist.v1, gates resumption on a successful backup, and forbids session writes if backup fails, verified by AS-12/AS-15/AS-16/AS-18/SC-4; §2 gives the WU-1→WU-9 dependency spine with hard gates, §3/§8 fix $0.00 ceilings and per-delegate write/read permissions, §6 supplies SC-1–SC-5 plus 19 scripted acceptance scenarios with a ship gate, and RISK-1–RISK-11 map each risk to a mitigating scenario, with §9 marking effort (UNK7), spec AC text (PL-A1) and quotas as unknown rather than invented; next action is to hand M1 (WU-1) to factory-build after this gate clears.

# factory-plan — Local one-person checklist app

**Status:** revision 2 — resubmitted for `audit-plan`. **No approval claimed. Nothing executed:** no files written, no browser opened, no code built by this stage.
**Inputs (untrusted data):** goal sentence; prior `idea`, `spec`, `design`, `architecture` outputs. Research leads `null`; reference pages `null`. No external sources consulted or cited.
**Carried forward (confirmed upstream, not reopened):** D1 — one self-contained `index.html`, vanilla HTML/CSS/JS, no build, no network, `localStorage` under `checklist.v1`, payload `{version:1,tasks:[{id,text,completed,createdAt}]}`, operations add / complete / delete, newest-first, completion never reorders, single-level ~6 s undo restoring by neighbour ids, backup-before-overwrite, memory-only degradation with persistent banner, `textContent` only.
*(Items marked **[A#]**, **PL-A#**, **UNK#** are assumptions or unknowns, not verified facts.)*

---

## 0. Revision log (why this supersedes the rejected plan)

The audit finding was: **PL-D2 / WU-7 / AS-15 overwrote `checklist.v1` with an empty payload after a successful corrupt-payload backup**, contradicting spec UF-6/F11 ("do not overwrite it"), and AS-15's "quiet second reload" depended on that write.

| Item | Was | Now |
|---|---|---|
| **PL-D2** | Backup raw → then write empty payload to `checklist.v1` → then notice | Backup raw → **no write to `checklist.v1` at load, ever**. App runs from an empty in-memory list with a notice. Primary key stays byte-identical until the user's first mutation, and only if the backup succeeded (§4 rule table) |
| **WU-7** | Exit criterion: "primary holds empty payload after recovery" | Exit criterion: **`checklist.v1` is byte-identical before and after a corrupt load**, the only `setItem` on the recovery path is the backup key, and primary writes are gated (§4 table) |
| **AS-15** | Second reload was silent | Second reload **repeats the notice** and asserts the primary is still byte-identical; no empty payload is ever asserted |
| **PL-D3** (new) | — | Backup is idempotent for an *identical* raw string; a *different* corrupt value still overwrites the single slot (architecture LIM-2 unchanged) |
| **PL-D4** (new) | — | Repeating the notice on every corrupt load is accepted. No "already noticed" marker key (a non-destructive marker was considered and rejected as extra state for no user gain) |
| **AS-16** (new) | — | Covers the *post-mutation* branch, so the "writes resume on first user mutation" rule is verified rather than assumed |

No other work unit, scenario, or decision changes meaning. Spec OQ-1 (export/import) remains deferred and is **not** promoted by this plan.

---

## 1. Scope of this plan

Build and verify **R1** of the app described above: a single `index.html` deliverable, three operations plus single-level undo, honest persistence, no accounts, no network, no build step, no install.

**Explicitly out of R1** (unchanged from spec/design): text editing, reordering, multiple lists, tags/priorities/dates/reminders, search/filter/sort, hiding completed, import/export, dark theme, settings, onboarding, PWA/service worker, framework, bundler, automated test suite, analytics, telemetry.

**Plan success condition:** an independent reviewer can run a scripted set of acceptance scenarios against the file, in a fresh browser profile, and produce a pass/fail evidence table without asking the implementer anything — including the corrupt-storage scenario, which must show the stored value preserved.

---

## 2. Release slicing and sequencing

Two axes: **one release** (R1 ships once), **three build milestones** inside it on the same file, so there is a usable checkpoint early and failure handling is not bolted on last. **PL-D1.**

| Milestone | Contents | Checkpoint means |
|---|---|---|
| **M1 — Capture and list** | File shell, layout/tokens, add, render, valid/empty load, synchronous save | A task can be added, survives reload; nothing else promised |
| **M2 — Complete, delete, undo** | Toggle without reorder, delete, single-level undo with neighbour restore, deadline timing, focus restoration | The three operations work end-to-end |
| **M3 — Honest failure, accessibility, scale** | Corrupt/unavailable recovery, banners, notices, labels/live regions/targets/reflow/reduced motion, 200-task pass | All acceptance scenarios pass |

**Dependency spine:** WU-1 → {WU-2, WU-3 in parallel} → {WU-4, WU-5 in parallel} → WU-6 → WU-7 → WU-8 → WU-9.
Hard gates: **WU-7 cannot start before WU-3's `load()` status vocabulary is frozen**; **WU-9 cannot start before WU-6, WU-7, WU-8 are all complete**; **no milestone is declared done without its scenarios re-run**.

---

## 3. Work units

Each unit is a bounded change inside `index.html` (logical modules from architecture §5). **Spending ceiling per unit: $0.00. Tool calls are not capped.**

| ID | Unit | Touches | Exit criteria | Depends on | Risk |
|---|---|---|---|---|---|
| **WU-1** | Document shell, layout, tokens, CSP meta | whole file skeleton; `<main>`, `<h1>`, form, list, toast/banner containers, CSS tokens, `Content-Security-Policy` meta | File opens by double-click; no network requests in devtools; layout matches design §7 at 1440 px and 320 px; CSP verified not to break the page on `file://` (UNK6 — if it does, drop the meta tag, keep the feature, and record it) | — | RISK-3 |
| **WU-2** | `domain`: validation, `makeTask`, id generation | `domain` block only | `validatePayload` accepts only `version===1` + array + every task valid; rejects future versions, non-objects, wrong types; `makeTask` trims and refuses empty; id generator retries on collision and has a fallback when `crypto.randomUUID` is absent | WU-1 | RISK-4 |
| **WU-3** | `storage`: `load()/save()/backup()` | `storage` block only | `load()` returns exactly `ok \| empty \| corrupt \| unavailable` with `tasks?`/`raw?`; **`load()` never calls `setItem` on `checklist.v1`**; `backup(raw)` writes only `checklist.v1.corrupt-backup` and returns boolean; every `localStorage` reference in the file lives in this block | WU-1 | RISK-2, RISK-6 |
| **WU-4** | `render` + focus restoration | `render` block, row markup, `data-task-id`, `data-completed` | Writes all user text via `textContent`; restores focus by `data-task-id` after full re-render; renders empty state; renders 200 rows without dropping input focus | WU-2 | RISK-6, RISK-9 |
| **WU-5** | `reduce`: events and effects | `reduce` block | Pure (no DOM, no storage); covers `LOAD_*`, `ADD`, `TOGGLE`, `DELETE`, `UNDO`, `UNDO_EXPIRED`, `SAVE_OK/FAILED`; unknown id and empty add are no-ops with no effects; delete captures `{task, prevId, nextId, index}` | WU-2 | RISK-7 |
| **WU-6** | `controller` + `boot`: wiring, undo timing, announcements | `controller`/`boot` blocks, listeners, live region | Enter and Add both submit; toggle survives full re-render; delete shows toast; undo restores per neighbour rule; expiry evaluated against `Date.now()` on tick *and* lazily, so a throttled background tab cannot keep a stale toast alive; timer freezes on hover/focus; announcements are opted-in only where design §8 says so | WU-3, WU-4, WU-5 | RISK-5, RISK-8 |
| **WU-7** | **Corrupt / unavailable recovery (revised)** | `boot`/`controller` recovery branch, banner + notice copy | Follows the §4 rule table exactly. On corrupt load: backup attempted first; **no `setItem` other than the backup key occurs during boot**; `checklist.v1` is byte-identical before and after load; in-memory list is empty; one-line notice shown; if backup fails, **no primary write for the whole session** and the storage banner is shown instead. On the first user mutation after a *successful* backup, normal saving resumes. Code review plus AS-12/AS-15/AS-16 | WU-3, WU-6 | **RISK-1** |
| **WU-8** | Accessibility and responsive pass | labels, accessible names, live regions, focus rings, target sizes, wrap, reduced motion | Hidden label on input; `Delete task: {text}` on every delete control; visible focus ring; ≤44 px-effective targets; 200% zoom and 320 px with no horizontal scroll; `prefers-reduced-motion` removes toast motion; completion not colour-only | WU-4, WU-6 | RISK-9 |
| **WU-9** | Verification and evidence capture | none (read-only inspection of the file) | AS-1…AS-18 executed and recorded pass/fail with notes; static greps clean (§6); evidence table produced for the coordinator | WU-6, WU-7, WU-8 | RISK-10 |

**Not work units, deliberately:** no automated test harness, no lint tooling, no dependency installation — each would add a build step or a network fetch, both forbidden by spec F1 and architecture §1. **PL-D5.**

---

## 4. PL-D2 (rev 2) — the authoritative recovery rule table

The corrupt-payload rule is stated once, here, and WU-7/AS-12/AS-15/AS-16 are written against this table.

| Boot outcome | `persistence` | User sees | `checklist.v1` written during boot? | Writes later? |
|---|---|---|---|---|
| Key absent | `ok` | Empty state | No | Yes, from the first mutation |
| Payload valid | `ok` | List | No | Yes, from the first mutation |
| Payload corrupt, **backup succeeded** | `recovered` | One-line notice + empty list | **No — only the backup key is written.** Primary stays byte-identical | **Yes, from the first *user mutation*** (the raw value is already preserved in the backup key, satisfying F11's "preserve … under a separate backup key" before any overwrite) |
| Payload corrupt, **backup failed** | `unavailable` | Storage banner (no false "saved") | **No** | **No, for the whole session** — an unbacked corrupt value is never overwritten |
| `localStorage` throws on read | `unavailable` | Storage banner; app works in memory | No | Attempted per mutation; a throw keeps the banner up (no retry loop, no success claim) |

Consequences recorded deliberately:

- A user who reloads without touching anything sees the notice **again**, and the primary is still untouched. **PL-D4** — accepted; in scope this is the honest behaviour.
- The notice is not a permanent state marker; nothing is written to suppress it.
- "Do not overwrite it" is read as: *the recovery path itself never destroys the unreadable value*. Once the value is safely in the backup key, later user-driven saves may replace the primary — otherwise the app would be permanently read-only, which contradicts UF-6 and F10. **[PL-A4]**
- If the audit or a later stage interprets F11 as "never overwrite `checklist.v1` for the rest of the session even after backup", the fallback is a one-line change (suppress writes while `persistence==='recovered'`); it makes the app read-only until reload and would need the banner copy changed. Recorded as an accepted alternative, not chosen.

---

## 5. Decisions and authorization

| ID | Decision | Reversible? | Needs authorization? |
|---|---|---|---|
| PL-D1 | One release R1, three internal milestones M1–M3 | Yes, checkpoint labels only | No |
| **PL-D2** | Recovery never writes the primary key at load; writes resume on first user mutation only after a successful backup; no primary writes for the session if the backup failed | Yes — one guard flag in `boot` | **No** — this is the spec F11 requirement, restated |
| PL-D3 | Backup write skipped when the existing backup already holds an identical raw string; a different corrupt value still overwrites the single slot | Yes — one comparison | No (does not change LIM-2) |
| PL-D4 | Repeat notice on repeat corrupt load accepted; no non-destructive marker key added | Yes — could add a marker later | No |
| PL-D5 | Verification is manual, scripted, evidence in a text table; no test framework, no dependencies | Yes | No |
| PL-D6 | Optional parallel delegation of WU-2 and WU-3 only; ceiling $0.00 each; no cap on tool calls | Yes | No |
| PL-D7 | Ship gate = every AS passes or has a recorded, accepted deviation | Yes | No |

**No paid dependency, no schema break, no API break, no spend, no workflow change is proposed.** The one added storage key (`checklist.v1.corrupt-backup`) is the backup slot spec F11 already authorises; the payload schema `{version:1,tasks}` is unchanged.

**Blocking user decision: none.** If the audit disagrees with the reading in §4, the only user-facing consequence is the read-only fallback noted there, which is a copy change plus one guard.

---

## 6. Verification and evidence

**Method:** manual, scripted, reproducible. Fresh copy of `index.html`, **fresh browser profile**, no devtools except in the scenarios that say so. Static checks are greps over the file.

**Static ship checks (SC):**

| ID | Check |
|---|---|
| SC-1 | The deliverable is one file; no other runtime files required |
| SC-2 | No `http://`, `https://`, `fetch(`, `XMLHttpRequest`, `import(`, `@import`, external `src=`/`href=` (excluding `#`) |
| SC-3 | No `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`, `eval` |
| SC-4 | Every `localStorage` reference is inside the `storage` block; no `setItem` on `checklist.v1` reachable from `load()` |
| SC-5 | Event handlers are attached with `addEventListener`; no inline `on*=` attributes that would be blocked by CSP |

**Acceptance scenarios (independent — runnable by someone who did not write the code):**

| AS | Scenario | Evidence recorded |
|---|---|---|
| **AS-1** | Open the file. Devtools Network tab shows zero requests. | Request count = 0; screenshot of empty page |
| **AS-2** | First open, nothing stored. | Empty-state copy visible; input focused; no spinner |
| **AS-3** | Add "Buy milk" via Enter, then "Call Sam" via the Add button, then "  spaced  ". | Rows appear newest-first; text trimmed; input cleared and refocused after each |
| **AS-4** | Submit empty and whitespace-only input via Enter and via Add. | Nothing added; no dialog; focus stays in input; stored value unchanged |
| **AS-5** | Toggle the middle row complete; add a new task. | Checkbox checked, strikethrough + dim, `data-completed="true"`, **row does not move**; new task at top |
| **AS-6** | Delete a row by pointer; click Undo. Then delete A, delete B, click Undo. | Row returns to its original relative position with its original completed state; only **B** returns, single-level undo |
| **AS-7** | Delete a row and hover (then focus) the toast until past 6 s, then let it go; separately delete and wait. | Timer visibly pauses while hovered/focused; deletion is final only after the window actually elapses; toast is not clickable after expiry |
| **AS-8** | Add three tasks, toggle one, delete one, reload. | Exact list, order and completion restored; undo state does not survive |
| **AS-9** | After each mutation, inspect `localStorage['checklist.v1']`. | Valid JSON, `version===1`, task objects have exactly `id/text/completed/createdAt`, array order equals visual order, contents equal the visible list |
| **AS-10** | Add `<b>bold</b>`, `<img src=x onerror=alert(1)>`, and `a & b`. | All render literally as text; no element created; no alert; no console error |
| **AS-11** | Block storage (devtools: override `Storage.prototype.getItem/setItem` to throw, then reload) and use the app. | Persistent banner "Changes won't be saved…"; add/toggle/delete still work in memory; no "saved" claim anywhere |
| **AS-12** | Corrupt a payload **and** make the backup write fail (override `setItem` to throw only for keys containing `backup`). | Banner shown; **`checklist.v1` still holds the original corrupt string**; no write to the primary for the rest of the session |
| **AS-13** | Keyboard only, from load: tab through, add, toggle with Space, delete, reach and activate Undo. | Every control reachable in the design §8 focus order; focus ring visible at all times; focus lands per design §8 after add/toggle/delete/undo; nothing requires a pointer |
| **AS-14** | Accessibility spot checks: names, live regions, targets, 200% zoom, 320 px width, reduced motion. | Delete announces `Delete task: {text}`; input has a real label; "Task added."/"Task restored." announced once; no duplicate completion announcement; ≥44 px targets; no horizontal scroll at 200% zoom or 320 px; toast motion removed under `prefers-reduced-motion` |
| **AS-15** *(rev 2)* | Pre-seed `checklist.v1` with invalid JSON. Record the exact string. Reload twice, touching nothing in between. | Notice shown both times; list empty; **`checklist.v1` byte-identical to the recorded string after both loads**; `checklist.v1.corrupt-backup` contains an identical copy; **no empty `{version:1,tasks:[]}` payload is ever written** |
| **AS-16** *(new)* | Continue from AS-15: add one task, then reload. | New list works normally; on reload the task is present and **no notice** appears; `corrupt-backup` still holds the original raw string; `checklist.v1` now holds a valid payload |
| **AS-17** | Seed 200 tasks; add, toggle, delete, undo. | No perceptible delay; input keeps focus after add; focus restored to the same task after toggle; list scrolls, no virtualization |
| **AS-18** | Seed structurally wrong payloads in turn: `version:2`, `tasks` not an array, task missing `completed`, task `text` a number. | Each routes to the recovery path exactly like AS-15 (backup, notice, empty list, primary untouched); none is silently migrated or partially salvaged |
| **AS-19** | SC-1…SC-5 greps. | Command output pasted into the evidence table |

**Evidence to ship:** a filled table with one row per AS (`pass` / `fail` / `accepted deviation` + the recorded observation), the browser and OS used, the raw corrupt string from AS-15, and SC output. Persisted by the coordinator alongside the plan (target: `docs/factory/build-evidence.md`); **this stage writes nothing**.

**Definition of done (PL-D7):** all of SC clean, AS-1…AS-19 pass or have a deviation accepted in writing, no scenario skipped, no scenario reported as "verified in code review" where an executable check was possible.

---

## 7. Risks

| ID | Risk | Mitigation | Verified by |
|---|---|---|---|
| **RISK-1** | Recovery path destroys or shadows the unreadable payload (the rejected plan's defect) | §4 rule table; no boot-time primary write; backup-before-overwrite; no-write session when backup fails | AS-12, AS-15, AS-16, AS-18, SC-4 |
| RISK-2 | `file://` storage is blocked or unreliable in a target browser (UNK5, LIM-4) | Treat as a first-class state, not an error; banner + in-memory; note the static-serve fallback | AS-11 |
| RISK-3 | CSP meta breaks the page on `file://` (UNK6) | Verify in WU-1; if it breaks, remove the tag and record the deviation rather than weakening the feature | AS-1, AS-2, SC-5 |
| RISK-4 | `crypto.randomUUID` absent (UNK4) | Fallback id generator with collision retry, exercised by forcing the fallback | AS-3, AS-9 |
| RISK-5 | Background-tab timer throttling lets the undo window overrun | Deadline comparison on tick and on interaction; freeze `remainingMs` on pause | AS-7 |
| RISK-6 | Full re-render loses focus for keyboard users | Focus restored by `data-task-id` after every render | AS-13, AS-17 |
| RISK-7 | A reducer branch touches DOM/storage and reintroduces dishonesty | Purity rule checked in WU-5; all `localStorage` confined to `storage` | SC-4 |
| RISK-8 | Multi-tab clobbering (LIM-1) | Out of scope for R1; listed as a limit, not silently "solved" | recorded, not tested |
| RISK-9 | Completion communicated by colour only, or a control unreachable | Checkbox + strikethrough + dim; visible focus; target sizes | AS-13, AS-14 |
| RISK-10 | Verification becomes self-attestation | Scripted AS list, fresh profile, recorded raw evidence, independent runner | AS-1…AS-19 |
| RISK-11 | Plan drifts into scope the spec excluded | §1 exclusion list restated at every WU review; any addition requires a new plan | review |

---

## 8. Delegation

**Default: no delegation.** The unit is small and every unit touches the same file, so parallel editing of `index.html` risks conflicting writes.

**Optional and bounded — PL-D6:** delegate **WU-2** (`domain`) and **WU-3** (`storage`) to two cheap delegates, only if they work on separate scratch copies that are merged serially by the implementer.

- Permissions per delegate: read the plan and architecture; write only their own scratch file; no network access; no new files beyond the scratch copy; no changes to layout, copy, or the reducer.
- **Spending ceiling: $0.00 per delegated task.** Tool calls are **not** capped.
- Nothing else is delegated: WU-4…WU-9 are interdependent within one file.

---

## 9. Assumptions and unknowns

**Assumptions**
- **PL-A1:** The full spec AC-1…AC-16 text is not present in the stage inputs available here (the excerpt is truncated). AS-1…AS-19 are written against F1–F14 and the AC descriptions quoted in the architecture audit (AC-1 zero requests, AC-6/AC-8 undo, AC-9 payload, AC-12 blocked storage, AC-13 corrupt backup, AC-14 text-only, AC-16 200 tasks); the remaining AC ids are covered by intent, and the build stage must re-read the full spec before AS sign-off.
- **PL-A2:** Desktop with keyboard and mouse is the primary context; mobile works but is not acceptance-gated (design AD-1).
- **PL-A3:** ~6 s single-level undo with pause on hover/focus is the intended behaviour (design DD-6, AD-2).
- **PL-A4:** F11's "do not overwrite it" is satisfied by preserving the raw value in the backup key before any user-driven write; the primary may be replaced only after that, and only by an explicit user action (§4).
- **PL-A5:** Manual scripted verification is adequate at this size; the architecture explicitly excludes an automated suite.
- **PL-A6:** 200 tasks is the ceiling; performance claims at that size are estimates until AS-17 is run.
- **PL-A7:** No time estimates are given; sequencing and gates are authoritative (**UNK7**: schedule/effort unknown).
- **PL-A8:** The backup key name `checklist.v1.corrupt-backup` is a local choice; renaming it is a one-constant change.

**Unknowns carried forward:** UNK2 multi-tab reality; UNK3 browser quota; UNK4 `randomUUID` availability; UNK5 which browsers block `file://` storage; UNK6 CSP behaviour on `file://`; **UNK7** effort/schedule.

---

## 10. Traceability

| Upstream | Plan response |
|---|---|
| F1 single file, no requests | WU-1, WU-3, SC-1/SC-2; no dependencies, no test harness (PL-D5) |
| F2 add via Enter/button, trim, reject empty | WU-5, WU-6, AS-3, AS-4 |
| F3 newest at top | WU-4, WU-5, AS-3 |
| F4 toggle without reorder | WU-4, WU-5, AS-5 |
| F5 delete + single-level undo | WU-5, WU-6, AS-6, AS-7 |
| F6/F7 persist and reload | WU-3, WU-6, AS-8, AS-9 |
| F8/F9 payload and task shape | WU-2, WU-3, AS-9, AS-18 |
| F10 storage failure | WU-7, AS-11 |
| F11 corrupt payload preserved, never silently overwritten | **WU-7, §4 rule table, AS-12, AS-15, AS-16, AS-18** |
| F12 text never HTML | WU-4, AS-10, SC-3 |
| F13 accessibility | WU-8, AS-13, AS-14 |
| F14 ~200 tasks | WU-4, WU-6, AS-17 |
| Architecture ARCH-D1/D2 (one key, synchronous saves) | WU-3, AS-9 |
| Architecture ARCH-D3/D10 (strict validation, backup-before-overwrite) | WU-2, WU-7, AS-12, AS-15, AS-18 |
| Architecture ARCH-D4 (degrade, never lie) | WU-7, AS-11 |
| Architecture ARCH-D6/D7 (pure reducer, deadline timing) | WU-5, WU-6, AS-7, AS-13 |
| Architecture LIM-1/LIM-2/LIM-5/LIM-6 | Recorded as accepted limits; RISK-8; not tested in R1 |
| Design DD-6/DD-8/DD-9/DD-12, AD-8 | WU-6, WU-7, WU-8, AS-6, AS-7, AS-14 |

---

## 11. Handoff and next action

- **Goal carried forward (unchanged):** local one-person checklist; add, complete, delete; no account or cloud sync; keep it simple.
- **Confirmed decisions carried:** D1 single-file static page with `localStorage`; add/complete/delete only; newest-first; completion never reorders; single-level undo; no network/account/sync; explicit exclusions.
- **New plan decisions:** PL-D1 (milestones), **PL-D2 rev 2** (recovery never writes the primary key at load; writes resume on first user mutation only after a successful backup; no primary writes at all if the backup failed), PL-D3 (idempotent backup for identical raw), PL-D4 (repeat notice accepted, no marker key), PL-D5 (manual scripted verification), PL-D6 (optional $0 delegation of WU-2/WU-3 only), PL-D7 (ship gate).
- **Artifact paths:** output target `docs/factory/plan.md` (persisted by the coordinator **after** audit); build evidence target `docs/factory/build-evidence.md`; deliverable `index.html`. **No files were written by this stage.**
- **Open questions:** none blocking. PL-OQ-1 (should the recovery notice ever be dismissible — default no, design AD-9), PL-OQ-2 (should writes be suppressed for the whole session after recovery — default no, see §4 fallback), PL-OQ-3 (full spec AC text to be re-read at build, PL-A1). Spec OQ-1 (export/import) stays deferred.
- **Audit target:** `audit-plan`. No `PASS: evidence` is asserted; this stage does not advance itself.
- **Next action:** run `audit-plan` against this revision. On `PASS: evidence`, hand `factory-build` the goal, the confirmed decisions above, artifact paths, open questions and this next action, and begin **M1 (WU-1)** — in particular, implement the §4 rule table as written, with WU-7's exit criterion "`checklist.v1` byte-identical across a corrupt load" treated as non-negotiable. Do not load the following stage until that gate clears.
