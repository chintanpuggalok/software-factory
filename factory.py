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


def run(workspace, goal, fail_stage=None):
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
        for step in state["stages"]:
            if step["status"] == "passed":
                continue
            # Replaying a running step is safe only because this adapter has no external effects.
            name = step["name"]
            step.clear()
            step.update(name=name, status="running")
            save(state_path, state)
            if name == fail_stage:
                step.update(status="failed", audit="failed", evidence="Simulated audit failure")
                save(state_path, state)
                break
            step.update(status="passed", audit="passed", evidence=f"Simulated {name} and audit")
            save(state_path, state)
        return state


def main():
    parser = argparse.ArgumentParser(description="Run a simulated factory workflow")
    parser.add_argument("workspace", help="Existing project directory")
    parser.add_argument("--goal", required=True, help="Goal for this run")
    parser.add_argument("--mode", choices=("simulate", "pi"), default="simulate")
    parser.add_argument("--fail-stage", choices=STAGES, help="Simulate an audit failure")
    parser.add_argument("--subscription-confirmed", action="store_true",
                        help="Attest the Pi account is subscription-only; no dollar cap is enforced")
    args = parser.parse_args()
    if not args.goal.strip():
        parser.error("--goal must not be empty")
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
        result = run(args.workspace, args.goal, args.fail_stage)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 1 if any(x["status"] == "failed" for x in result["stages"]) else 0


if __name__ == "__main__":
    sys.exit(main())
