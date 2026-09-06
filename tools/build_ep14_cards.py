#!/usr/bin/env python3
"""EP14 typographic cards.

Same hand as EP13: Georgia on the generated paper and wood substrates, an ember
accent, irregular ink rules. A viewer moving between episodes should see one
series, so the card system is inherited rather than redesigned.

What the cards carry here is different, because this episode counts things. The
object is a list: 83 signatures, 81 seals, 4 absences. Numbers that specific
belong on screen where they can be read, not only in the narration where they
slide past.
"""

from __future__ import annotations

import argparse
import pathlib

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[1]
SUB = ROOT / "tmp" / "imagegen" / "ep13_vertex_raw" / "cards"
OUT = ROOT / "tmp" / "imagegen" / "ep14_cards"

W, H = 2752, 1536
FONTS = pathlib.Path("C:/Windows/Fonts")
SERIF = FONTS / "georgia.ttf"
SERIF_B = FONTS / "georgiab.ttf"
SERIF_I = FONTS / "georgiai.ttf"
INK = (30, 24, 17)
INK_SOFT = (74, 63, 50)
EMBER = (180, 80, 28)
EMBER_LIT = (222, 138, 70)
CREAM = (240, 234, 224)
CREAM_SOFT = (196, 184, 168)

CARDS = []


def card(fn):
    CARDS.append(fn)
    return fn


def f(p, s):
    return ImageFont.truetype(str(p), s)


def tracked(d, xy, text, font, fill, track=0):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        x += d.textlength(ch, font=font) + track
    return x - xy[0]


def ink_rule(d, x0, y, x1, colour, weight=5, jitter=2.0, seed=1):
    import random
    r = random.Random(seed)
    step = 26
    x = x0
    while x < x1:
        nx = min(x1, x + step)
        d.line((x, y + r.uniform(-jitter, jitter), nx, y + r.uniform(-jitter, jitter)),
               fill=colour, width=weight)
        x = nx


def substrate(name, rotate=0.0, flip=False):
    p = SUB / name
    im = Image.open(p).convert("RGB") if p.is_file() else Image.new("RGB", (W, H), (232, 226, 214))
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    if rotate:
        im = im.rotate(rotate, resample=Image.BICUBIC, expand=False)
    sc = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
    left, top = (im.width - W) // 2, (im.height - H) // 2
    return im.crop((left, top, left + W, top + H))


