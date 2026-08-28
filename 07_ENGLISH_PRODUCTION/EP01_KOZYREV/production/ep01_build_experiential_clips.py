#!/usr/bin/env python3
"""Build the four justified progressive clips added by the experiential pass."""

from __future__ import annotations

import math
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps


EP = Path(__file__).resolve().parents[1]
UPGRADE = EP / "04_ASSETS/GENERATED/NATIVE_IMAGEGEN/EXPERIENTIAL_UPGRADE"
DETERMINISTIC = EP / "04_ASSETS/GENERATED/DETERMINISTIC"
OUT = EP / "04_ASSETS/CLIPS/LOCAL_PROGRESSIVE"
QA = EP / "05_QA/CLIP_TRIPLETS"
W, H, FPS = 1920, 1080, 25
OUT.mkdir(parents=True, exist_ok=True)
QA.mkdir(parents=True, exist_ok=True)


def fit(path: Path) -> Image.Image:
    return ImageOps.fit(Image.open(path).convert("RGB"), (W, H), Image.Resampling.LANCZOS)


def information_frame(base: Image.Image, t: float) -> Image.Image:
    im = ImageEnhance.Brightness(base).enhance(0.88 + 0.10 * math.sin(math.pi * t))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")
    # Reflected points become ordered from the perimeter inward; the target stays sealed.
    cx, cy = 1015, 455
    count = int(7 + 34 * t)
    for i in range(count):
        phase = i / 40.0
        radius_x = 230 * (1 - 0.55 * t) + 34 * math.sin(i * 1.7)
        radius_y = 150 * (1 - 0.42 * t) + 20 * math.cos(i * 1.3)
        angle = i * 2.399 + t * 0.9
        x = cx + math.cos(angle) * radius_x
        y = cy + math.sin(angle) * radius_y
        alpha = int(28 + 115 * max(0.0, t - phase * 0.18))
        draw.ellipse((x - 2, y - 6, x + 2, y + 6), fill=(188, 225, 232, alpha))
    sweep = int(-240 + t * 2050)
    draw.polygon([(sweep - 160, 0), (sweep + 20, 0), (sweep + 370, H), (sweep + 170, H)], fill=(165, 216, 226, 18))
    return Image.alpha_composite(im.convert("RGBA"), layer).convert("RGB")


def missing_frame(base: Image.Image, t: float) -> Image.Image:
    im = ImageEnhance.Brightness(base).enhance(1.0 - 0.38 * t)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")
    # The analog status lamp extinguishes and illumination withdraws from the empty tray.
    lamp_alpha = int(210 * (1.0 - min(1.0, t * 1.4)))
    draw.ellipse((223, 205, 243, 225), fill=(255, 176, 54, lamp_alpha))
    shadow = int(255 * max(0.0, (t - 0.20) / 0.80))
    draw.rectangle((1300, 760, W, H), fill=(0, 5, 9, int(0.32 * shadow)))
    draw.rectangle((0, 0, W, H), fill=(0, 8, 14, int(58 * t)))
    # A last real reflection recedes across the metal instead of simulating camera movement.
    x = int(1480 - 820 * t)
    draw.polygon([(x - 130, 120), (x + 40, 120), (x + 270, 850), (x + 70, 850)], fill=(185, 220, 226, int(30 * (1 - t))))
    return Image.alpha_composite(im.convert("RGBA"), layer).convert("RGB")


def observers_frame(base: Image.Image, t: float) -> Image.Image:
    im = ImageEnhance.Brightness(base).enhance(0.80 + 0.16 * math.sin(math.pi * t))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")
    # One light event reaches the chamber chair, outer stool, then observation chair.
    positions = [(472, 478, 170), (1010, 700, 145), (1638, 712, 130)]
    for index, (x, y, radius) in enumerate(positions):
        local = max(0.0, min(1.0, t * 3.0 - index))
        pulse = math.sin(math.pi * local) ** 1.4
        if pulse <= 0:
            continue
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(166, 218, 230, int(48 * pulse)))
        draw.line((x - 210, y + 135, x + 210, y + 135), fill=(220, 235, 236, int(86 * pulse)), width=5)
    draw.rectangle((0, 0, W, H), fill=(0, 4, 8, int(34 * t)))
    return Image.alpha_composite(im.convert("RGBA"), layer).convert("RGB")


def patent_frames() -> list[Image.Image]:
    names = [
        "KZ_SRC_PATENT_AUTHORITY_FULL.png",
        "KZ_SRC_PATENT_NUMBER_CROP.png",
        "KZ_SRC_PATENT_DATES_CROP.png",
        "KZ_SRC_PATENT_INVENTORS_CROP.png",
        "KZ_SRC_PATENT_DRAWINGS.png",
    ]
    return [fit(DETERMINISTIC / name) for name in names]


def patent_frame(slides: list[Image.Image], t: float) -> Image.Image:
    position = t * (len(slides) - 0.001)
    index = min(len(slides) - 1, int(position))
    local = position - index
    current = slides[index]
    if index == len(slides) - 1 or local < 0.77:
        im = current.copy()
    else:
        mix = (local - 0.77) / 0.23
        im = Image.blend(current, slides[index + 1], mix)
    # A restrained scan band supplies continuous progression while preserving source text.
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")
    y = int(90 + (H - 180) * ((t * 4.0) % 1.0))
    draw.rectangle((90, y - 18, W - 90, y + 18), fill=(244, 193, 92, 18))
    return Image.alpha_composite(im.convert("RGBA"), layer).convert("RGB")


def encode(asset_id: str, duration: float, renderer) -> None:
    frames = round(duration * FPS)
    target = OUT / f"{asset_id}.mp4"
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(target),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    samples = {0: "start", frames // 2: "mid", frames - 1: "end"}
    try:
        for i in range(frames):
            frame = renderer(i / max(1, frames - 1))
            if i in samples:
                frame.save(QA / f"{asset_id}_{samples[i]}.jpg", quality=94, subsampling=0)
            assert proc.stdin is not None
            proc.stdin.write(frame.tobytes())
    finally:
        if proc.stdin:
            proc.stdin.close()
    if proc.wait():
        raise RuntimeError(f"ffmpeg failed for {asset_id}")
    print(f"{asset_id}: {frames / FPS:.2f}s")


def main() -> int:
    info = fit(UPGRADE / "KZ_INFO_BEFORE_REVEAL_START.png")
    missing = fit(UPGRADE / "KZ_MISSING_EXPERIMENT_VOID_START.png")
    observers = fit(UPGRADE / "KZ_THREE_OBSERVERS_TRANSITION_START.png")
    patents = patent_frames()
    encode("KZ_CLIP_INFORMATION_BEFORE_REVEAL", 4.80, lambda t: information_frame(info, t))
    encode("KZ_CLIP_MISSING_EXPERIMENT_VOID", 5.60, lambda t: missing_frame(missing, t))
    encode("KZ_CLIP_THREE_OBSERVERS_TRANSITION", 7.40, lambda t: observers_frame(observers, t))
    encode("KZ_CLIP_PATENT_EVIDENCE_DECONSTRUCTION", 5.80, lambda t: patent_frame(patents, t))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
