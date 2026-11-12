"""Read-only Pi adapter with explicit subscription attestation.

The adapter cannot verify billing or enforce a dollar limit. It performs one
Pi invocation only. It does not run the factory workflow.
"""
import shutil
import subprocess
from pathlib import Path


class PrepaidUnavailable(RuntimeError):
    """The user has not confirmed subscription-only usage."""


def run_text(workspace, prompt, *, subscription_confirmed=False, timeout=120):
    """Run one Pi request with tools and context-file discovery disabled."""
    workspace = Path(workspace).resolve()
    if not workspace.is_dir():
        raise ValueError("Workspace must be an existing directory")
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("Prompt must not be empty")
    if not subscription_confirmed:
        raise PrepaidUnavailable("Subscription not confirmed; no Pi call was made")
    executable = shutil.which("pi")
    if not executable:
        raise FileNotFoundError("Pi executable not found")
    return subprocess.run(
        [executable, "--print", "--no-session", "--no-extensions", "--no-mcp",
         "--offline", "--no-tools", "--no-skills", "--no-context-files", "--", prompt],
        cwd=workspace, text=True, capture_output=True, timeout=timeout, check=False,
    )


def run_read_only(workspace, prompt, *, subscription_confirmed=False, timeout=120):
    """Run one read-only Pi request after explicit subscription attestation."""
    workspace = Path(workspace).resolve()
    if not workspace.is_dir():
        raise ValueError("Workspace must be an existing directory")
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("Prompt must not be empty")
    if not subscription_confirmed:
        raise PrepaidUnavailable("Subscription not confirmed; no Pi call was made")
    executable = shutil.which("pi")
    if not executable:
        raise FileNotFoundError("Pi executable not found")
    return subprocess.run(
        [executable, "--print", "--no-session", "--no-extensions", "--no-mcp",
         "--offline", "--tools", "read", "--", prompt],
        cwd=workspace, text=True, capture_output=True, timeout=timeout, check=False,
    )
