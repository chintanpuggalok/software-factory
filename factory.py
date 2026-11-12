#!/usr/bin/env python3
"""Local factory coordinator. Only the deterministic simulator is enabled."""
import argparse
import fcntl
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pi_adapter

STAGES = ("idea", "spec", "design", "architecture", "plan", "build", "verify", "release")
VERSION = 1


def save(path, state):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".state-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(state, handle, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def validate(state):
    if not isinstance(state, dict) or state.get("version") != VERSION or state.get("mode") != "simulate":
        raise ValueError("Unsupported or invalid state")
    if not isinstance(state.get("goal"), str) or not state["goal"].strip():
        raise ValueError("Invalid goal")
    steps = state.get("stages")
    if not isinstance(steps, list) or len(steps) != len(STAGES):
        raise ValueError("Invalid stages")
    pending_seen = False
    for expected, item in zip(STAGES, steps):
        if not isinstance(item, dict) or item.get("name") != expected:
            raise ValueError("Invalid stage order")
        status = item.get("status")
        if status not in ("pending", "running", "passed", "failed"):
            raise ValueError("Invalid stage status")
        if status == "passed":
            if pending_seen or item.get("audit") != "passed" or not item.get("evidence"):
                raise ValueError("Passed stage lacks audit or evidence")
        else:
            pending_seen = True
    return state


def initial(goal):
    return {"version": VERSION, "mode": "simulate", "goal": goal,
            "stages": [{"name": stage, "status": "pending"} for stage in STAGES]}


def run(workspace, goal, fail_stage=None, progress=None):
    workspace = Path(workspace).resolve()
    if not workspace.is_dir():
        raise ValueError("Workspace must be an existing directory")
    directory = workspace / ".factory"
    directory.mkdir(exist_ok=True)
    lock_path = directory / "lock"
    state_path = directory / "state.json"
    with lock_path.open("a", encoding="utf-8") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if state_path.exists():
            state = validate(json.loads(state_path.read_text(encoding="utf-8")))
            if state["goal"] != goal:
                raise ValueError("Existing run has a different goal")
        else:
            state = initial(goal)
            save(state_path, state)
        notify = progress or (lambda event: None)
        for index, step in enumerate(state["stages"]):
            if step["status"] == "passed":
                continue
            notify({"event": "stage_start", "stage": step["name"], "index": index + 1,
                    "total": len(STAGES)})
            # Replaying a running step is safe only because this adapter has no external effects.
            name = step["name"]
            step.clear()
            step.update(name=name, status="running")
            save(state_path, state)
            if name == fail_stage:
                step.update(status="failed", audit="failed", evidence="Simulated audit failure")
                save(state_path, state)
                notify({"event": "stage_result", "stage": name, "passed": False,
                        "verdict": "Simulated audit failure", "blocked": True})
                break
            step.update(status="passed", audit="passed", evidence=f"Simulated {name} and audit")
            save(state_path, state)
            notify({"event": "stage_result", "stage": name, "passed": True,
                    "verdict": "Simulated audit passed", "blocked": False})
        return state


