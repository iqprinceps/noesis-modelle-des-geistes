#!/usr/bin/env python3
"""Build the one progressive physical-variables clip required by the upgraded EDL."""

from __future__ import annotations

import math
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps


EP = Path(__file__).resolve().parents[1]
SOURCE = EP / "04_ASSETS/GENERATED/NATIVE_IMAGEGEN/CLUSTER_BREAKS/KZ_PHYSICAL_VARIABLES_SENSOR_RIG.png"
TARGET = EP / "04_ASSETS/CLIPS/LOCAL_PROGRESSIVE/KZ_CLIP_PHYSICAL_VARIABLES_SENSOR_RIG.mp4"
QA = EP / "05_QA/CLIP_TRIPLETS"
W, H, FPS, DURATION = 1920, 1080, 25, 7.42


def frame(base: Image.Image, t: float) -> Image.Image:
    # Real development rather than a cosmetic pan: instrument readings change in sequence.
    im = ImageEnhance.Brightness(base).enhance(1.0 - 0.025 * t)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer, "RGBA")

    # Thermometer column at left rises gradually by a plausible small amount.
    y_bottom = 777
    y_top = int(718 - 14 * max(0.0, min(1.0, (t - 0.08) / 0.45)))
    d.rounded_rectangle((183, y_top, 188, y_bottom), radius=3, fill=(132, 49, 39, 175))

    # Central round gauge responds next.
    cx, cy, radius = 468, 791, 50
    a = math.radians(198 + 29 * max(0.0, min(1.0, (t - 0.25) / 0.42)))
    d.line((cx, cy, cx + math.cos(a) * radius, cy + math.sin(a) * radius), fill=(185, 63, 44, 230), width=4)

    # Rectangular analog meter settles last.
    cx2, cy2, radius2 = 659, 718, 58
    a2 = math.radians(202 + 36 * max(0.0, min(1.0, (t - 0.48) / 0.40)))
    d.line((cx2, cy2, cx2 + math.cos(a2) * radius2, cy2 + math.sin(a2) * radius2), fill=(58, 48, 39, 235), width=4)

    # Three restrained pressure rings leave the microphone only while sound is named.
    pulse = max(0.0, 1.0 - abs(t - 0.32) / 0.25)
    for i in range(3):
        rr = 20 + i * 23 + int(32 * t)
        d.arc((688 - rr, 430 - rr, 688 + rr, 430 + rr), 285, 75, fill=(187, 208, 208, int(55 * pulse)), width=2)

    layer = layer.filter(ImageFilter.GaussianBlur(0.35))
    return Image.alpha_composite(im.convert("RGBA"), layer).convert("RGB")


def main() -> int:
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    QA.mkdir(parents=True, exist_ok=True)
    base = ImageOps.fit(Image.open(SOURCE).convert("RGB"), (W, H), Image.Resampling.LANCZOS)
    frames = round(DURATION * FPS)
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart", str(TARGET),
    ]
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    samples = {0: "start", frames // 2: "mid", frames - 1: "end"}
    try:
        for index in range(frames):
            t = index / max(1, frames - 1)
            rendered = frame(base, t)
            if index in samples:
                rendered.save(QA / f"KZ_CLIP_PHYSICAL_VARIABLES_SENSOR_RIG_{samples[index]}.jpg", quality=94, subsampling=0)
            assert process.stdin is not None
            process.stdin.write(rendered.tobytes())
    finally:
        if process.stdin:
            process.stdin.close()
    if process.wait():
        raise RuntimeError("ffmpeg failed")
    print(f"{TARGET} {frames / FPS:.2f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
