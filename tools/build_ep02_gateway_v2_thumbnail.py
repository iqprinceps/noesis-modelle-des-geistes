from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "05_GENERATED" / "EP02_GATEWAY_V2" / "AI_FINAL" / "GWV2_IMG01_THREE_OBSERVERS_16x9.png"
DOC = ROOT / "06_PRODUCTION" / "EP02_GATEWAY_V2" / "visuals" / "document_crops" / "V2_DOC09_RECOMMENDATION_H.png"
OUT = ROOT / "06_PRODUCTION" / "EP02_GATEWAY_V2" / "thumbnail" / "GATEWAY_V2_THUMBNAIL_1920x1080.png"


def cover(im: Image.Image, size: tuple[int, int]) -> Image.Image:
    scale = max(size[0] / im.width, size[1] / im.height)
    resized = im.resize((round(im.width * scale), round(im.height * scale)), Image.Resampling.LANCZOS)
    left = (resized.width - size[0]) // 2
    top = (resized.height - size[1]) // 2
    return resized.crop((left, top, left + size[0], top + size[1]))


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(Path("C:/Windows/Fonts") / path), size)


def main() -> None:
    canvas = cover(Image.open(BASE).convert("RGB"), (1920, 1080))
    canvas = ImageEnhance.Contrast(canvas).enhance(1.12)
    canvas = ImageEnhance.Color(canvas).enhance(0.82)

    # Reserve a calm, high-contrast title field without hiding the three observers.
    shade = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    for x in range(1920):
        a = int(225 * max(0.0, 1.0 - x / 1280))
        sd.line((x, 0, x, 1080), fill=(2, 12, 15, a))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), shade)

    # The actual highlighted Recommendation H passage acts as evidence, not texture.
    doc = Image.open(DOC).convert("RGB")
    doc.thumbnail((780, 470), Image.Resampling.LANCZOS)
    doc = ImageEnhance.Contrast(doc).enhance(1.08)
    shadow = Image.new("RGBA", (doc.width + 50, doc.height + 50), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((20, 20, doc.width + 30, doc.height + 30), 18, fill=(0, 0, 0, 190))
    shadow = shadow.filter(ImageFilter.GaussianBlur(15))
    px, py = 1085, 520
    canvas.alpha_composite(shadow, (px - 25, py - 25))
    canvas.alpha_composite(doc.convert("RGBA"), (px, py))

    d = ImageDraw.Draw(canvas)
    white = (240, 241, 233, 255)
    gold = (236, 190, 65, 255)
    teal = (101, 214, 207, 255)
    small = font("arialbd.ttf", 34)
    title = font("arialbd.ttf", 112)
    d.text((88, 76), "U.S. ARMY FILE  •  1983", font=small, fill=teal, stroke_width=1, stroke_fill=(0, 0, 0, 220))
    d.text((80, 155), "PAST.", font=title, fill=white, stroke_width=5, stroke_fill=(0, 0, 0, 230))
    d.text((80, 275), "NOW.", font=title, fill=white, stroke_width=5, stroke_fill=(0, 0, 0, 230))
    d.text((80, 395), "FUTURE.", font=title, fill=gold, stroke_width=5, stroke_fill=(0, 0, 0, 230))
    d.rounded_rectangle((84, 548, 710, 618), 16, fill=(2, 18, 20, 225), outline=gold, width=3)
    d.text((112, 564), "THREE OBSERVERS. ONE TARGET.", font=font("arialbd.ttf", 29), fill=white)
    d.rounded_rectangle((1110, 469, 1505, 523), 12, fill=(2, 18, 20, 235), outline=teal, width=2)
    d.text((1131, 481), "THE ORIGINAL PASSAGE", font=font("arialbd.ttf", 25), fill=white)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(OUT, quality=95)
    print(OUT)


if __name__ == "__main__":
    main()
