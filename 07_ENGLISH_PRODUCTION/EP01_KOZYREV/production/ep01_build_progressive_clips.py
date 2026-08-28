from __future__ import annotations

import math
import random
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageOps


EP = Path(__file__).resolve().parents[1]
STILLS = EP / "04_ASSETS" / "GENERATED" / "NATIVE_IMAGEGEN"
OUT = EP / "04_ASSETS" / "CLIPS" / "LOCAL_PROGRESSIVE"
QA = EP / "05_QA" / "CLIP_TRIPLETS"
W, H, FPS = 1920, 1080, 25
OUT.mkdir(parents=True, exist_ok=True)
QA.mkdir(parents=True, exist_ok=True)


def load(name: str) -> Image.Image:
    return ImageOps.fit(Image.open(STILLS / name).convert("RGB"), (W, H), Image.Resampling.LANCZOS)


def vignette(strength: float) -> Image.Image:
    mask = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(mask)
    inset = int(80 + strength * 260)
    d.ellipse((-inset, -inset, W + inset, H + inset), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(180 + int(strength * 120)))
    dark = Image.new("RGB", (W, H), (0, 0, 0))
    return Image.composite(Image.new("RGB", (W, H), (255, 255, 255)), dark, mask)


def rotation_frame(base: Image.Image, t: float) -> Image.Image:
    im = base.copy()
    d = ImageDraw.Draw(im, "RGBA")
    # The coupling marker and traveling metal highlight supply real mechanical progression.
    cx, cy, r = 605, 822, 34
    a = t * math.pi * 2 * 1.35
    d.ellipse((cx-r, cy-r, cx+r, cy+r), outline=(210, 220, 220, 120), width=3)
    d.line((cx, cy, cx + math.cos(a)*r, cy + math.sin(a)*r), fill=(245, 190, 88, 235), width=6)
    x = int(260 + t * 1160)
    d.polygon([(x-120, 70), (x+70, 70), (x+350, 640), (x+100, 640)], fill=(255, 228, 172, int(18 + 34*math.sin(t*math.pi))))
    return im


def isolation_frame(base: Image.Image, t: float) -> Image.Image:
    cool = ImageEnhance.Color(base).enhance(1.0 - .28*t)
    cool = ImageEnhance.Brightness(cool).enhance(1.0 - .18*t)
    # The open workshop visually recedes while the chamber reflection and tissue strip change.
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay, "RGBA")
    d.rectangle((0, 0, 470, H), fill=(2, 7, 10, int(30 + 125*t)))
    x = 870 + int(18*math.sin(t*math.pi*4))
    d.line((x, 132, x+8, 420), fill=(232, 230, 214, 150), width=8)
    band = int(160 - 95*t)
    d.polygon([(690-band, 0), (690+band, 0), (850+band, H), (850-band, H)], fill=(245, 176, 92, int(26*(1-t))))
    for i in range(4):
        rr = 55 + i*48 + t*80
        d.arc((1050-rr, 410-rr, 1050+rr, 410+rr), 120, 240, fill=(100, 194, 211, int(45*(1-t))), width=3)
    return Image.alpha_composite(cool.convert("RGBA"), overlay).convert("RGB")


def internal_frame(base: Image.Image, t: float) -> Image.Image:
    im = ImageEnhance.Brightness(base).enhance(1.0 - .11*t)
    # Delayed reflected silhouette shifts progressively, while two particle systems move oppositely.
    region = base.crop((1030, 180, 1800, 870)).filter(ImageFilter.GaussianBlur(2))
    alpha = Image.new("L", region.size, int(4 + 126*t))
    im.paste(region, (1020 - int(78*t), 180), alpha)
    d = ImageDraw.Draw(im, "RGBA")
    rng = random.Random(9137)
    for _ in range(int(12 + 118*t)):
        x = rng.randrange(420, 1600)
        y0 = rng.randrange(-H, H)
        y = int((y0 + t*980) % H)
        rr = rng.choice((1, 1, 2, 3))
        d.ellipse((x-rr, y-rr, x+rr, y+rr), fill=(236, 219, 177, rng.randrange(55, 145)))
    rng = random.Random(5512)
    for _ in range(int(4 + 56*t)):
        x = rng.randrange(45, 720)
        y0 = rng.randrange(100, 940)
        y = int(940 - ((940-y0 + t*430) % 840))
        rr = rng.randrange(2, 6)
        d.ellipse((x-rr, y-rr, x+rr, y+rr), outline=(175, 212, 222, 125), width=2)
    return im


