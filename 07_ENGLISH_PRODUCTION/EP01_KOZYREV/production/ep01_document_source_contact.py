#!/usr/bin/env python3
"""Create local-only source review sheets for EP01 document evidence QA."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


EP = Path(__file__).resolve().parents[1]
OUT = EP / "05_QA" / "DOCUMENT_EVIDENCE" / "SOURCE_REVIEW"


def font(size: int):
    for path in (Path("C:/Windows/Fonts/segoeui.ttf"), Path("C:/Windows/Fonts/arial.ttf")):
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def sheet(paths: list[Path], out: Path, title: str) -> None:
    cell_w, cell_h = 960, 820
    page = Image.new("RGB", (cell_w * 2, cell_h * 2), (13, 18, 21))
    draw = ImageDraw.Draw(page)
    for slot, path in enumerate(paths):
        x = (slot % 2) * cell_w
        y = (slot // 2) * cell_h
        image = Image.open(path).convert("RGB")
        image.thumbnail((900, 720), Image.Resampling.LANCZOS)
        page.paste(image, (x + (cell_w - image.width) // 2, y + 78 + (720 - image.height) // 2))
        draw.text((x + 24, y + 18), path.name, font=font(28), fill=(239, 236, 224))
        draw.rectangle((x, y, x + cell_w - 1, y + cell_h - 1), outline=(77, 87, 89), width=2)
    draw.text((24, page.height - 32), title, font=font(18), fill=(224, 174, 71))
    out.parent.mkdir(parents=True, exist_ok=True)
    page.save(out, quality=94)


def main() -> None:
    patent = EP / "04_SOURCES" / "RENDERS" / "PATENT"
    pages = [patent / f"RU2122446C1-{number}.png" for number in range(1, 9)]
    sheet(pages[:4], OUT / "PATENT_SOURCE_PAGES_01.jpg", "Official source scan | pages 1-4")
    sheet(pages[4:], OUT / "PATENT_SOURCE_PAGES_02.jpg", "Official source scan | pages 5-8")


if __name__ == "__main__":
    main()
