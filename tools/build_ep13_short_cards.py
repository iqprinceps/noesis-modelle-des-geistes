#!/usr/bin/env python3
"""End cards for the EP13 teaser shorts, 1080x1920.

One card per short per language. They carry the series name and the one thing a
teaser has to do at the end, which is say that there is more and where it is.
The open question stays on screen with it, because the comment is the point.

Type and substrate come from the episode's card system, so a viewer who arrives
from a short and then opens the episode sees the same hand.
"""

from __future__ import annotations

import argparse
import pathlib

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[1]
SUB = ROOT / "tmp" / "imagegen" / "ep13_vertex_raw" / "cards"
OUT = ROOT / "tmp" / "imagegen" / "ep13_short_cards"

W, H = 1080, 1920
FONTS = pathlib.Path("C:/Windows/Fonts")
SERIF = FONTS / "georgia.ttf"
SERIF_B = FONTS / "georgiab.ttf"
SERIF_I = FONTS / "georgiai.ttf"
EMBER_LIT = (222, 138, 70)
CREAM = (240, 234, 224)
CREAM_SOFT = (196, 184, 168)


def f(p, s):
    return ImageFont.truetype(str(p), s)


def tracked(d, xy, text, font, fill, track=0):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        x += d.textlength(ch, font=font) + track
    return x - xy[0]


def substrate() -> Image.Image:
    """The episode's dark wood, cropped tall and darkened at top and bottom so the
    interface a phone puts there has something to sit on."""
    src = SUB / "EP13_SUB03_DARK_WOOD.png"
    im = Image.open(src).convert("RGB") if src.is_file() else Image.new("RGB", (W, H), (26, 20, 15))
    sc = max(W / im.width, H / im.height) * 1.2
    im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
    left = (im.width - W) // 2
    top = (im.height - H) // 2
    im = im.crop((left, top, left + W, top + H))
    lay = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(lay)
    for i in range(H):
        t = i / H
        v = max(0.0, 1 - t / 0.26) ** 1.6 + max(0.0, (t - 0.74) / 0.26) ** 1.6
        d.line((0, i, W, i), fill=int(150 * min(1.0, v)))
    return Image.composite(Image.new("RGB", (W, H), (8, 6, 5)), im, lay)


CARDS = {
    "EN_S01": ("VATICAN FILES", ["The full", "file is", "linked."],
               "WORLD", "or", "MYSELF", "Leave one word."),
    "EN_S02": ("VATICAN FILES", ["The full", "file is", "linked."],
               "WORLD", "or", "MYSELF", "What did you assume?"),
    "DE_S01": ("VATIKAN-AKTEN", ["Die ganze", "Akte ist", "verlinkt."],
               "WELT", "oder", "ICH", "Ein Wort genügt."),
    "DE_S02": ("VATIKAN-AKTEN", ["Die ganze", "Akte ist", "verlinkt."],
               "WELT", "oder", "ICH", "Was haben Sie vermutet?"),
}


def build(key):
    label, lines, a, conn, b, foot = CARDS[key]
    base = substrate()
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    x, y = 96, 560
    tracked(d, (x, y), label, f(SERIF_B, 40), EMBER_LIT, track=16)
    for i, line in enumerate(lines):
        d.text((x - 3, y + 92 + i * 118), line, font=f(SERIF, 108), fill=CREAM)
    ry = y + 92 + len(lines) * 118 + 66
    d.line((x, ry, x + 700, ry), fill=CREAM_SOFT, width=3)
    fb = f(SERIF_B, 76)
    fi = f(SERIF_I, 50)
    w1 = tracked(d, (x, ry + 46), a, fb, CREAM, track=10)
    d.text((x + w1 + 40, ry + 62), conn, font=fi, fill=CREAM_SOFT)
    gap = 40 + d.textlength(conn, font=fi) + 38
    tracked(d, (x + w1 + gap, ry + 46), b, fb, EMBER_LIT, track=10)
    d.text((x - 2, ry + 168), foot, font=f(SERIF_I, 54), fill=CREAM_SOFT)
    sh = lay.split()[3].filter(ImageFilter.GaussianBlur(6))
    out = Image.new("RGB", (W, H))
    out.paste(Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), base, sh.point(lambda v: v // 3)))
    return Image.alpha_composite(out.convert("RGBA"), lay).convert("RGB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default=str(OUT))
    a = ap.parse_args()
    outdir = pathlib.Path(a.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    for key in CARDS:
        img = build(key)
        name = f"EP13_SHORTCARD_{key}.png"
        img.save(outdir / name)
        print("OK  " + name)
    print(f"{len(CARDS)} cards -> {outdir}")


if __name__ == "__main__":
    main()
