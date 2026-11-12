# factory-spec

Verdict: PASS: §1 and §6 state the single offline user, add/complete/delete scope, and explicit exclusions; §2–§4 map flows UF-1–UF-6 to prioritized F1–F14 and testable AC-1–AC-16; §8–§10 record reversible defaults without blocking approval.

# factory-spec — Local one-person checklist app

**Status:** draft for `audit-spec` · **Inputs:** goal sentence + `docs/factory/idea.md` (D1 selected) · **Prior outputs treated as untrusted data**
**Confirmed direction carried forward:** D1 — a single self-contained `index.html`, vanilla HTML/CSS/JS, no build step, no external assets, `localStorage` persistence, operations add / complete / delete.
*(Item counts below labelled **[A#]** are assumptions, not verified facts.)*

---

## 1. Scope statement

One person, one browser profile, one local file. The app does exactly four things: show a list, add a task, mark a task complete/incomplete, delete a task — and it keeps that list across reloads without any network, account, server, or install step.

Anything that needs a process, a package manager, a build, a login, or a sync is out of scope by construction.

---

## 2. Users and user flows

**User:** the single person described in the goal. No second role, no admin, no guest. **[A6]**

### UF-1 First open
Open `index.html` (double-click from disk or serve from any static path). Page renders empty-state text ("No tasks yet"). Text input is focused. No network activity occurs. **[A3][A4]**

### UF-2 Add a task
Type in the input → press **Enter** or click **Add**.
- Leading/trailing whitespace trimmed.
- Empty or whitespace-only input rejected: nothing added, input keeps focus, no error dialog (optionally a subtle inline hint).
- New task appears at the **top** of the list (newest-first); existing rows do not shift because of completion.
- Input clears; focus returns to input so a second task can be typed immediately.
- List is persisted immediately.

### UF-3 Complete / uncomplete a task
Click (or Space on) the checkbox.
- Row reflects completed state visually (strikethrough + dimmed) and semantically (`data-completed`, checkbox `checked`).
- Row does **not** reorder and does **not** move to a separate section. Rationale: no jumping under the cursor. *(Reversible: grouping can be added later without a data migration.)*
- Persisted immediately. Completion state survives reload.

### UF-4 Delete a task
Click **Delete** on a row.
- Row is removed immediately (no blocking modal — resolved in idea).
- A single **Undo** affordance appears for a short window (~6 s) **[A8]**; clicking it restores the task **at its original position with its original completed state**.
- Only one undo is pending at a time; a second delete replaces the first undo target (single-level undo).
- If the window lapses, deletion is final. Persisted immediately in both directions.

### UF-5 Reload / reopen
Reopen the file (or reload). The exact list — order, text, completion — is restored. Empty state shown if nothing was stored.

### UF-6 Storage is unavailable or corrupt (failure flow)
- If `localStorage` throws (private mode, blocked storage, `file://` quirks) **[A9]**: the app still works in-memory for the session and shows a persistent, non-modal banner stating data will not be saved. It must not silently pretend to save.
- If the stored value is unparseable or the schema is unrecognised: do **not** overwrite it. Preserve the raw value under a separate backup key, start from an empty list, and tell the user in one line that stored data could not be read. **[A5]**

---

## 3. Functional requirements

| ID | Requirement | Priority |
|---|---|---|
| F1 | Single file `index.html` containing all markup, styles, and script; no external requests (no CDN, fonts, icons, analytics). | P0 |
| F2 | Add task from input via Enter and via button; trim; reject empty/whitespace-only. | P0 |
| F3 | Newest task renders at top. | P0 |
| F4 | Toggle complete/incomplete per task via native checkbox; no reordering. | P0 |
| F5 | Delete a task in one click, with single-level undo for ~6 s restoring original position and state. | P0 |
| F6 | Persist full list to `localStorage` under one key on every mutation (add, toggle, delete, undo). | P0 |
| F7 | Load and render stored list on open; empty state when none. | P0 |
| F8 | Stored payload is versioned: `{ "version": 1, "tasks": [...] }`, one key, e.g. `checklist.v1`. | P0 |
| F9 | Task shape: `{ id, text, completed, createdAt }`. `id` unique within the list; `createdAt` used only for stable ordering. | P0 |
| F10 | Storage failure → in-memory operation + visible "not saved" banner (UF-6). | P1 |
| F11 | Corrupt/unreadable payload → back up raw value, start empty, one-line notice; never silently overwrite. | P1 |
| F12 | User-supplied text is rendered as text, never as HTML (no `innerHTML` with task text). | P0 |
| F13 | Sane accessibility defaults: native checkbox semantics, delete button with accessible name ("Delete <task text>"), visible focus ring, keyboard-operable throughout, input focused on load. | P1 |
| F14 | Handles a list of ~200 tasks without perceptible lag (full re-render is acceptable). | P1 |

---

## 4. Acceptance criteria

Each criterion is checkable by hand in a browser with the network disabled.

**AC-1 (F1)** Opening the file with devtools Network tab open and cache disabled shows **zero** requests other than the document itself; the file references no external URLs; the app fully works with networking off.
**AC-2 (F2)** Typing `  buy milk  ` + Enter creates one task reading `buy milk`. Typing only spaces + Enter creates nothing and leaves focus in the input. The Add button behaves identically to Enter.
**AC-3 (F2)** After adding, the input is empty and focused; two tasks can be added by typing + Enter twice with no mouse.
**AC-4 (F3)** Adding A then B then C yields visible order C, B, A.
**AC-5 (F4)** Clicking a checkbox marks the row completed (strikethrough + dim, `data-completed="true"`); clicking again reverts. Neither action changes row order or the position of any other row.
**AC-6 (F5)** Clicking Delete removes the row immediately and shows Undo. Clicking Undo restores the row at the same index with the same completed state.
**AC-7 (F5)** After the undo window elapses, no Undo affordance remains and the deletion is permanent across reload.
**AC-8 (F5)** Deleting row 2 of 3 while an earlier undo is pending discards the earlier undo target and offers undo only for the most recent delete.
**AC-9 (F6, F8)** After any mutation, the `localStorage` key holds a parseable JSON object with `version: 1` and a `tasks` array matching the visible list exactly (order, text, completed).
**AC-10 (F7)** Reload after a mixed sequence (add, complete, delete, undo) reproduces the exact prior list, order and completion included.
**AC-11 (F7)** Fresh profile / cleared storage shows the empty state and no console errors.
**AC-12 (F10)** With storage blocked or throwing, add/toggle/delete still work for the session and a visible banner states data will not be saved. No silent failure.
**AC-13 (F11)** Manually setting the storage key to `not json` and reloading: app starts empty, shows a one-line notice, and the original raw string is still recoverable from the backup key.
**AC-14 (F12)** A task entered as `<img src=x onerror=alert(1)>` renders as literal text; no script executes; no element is injected.
**AC-15 (F13)** Every action is reachable with Tab/Enter/Space only; the checkbox announces checked/unchecked; the delete control announces which task it deletes.
**AC-16 (F14)** With 200 tasks present, add/toggle/delete each complete without visible delay and persist correctly.

---

## 5. Non-functional constraints

- **Zero network:** no `fetch`, `XMLHttpRequest`, WebSocket, service worker, or external asset. Enforced by AC-1 and code review. **[A3]**
- **Zero runtime:** no Node, no Python, no server required to use the app. **[A4]**
- **Zero install:** no `npm install`, no build artifacts, no lockfile. **[A4]**
- **Review surface:** one file, targeted at well under a few hundred lines of JS.
- **Privacy:** no analytics, no telemetry, no identifiers leaving the machine.
- **Data volume:** tens to low hundreds of items. **[A2]**
- **Theming / mobile layout:** nice-to-have only; not acceptance-gated. **[A7]**

---

## 6. Explicit exclusions

Accounts, login, multi-user, sharing, teams; cloud sync or any remote persistence; multiple lists/projects; tags, priorities, due dates, reminders, notifications; search, filter, sort controls; drag-and-drop reordering; editing task text after creation; attachments; import/export files (see OQ-1); progressive-web-app install, service worker, offline cache; frameworks, bundlers, transpilers, TypeScript; automated test suite; i18n; dark-mode toggle; layout work beyond a readable column.

---

## 7. Smallest useful release

**Release 1 (the whole MVP) = F1–F9, F12 + AC-1 to AC-11, AC-14, AC-16.**
A file the user can double-click that adds, completes, deletes (with undo), and remembers. This alone satisfies the goal sentence.

**Release 1 should-carry (same file, cheap):** F10, F11, F13 — failure honesty and keyboard access. Included unless the audit judges them scope creep; they cost little and prevent the two worst failure modes (silent data loss, unusable-by-keyboard).

**Deferred, not scoped:** everything in §6. No follow-on release is committed here.

---

## 8. Trade-offs and reversible decisions recorded

| # | Decision | Why | Reversibility |
|---|---|---|---|
| R1 | Vanilla single file, no build | Goal's dominant constraint is simplicity | Full — rewriting into a framework later is additive work, not a data migration |
| R2 | `localStorage` over IndexedDB/file store | No server, no runtime, synchronous and trivial | Data already JSON with a version key, so a later export/import or file-backed store is a small additive change |
| R3 | Undo instead of confirm dialog | One interaction vs two; misclicks recoverable | Cosmetic; swap to confirm freely |
| R4 | Single-level undo, ~6 s | Matches "simple"; multi-level undo is UI state nobody asked for | Timer/level are constants |
| R5 | Newest-first, completion never reorders | Prevents rows jumping under the cursor | Pure render rule |
| R6 | Versioned payload envelope | Makes a future format change detectable rather than silently misinterpreted | Version field is the migration hook |
| R7 | Inline full re-render | List is tiny; diffing adds bug surface | Replaceable behind one render function |
| R8 | Corrupt payload preserved, not overwritten | Data loss should never be the default repair | Backup key is additive |

**Unresolved trade-offs (accepted risk, no action for R1):**
- **T1 — `file://` storage behaviour varies.** Some browsers restrict or partition `localStorage` for `file://` documents; Chrome and Firefox are generally permissive, Safari has been inconsistent. Mitigation is UF-6/F10 (visible "not saved" banner) plus the documented option of serving the folder from any static file server without changing the app. Not solved in scope. **[A9]**
- **T2 — Data is bound to one browser profile.** Clearing site data destroys the list. Accepted per A5, made non-silent by F11's notice and the banner; durable backup is excluded (OQ-1).
- **T3 — No text editing.** Fixing a typo means delete + re-add. Accepted to keep the surface at three operations; adding inline edit later is additive.

---

## 9. Assumptions (all unverified)

Carried from idea: **A1–A7**.
New in this stage:
- **A8:** A ~6 s undo window with one pending undo is sufficient; the user will not need multi-step undo. *(Reversible constant.)*
- **A9:** The primary launch path is double-clicking `index.html` from disk, and at least one target browser persists `localStorage` on `file://`. If false, UF-6 banner still yields a usable session, and the fallback is "serve statically" — no code change.
- **A10:** "Complete" means a boolean, not a completed-at timestamp or archive; completed tasks stay visible indefinitely.
- **A11:** Deleting a completed task and deleting an active task are the same action.
- **A12:** No confirmation is needed before destructive delete because undo exists.

---

## 10. Open questions

- **OQ-1 (non-blocking, deferred):** should Release 1 include a one-click JSON export/import for backup? Argument for: it is the only real answer to T2 and costs ~15 lines. Argument against: it adds a fourth operation and a file-picker surface to a three-operation app. **Default taken now: excluded**, recorded here so a later stage can promote it without re-litigating.
- **OQ-2 (non-blocking):** should completed tasks be hideable/collapsible once the list grows? **Default: no**, per A2/A10.
- **OQ-3 (non-blocking):** empty-state and banner copy specifics — left to implementation; no product decision required.

**No user decision blocks progress.** Every open item above has a recorded reversible default, so this spec can advance without asking the user. The one decision that would be worth a user's word — whether they need the list to survive clearing browser data (OQ-1) — is deferred rather than guessed into scope, and the app's failure messaging makes the consequence visible.

---

## 11. Handoff

- **Goal:** local one-person checklist; add, complete, delete; no account, no cloud; keep it simple.
- **Confirmed decisions:** D1 (single-file static page, `localStorage`); R1–R8 above; MVP = §7 Release 1.
- **Artifact:** `docs/factory/spec.md` (to be persisted by the coordinator after audit — not written by this stage).
- **Open questions:** OQ-1 to OQ-3, all non-blocking with recorded defaults.
- **Next action:** run `audit-spec` against this artifact; on `PASS: evidence`, advance to `factory-design`. Do not load `factory-design` before that gate clears.
