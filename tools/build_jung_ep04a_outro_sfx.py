#!/usr/bin/env python3
"""Create the project-owned 20-second EP04A end-screen sound bed."""

from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "06_PRODUCTION" / "JUNG_SERIES_V1" / "RENDER_EP04A" / "audio"
TARGET = OUT / "EP04A_OUTRO_SFX_20S.wav"
SR = 48_000
DURATION = 20.0
SEED = 40412


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    count = int(SR * DURATION)
    t = np.arange(count, dtype=np.float64) / SR
    rng = np.random.default_rng(SEED)

    fade_in = np.clip(t / 1.2, 0.0, 1.0)
    fade_out = np.clip((DURATION - t) / 4.0, 0.0, 1.0)
    envelope = fade_in * fade_out

    room = rng.normal(0.0, 1.0, count)
    kernel = np.ones(1600, dtype=np.float64) / 1600.0
    room = np.convolve(room, kernel, mode="same")
    bed = (
        0.014 * np.sin(2 * np.pi * 146.83 * t)
        + 0.008 * np.sin(2 * np.pi * 220.00 * t + 0.4)
        + 0.004 * np.sin(2 * np.pi * 293.66 * t + 1.1)
        + 0.035 * room
    ) * envelope

    for start, freq in ((0.7, 440.0), (4.6, 587.33)):
        rel = t - start
        mask = rel >= 0
        bed[mask] += 0.020 * np.exp(-1.45 * rel[mask]) * np.sin(2 * np.pi * freq * rel[mask])

    left = bed * (0.97 + 0.03 * np.sin(2 * np.pi * 0.035 * t))
    right = bed * (0.97 + 0.03 * np.sin(2 * np.pi * 0.035 * t + np.pi))
    stereo = np.stack((left, right), axis=1).astype("<f4")

    raw = OUT / ".EP04A_OUTRO_SFX_20S.f32"
    raw.write_bytes(stereo.tobytes())
    subprocess.run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", str(raw),
        "-c:a", "pcm_s24le", str(TARGET),
    ], check=True)
    raw.unlink()
    print(TARGET)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