def main():
    parser = argparse.ArgumentParser(description="Run a simulated factory workflow")
    parser.add_argument("workspace", help="Existing project directory")
    parser.add_argument("--goal", required=True, help="Goal for this run")
    parser.add_argument("--mode", choices=("simulate", "pi", "pi-plan"), default="simulate")
    parser.add_argument("--runtime", choices=("pi", "codex", "claude"), default="pi",
                        help="Execution adapter. Only pi is implemented.")
    parser.add_argument("--fail-stage", choices=STAGES, help="Simulate an audit failure")
    parser.add_argument("--build-static", action="store_true", help="After a passed Pi plan, generate one static HTML prototype")
    parser.add_argument("--progress", action="store_true", help="Write PROGRESS JSON lines to stderr")
    parser.add_argument("--acceptance-file", help="Optional JSON browser acceptance contract")
    parser.add_argument("--research-query", help="Public search query sent to Wikipedia; do not include secrets")
    parser.add_argument("--reference-url", action="append", default=[],
                        help="Public reference URL from the approved host list; up to three")
    parser.add_argument("--subscription-confirmed", action="store_true",
                        help="Attest the Pi account is subscription-only; no dollar cap is enforced")
    args = parser.parse_args()
    if not args.goal.strip():
        parser.error("--goal must not be empty")
    def emit(event):
        if args.progress:
            print("PROGRESS " + json.dumps(event), file=sys.stderr, flush=True)
    if args.acceptance_file and args.mode != 'pi-plan':
        parser.error('--acceptance-file requires --mode pi-plan')
    if args.mode == "pi-plan":
        import pi_workflow
        import runtime_adapter
        try:
            runtime = runtime_adapter.get_runtime(args.runtime)
            if not isinstance(runtime, runtime_adapter.PiRuntime):
                raise runtime_adapter.RuntimeUnavailable(
                    f"{args.runtime} adapter is not implemented; use --runtime pi")
            if not runtime.available():
                raise runtime_adapter.RuntimeUnavailable("The pi executable is not available")
        except runtime_adapter.RuntimeUnavailable as exc:
            print(f"BLOCKED: {exc}", file=sys.stderr)
            return 2
        acceptance = None
        if args.acceptance_file:
            if not args.build_static:
                parser.error('--acceptance-file requires --build-static')
            try:
                import browser_verify
                contract = Path(args.acceptance_file).read_text(encoding='utf-8')
                if len(contract) > 50000:
                    raise ValueError('Acceptance contract exceeds size limit')
                acceptance = browser_verify.validate_acceptance(json.loads(contract))
            except (OSError, ValueError) as exc:
                print(f'BLOCKED: invalid acceptance contract: {exc}', file=sys.stderr)
                return 2
        try:
            if args.subscription_confirmed:
                print("WARNING: up to 10 planning calls, 2 build calls, and 1 browser repair call; no dollar limit is enforced.", file=sys.stderr)
            state, blocker = pi_workflow.run_plan(args.workspace, args.goal,
                                                  subscription_confirmed=args.subscription_confirmed,
                                                  research_query=args.research_query,
                                                  reference_urls=args.reference_url,
                                                  runtime=runtime, progress=emit)
        except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
            print(f"BLOCKED: {exc}", file=sys.stderr)
            return 2
        if blocker:
            print(json.dumps(state, indent=2))
            print(f"BLOCKED: {blocker}", file=sys.stderr)
            return 1
        if args.build_static:
            import pi_static
            try:
                original = pi_static.generate(args.workspace, args.goal,
                                              subscription_confirmed=args.subscription_confirmed)
                import browser_pipeline
                import browser_verify
                browser_result = browser_pipeline.verify_and_repair(
                    args.workspace, args.goal, original, subscription_confirmed=args.subscription_confirmed,
                    probe_fn=lambda path: browser_verify.probe(path, acceptance=acceptance))
                state['prototype_path'] = browser_result['artifact']
                state['browser_verification'] = browser_result
                evidence_path = original.parent / 'browser-evidence.json'
                fd, temp_evidence = tempfile.mkstemp(prefix='.evidence-', dir=original.parent)
                with os.fdopen(fd, 'w', encoding='utf-8') as evidence:
                    json.dump(browser_result, evidence, indent=2)
                    evidence.write('\n')
                    evidence.flush()
                    os.fsync(evidence.fileno())
                os.replace(temp_evidence, evidence_path)
                state['browser_evidence_path'] = str(evidence_path)
            except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
                print(json.dumps(state, indent=2))
                print(f"BLOCKED: prototype generation or verification failed: {exc}", file=sys.stderr)
                return 2
            if browser_result['browser']['status'] != 'passed':
                print(json.dumps(state, indent=2))
                print('BLOCKED: browser verification did not pass.', file=sys.stderr)
                return 1 if browser_result['browser']['status'] == 'failed' else 2
        print(json.dumps(state, indent=2))
        return 0
    if args.mode == "pi":
        try:
            if args.subscription_confirmed:
                print("WARNING: subscription attested by user; no dollar limit is enforced.", file=sys.stderr)
            result = pi_adapter.run_read_only(args.workspace, args.goal,
                                              subscription_confirmed=args.subscription_confirmed)
        except (OSError, ValueError, subprocess.TimeoutExpired, pi_adapter.PrepaidUnavailable) as exc:
            print(f"BLOCKED: {exc}", file=sys.stderr)
            return 2
        print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
        return result.returncode
    try:
        result = run(args.workspace, args.goal, args.fail_stage, progress=emit)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 1 if any(x["status"] == "failed" for x in result["stages"]) else 0


if __name__ == "__main__":
    sys.exit(main())
