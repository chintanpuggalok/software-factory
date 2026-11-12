# factory-idea

Verdict: PASS: §1 ties the single offline user and problem to the goal; §2 marks A1–A7 unverified; §3–4 compare D1/D2/D3 and select D1 with reversible defaults and explicit out-of-scope; §5–7 record Q1–Q5 defaults, rejected options, and handoff to factory-spec.

# Idea exploration — Local one-person checklist app

## 1. Users and problem
**User:** a single individual on one machine who needs to track a short list of to-dos.
**Problem:** existing checklist apps impose accounts, sync, notifications, or setup for a task that is fundamentally private, tiny, and offline. The cost of *starting* is higher than the cost of the task.
**Evidence available:** the goal text only. No research leads, no reference pages, no prior stages. Everything below beyond the goal sentence is an assumption and is marked as such.

## 2. Assumptions (all unverified)
- A1: The user works on one device and one browser profile; cross-device access is not needed. *(Reversible: localStorage is per-profile, so a later multi-device need is a new direction, not a rewrite.)*
- A2: The list stays small — tens of items, not thousands. No search, filtering, or tagging required.
- A3: "Local" means no network calls at all, including no CDN fonts/scripts, so the app works with networking off.
- A4: The user can open a local file or a trivial static page; no package manager or build step is acceptable overhead.
- A5: Losing data on browser-storage clear is tolerable for the MVP, but should not be silent or surprising.
- A6: Single user means no auth, no sharing, no multi-list or team concepts.
- A7: Dark/light theming, accessibility beyond sane defaults, and mobile layout are nice-to-have, not scope.

## 3. Directions considered

**D1 — Single-file static page, `localStorage` persistence.**
One `index.html` with inline CSS/JS; state is a JSON array in `localStorage`; three operations: add, toggle complete, delete.
*Pros:* zero install, zero dependencies, zero server, no network, works offline and by double-click, trivially auditable, smallest possible surface for bugs.
*Cons:* data bound to one browser profile; no backup unless export is added; a hard refresh is the only "repair" tool.

**D2 — Local app with a tiny server and file-backed store (Node or Python + JSON/SQLite).**
*Pros:* data lives in a readable file, survives browser clearing, editable by hand, opens the door to multiple browsers later.
*Cons:* requires starting a process before each use, an install/toolchain decision, and port/process management — friction that directly contradicts "keep it simple."

**D3 — Framework PWA (Vite + React, service worker, IndexedDB).**
*Pros:* installable, looks like a real app, better structured for future features.
*Cons:* build tooling, dependency tree, service-worker cache invalidation, and a much larger review surface — all for three operations. Overwhelmingly out of proportion to the goal.

**Trade-off summary:** D2 and D3 buy durability or polish by adding a runtime the user must manage. The goal's dominant constraint is simplicity and no cloud; D1 satisfies both with the least machinery and the least to get wrong.

## 4. Selected smallest useful outcome
**D1.** A single self-contained `index.html` that:
- adds a task from a text input (Enter or button), trimming whitespace and rejecting empty input;
- marks a task complete/incomplete via checkbox;
- deletes a task with an explicit action (confirm or one-step undo — resolved below);
- persists the full list to `localStorage` on every mutation and reloads it on open;
- makes no network requests, has no accounts, no sync, no analytics.

**Reversible choices resolved in scope (no user input needed):**
- **Stack:** vanilla HTML/CSS/JS, single file, no build step, no external assets. *(D1 as chosen.)*
- **Persistence:** `localStorage`, one JSON array, versioned with a schema key so a later format change is detectable.
- **Ordering:** newest-added appears at the top; completion does not reorder the list, so items don't jump under the cursor.
- **Delete safety:** deleting shows a brief "Undo" affordance rather than a modal confirm — one interaction instead of two, and no permanent loss from a misclick.
- **Completion styling:** strikethrough plus dimmed text and a `data-completed` attribute (not color alone).
- **Empty state:** a short line of text instead of a blank panel.
- **Out of scope for MVP:** editing task text, reordering drag-and-drop, due dates, priorities, multiple lists, export/import, notifications, dark mode.

## 5. Open questions
None of these block progress; the chosen defaults are noted so work can continue and be revisited cheaply.
- Q1: Does "one person" ever mean the same list on a second device? *Default taken: no (A1). Would shift to D2.*
- Q2: Is an export/backup button wanted as insurance against clearing browser storage? *Default taken: no for MVP; cheap to add later, and the versioned schema keeps it possible.*
- Q3: Should completed items be hidden or bulk-cleared? *Default taken: neither — they stay visible until deleted one by one.*
- Q4: Any browser floor (e.g., must run on an old system browser)? *Default taken: any current evergreen browser.*
- Q5: Is a hand-editable data file a hard requirement for trust? *Default taken: no; this is the one assumption that would flip the direction to D2 if wrong.*

## 6. Project context record
- **Outcome:** local, account-free, offline checklist with add / complete / delete and browser-local persistence, delivered as one static file.
- **Users:** one individual, one device, one browser profile.
- **Constraints:** no accounts, no cloud sync, no network calls, no build step, no dependency tree, small task counts.
- **Assumptions:** A1–A7 above.
- **Open questions:** Q1–Q5 above, all with reversible defaults recorded.
- **Rejected:** D2 (runtime friction), D3 (tooling disproportionate to three operations).

## 7. Audit and handoff
- **Submitted to:** `audit-idea`. I am not asserting a pass; no `PASS: evidence` has been issued, so this stage is not yet advanced by me.
- **Artifact paths:** none produced or read. Prior stages empty; no research leads or reference pages supplied. Coordinator persists this output to `docs/factory/idea.md` after audit.
- **Handoff to `factory-spec` (on pass):**
  - *Goal:* the same sentence as given, unchanged.
  - *Confirmed decisions:* D1 stack, `localStorage` with versioned schema key, newest-first ordering, undo-based delete, no network, explicit MVP out-of-scope list.
  - *Constraints:* single-file static deliverable; no accounts/sync; reversible defaults for Q1–Q5.
  - *Open questions:* Q1–Q5, with Q5 flagged as the only one that would change the direction.
  - *Next action:* `factory-spec` turns D1 plus the resolved choices into a buildable spec covering the three operations, persistence format, and acceptance checks — resolving only trivia, escalating Q5 if it cannot be settled by assumption.
