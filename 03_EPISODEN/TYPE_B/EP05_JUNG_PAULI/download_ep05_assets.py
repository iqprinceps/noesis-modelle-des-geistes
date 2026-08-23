#!/usr/bin/env python3
"""EP05 Jung & Pauli wrapper for the shared NOESIS resilient asset engine."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.noesis_asset_downloader import main_for

HERE = Path(__file__).resolve().parent

if __name__ == "__main__":
    raise SystemExit(main_for(
        "EP05_JUNG_PAULI",
        HERE / "asset_manifest_v5.csv",
        Path.cwd() / "EP05_JUNG_PAULI_MEDIA",
        ("EP05",),
    ))
