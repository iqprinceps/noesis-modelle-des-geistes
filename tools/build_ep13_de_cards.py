#!/usr/bin/env python3
"""EP13 viewer cards.

Each card is composited onto a photographed material surface generated for this
episode, not drawn as a primitive. Typography is Georgia, which the channel
already uses for card titles, set large enough to survive a 246 px viewport.

Ink never sits at pure black and the ember accent is the only colour allowed, so
the cards belong to the same palette as the episode's two registers.
"""

from __future__ import annotations

import argparse
import math
import pathlib
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
SUB = ROOT / "tmp" / "imagegen" / "ep13_vertex_raw" / "cards"
OUT = ROOT / "tmp" / "imagegen" / "ep13_cards_de"

W, H = 2752, 1536
FONTS = pathlib.Path("C:/Windows/Fonts")
SERIF = FONTS / "georgia.ttf"
SERIF_B = FONTS / "georgiab.ttf"
SERIF_I = FONTS / "georgiai.ttf"

INK = (30, 24, 17)
INK_SOFT = (74, 63, 50)
EMBER = (180, 80, 28)
EMBER_LIT = (222, 138, 70)      # Ember auf dunklem Holz, sonst unlesbar
CREAM = (240, 234, 224)
CREAM_SOFT = (196, 184, 168)
PALE_INK = (56, 54, 54)         # dunkler als zuvor, fuer Mobilkontrast
PALE_SOFT = (118, 116, 116)


def f(path: pathlib.Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size)


