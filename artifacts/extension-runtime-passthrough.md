# Extension runtime passthrough review

## Scope
The author updated the `/factory` extension to pass `--runtime` to the coordinator and fixed the plan-mode arguments. This is a self-review, not an independent audit. The extension UI (`factory.ts`) was not exercised in a live Pi TUI; the testable core and the real coordinator spawn were.

## Evidence
- `node --test tests/test_extension_core.mjs`: 17 tests passed, including new tests for runtime parsing (both `--runtime=v` and `--runtime v`), unknown-runtime rejection, exact plan-mode and build-mode argument lists, and a real coordinator spawn with `--runtime codex` that failed closed with `BLOCKED: codex adapter is not implemented`, exit 2, no model calls.
- `python3 -m unittest discover -s tests -v`: 92 tests passed.
- Before this change, the plan path built `[workspace, --goal, goal, --progress]` with no `--mode`, so `/factory plan` ran the deterministic simulator while the confirmation dialog promised up to 13 model calls. A scratch coordinator run reproduced it: it wrote `.factory/state.json` and no `pi-plan.json`.

## Design
- `buildCoordinatorArgs` now takes an explicit `mode`: `plan` (pi-plan with spend confirmation, no build), `build` (pi-plan plus `--build-static` and the acceptance contract), and `simulate` (plain progress args).
- `--runtime` is a value option validated against the implemented set (`pi`, `opencode`), which mirrors `factory.py`. Unknown values are rejected at parse time, before any confirmation dialog or process.
- The widget shows the selected runtime from the first stage; saved extension options keep the choice for later inspection.
- Plan-mode runs now also carry `--research-query` and `--reference-url`, which the old plan path dropped.

## Limits
- No live plan or build was run through the extension wiring in this review; the coordinator's plan path was already verified by the live run in `artifacts/live-run-review.md`, and the OpenCode adapter was verified separately.
- The runtime list is duplicated between the extension and `factory.py`; a third adapter must update both.

## Next action
Define a deployment target and release contract, then decide the metering design for autonomous runs.
