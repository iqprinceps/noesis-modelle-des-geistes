#!/usr/bin/env python3
"""Run the shared NOESIS ElevenLabs CLI against this workspace.

The shared CLI owns the encrypted ElevenLabs account profiles.  Its project root
normally points at the NOESIS workspace, so this small adapter keeps all relative
batch paths inside the current "Modelle des Geistes" workspace.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
SHARED_CLI = (
    Path.home()
    / "Documents"
    / "Codex"
    / "NOESIS Channel"
    / "tools"
    / "elevenlabs_cli.py"
)


def main() -> int:
    if not SHARED_CLI.exists():
        raise FileNotFoundError(f"Shared ElevenLabs CLI not found: {SHARED_CLI}")

    spec = importlib.util.spec_from_file_location("noesis_elevenlabs_cli", SHARED_CLI)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load shared ElevenLabs CLI: {SHARED_CLI}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.PROJECT_ROOT = WORKSPACE_ROOT
    return int(module.main())


if __name__ == "__main__":
    raise SystemExit(main())
