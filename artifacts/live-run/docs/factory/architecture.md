# factory-architecture

Verdict: PASS: §2 lists scale targets with UNK2–UNK6 marked unknown and 12 KB/quota as unmeasured estimates; §6 compares A/B/C with rejection reasons; §7 covers storage-blocked, quota, corrupt, backup-failure, timer-throttle and multi-tab recovery plus textContent/CSP security; §8 flags LIM-1–LIM-6; §9 gives growth change triggers; §10 records reversibility and "No approval claimed"; next action is audit-architecture itself.

# factory-architecture — Local one-person checklist app

**Status:** draft for `audit-architecture` · **No approval claimed** · **Nothing executed:** no files written, no browser opened, no code built by this stage.
**Inputs (untrusted data):** goal sentence; prior `idea`, `spec`, `design` outputs. Research leads `null`; reference pages `null`. No external sources were consulted and none are cited.
**Selected direction carried forward:** D1 — one self-contained `index.html`, vanilla HTML/CSS/JS, no build, no network, `localStorage` persistence, add / complete / delete with single-level undo.
*(Items marked **[A#]**, **ARCH-A#**, **UNK#** are assumptions/unknowns, not verified facts.)*

---

## 1. Scope, constraints, existing contracts

Constraints inherited and non-negotiable for this stage: zero network requests, zero runtime process, zero install/build, single file, one user, one browser profile, `localStorage` as the only store, three operations plus undo.

**Contracts already fixed upstream (treated as input, not reopened):**

| Contract | Source | Binding on architecture |
|---|---|---|
| Storage key `checklist.v1`, payload `{"version":1,"tasks":[…]}`, task `{id,text,completed,createdAt}` | spec F8/F9 | Storage adapter serialises exactly this; no extra fields in R1 |
| Newest-first order; completion never reorders | spec F3/F4, design DD-3/DD-8 | Ordering authority is the array, not a sort |
| Single-level undo, ~6 s, pause on hover/focus, neighbour-based restore | spec F5/AC-8, design §6 | Undo state is ephemeral, derived, never persisted (design AD-8) |
| Text rendered as text only | spec F12/AC-14 | `textContent` exclusively; no HTML interpolation anywhere |
| Corrupt payload preserved before any overwrite | spec F11/AC-13 | Write-order rule: backup succeeds before primary is touched |
| Storage failure visible and persistent | spec F10/AC-12 | Save path returns a result; there is no optimistic "saved" state |

Out of scope at this stage, unchanged: accounts, sync, search/filter/sort, editing text, reordering, multiple lists, import/export (spec OQ-1 deferred), PWA/service worker, frameworks, automated test suite.

---

## 2. Scale targets, load, and unknowns

Nothing here is a business target; these are the numbers the design must not exceed. **Values not supplied upstream are marked UNK rather than invented.**

| Dimension | Value used | Status |
|---|---|---|
| Concurrent users | 1 human | [[A6] given] |
| Concurrent writers | 1 tab typical; **UNK2** whether multiple tabs of the file are ever open at once | Unknown |
| Network traffic | 0 requests, 0 bytes | [spec F1/AC-1] |
| Tasks per list | tens typical, 200 is the acceptance ceiling | [spec F14/AC-16, A2] |
| Payload size at 200 tasks | ~12 KB estimated (200 × ~60 B) | Estimate, unmeasured |
| Store quota | **UNK3** browser-dependent, commonly ~5 MB | Not verified |
| Mutations per session | low tens | Assumption [ARCH-A2] |
| Reads | one per page load | Given by design |
| Availability target | none; no SLA, no server | Given |
| Durability | until browser storage is cleared | [A5, T2] |
| Budget | $0; no services, no spend | Stage rule |
| Growth plan | none in R1 | Given |

**Implication:** every load concern is trivial except *durability* and *failure honesty*, which are the two axes the architecture must actually defend. Write amplification of whole-list saves is bounded and irrelevant at 12 KB.

---

## 3. Domain model and invariants

**Entities**

- `Task`: `id: string` (unique in list), `text: string` (trimmed, non-empty), `completed: boolean`, `createdAt: number`.
- `PersistedPayload`: `{ version: 1, tasks: Task[] }`.
- `AppState`: `{ tasks: Task[], persistence: 'ok' | 'unavailable' | 'recovered', pendingUndo: PendingUndo | null }`.
- `PendingUndo` (ephemeral, memory only): `{ task: Task, prevId: string|null, nextId: string|null, index: number, remainingMs: number, paused: boolean }`.

**Invariants**

1. `tasks[i].text === tasks[i].text.trim()` and is non-empty for every rendered row.
2. `id` is unique within `tasks`; ids of removed tasks may be reused only after their undo window ends (no stronger guarantee needed).
3. Array index 0 is the top row. **Order is the array; `createdAt` is diagnostic only.** *Interpretation of spec F9 recorded explicitly* (see ARCH-D5).
4. `completed` is a boolean, never a timestamp or archive flag [A10].
5. A `PersistedPayload` read from storage is accepted only if it is valid JSON, an object, `version === 1`, `tasks` is an array, and **every** item passes task validation. Partial salvage is deliberately not attempted (ARCH-D3).
6. `pendingUndo` is never serialised and never survives reload.

**Rejected states and guards**

| Invalid state | Guard |
|---|---|
| Empty/whitespace-only task | Trim → reject; no state change, no write |
| Toggle/delete on unknown id | No-op; do not write, do not announce |
| Undo with `pendingUndo === null` | No-op |
| Undo after its target already restored | Impossible: restore clears `pendingUndo` synchronously |
| Duplicate id after add | Id generator retries while the id exists in `tasks` |
| Two tasks with identical `createdAt` | Harmless — order is array order, no sorting |
| Envelope with future/unknown `version` | Treated as unreadable: backup, empty list, notice (never migrated) |
| Non-array `tasks`, non-object item, missing field, wrong type | Whole payload treated as unreadable (ARCH-D3) |
| `localStorage` getter/setter throws | Session runs in memory, banner shown (ARCH-D4) |

---

## 4. State transitions

Pure reducer `reduce(state, event) → { state, effects[] }`, where effects are `persist`, `showToast`, `hideToast`, `announce`, `focus(intent)`. No reducer branch touches DOM or storage (ARCH-D6).

| Event | Guard | State change | Effects |
|---|---|---|---|
| `LOAD_OK(payload)` | valid | `tasks = payload.tasks` (order preserved verbatim), `persistence='ok'`, `pendingUndo=null` | render, focus input |
| `LOAD_EMPTY` | key absent | `tasks=[]`, `persistence='ok'` | render, focus input |
| `LOAD_CORRUPT(raw)` | unreadable | **backup first**; only on backup success `persistence='recovered'`, `tasks=[]`; on backup failure `persistence='unavailable'` and primary untouched | banner/notice, render |
| `LOAD_UNAVAILABLE` | storage throws on read | `persistence='unavailable'`, `tasks=[]` | banner, render |
| `ADD(rawText)` | `rawText.trim() !== ''` | prepend task | persist, clear+focus input, announce "Task added." |
| `ADD('')` / `ADD('  ')` | — | none | none (no error dialog) |
| `TOGGLE(id)` | id exists | flip `completed` in place, index unchanged | persist, render, focus same id |
| `DELETE(id)` | id exists | capture `{task, prevId, nextId, index}` as `pendingUndo` (replaces any existing), remove from array | persist, show toast, focus next-row (`pointer`) or toast Undo (`keyboard`) |
| `UNDO` | `pendingUndo !== null` | reinsert per §5 rule; `pendingUndo=null` | persist, hide toast, focus restored id, announce "Task restored." |
| `UNDO_EXPIRED` | `now ≥ deadline` | `pendingUndo=null` | hide toast |
| `SAVE_FAILED` | setter throws | `persistence='unavailable'` | banner (no retry loop) |
| `SAVE_OK` | success | `persistence='ok'` | no UI change (no "saved" toast — design principle 5) |

**Ordering of a delete→undo pair relative to concurrent adds** is defined by neighbour ids, not by index: if `prevId` still exists insert immediately after it; else if `nextId` exists insert immediately before it; else insert at `min(index, length)`. This satisfies AC-6/AC-8 and design §6 even when tasks were added at the top during the window.

---

## 5. Interfaces and module boundaries

One file, but six logical modules with explicit contracts. Boundaries exist so each can be reasoned about and replaced without touching the others.

| Module | Contract | May touch |
|---|---|---|
| `storage` | `load() → {status:'ok'\|'empty'\|'corrupt'\|'unavailable', tasks?, raw?}`; `save(tasks) → 'ok'\|'unavailable'`; `backup(raw) → boolean` | `localStorage` **only here** |
| `domain` | `validatePayload(raw) → {ok, tasks?}`; `makeTask(text) → Task`; pure helpers | nothing |
| `reduce` | `reduce(state, event) → {state, effects}` | nothing |
| `render` | `render(state, focusIntent)`; writes text via `textContent`; stamps `data-task-id` / `data-completed` | DOM only |
| `controller` | event listeners, undo deadline/pause bookkeeping, announcements, focus intents | `domain`, `reduce`, `render`, `storage` |
| `boot` | read once, dispatch `LOAD_*`, wire listeners | `controller` |

**Key interface decisions**

- **ARCH-D1 — One key, whole-list writes.** No per-task keys. Cost: full JSON re-serialisation per mutation (~12 KB ceiling). Benefit: the list is atomic and always consistent; AC-9 is trivially true; no orphan-key garbage. Reversible behind `storage` alone.
- **ARCH-D2 — Synchronous write on every mutation, no debounce.** AC-9 requires the key to match the visible list after *any* mutation; a debounce window would make reload-after-immediate-mutation lossy. At these sizes the write is sub-millisecond.
- **ARCH-D3 — Strict payload validation, no partial salvage.** Salvaging valid items out of a damaged payload would silently drop the rest. Strict rejection routes to the corrupt path, which preserves the raw bytes — the conservative choice, and fewer code paths.
- **ARCH-D4 — Degrade to memory, never lie.** A single `persistence` flag drives the banner. No optimistic UI, no retry storm; each later mutation simply tries again.
- **ARCH-D5 — Array order is authoritative; no sort on load.** Sorting by `createdAt` would reorder ties and any user whose clock moves backwards. Recorded as the architectural reading of spec F9 ("stable ordering"); reversible by changing one function.
- **ARCH-D6 — Pure reducer + effects, full re-render.** No DOM diffing, no framework. Focus is restored by `data-task-id` after render, which is what makes full re-render safe for keyboard users (design §8) and keeps 200-row re-renders well inside AC-16.
- **ARCH-D7 — Deadline-based undo timing, not timer-driven correctness.** `pendingUndo` carries `remainingMs`; expiry is evaluated against `Date.now()` on the timer tick *and* lazily on any interaction. Background-tab timer throttling therefore cannot leave a toast tappable past its window or fire an early expiry. Pause-on-hover/focus = freeze `remainingMs`.
- **ARCH-D8 — Ids without network.** `crypto.randomUUID()` when available, else `t-<base36 time>-<counter>`, retried while the id already exists. Neither form is a durable global identifier, and nothing depends on it. **UNK4:** whether `randomUUID` is exposed on `file://` in every target browser — hence the fallback exists.

**Rationale for one file with internal boundaries rather than several files:** spec F1 forbids external requests, so a separate `.js` file is an extra GET (and a `file://` CORS failure in some browsers). Boundaries are therefore documentation-and-discipline, not separate artifacts.

---

## 6. Designs compared

| | **A — Reducer + single storage adapter (chosen)** | **B — DOM-as-state** | **C — Per-task keys + `storage`-event coherence** |
|---|---|---|---|
| Where truth lives | `AppState.tasks` in memory; DOM is a projection | The DOM rows; list re-derived by querying them on each mutation | Same as A, but one `localStorage` key per task + one index key |
| Persistence | One atomic whole-list `setItem` | Same, after scraping the DOM | N+1 writes per mutation; multi-key updates are not atomic |
| Complexity | 6 small modules; reducer is pure and inspectable | Fewer concepts, less code | Highest: key lifecycle, orphan keys, migration, write-ordering, quota spread |
| Recovery | Corrupt → raw preserved, empty list, notice | Corrupt handling tangles with rendering (state is markup) | Partial-write states produce a list that never existed; recovery is materially harder |
| Multi-tab | Last-writer-wins (**LIM-1**) | Same | `storage` events give near-live coherence by construction |
| Scale headroom | Fine to ~low thousands of tasks | Fine to 200; DOM queries get slow after that | Fine, but write cost and key count grow with tasks |
| Ops cost | zero | zero | zero, but more failure surface for no user-visible gain at 200 tasks |
| Fit to goal ("keep it simple") | Best: atomicity and honesty for the least machinery | Simple to write, hard to keep honest — persistence depends on markup staying parseable | Solves a concurrency problem **UNK2** says we may not have |

**Rejected B:** state in markup means a rendering change silently changes the data model, and "save what the DOM says" is one careless `innerHTML` away from violating AC-14. **Rejected C:** it buys cross-tab coherence the spec never asked for, at the cost of atomicity — the one property that makes the corruption path simple and the AC-13 test passable. **D2 (file-backed local server) and D3 (framework PWA) were rejected at the idea stage and are not reopened here.**

---

## 7. Failure modes and recovery

| Failure | Detection | Behaviour | Residual risk |
|---|---|---|---|
| `localStorage` blocked/throwing (private mode, `file://` policy) | throw on read or write | In-memory session + persistent banner; no false "saved" | Data lost at tab close — visible, not silent. **UNK5** which target browsers this hits |
| Quota exceeded mid-session | `setItem` throws | Switch to `unavailable` + banner | Unlikely at ~12 KB |
| Corrupt JSON / bad shape / unknown version | validation in `storage.load` | Backup raw → empty list → one-line notice | Only one backup copy kept (**LIM-2**) |
| Backup write itself fails | `backup()` returns false | **Do not clear or overwrite the primary key**; start in memory with banner | User sees a banner instead of silent destruction |
| Timer throttling in a background tab | deadline comparison, not timer firing | Undo expires correctly; no stale toast | None material |
| Immediate reload mid-undo | `pendingUndo` never persisted | Deletion is final, as designed (AD-8) | Expected |
| User clears site data externally | Next save recreates the key | Session state remains authoritative until reload | Accepted [T2] |
| Add/toggle/delete on unknown id | reducer guard | No-op, no write | None |
| Two tabs open (if **UNK2** is ever true) | Not detected | Last write wins; a stale tab can overwrite | **LIM-1**, accepted for R1; mitigation is a ~6-line `storage` listener deferred to a later release |
| Focus loss after full re-render | focus restored by `data-task-id` | Focus lands on the same task after toggle; on next/previous row after pointer delete; on Undo after keyboard delete | Design OQ-D1 already allows one fallback |

**Recovery story overall:** the app has no server and no backup service, so recovery = *do not destroy what you cannot parse* (ARCH-D3, backup-before-overwrite) + *do not claim success you did not get* (ARCH-D4). Those two rules are the entire durability architecture.

**Security:** single local document; no network, no eval, no dynamic script, no `innerHTML` with user text. Recommended hardening: a `<meta http-equiv="Content-Security-Policy">` of `default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'`, which mechanically enforces AC-1. **UNK6:** unverified that this directive set breaks nothing on `file://` — must be confirmed in build; if it does, drop the meta tag, not the feature.

---

## 8. Limits

- **LIM-1:** no cross-tab coherence; concurrent tabs can clobber each other (last writer wins).
- **LIM-2:** one corrupt-payload backup slot; a second corruption overwrites the first. Bounded deliberately to avoid key sprawl/quota games.
- **LIM-3:** data bound to one browser profile; clearing site data is unrecoverable (no export in R1, spec OQ-1 deferred).
- **LIM-4:** `file://` storage behaviour is browser-dependent; the fallback is serving the folder statically with no code change [A9, T1].
- **LIM-5:** no text editing; typo = delete + re-add [T3].
- **LIM-6:** full re-render per mutation; comfortable at 200 tasks, not designed for thousands.

---

## 9. When this design must change

- Need for multi-device, sharing, or surviving storage clear → new persistence direction (D2 file-backed store, or the deferred export/import): **replace the `storage` module and the payload envelope; reducer and render survive.**
- Multiple tabs/processes become real → per-key store or `storage`-event sync plus conflict rules; today's answer is LIM-1.
- Task counts reach thousands or search/filter is requested → IndexedDB with a query layer; the reducer's event vocabulary is reusable, `render` is not.
- A formally verified accessibility or i18n obligation appears → `render` and copy layer change; domain does not.
- A target browser turns out not to persist `localStorage` on `file://` **and** static serving is unacceptable → the goal's "keep it simple" trade-off must be re-decided with the user (this is the one place the architecture would need a *user* decision, not an assumption).

---

## 10. Decisions and assumptions recorded

| # | Decision | Reversibility |
|---|---|---|
| ARCH-D1 | Single `checklist.v1` key, atomic whole-list writes | Storage-module swap only |
| ARCH-D2 | Synchronous save on every mutation, no debounce | Constant |
| ARCH-D3 | Strict payload validation; no partial salvage; corrupt → preserve raw | Validation function only |
| ARCH-D4 | Persistence flag degrades to in-memory + persistent banner; no false success | Copy/flag |
| ARCH-D5 | Array order authoritative; `createdAt` diagnostic; never sorted on load | One function |
| ARCH-D6 | Pure reducer + effects; full re-render; focus restored by task id | Render internals |
| ARCH-D7 | Deadline-based undo timing with pause-on-hover/focus | Constants |
| ARCH-D8 | Client-side id generation with collision retry | Local |
| ARCH-D9 | Six logical modules inside one file (F1 forbids external script requests) | Refactorable |
| ARCH-D10 | Backup-before-overwrite; abort clearing if backup failed | Code path |
| ARCH-D11 | Recommended restrictive CSP meta tag (pending build verification) | Delete one line |

**Assumptions (unverified):** ARCH-A1 the primary launch path is double-clicking `index.html` [A9]. ARCH-A2 a session produces low-tens of mutations, so whole-list writes are never a bottleneck. ARCH-A3 200 tasks ≈ 12 KB, comfortably inside any plausible quota. ARCH-A4 `crypto.randomUUID` may be missing on `file://`, so the fallback is required. ARCH-A5 `'unsafe-inline'` CSP is acceptable because the document is local and single-origin — there is no untrusted code to inject. ARCH-A6 single-level undo state can live purely in memory with no persistence. **Unknowns:** UNK2 multi-tab reality; UNK3 browser quota; UNK4 `randomUUID` availability; UNK5 which browsers block `file://` storage; UNK6 CSP behaviour on `file://`. **Evidence available:** the goal sentence and prior stage documents only. No market-share evidence, no browser testing, no reference pages (`null`), no profiling. Every numeric claim above is an estimate or inherited from a prior stage.

**Blocking user decision: none.** Every choice is reversible within approved scope, and each has a recorded fallback. Spec OQ-1 (export/import) remains deferred; this stage does not promote it.

---

## 11. Handoff

- **Goal carried forward (unchanged):** local one-person checklist; add, complete, delete; no account or cloud sync; keep it simple.
- **Architecture:** one `index.html`; `storage` / `domain` / `reduce` / `render` / `controller` / `boot` boundaries; `{version:1,tasks[]}` under `checklist.v1`; atomic synchronous saves; deadline-based single-level undo restoring by neighbour ids; memory-only degradation with a persistent banner; backup-before-overwrite on corrupt reads.
- **Limits flagged for build and later stages:** LIM-1 (multi-tab), LIM-2 (single backup slot), LIM-3 (profile-bound data), LIM-4 (`file://` variance), LIM-5 (no edit), LIM-6 (full re-render).
- **Build-time verification items (no tests written by this stage):** AC-1 (zero requests, plus CSP interaction — UNK6), AC-9/AC-13 (payload shape and corrupt-backup ordering), AC-12 (blocked storage), AC-14 (text-only rendering), AC-16 (200-task responsiveness — UNK3/ARCH-A3 estimates unmeasured), and `file://` persistence on at least one target browser (UNK5).
- **Artifact:** output target `docs/factory/architecture.md`, to be persisted by the coordinator **after** audit. No files were written by this stage.
- **Audit target:** `audit-architecture`. No `PASS: evidence` is asserted; this stage does not advance itself.
- **Next action:** run `audit-architecture` against this output. On `PASS: evidence`, advance to the build/implementation stage. Do not load the next stage before that gate clears.
