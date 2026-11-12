"""Selectable execution runtimes for the factory coordinator.

Only the Pi adapter is implemented and tested. Codex and Claude are declared
placeholders so the interface is stable when those adapters are added.
"""
import os
import shutil

import pi_adapter

IMPLEMENTED = ("pi",)
DECLARED = ("codex", "claude")


class RuntimeUnavailable(RuntimeError):
    """The selected runtime cannot be used."""


class PiRuntime:
    name = "pi"
    binary = "pi"

    def available(self):
        return shutil.which(self.binary) is not None

    def run_text(self, workspace, prompt, *, confirmed=False, timeout=120):
        return pi_adapter.run_text(workspace, prompt, subscription_confirmed=confirmed, timeout=timeout)

    def run_read_only(self, workspace, prompt, *, confirmed=False, timeout=120):
        return pi_adapter.run_read_only(workspace, prompt, subscription_confirmed=confirmed, timeout=timeout)


class PlannedRuntime:
    """A declared runtime with no verified adapter yet."""

    binary = None

    def __init__(self, name):
        self.name = name

    def available(self):
        return False

    def run_text(self, workspace, prompt, *, confirmed=False, timeout=120):
        raise RuntimeUnavailable(
            f"The {self.name} runtime adapter is not implemented. Use --runtime pi or add an adapter "
            "that follows docs/runtime-adapters.md.")

    def run_read_only(self, workspace, prompt, *, confirmed=False, timeout=120):
        return self.run_text(workspace, prompt, confirmed=confirmed, timeout=timeout)


def get_runtime(name=None):
    """Return a runtime adapter. Defaults to Pi, then FACTORY_RUNTIME."""
    selected = (name or os.environ.get("FACTORY_RUNTIME") or "pi").strip().lower()
    if selected == "pi":
        return PiRuntime()
    if selected in DECLARED:
        return PlannedRuntime(selected)
    raise RuntimeUnavailable(f"Unknown runtime: {selected}. Use one of: {', '.join(IMPLEMENTED + DECLARED)}")