def distant_frame(base: Image.Image, t: float) -> Image.Image:
    gray = ImageOps.grayscale(base).convert("RGB")
    gray = ImageEnhance.Brightness(gray).enhance(.38)
    gray = ImageEnhance.Contrast(gray).enhance(.72)
    reveal = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(reveal)
    bands = [(140, 335), (380, 575), (635, 840)]
    for i, (y0, y1) in enumerate(bands):
        local = max(0.0, min(1.0, t*1.55 - i*.22))
        x1 = int(W*local)
        if x1 > 0:
            d.rectangle((0, y0, x1, y1), fill=int(255*local))
    reveal = reveal.filter(ImageFilter.GaussianBlur(28))
    im = Image.composite(base, gray, reveal)
    gloss = Image.new("RGBA", (W, H), (0,0,0,0))
    gd = ImageDraw.Draw(gloss, "RGBA")
    x = int(-300 + t*(W+600))
    gd.polygon([(x-160,0),(x+60,0),(x+420,H),(x+180,H)], fill=(204,235,241,34))
    return Image.alpha_composite(im.convert("RGBA"), gloss).convert("RGB")


def empty_frame(base: Image.Image, t: float) -> Image.Image:
    dim = ImageEnhance.Brightness(base).enhance(1.0 - .52*t)
    layer = Image.new("RGBA", (W, H), (0,0,0,0))
    d = ImageDraw.Draw(layer, "RGBA")
    # A warm reflection crosses the actual metal; a separate floor shadow changes direction.
    x = int(120 + t*1030)
    d.polygon([(x-260,80),(x-50,60),(x+370,920),(x+80,930)], fill=(255,190,101,int(52*(1-.35*t))))
    ang = math.radians(-18 + 28*t)
    ox, oy = 920, 870
    length, width = 650, 100
    dx, dy = math.cos(ang)*length, math.sin(ang)*length
    d.polygon([(ox,oy-width),(ox+dx,oy+dy-width),(ox+dx,oy+dy+width),(ox,oy+width)], fill=(0,0,0,int(35+85*t)))
    d.rectangle((0,0,W,H), fill=(0,8,14,int(60*t)))
    return Image.alpha_composite(dim.convert("RGBA"), layer).convert("RGB")


def encode(asset_id: str, source: str, duration: float, renderer) -> None:
    frames = round(duration * FPS)
    target = OUT / f"{asset_id}.mp4"
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(target),
    ]
    base = load(source)
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    samples = {0: "start", frames//2: "mid", frames-1: "end"}
    try:
        for i in range(frames):
            t = i / max(1, frames-1)
            frame = renderer(base, t)
            if i in samples:
                frame.save(QA / f"{asset_id}_{samples[i]}.jpg", quality=94, subsampling=0)
            proc.stdin.write(frame.tobytes())
    finally:
        if proc.stdin:
            proc.stdin.close()
    rc = proc.wait()
    if rc:
        raise RuntimeError(f"ffmpeg failed for {asset_id}: {rc}")
    print(f"{asset_id}: {frames/FPS:.2f}s {target}")


if __name__ == "__main__":
    only = sys.argv[1] if len(sys.argv) > 1 else "all"
    jobs = {
        "rotation": ("KZ_CLIP_ROTATION_HOOK", "KZ_CLIP_ROTATION_HOOK_START.png", 2.02, rotation_frame),
        "isolation": ("KZ_CLIP_ISOLATION_SENSORY_CONTINUOUS", "KZ_CLIP_ISOLATION_SENSORY_START.png", 9.66, isolation_frame),
        "internal": ("KZ_CLIP_INTERNAL_TIME_CONTINUOUS", "KZ_INNER01_INTERNAL_TIME_START.png", 10.72, internal_frame),
        "distant": ("KZ_CLIP_DISTANT_IMAGE_CONTINUOUS", "KZ_INNER02_DISTANT_IMAGE_START.png", 6.48, distant_frame),
        "empty": ("KZ_CLIP_EMPTY_SPIRAL_PAYOFF", "KZ_CLIP_EMPTY_SPIRAL_PAYOFF_START.png", 8.42, empty_frame),
    }
    selected = jobs.values() if only == "all" else [jobs[only]]
    for args in selected:
        encode(*args)
