# factory-design

Verdict: PASS: §2 reports the missing taste index and marks its baseline as an instructed default; §3 labels Apple Reminders/Microsoft To Do/Todoist as unverified non-leaders and records market-share evidence as absent; §5–§6 cover all spec flows and states; §8 specifies keyboard, focus, live-region, contrast, reduced-motion and reflow behavior; §11–§12 record reversible defaults with F1–F14 traceability and no blocking user decision.

# factory-design — Local one-person checklist app

**Status:** draft for `audit-design` · **No approval claimed**
**Inputs:** goal + prior `idea` and `spec` outputs, treated as untrusted data
**Output target:** `docs/factory/design.md` — persisted by the coordinator only after a `PASS: evidence`

**Selected direction:** **Quiet column** — one screen, top capture field, native checkbox rows, always-visible Delete, single-level undo toast, persistent failure banners. No new product features.

---

## 1. Scope and design constraints

The design must serve exactly this product:

- one person, one browser profile, one local file;
- add, complete/incomplete, delete;
- newest task at top;
- completion never reorders rows;
- delete is reversible for a short window;
- persistence is invisible unless it fails;
- no account, cloud, network, build step, install, or server.

Explicitly excluded from the experience: editing task text, reordering, multiple lists, tags, priorities, dates, reminders, search/filter, hiding completed tasks, import/export, dark-mode toggle, onboarding, settings, and navigation.

**Design success condition:** the user can open the file and start typing immediately; every visible action is understandable without instruction; a misclick is recoverable; nothing pretends to save when it did not.

---

## 2. Taste baseline and gap

No taste index or taste records were supplied in the stage inputs. **Gap reported.** The baseline below is applied as an instructed default, not as a recorded taste decision.

Baseline: minimalism and Apple-inspired restraint — content first, generous whitespace, system typography, one primary accent, direct manipulation, quiet feedback, and no decoration that does not carry information. This is not a claim of Apple brand fit; no Apple assets, icons, fonts, or branding are used.

Design principles:

1. **One screen, one obvious action.** No menus, routes, modals, or settings.
2. **Familiar where it reduces learning.** Text field + Enter, checkbox, Delete, Undo.
3. **Reversible over interruptive.** Undo instead of a confirmation dialog.
4. **Visible state, not hidden gesture.** No swipe-only or hover-only destructive action.
5. **Feedback only when it matters.** No “saved” toast on every mutation; do show storage failure.
6. **Accessible by default.** Keyboard reachable, native semantics, visible focus, no color-only status.
7. **Motion explains, never entertains.** At most a short toast transition.

---

## 3. Market segment and reference status

**Working segment:** single-user personal task/checklist utilities used offline or local-first, with no collaboration or account requirement. Adjacent alternatives are paper checklists and general notes apps.

**Market leaders: none identified.** No reliable, dated market-share evidence was supplied. This brief therefore makes **no market-leader claim**.

**Unverified reference alternatives — not leaders:** Apple Reminders, Microsoft To Do, Todoist. These are named only as commonly encountered examples of the category. No claim is made about their current market share, current UI, or feature set.

**Sources, access dates, limits:**

| Input | Status | Use |
|---|---|---|
| Goal sentence | given | scope |
| `idea` / `spec` excerpts | prior outputs, untrusted | constraints, F/AC |
| Taste index | absent | gap reported |
| Research leads | `null` | no external study |
| Reference pages | `null` | no live inspection |
| Market-share evidence | absent | no leader claim |

No external pages, screenshots, analytics, or user testing were accessed. Pattern notes below are **category conventions and hypotheses**, not verified observations of any named product. No protected assets or branding are copied.

---

## 4. Patterns adopted and avoided

| Pattern | Decision | Reason |
|---|---|---|
| Persistent capture field; Enter submits | Adopt | Fastest path to the primary action |
| Leading checkbox; task text is its label | Adopt | Native semantics and a large target |
| Completion = checked + strikethrough + dim | Adopt | Redundant visual and semantic signal |
| Completed rows stay in place | Adopt | No jumping under the cursor |
| Destructive action at row end | Adopt | Predictable location |
| Undo snackbar after delete | Adopt | One interaction, recoverable |
| Swipe-to-delete or hover-only Delete | Avoid | Hidden, inaccessible, unnecessary |
| Confirmation modal before delete | Avoid | Slower; Undo is lighter |
| Separate “completed” section | Avoid | Breaks spatial memory |
| Inline text editing | Avoid | Out of scope |
| Counts, progress rings, streaks | Avoid | Not needed for three operations |
| Account, onboarding, sync status | Avoid | Contradicts the goal |

---

