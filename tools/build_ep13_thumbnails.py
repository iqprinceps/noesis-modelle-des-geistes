#!/usr/bin/env python3
"""EP13_EN thumbnail variants.

Three concepts, built on this episode's own material rather than a template, and
checked at the sizes a viewer actually sees them: 25 percent and 18.75 percent of
full width.

The click reason is a bullet sitting in a jewelled crown, so variant A is the
object with nothing in its way. B adds the question the episode answers. C offers
the document angle for a test against A.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[1]
EP = ROOT / "07_ENGLISH_PRODUCTION" / "EP13_VATICAN_01"
AUTH = EP / "03_VISUALS" / "ASSETS" / "SELECTED" / "AUTHENTIC"
GEN = EP / "03_VISUALS" / "ASSETS" / "SELECTED" / "GENERATED"
OUT = EP / "07_THUMBNAILS"

W, H = 1920, 1080
FONTS = pathlib.Path("C:/Windows/Fonts")
SERIF_B = FONTS / "georgiab.ttf"
SERIF_I = FONTS / "georgiai.ttf"
CREAM = (243, 238, 229)
EMBER = (226, 138, 62)


def f(p, s):
    return ImageFont.truetype(str(p), s)


def tracked(d, xy, text, font, fill, track=0, shadow=6):
    """Letter-spaced line with a hard offset shadow, which survives the 18.75
    percent downscale better than a blurred one."""
    x, y = xy
    for dx, dy, col in ((shadow, shadow, (0, 0, 0)), (0, 0, fill)):
        xx = x + dx
        for ch in text:
            d.text((xx, y + dy), ch, font=font, fill=col)
            xx += d.textlength(ch, font=font) + track
    return xx - x


def fit(src: pathlib.Path, focus=(0.5, 0.5), zoom=1.0):
    """Crop to 16:9 and return the image plus a mapper from normalised source
    coordinates to canvas pixels, so an annotation can be pinned to the object
    rather than to a guessed screen position."""
    im = Image.open(src).convert("RGB")
    sc = max(W / im.width, H / im.height) * zoom
    sw, sh = max(W, int(im.width * sc)), max(H, int(im.height * sc))
    im = im.resize((sw, sh), Image.LANCZOS)
    cx, cy = int(sw * focus[0]), int(sh * focus[1])
    left = min(max(0, cx - W // 2), sw - W)
    top = min(max(0, cy - H // 2), sh - H)

    def where(u, v):
        return sw * u - left, sh * v - top

    return im.crop((left, top, left + W, top + H)), where, sc


# The projectile in EP13_HA01: the dull grey cone at the junction of the arches,
# directly under the sky-blue orb. Measured off the source frame, not estimated.
BULLET = (0.534, 0.497)
BULLET_R = 0.062   # of source width


def ring(d, cxy, r, weight=8):
    """Ember circle with a dark inner halo, so it holds against gold at 18.75
    percent."""
    x, y = cxy
    for rr, col, wd in ((r + weight * 1.6, (12, 8, 6), weight + 5),
                        (r, EMBER, weight)):
        d.ellipse((x - rr, y - rr, x + rr, y + rr), outline=col, width=wd)


def scrim(im, side="bottom", strength=190):
    lay = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(lay)
    for i in range(H):
        t = i / H
        v = t if side == "bottom" else (1 - t)
        d.line((0, i, W, i), fill=int(strength * (v ** 1.7)))
    dark = Image.new("RGB", (W, H), (8, 6, 5))
    return Image.composite(dark, im, lay)


def crown(zoom, focus, scrim_strength):
    """Base plate: the crown stays whole and readable as a crown, and the
    projectile is ringed. Ringing it is the whole point — dull grey lead against
    gold is invisible at thumbnail size, and a claim the viewer cannot see is a
    claim they will not click."""
    im, where, _ = fit(AUTH / "EP13_HA01_crown_bullet_CTV_2017.png", focus, zoom)
    im = scrim(im, "bottom", scrim_strength)
    d = ImageDraw.Draw(im)
    ring(d, where(*BULLET), BULLET_R * 1174 * (W / 1174) * zoom * 0.92)
    return im, d


def variant_a():
    """The object, named, nothing else."""
    im, d = crown(1.02, (0.50, 0.46), 200)
    tracked(d, (104, 762), "THE BULLET", f(SERIF_B, 150), CREAM, 6)
    tracked(d, (104, 912), "IN THE CROWN", f(SERIF_B, 150), EMBER, 6)
    return im, "EP13_EN_THUMB_A_OBJECT.jpg", "the ringed object, named, no question asked"


def variant_b():
    """The object plus the question the episode answers."""
    im, d = crown(1.02, (0.50, 0.46), 214)
    tracked(d, (104, 692), "IT WAS FIRED", f(SERIF_B, 130), CREAM, 5)
    tracked(d, (104, 820), "AT A POPE.", f(SERIF_B, 130), CREAM, 5)
    d.text((108, 966), "Why is it in her crown?", font=f(SERIF_I, 82), fill=(0, 0, 0))
    d.text((104, 962), "Why is it in her crown?", font=f(SERIF_I, 82), fill=EMBER)
    return im, "EP13_EN_THUMB_B_QUESTION.jpg", "ringed object plus the question, strongest promise"


def variant_c():
    """The sealed document angle, for a test against the object."""
    im, _, _ = fit(GEN / "EP13_H01_ENVELOPE_SEALED.png", focus=(0.5, 0.5), zoom=1.2)
    im = scrim(im, "bottom", 200)
    d = ImageDraw.Draw(im)
    tracked(d, (110, 700), "TWO POPES", f(SERIF_B, 140), CREAM, 5)
    tracked(d, (110, 836), "READ IT.", f(SERIF_B, 140), CREAM, 5)
    d.text((118, 984), "Neither said what was inside.", font=f(SERIF_I, 76), fill=(0, 0, 0))
    d.text((114, 980), "Neither said what was inside.", font=f(SERIF_I, 76), fill=EMBER)
    return im, "EP13_EN_THUMB_C_SEALED.jpg", "the sealed document angle"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default=str(OUT))
    a = ap.parse_args()
    outdir = pathlib.Path(a.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    entries = []
    for fn in (variant_a, variant_b, variant_c):
        im, name, concept = fn()
        p = outdir / name
        im.save(p, quality=94, subsampling=0)
        for pct, tag in ((0.25, "25"), (0.1875, "1875")):
            s = im.resize((int(W * pct), int(H * pct)), Image.LANCZOS)
            s.resize((int(W * 0.6), int(H * 0.6)), Image.NEAREST).save(
                outdir / f"QA_{tag}_{name}", quality=88)
        entries.append({"file": name, "concept": concept, "size": f"{W}x{H}",
                        "bytes": p.stat().st_size,
                        "sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
        print("OK  " + name)
    (outdir / "THUMBNAIL_MANIFEST.json").write_text(
        json.dumps({"variants": entries,
                    "base_asset": "EP13_HA01 crown, Centro Televisivo Vaticano, CC BY 3.0",
                    "note": "1920x1080 rather than 4K: the only rights-clear photograph of "
                            "the crown is 1174x768, so a larger canvas would be empty upscale."},
                   indent=2) + "\n", encoding="utf-8")
    print(f"{len(entries)} variants -> {outdir}")


if __name__ == "__main__":
    main()
