"""OpenCode adapter for one non-interactive factory request.

The adapter cannot verify billing or enforce a dollar limit. It performs one
OpenCode invocation only. It does not run the factory workflow.

Each call starts a private OpenCode server with an isolated configuration
directory, so the user's global plugins, MCP servers, skills, and instruction
files do not apply. Project configuration and project AGENTS.md discovery are
disabled with OPENCODE_DISABLE_PROJECT_CONFIG. The session record is still
saved in the user's OpenCode database; OpenCode has no no-session mode.
"""
import json
import os
import shutil
import signal
import subprocess
import tempfile
from pathlib import Path

from pi_adapter import PrepaidUnavailable

BINARY = "opencode"
PLANNER_AGENT = "factory-planner"
READONLY_AGENT = "factory-readonly"
MODEL_ENV = "FACTORY_OPENCODE_MODEL"


def _permissions(read_allowed):
    """Ordered deny-first rules; the last matching rule wins."""
    rules = [{"action": "*", "resource": "*", "effect": "deny"}]
    if read_allowed:
        rules.extend([
            {"action": "read", "resource": "*", "effect": "allow"},
            {"action": "read", "resource": "*.env", "effect": "deny"},
            {"action": "read", "resource": "*.env.*", "effect": "deny"},
            {"action": "read", "resource": "*.env.example", "effect": "allow"},
        ])
    return rules


def adapter_config():
    """The injected configuration that restricts both factory agents."""
    return {
        "$schema": "https://opencode.ai/config.json",
        "update": "disable",
        "snapshots": False,
        "compaction": {"auto": False},
        "agents": {
            "title": {"disabled": True},
            PLANNER_AGENT: {
                "description": "Factory planning call. Every tool and action is denied.",
                "mode": "primary",
                "system": ("You complete one planning request and return its text. "
                           "You have no tools. Do not attempt to run tools or ask questions. "
                           "Return the requested text only."),
                "permissions": _permissions(read_allowed=False),
            },
            READONLY_AGENT: {
                "description": "Factory read-only call. Only file reads are permitted.",
                "mode": "primary",
                "system": ("You complete one request and return its text. You may read "
                           "project files. You cannot edit files, run commands, or use the "
                           "web. Return the requested text only."),
                "permissions": _permissions(read_allowed=True),
            },
        },
    }


def _write_config(config_root):
    directory = config_root / "opencode"
    directory.mkdir()
    path = directory / "opencode.json"
    path.write_text(json.dumps(adapter_config(), indent=2) + "\n", encoding="utf-8")
    return path


def _call_environment(config_root, workspace):
    env = dict(os.environ)
    env["XDG_CONFIG_HOME"] = str(config_root)
    env["OPENCODE_DISABLE_PROJECT_CONFIG"] = "1"
    # OpenCode resolves its project location from PWD, not the process cwd.
    env["PWD"] = str(workspace)
    return env


def _command(agent, prompt):
    executable = shutil.which(BINARY)
    if not executable:
        raise FileNotFoundError("OpenCode executable not found")
    argv = [executable, "run", "--standalone", "--agent", agent]
    model = (os.environ.get(MODEL_ENV) or "").strip()
    if model:
        argv.extend(["--model", model])
    argv.extend(["--archived", "--title", "factory", "--", prompt])
    return argv


def _terminate_group(process):
    try:
        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
    except OSError:
        process.kill()


def _run(argv, workspace, env, timeout):
    process = subprocess.Popen(
        argv, cwd=workspace, env=env, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        _terminate_group(process)
        stdout, stderr = process.communicate()
        raise subprocess.TimeoutExpired(argv, timeout, output=stdout, stderr=stderr) from None
    return subprocess.CompletedProcess(argv, process.returncode, stdout, stderr)


def _invoke(agent, read_allowed, workspace, prompt, *, subscription_confirmed, timeout):
    workspace = Path(workspace).resolve()
    if not workspace.is_dir():
        raise ValueError("Workspace must be an existing directory")
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("Prompt must not be empty")
    if not subscription_confirmed:
        raise PrepaidUnavailable("Subscription not confirmed; no OpenCode call was made")
    argv = _command(agent, prompt)
    config_root = Path(tempfile.mkdtemp(prefix="factory-opencode-"))
    try:
        _write_config(config_root)
        return _run(argv, workspace, _call_environment(config_root, workspace), timeout)
    finally:
        shutil.rmtree(config_root, ignore_errors=True)


def run_text(workspace, prompt, *, subscription_confirmed=False, timeout=120):
    """Run one OpenCode request with every tool and action denied."""
    return _invoke(PLANNER_AGENT, False, workspace, prompt,
                   subscription_confirmed=subscription_confirmed, timeout=timeout)


def run_read_only(workspace, prompt, *, subscription_confirmed=False, timeout=120):
    """Run one read-only OpenCode request; only file reads are permitted."""
    return _invoke(READONLY_AGENT, True, workspace, prompt,
                   subscription_confirmed=subscription_confirmed, timeout=timeout)