## 5. Core flow and screen model

**Single screen. No navigation. No modal dialogs.**

```
┌─────────────────────────────────────────┐
│ Checklist                               │
│ [ Add a task…                ] [ Add ]  │
│                                         │
│ ☐  Buy milk                      Delete │
│ ☑  Send report                   Delete │
│ ☐  Call Sam                      Delete │
│                                         │
│ No tasks yet. Add one above.            │  ← empty only
└─────────────────────────────────────────┘
                Task deleted.   Undo
```

**Core flow**

1. **Open** → title, add field focused, list restored or empty state shown.
2. **Type** → Add enables when trimmed input is non-empty.
3. **Add** → Enter or Add creates a row at the top; input clears and keeps focus.
4. **Scan** → rows are stable; completion does not reorder or hide anything.
5. **Complete** → click checkbox or task text; visual and semantic state update immediately.
6. **Delete** → row disappears; undo toast appears; focus moves to a safe place.
7. **Undo** → row returns to its relative position with its original completed state.
8. **Reload** → exact list, order, and completion state return.

**Focus order:** input → Add → each row’s checkbox → each row’s Delete → toast Undo, when present.

---

## 6. States and content

| State | UI | Behaviour and focus |
|---|---|---|
| First open, nothing stored | Title, add form, muted empty text | Input focused; no spinner; no network activity |
| First open, stored tasks | List newest-first | Input focused; list starts at top |
| Input empty or whitespace-only | Add disabled; no error text | Enter/click is a no-op; focus stays in input |
| Valid add | New row at top; input clears | Focus stays in input; polite “Task added.” |
| Toggle complete | Checkbox checked; strikethrough + dim; no reorder | Focus stays on the same checkbox; native state announcement |
| Delete | Row removed; toast with Undo | Pointer: focus next/previous checkbox or input. Keyboard: focus Undo. Timer pauses on hover/focus |
| Undo | Row restored at relative position and state; toast gone | Focus returns to restored task’s checkbox |
| Undo window expires | Toast disappears; deletion final | No extra message; focus unaffected |
| Second delete while undo pending | Previous undo target discarded; new toast replaces it | Single-level undo only |
| Reload | Exact list restored; undo does not survive reload | Input focused |
| Storage unavailable | Persistent amber banner above form; app works in-memory | No modal; no silent save |
| Corrupt payload | Raw value preserved under backup key; list starts empty; one-line notice | Backup before any overwrite; input focused |
| Long task text | Row wraps; Delete stays visible | Full text in accessible names |
| 200 tasks | Scrollable list; no virtualization | Full render acceptable if focus is preserved by task id |
| Keyboard-only | Visible focus ring; all controls reachable | No hover-only actions |
| Reduced motion | Toast appears without motion | No decorative animation |
| Narrow viewport | One column; no horizontal scroll; 44 px targets | Touch works; hover not required |

**Copy**

- Title: `Checklist`
- Input label: `New task` *(visually hidden)*
- Placeholder: `Add a task`
- Add button: `Add`
- Empty: `No tasks yet. Add one above.`
- Delete accessible name: `Delete task: {task text}`
- Delete visible label: `Delete`
- Toast: `Task deleted.` + `Undo`
- Storage banner: `Changes won’t be saved. This browser is blocking local storage.`
- Corrupt notice: `Saved tasks couldn’t be read. The old data was kept, and the list starts empty.`
- Live-region additions: `Task added.` / `Task restored.`

**Undo positioning detail:** store the deleted task plus its neighbouring task ids. On undo, insert before the next surviving neighbour; otherwise after the previous one; otherwise at the stored index. This preserves the task’s relative position even if new tasks were added at the top during the undo window.

---

## 7. Visual direction

**Layout:** centred white surface on a light neutral page. Max width ~40 rem. One column. Page padding 24 px desktop, 16 px narrow. No sidebar, tabs, or card grid.

**Type:** system UI stack only. Base 16 px, line-height 1.5. Title 22 px/600. Task text 16 px/400. Secondary/help 13 px/400. Buttons 15 px/500.

**Core tokens**

| Role | Value |
|---|---|
| Page background | `#F5F5F7` |
| Surface | `#FFFFFF` |
| Primary text | `#1D1D1F` |
| Secondary text | `#6E6E73` |
| Hairline separator | `#E5E5EA` |
| Control border | `#8E8E93` |
| Accent / focus | `#0066CC` |
| Danger text | `#B42318` |
| Warning background | `#FFF4D6` |
| Warning text | `#5C3D00` |
| Warning border | `#C99700` |
| Toast background | `#1D1D1F` |
| Toast text | `#FFFFFF` |
| Toast Undo | `#8EC5FF` |

