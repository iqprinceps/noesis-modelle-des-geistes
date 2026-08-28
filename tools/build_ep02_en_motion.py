#!/usr/bin/env python3
"""Render deterministic, voice-exact EP02_EN motion clips and QA frames."""

from __future__ import annotations

import argparse
import json
import math
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont


ROOT = Path(__file__).resolve().parents[1]
EP = ROOT / "07_ENGLISH_PRODUCTION" / "EP02_GATEWAY"
OUT = EP / "03_VISUALS" / "CLIPS"
QA = EP / "03_VISUALS" / "QA" / "CLIP_FRAMES"
FPS, W, H = 30, 1920, 1080
BG = (8, 15, 18)
CYAN = (91, 210, 211)
AMBER = (224, 174, 71)
PAPER = (236, 232, 218)
FONT = "C:/Windows/Fonts/arial.ttf"
FONT_B = "C:/Windows/Fonts/arialbd.ttf"


def font(size: int, bold: bool = False):
    return ImageFont.truetype(FONT_B if bold else FONT, size)


def ease(x: float) -> float:
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def cover(path: Path) -> Image.Image:
    im = Image.open(path).convert("RGB")
    scale = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * scale), round(im.height * scale)), Image.Resampling.LANCZOS)
    return im.crop(((im.width - W) // 2, (im.height - H) // 2, (im.width + W) // 2, (im.height + H) // 2))


def text_center(d: ImageDraw.ImageDraw, text: str, y: int, size: int, color, bold=True):
    f = font(size, bold)
    box = d.textbbox((0, 0), text, font=f)
    d.text(((W - box[2] + box[0]) // 2, y), text, font=f, fill=color)


def clip_three_times(t: float) -> Image.Image:
    base = cover(EP / "03_VISUALS/GENERATED/STILLS/GW_EN_STILL05_THREE_OBSERVERS_V2_FINAL.png")
    base = ImageEnhance.Brightness(base).enhance(0.62)
    d = ImageDraw.Draw(base, "RGBA")
    d.rectangle((0, 780, W, H), fill=(4, 10, 12, 215))
    xs = [420, 960, 1500]
    labels = ["PRESENT", "IMMEDIATE PAST", "IMMEDIATE FUTURE"]
    for i, (x, label) in enumerate(zip(xs, labels)):
        active = ease((t - i * 2.2) / 1.1)
        d.ellipse((x - 28, 866 - 28, x + 28, 866 + 28), fill=(*CYAN, round(255 * active)), outline=(190, 210, 210, 220), width=3)
        if active > 0.35:
            f = font(36, True)
            box = d.textbbox((0, 0), label, font=f)
            d.text((x - (box[2] - box[0]) / 2, 930), label, font=f, fill=(*PAPER, round(255 * active)))
    d.line((xs[0], 866, xs[-1], 866), fill=(82, 105, 108, 220), width=5)
    if t > 7.0:
        alpha = round(255 * ease((t - 7.0) / 1.2))
        d.line((xs[0], 810, xs[1], 770, xs[2], 810), fill=(*AMBER, alpha), width=6)
    return base


def clip_archive_chain(t: float) -> Image.Image:
    a = cover(EP / "03_VISUALS/DOCUMENT_CROPS/GW_EN_DOC01_ARMY_HEADER.png")
    b = cover(EP / "03_VISUALS/CARDS/GW_EN_CARD_ARMY_NOT_CIA.png")
    p = ease((t - 3.8) / 2.0)
    frame = Image.blend(a, b, p)
    d = ImageDraw.Draw(frame, "RGBA")
    if t < 3.8:
        d.rectangle((70, 998, 1100, 1048), fill=(5, 10, 12, 210))
        d.text((90, 1005), "Army memorandum • 9 June 1983", font=font(30), fill=PAPER)
    return frame


def clip_beat(t: float) -> Image.Image:
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    mid = H // 2
    alpha1 = ease(t / 1.2)
    alpha2 = ease((t - 2.0) / 1.2)
    alpha3 = ease((t - 4.2) / 1.4)
    for idx, (freq, y, color, alpha) in enumerate([(4.0, 330, CYAN, alpha1), (4.1, 520, PAPER, alpha2)]):
        pts = []
        for x in range(110, 1810, 4):
            yy = y + math.sin((x / W * math.tau * freq * 2) - t * 3.0) * 70
            pts.append((x, yy))
        d.line(pts, fill=tuple(round(c * alpha) for c in color), width=5)
    if alpha3 > 0:
        pts = []
        for x in range(110, 1810, 4):
            carrier = math.sin(x / W * math.tau * 8 - t * 4)
            envelope = 0.25 + 0.75 * abs(math.sin(x / W * math.tau * 2.0))
            pts.append((x, 730 + carrier * envelope * 90))
        d.line(pts, fill=tuple(round(c * alpha3) for c in AMBER), width=6)
    d.text((120, 195), "400 Hz", font=font(54, True), fill=CYAN)
    if alpha2 > .2:
        d.text((120, 395), "410 Hz", font=font(54, True), fill=PAPER)
    if alpha3 > .2:
        d.text((120, 835), "10 beats/sec", font=font(54, True), fill=AMBER)
    return im


def clip_digits(t: float) -> Image.Image:
    im = cover(EP / "03_VISUALS/GENERATED/STILLS/GW_EN_STILL03_TEN_DIGIT_PARTICIPANT_V2_FINAL.png")
    im = ImageEnhance.Brightness(im).enhance(0.42)
    d = ImageDraw.Draw(im, "RGBA")
    d.rectangle((0, 720, W, H), fill=(5, 10, 12, 225))
    x0, gap, size = 250, 22, 118
    revealed = min(10, max(0, int((t - 1.0) * 1.5)))
    matches = {0, 1, 3, 5, 7, 8}
    for i in range(10):
        x = x0 + i * (size + gap)
        color = CYAN if i < revealed and i in matches else (95, 104, 105)
        if i < revealed and i not in matches:
            color = (45, 53, 55)
        d.rounded_rectangle((x, 790, x + size, 908), radius=12, fill=(*color, 230), outline=(200, 210, 208, 200), width=2)
        if i < revealed:
            d.text((x + 38, 810), str((i * 7 + 3) % 10), font=font(64, True), fill=PAPER)
    if t > 5.3:
        text_center(d, "Some digits matched.", 950, 46, CYAN)
    if t > 7.0:
        d.rectangle((0, 930, W, H), fill=(5, 10, 12, 245))
        text_center(d, "Nobody got all ten.", 960, 60, AMBER)
    return im


def clip_handoff(t: float) -> Image.Image:
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im, "RGBA")
    count = 28
    for i in range(count):
        x = 120 + (i % 14) * 122
        y = 240 + (i // 14) * 220
        p = ease((t - 1.0 - i * 0.08) / 1.2)
        value = (i * 13 + 7) % 10 if p < .5 else (i * 7 + int(t * 4)) % 2
        color = AMBER if p < .5 else CYAN
        d.text((x, y), str(value), font=font(92, True), fill=(*color, 235))
    if t < 4.2:
        text_center(d, "Remove the visions.", 720, 72, PAPER)
    if t > 3.6:
        alpha = round(255 * ease((t - 3.6) / 1.0))
        text_center(d, "Keep the test.", 820, 82, (*AMBER, alpha))
    return im


JOBS = [
    ("GW_EN_CLIP01_THREE_TIMES_RECOMMENDATION_H.mp4", 10.5, clip_three_times, "three observer candidate + Recommendation H geometry"),
    ("GW_EN_CLIP02_ARCHIVE_CHAIN.mp4", 7.0, clip_archive_chain, "Army authorship to CIA archive custody"),
    ("GW_EN_CLIP04_BEAT_RESONANCE.mp4", 8.0, clip_beat, "400/410 Hz to 10 beats per second"),
    ("GW_EN_CLIP07_TEN_DIGITS.mp4", 9.0, clip_digits, "reported partial match; incomplete sequence"),
    ("GW_EN_CLIP10_ZERO_ONE_HANDOFF.mp4", 7.0, clip_handoff, "Gateway digits to PEAR binary stream"),
]


def render(name: str, seconds: float, renderer, use: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    meta = path.with_suffix(".json")
    if path.is_file() and meta.is_file():
        print(f"SKIP {name}")
        return
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(path)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    assert proc.stdin
    for i in range(round(seconds * FPS)):
        proc.stdin.write(renderer(i / FPS).convert("RGB").tobytes())
    proc.stdin.close()
    if proc.wait():
        raise RuntimeError(f"ffmpeg failed for {name}")
    data = {"asset": name, "provider": "deterministic Python/Pillow + FFmpeg", "duration": seconds, "fps": FPS, "size": [W, H], "audio": False, "visible_mode_badge": False, "use": use}
    meta.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(path)


def qa_frames() -> None:
    QA.mkdir(parents=True, exist_ok=True)
    for name, seconds, _, _ in JOBS:
        path = OUT / name
        for label, ts in [("FIRST", 0.0), ("MIDDLE", seconds / 2), ("FINAL", max(0, seconds - 0.20))]:
            out = QA / f"{path.stem}_{label}.png"
            subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{ts:.3f}", "-i", str(path), "-frames:v", "1", str(out)], check=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["render", "qa", "all"])
    args = ap.parse_args()
    if args.action in ("render", "all"):
        for job in JOBS:
            render(*job)
    if args.action in ("qa", "all"):
        qa_frames()


if __name__ == "__main__":
    main()