def compose(base, lay):
    sh = lay.split()[3].filter(ImageFilter.GaussianBlur(7))
    dark = Image.new("RGB", (W, H), (0, 0, 0))
    base = Image.composite(dark, base, sh.point(lambda v: v // 4))
    return Image.alpha_composite(base.convert("RGBA"), lay).convert("RGB")


@card
def card01_the_object():
    base = substrate("EP13_SUB02_PAPER_FULL.png")
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    x, y = 300, 330
    tracked(d, (x, y), "13 JULY 1530", f(SERIF_B, 54), INK_SOFT, track=18)
    rows = [("83", "signatures, in thirteen columns"),
            ("81", "seals, each in its own tin case"),
            ("4", "positions where a seal never came")]
    yy = y + 130
    for num, label in rows:
        w = tracked(d, (x, yy), num, f(SERIF_B, 132), INK, track=4)
        d.text((x + max(w, 210) + 60, yy + 46), label, font=f(SERIF, 76), fill=INK_SOFT)
        ink_rule(d, x, yy + 168, x + 1900, INK_SOFT, weight=3, jitter=1.4, seed=int(num))
        yy += 220
    return base, lay, "EP14_CARD01_THE_OBJECT.png"


@card
def card02_secretum():
    base = substrate("EP13_SUB06_PAPER_LAID.png", flip=True)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    x, y = 320, 420
    tracked(d, (x, y), "THE WORD", f(SERIF_B, 54), INK_SOFT, track=18)
    d.text((x - 6, y + 128), "secretum", font=f(SERIF_I, 190), fill=INK)
    d.text((x - 2, y + 372), "private. Belonging to the pope,", font=f(SERIF, 84), fill=INK_SOFT)
    d.text((x - 2, y + 480), "the way a private secretary does.", font=f(SERIF, 84), fill=INK_SOFT)
    ink_rule(d, x, y + 630, x + 1500, INK_SOFT, weight=4, seed=17)
    d.text((x - 2, y + 676), "Renamed in 2019.", font=f(SERIF_I, 72), fill=EMBER)
    return base, lay, "EP14_CARD02_SECRETUM.png"


@card
def card03_opened():
    # SUB01 is a small sheet lying on wood and the lines ran off its edge; the
    # full-bleed warm paper takes the width this card needs.
    base = substrate("EP13_SUB07_PAPER_WARM.png")
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    x, y = 320, 400
    for year, line in (("1881", "Leo the Thirteenth opens it."),
                       ("1958", "Access reaches the end of Pius the Twelfth.")):
        tracked(d, (x, y), year, f(SERIF_B, 112), INK, track=6)
        d.text((x + 380, y + 30), line, font=f(SERIF, 68), fill=INK_SOFT)
        ink_rule(d, x, y + 146, x + 1780, INK_SOFT, weight=3, jitter=1.4, seed=len(line))
        y += 220
    d.text((x - 2, y + 34), "Catalogues. Call numbers. Reading rooms.",
           font=f(SERIF_I, 74), fill=EMBER)
    return base, lay, "EP14_CARD03_OPENED.png"


@card
def card04_1810():
    base = substrate("EP13_SUB03_DARK_WOOD.png")
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    x, y = 300, 360
    tracked(d, (x, y), "1810 TO 1813", f(SERIF_B, 54), EMBER_LIT, track=20)
    w = tracked(d, (x - 6, y + 122), "3,239", f(SERIF_B, 210), CREAM, track=6)
    d.text((x + w + 70, y + 236), "crates to Paris", font=f(SERIF, 92), fill=CREAM_SOFT)
    ink_rule(d, x, y + 420, x + 1800, CREAM_SOFT, weight=4, seed=31)
    w2 = tracked(d, (x - 6, y + 468), "2,450", f(SERIF_B, 150), EMBER_LIT, track=6)
    d.text((x + w2 + 60, y + 546), "came back", font=f(SERIF, 84), fill=CREAM_SOFT)
    return base, lay, "EP14_CARD04_1810.png"


@card
def card05_decision():
    base = substrate("EP13_SUB03_DARK_WOOD.png", rotate=180)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    head = "You cannot bring all of it home."
    fh = f(SERIF, 122)
    d.text(((W - d.textlength(head, font=fh)) / 2, 470), head, font=fh, fill=CREAM)
    fb = f(SERIF_B, 156)
    fi = f(SERIF_I, 84)
    w1 = d.textlength("KEEP", font=fb)
    wo = d.textlength("or", font=fi)
    w2 = d.textlength("LEAVE", font=fb)
    total = w1 + 90 + wo + 90 + w2
    x = (W - total) / 2
    tracked(d, (x, 700), "KEEP", fb, CREAM, track=12)
    d.text((x + w1 + 90, 730), "or", font=fi, fill=CREAM_SOFT)
    tracked(d, (x + w1 + 90 + wo + 90, 700), "LEAVE", fb, EMBER_LIT, track=12)
    sub = "One word below."
    d.text(((W - d.textlength(sub, font=f(SERIF_I, 76))) / 2, 940), sub,
           font=f(SERIF_I, 76), fill=CREAM_SOFT)
    return base, lay, "EP14_CARD05_DECISION.png"


@card
def card06_dividing_line():
    base = substrate("EP13_SUB04_PALE_FIELD.png")
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    x, y = 300, 350
    tracked(d, (x, y), "WHERE THE LINE ACTUALLY RUNS", f(SERIF_B, 52), INK_SOFT, track=16)
    pairs = [("preserved", "lost"), ("catalogued", "understood")]
    yy = y + 140
    for a, b in pairs:
        wa = tracked(d, (x, yy), a, f(SERIF_B, 116), INK, track=6)
        d.text((x + wa + 60, yy + 34), "against", font=f(SERIF_I, 72), fill=INK_SOFT)
        wo = d.textlength("against", font=f(SERIF_I, 72))
        tracked(d, (x + wa + 60 + wo + 60, yy), b, f(SERIF_B, 116), EMBER, track=6)
        yy += 200
    ink_rule(d, x, yy + 20, x + 1700, INK_SOFT, weight=4, seed=57)
    d.text((x - 2, yy + 70), "Open against secret is the least interesting of the three.",
           font=f(SERIF_I, 70), fill=INK_SOFT)
    return base, lay, "EP14_CARD06_DIVIDING_LINE.png"


@card
def card07_credit():
    base = substrate("EP13_SUB03_DARK_WOOD.png", flip=True)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    x, y = 320, 440
    tracked(d, (x, y), "RECONSTRUCTION", f(SERIF_B, 54), EMBER_LIT, track=20)
    d.text((x, y + 128), "The 1530 letter is shown as a", font=f(SERIF, 96), fill=CREAM)
    d.text((x, y + 254), "reconstruction, built to its", font=f(SERIF, 96), fill=CREAM)
    d.text((x, y + 380), "recorded measurements.", font=f(SERIF, 96), fill=CREAM)
    d.text((x, y + 546), "No signature on it is real.", font=f(SERIF_I, 78), fill=CREAM_SOFT)
    return base, lay, "EP14_CARD07_CREDIT.png"


@card
def card08_end_screen():
    base = substrate("EP13_SUB03_DARK_WOOD.png")
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    x, y = 250, 330
    tracked(d, (x, y), "VATICAN FILES", f(SERIF_B, 52), EMBER_LIT, track=22)
    d.text((x - 4, y + 116), "Next: a forgery that", font=f(SERIF, 132), fill=CREAM)
    d.text((x - 4, y + 268), "ran for seven hundred", font=f(SERIF, 132), fill=CREAM)
    d.text((x - 4, y + 420), "years.", font=f(SERIF, 132), fill=CREAM)
    ink_rule(d, x, y + 620, x + 940, CREAM_SOFT, weight=4, jitter=1.6, seed=113)
    fb, fi = f(SERIF_B, 84), f(SERIF_I, 56)
    w1 = tracked(d, (x, y + 672), "KEEP", fb, CREAM, track=12)
    d.text((x + w1 + 48, y + 688), "or", font=fi, fill=CREAM_SOFT)
    gap = 48 + d.textlength("or", font=fi) + 44
    tracked(d, (x + w1 + gap, y + 672), "LEAVE", fb, EMBER_LIT, track=12)
    d.text((x - 2, y + 800), "What did you decide at the crates?",
           font=f(SERIF_I, 62), fill=CREAM_SOFT)
    return base, lay, "EP14_CARD08_END_SCREEN.png"


def mobile_check(img, name, outdir):
    small = img.resize((246, int(246 * H / W)), Image.LANCZOS)
    small.resize((984, int(984 * H / W)), Image.NEAREST).save(
        outdir / ("MOBILE_" + name.replace(".png", ".jpg")), quality=85)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default=str(OUT))
    a = ap.parse_args()
    outdir = pathlib.Path(a.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    for fn in CARDS:
        base, lay, name = fn()
        img = compose(base, lay)
        img.save(outdir / name)
        mobile_check(img, name, outdir)
        print("OK  " + name)
    print(f"{len(CARDS)} cards -> {outdir}")


if __name__ == "__main__":
    main()