def tracked(draw: ImageDraw.ImageDraw, xy, text: str, font, fill, track: int = 0):
    """Draw text with manual letter tracking; returns the advance width."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + track
    return x - xy[0] - (track if text else 0)


def tracked_width(draw: ImageDraw.ImageDraw, text: str, font, track: int = 0) -> float:
    if not text:
        return 0.0
    return sum(draw.textlength(c, font=font) for c in text) + track * (len(text) - 1)


def ink_rule(draw: ImageDraw.ImageDraw, x0, y, x1, colour, weight=5, jitter=2.0, seed=1):
    """A slightly irregular ruled line so it reads as drawn, not as a UI divider."""
    rnd = random.Random(seed)
    steps = max(2, int((x1 - x0) / 24))
    pts = []
    for i in range(steps + 1):
        t = i / steps
        pts.append((x0 + (x1 - x0) * t, y + rnd.uniform(-jitter, jitter)))
    draw.line(pts, fill=colour, width=weight, joint="curve")


def substrate(name: str, rotate: float = 0.0) -> Image.Image:
    im = Image.open(SUB / name).convert("RGB").resize((W, H), Image.LANCZOS)
    if rotate:
        im = im.rotate(rotate, resample=Image.BICUBIC, expand=False)
    return im


def paper_shadow(layer: Image.Image) -> Image.Image:
    """Soft drop under the type so it sits on the surface instead of floating."""
    sh = layer.split()[3].filter(ImageFilter.GaussianBlur(7))
    out = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    out.paste((0, 0, 0, 60), (0, 5), sh)
    return Image.alpha_composite(out, layer)


CARDS = []


def card(fn):
    CARDS.append(fn)
    return fn


@card
def card01_1944():
    base = substrate("EP13_SUB06_PAPER_LAID.png")
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    x, y = 330, 460
    tracked(d, (x, y), "3. JANUAR 1944", f(SERIF_B, 58), INK_SOFT, track=16)
    d.text((x - 6, y + 124), "Sie schreibt den", font=f(SERIF, 186), fill=INK)
    d.text((x - 6, y + 336), "dritten Teil nieder.", font=f(SERIF, 186), fill=INK)
    ink_rule(d, x, y + 606, x + 700, INK_SOFT, weight=4, seed=4)
    return base, lay, "EP13_DE_CARD01_1944.png"


@card
def card02_1957():
    base = substrate("EP13_SUB05_ENVELOPE_BLANK.png")
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    x, y = 1560, 170
    tracked(d, (x, y), "1957", f(SERIF_B, 68), EMBER_LIT, track=22)
    d.text((x - 6, y + 132), "Der Umschlag", font=f(SERIF, 150), fill=CREAM)
    d.text((x - 6, y + 304), "erreicht Rom.", font=f(SERIF, 150), fill=CREAM)
    d.text((x, y + 516), "Archiv des", font=f(SERIF_I, 72), fill=CREAM_SOFT)
    d.text((x, y + 616), "Heiligen Offiziums", font=f(SERIF_I, 72), fill=CREAM_SOFT)
    return base, lay, "EP13_DE_CARD02_1957.png"


@card
def card03_two_popes():
    base = substrate("EP13_SUB02_PAPER_FULL.png")
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    x = 330
    tracked(d, (x, 320), "1959", f(SERIF_B, 158), INK, track=8)
    d.text((x + 500, 344), "Johannes XXIII. liest ihn.", font=f(SERIF, 116), fill=INK_SOFT)
    ink_rule(d, x, 566, W - 330, INK_SOFT, weight=3, jitter=2.5, seed=11)
    tracked(d, (x, 668), "1965", f(SERIF_B, 158), INK, track=8)
    d.text((x + 500, 692), "Paul VI. liest ihn.", font=f(SERIF, 116), fill=INK_SOFT)
    ink_rule(d, x, 914, W - 330, INK_SOFT, weight=3, jitter=2.5, seed=12)
    d.text((x, 1016), "Keiner veröffentlicht ihn.", font=f(SERIF_I, 132), fill=EMBER)
    return base, lay, "EP13_DE_CARD03_TWO_POPES.png"


@card
def card04_1981():
    base = substrate("EP13_SUB03_DARK_WOOD.png")
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    x, y = 320, 430
    tracked(d, (x, y), "18. JULI 1981", f(SERIF_B, 70), EMBER_LIT, track=20)
    d.text((x - 6, y + 140), "Zwei Umschläge", font=f(SERIF, 182), fill=CREAM)
    d.text((x - 6, y + 348), "werden ihm gebracht.", font=f(SERIF, 182), fill=CREAM)
    d.text((x, y + 606), "Das portugiesische Original und eine italienische Übersetzung",
           font=f(SERIF_I, 74), fill=CREAM_SOFT)
    return base, lay, "EP13_DE_CARD04_1981.png"


@card
def card05_2000():
    base = substrate("EP13_SUB07_PAPER_WARM.png")
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    x, y = 340, 440
    tracked(d, (x, y), "26. JUNI 2000", f(SERIF_B, 62), INK_SOFT, track=18)
    d.text((x - 6, y + 130), "Das Manuskript", font=f(SERIF, 184), fill=INK)
    d.text((x - 6, y + 340), "wird veröffentlicht.", font=f(SERIF, 184), fill=INK)
    d.text((x, y + 604), "Kongregation für die Glaubenslehre",
           font=f(SERIF_I, 72), fill=INK_SOFT)
    return base, lay, "EP13_DE_CARD05_2000.png"


def _subtraction(items, struck: bool, heading: str, out: str, seed0: int):
    base = substrate("EP13_SUB04_PALE_FIELD.png")
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    x, y = 360, 330
    tracked(d, (x, y), heading.upper(), f(SERIF_B, 50), PALE_SOFT, track=16)
    fnt = f(SERIF, 132)
    yy = y + 150
    for i, it in enumerate(items):
        col = PALE_SOFT if struck else PALE_INK
        d.text((x, yy), it, font=fnt, fill=col)
        if struck:
            wdt = d.textlength(it, font=fnt)
            ink_rule(d, x - 14, yy + 82, x + wdt + 14, (150, 74, 40), weight=6,
                     jitter=3.0, seed=seed0 + i)
        yy += 186
    return base, lay, out


@card
def card06_contains():
    return _subtraction(
        ["Ein Engel mit einem Flammenschwert", "Ein Bischof in Weiß",
         "Eine Stadt, halb in Trümmern", "Ein Berg und ein Kreuz"],
        False, "Auf der Seite steht", "EP13_DE_CARD06_CONTAINS.png", 20)


@card
def card07_never_says():
    return _subtraction(
        ["Ein Name", "Ein Datum", "Der Petersplatz", "Ein Überlebender"],
        True, "Auf der Seite steht nie", "EP13_DE_CARD07_NEVER_SAYS.png", 30)


@card
def card08_decision():
    base = substrate("EP13_SUB03_DARK_WOOD.png").transpose(Image.FLIP_LEFT_RIGHT)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    fnt = f(SERIF_B, 230)
    lab = f(SERIF_I, 74)
    w1 = tracked_width(d, "WELT", fnt, 20)
    w2 = tracked_width(d, "ICH", fnt, 20)
    orw = d.textlength("oder", font=lab)
    gap = 150
    total = w1 + gap + orw + gap + w2
    x = (W - total) / 2
    y = 600
    tracked(d, (x, y), "WELT", fnt, CREAM, track=20)
    d.text((x + w1 + gap, y + 82), "oder", font=lab, fill=(150, 140, 126))
    tracked(d, (x + w1 + gap + orw + gap, y), "ICH", fnt, EMBER_LIT, track=20)
    sub = "Wonach haben Sie gesucht?"
    sf = f(SERIF_I, 76)
    d.text(((W - d.textlength(sub, font=sf)) / 2, y + 340), sub, font=sf, fill=CREAM_SOFT)
    return base, lay, "EP13_DE_CARD08_DECISION.png"


@card
def card09_credit():
    base = substrate("EP13_SUB03_DARK_WOOD.png").transpose(Image.ROTATE_180)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    x, y = 330, 470
    tracked(d, (x, y), "BILD", f(SERIF_B, 58), EMBER_LIT, track=20)
    d.text((x, y + 128), "Krone Unserer Lieben", font=f(SERIF, 128), fill=CREAM)
    d.text((x, y + 274), "Frau von Fatima", font=f(SERIF, 128), fill=CREAM)
    d.text((x, y + 452), "Centro Televisivo Vaticano, 2017", font=f(SERIF_I, 78), fill=CREAM_SOFT)
    d.text((x, y + 566), "CC BY 3.0, beschnitten", font=f(SERIF, 72), fill=CREAM_SOFT)
    return base, lay, "EP13_DE_CARD09_CREDIT.png"


@card
def card10_decision_end():
    base = substrate("EP13_SUB07_PAPER_WARM.png").transpose(Image.FLIP_LEFT_RIGHT)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    x, y = 340, 400
    tracked(d, (x, y), "BEVOR SIE GEHEN", f(SERIF_B, 54), INK_SOFT, track=18)
    d.text((x - 6, y + 128), "Wonach haben Sie", font=f(SERIF, 168), fill=INK)
    d.text((x - 6, y + 320), "gesucht?", font=f(SERIF, 168), fill=INK)
    ink_rule(d, x, y + 566, x + 900, INK_SOFT, weight=4, seed=71)
    w1 = tracked(d, (x, y + 616), "WELT", f(SERIF_B, 108), INK, track=12)
    fi = f(SERIF_I, 68)
    d.text((x + w1 + 60, y + 636), "oder", font=fi, fill=INK_SOFT)
    gap = 60 + d.textlength("oder", font=fi) + 55
    tracked(d, (x + w1 + gap, y + 616), "ICH", f(SERIF_B, 108), EMBER, track=12)
    return base, lay, "EP13_DE_CARD10_DECISION_END.png"


@card
def card11_end_screen():
    """The end screen hold.

    YouTube places its end screen elements over the last seconds of the film, so
    the right of the frame is deliberately left as bare wood: the subscribe badge
    and the next-video thumbnail go there. Everything written sits in the left
    third, and nothing important comes near the lower right corner.
    """
    base = substrate("EP13_SUB03_DARK_WOOD.png")
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    x, y = 250, 330
    tracked(d, (x, y), "VATIKAN-AKTEN", f(SERIF_B, 52), EMBER_LIT, track=22)
    d.text((x - 4, y + 116), "Nächstes Mal: 81", font=f(SERIF, 132), fill=CREAM)
    d.text((x - 4, y + 268), "Siegel, und ein Papst,", font=f(SERIF, 132), fill=CREAM)
    d.text((x - 4, y + 420), "der Nein sagte.", font=f(SERIF, 132), fill=CREAM)
    ink_rule(d, x, y + 620, x + 940, CREAM_SOFT, weight=4, jitter=1.6, seed=113)
    w1 = tracked(d, (x, y + 672), "WELT", f(SERIF_B, 84), CREAM, track=12)
    fi = f(SERIF_I, 56)
    d.text((x + w1 + 48, y + 688), "oder", font=fi, fill=CREAM_SOFT)
    gap = 48 + d.textlength("oder", font=fi) + 44
    tracked(d, (x + w1 + gap, y + 672), "ICH", f(SERIF_B, 84), EMBER_LIT, track=12)
    d.text((x - 2, y + 800), "Ein Wort in die Kommentare.", font=f(SERIF_I, 62), fill=CREAM_SOFT)
    return base, lay, "EP13_DE_CARD11_END_SCREEN.png"


def mobile_check(img: Image.Image, name: str, outdir: pathlib.Path) -> None:
    small = img.resize((246, int(246 * H / W)), Image.LANCZOS)
    small.resize((984, int(984 * H / W)), Image.NEAREST).save(
        outdir / ("MOBILE_" + name.replace(".png", ".jpg")), quality=85)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default=str(OUT))
    args = ap.parse_args()
    outdir = pathlib.Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    made = []
    for fn in CARDS:
        base, lay, name = fn()
        composed = Image.alpha_composite(base.convert("RGBA"), paper_shadow(lay)).convert("RGB")
        composed.save(outdir / name)
        mobile_check(composed, name, outdir)
        made.append(name)
        print("OK  " + name, flush=True)
    print(str(len(made)) + " Karten -> " + str(outdir))


if __name__ == "__main__":
    main()