**Components**

- **Header:** `Checklist`, no subtitle, no count.
- **Add form:** input + `Add` button, 44 px high, gap 8 px. Input has a visible border and hidden label. Add is filled accent when enabled; neutral disabled state with readable text, no opacity fade.
- **Task row:** native checkbox 20 px with a 44 px label target; text flexes and wraps; `Delete` is a text button, always visible, muted by default, danger on hover/focus. Hairline separators, no per-row card. Completed text is strikethrough and secondary-coloured; checkbox remains checked. `data-completed="true"` supports styling.
- **Empty state:** muted, left-aligned in the list area. No illustration.
- **Toast:** bottom centre, dark, radius 12 px, padding 12×16 px, max width ~32 rem, single level. `Undo` is a clearly focusable button. No countdown.
- **Banners:** full-width warning strip inside the card, 3 px left border, 13–14 px text. Persistent, non-modal, not dismissible in R1.
- **Motion:** toast fades/slides 8 px over ~140 ms. Hover/focus transitions ~120 ms. No row animations. `prefers-reduced-motion` removes the toast motion.
- **Assets:** no external fonts, icons, images, or scripts. Native checkbox only.

---

## 8. Interaction and accessibility

- **Semantics:** `<main>`, one `<h1>`, `<form>`, `<ul>/<li>`, native `<input type="checkbox">`, `<label>` associated with each task, `<button type="button">` for Delete.
- **Names:** input has a real label; each Delete control announces `Delete task: {text}`; task text is the checkbox label.
- **Focus:** input focused on load; after add, focus returns to input; after toggle, focus stays on the same checkbox — if the list is fully re-rendered, restore focus by task id; after pointer delete, focus the next/previous row checkbox or input; after keyboard delete, focus the toast Undo button and pause the timer; after undo, focus the restored task’s checkbox.
- **Live regions:** one visually hidden polite region for `Task added.` and `Task restored.` The toast text uses `role="status"`. Completion relies on the native checkbox announcement; no duplicate completion announcement.
- **Timing:** undo lasts ~6 seconds. The timer pauses while the toast is hovered or focused, so keyboard users are not forced to race it. If focus leaves, the remaining/restarted window applies; deletion becomes final when it expires.
- **Contrast:** text and focus indicators target WCAG AA. Completion is not communicated by colour alone: checkbox state + strikethrough + dimmed text.
- **Targets:** all interactive controls at least 44×44 px effective target.
- **Reflow:** works at 320 CSS px and at 200% zoom without horizontal scrolling.
- **No hidden actions:** Delete is always visible; no swipe, long-press, or hover-only menu.
- **Safety:** task text is rendered as text, never HTML. No task text is interpolated into markup.
- **Failure honesty:** storage failure is visible and persistent; corrupt data is not overwritten before preservation; no “saved” confirmation appears when storage is unavailable.

---

## 9. Directions considered

| Direction | Description | Verdict |
|---|---|---|
| **A — Quiet column** | Centred single column; top capture field; checkbox rows; always-visible Delete; bottom undo toast | **Selected** |
| **B — Capture bar** | Full-bleed mobile-style list with fixed bottom composer and swipe/overflow delete | Rejected for R1: hidden destructive gesture, fixed bar overlays content, more chrome, less keyboard-natural |
| **C — Focus cards** | One task at a time or large stacked cards with progress treatment | Rejected: poor scanning, extra navigation, visual weight disproportionate to three operations |

**Why A:** it uses the most familiar desktop checklist conventions, keeps every action visible, is naturally keyboard-operable, and adds no machinery beyond the spec. It is the lowest-learning, lowest-risk expression of “keep it simple.”

**Deliberate departures from familiar checklist apps**

- No inline editing: fixing a typo means delete + re-add. Accepted to keep the surface at three operations.
- No delete confirmation: Undo replaces it. One interaction instead of two.
- No completed section or hiding: rows stay put, preserving spatial memory.
- Newest-first rather than append-at-bottom: a new task is visible without scrolling.
- No counts/progress: the list itself is the status.

---

## 10. Decisions and assumptions

| # | Decision | Reversibility |
|---|---|---|
| DD-1 | Single screen, no navigation or settings | Additive later |
| DD-2 | Desktop-first quiet column; responsive but not mobile-first | Layout-only change |
| DD-3 | Add form at top; newest task at top | Render rule |
| DD-4 | Native checkbox leads each row; task text is its label | Component-level |
| DD-5 | Delete is always-visible text, not an icon or hidden menu | Cosmetic |
| DD-6 | Single-level undo toast, ~6 s, pauses on hover/focus | Constants |
| DD-7 | No confirmation modal | Cosmetic |
| DD-8 | Completed rows do not reorder or hide | Render rule |
| DD-9 | Persistent storage/corruption banners, non-modal | Copy/layout |
| DD-10 | System fonts, native checkbox, no external assets | Fully reversible |
| DD-11 | No count, progress, theme toggle, or settings in R1 | Additive later |
| DD-12 | Long task text wraps fully; no truncation | CSS-only |

