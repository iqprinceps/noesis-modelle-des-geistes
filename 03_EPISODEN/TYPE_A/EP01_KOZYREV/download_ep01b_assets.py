#!/usr/bin/env python3
"""EP01B Kozyrev V3 wrapper for the shared NOESIS resilient asset engine."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.noesis_asset_downloader import main_for

HERE = Path(__file__).resolve().parent

if __name__ == "__main__":
    raise SystemExit(main_for(
        "EP01B_KOZYREV_V3",
        HERE / "asset_manifest_v3.csv",
        Path.cwd() / "EP01B_KOZYREV_MEDIA",
        ("EP01B",),
    ))