**Assumptions**

- **AD-1:** Desktop/laptop with keyboard and mouse is the primary context; mobile works but is not acceptance-gated. *(A7)*
- **AD-2:** A ~6 s single-level undo is sufficient; pausing on hover/focus is an accessibility exception, not a new feature. *(A8)*
- **AD-3:** Always-visible `Delete` text is clearer than an icon-only control and avoids external icon assets.
- **AD-4:** Add is disabled when trimmed input is empty; no inline error copy is needed.
- **AD-5:** No task count or progress indicator is wanted; the empty state is the only summary.
- **AD-6:** No dark theme or theme toggle in R1.
- **AD-7:** Long text should wrap rather than truncate; the user should not lose task content.
- **AD-8:** Undo state is session-only; reload commits the deletion. This matches immediate persistence.
- **AD-9:** Storage/corruption notices persist for the session; no dismiss control in R1.
- **AD-10:** Clicking task text toggles completion, giving a larger target than the checkbox alone.

---

## 11. Open questions

All have reversible defaults; none blocks progress.

- **OQ-D1:** Should keyboard-delete focus the Undo button, while pointer-delete focuses the next row? **Default: yes.** If this feels too modality-specific in build, fall back to always focusing the next row and keeping Undo in tab order.
- **OQ-D2:** Should Add be disabled when empty, or always enabled with a no-op? **Default: disabled.** Reversible.
- **OQ-D3:** Should long task text be capped at a few lines? **Default: no cap.** Reversible CSS.
- **OQ-D4:** Should warning banners be dismissible? **Default: no.** Persistence keeps the warning honest.
- **OQ-D5:** Is ~6 s the right undo window? **Default: yes, with pause on hover/focus.** Constant.
- **OQ-D6:** Should completion changes be announced in a live region? **Default: no**, rely on the native checkbox state to avoid double announcements.

Spec OQ-1 (export/import for backup) remains deferred and out of scope; this design does not reopen it.

**Blocking user decision: none.** Every choice above is reversible and inside the approved scope.

---

## 12. Traceability to the approved spec

| Spec item | Design response |
|---|---|
| F1 single file, no external requests | System fonts, native controls, no assets or network references |
| F2 add via Enter/button, trim, reject empty | Top form; disabled Add when empty; focus stays in input |
| F3 newest at top | New rows prepend; list stable |
| F4 toggle without reorder | Native checkbox; strikethrough + dim; no movement |
| F5 delete + single-level undo | Always-visible Delete; bottom toast; neighbour-based restore |
| F6/F7 persistence and reload | Invisible on success; exact list restored; no spinner |
| F8/F9 versioned payload, task shape | No UI surface; implementation detail |
| F10 storage failure | Persistent warning banner; in-memory operation |
| F11 corrupt payload | Backup preserved; empty list; one-line notice |
| F12 text rendered as text | `textContent` only; no HTML interpolation |
| F13 accessibility | Native semantics, labels, focus management, live regions, 44 px targets, visible focus |
| F14 ~200 tasks | Scrollable single list; full render allowed with focus restoration |

---

## 13. Audit and handoff

- **Audit target:** `audit-design`. No `PASS: evidence` is asserted; this stage is not advanced by this output.
- **Artifact paths:** inputs are the prior `docs/factory/idea.md` and `docs/factory/spec.md` outputs; output target is `docs/factory/design.md`, to be persisted by the coordinator after audit. **No files were written by this stage.**
- **Goal carried forward:** local one-person checklist; add, complete, delete; no account or cloud; keep it simple.
- **Confirmed decisions carried:** D1 single-file static page with `localStorage`; add/complete/delete only; newest-first; completion never reorders; single-level undo; no network/account/sync; explicit exclusions from the spec.
- **Design decisions:** Quiet column; top capture field; native checkbox rows; always-visible Delete; bottom undo toast with pause-on-focus; persistent failure banners; system typography and no external assets.
- **Open questions:** OQ-D1 to OQ-D6, all non-blocking with recorded defaults. Spec OQ-1 remains deferred.
- **Next action:** run `audit-design` against this output. On `PASS: evidence`, hand off to the build/implementation stage. Do not load the next stage before that gate clears.
