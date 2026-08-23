#!/usr/bin/env python3
"""Create manually framed 16:9 composites from EP01 original source assets."""

from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter, ImageOps


ROOT = Path(__file__).resolve().parent.parent
APPROVED = ROOT / "04_ASSETS" / "02_CURATED" / "EP01_KOZYREV" / "APPROVED"
DOWNLOADS = ROOT / "04_ASSETS" / "01_DOWNLOADS" / "EP01_KOZYREV"
OUT = ROOT / "05_GENERATED" / "EP01_KOZYREV" / "05_ORIGINAL_COMPOSITES"
SRC = OUT / "sources"
COMMONS = DOWNLOADS / "WIKIMEDIA_COMMONS"
ADDITIONS = ROOT / "05_GENERATED" / "EP01_KOZYREV" / "06_IMAGEGEN_ADDITIONS"
SIZE = (2560, 1440)


def cover(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    ratio = max(size[0] / image.width, size[1] / image.height)
    resized = image.resize((round(image.width * ratio), round(image.height * ratio)), Image.Resampling.LANCZOS)
    left = (resized.width - size[0]) // 2
    top = (resized.height - size[1]) // 2
    return resized.crop((left, top, left + size[0], top + size[1]))


def contain_on_blur(source: Path, target: str | Path, *, position: float = 0.5,
                    crop: tuple[int, int, int, int] | None = None,
                    foreground_height: int = 1320, monochrome: bool = False) -> None:
    image = Image.open(source).convert("RGB")
    if crop:
        image = image.crop(crop)
    if monochrome:
        image = ImageOps.grayscale(image).convert("RGB")
    background = cover(image, SIZE).filter(ImageFilter.GaussianBlur(42))
    background = ImageEnhance.Brightness(background).enhance(0.30)
    background = ImageEnhance.Contrast(background).enhance(0.92)
    canvas = background.convert("RGBA")
    scale = min((SIZE[0] - 160) / image.width, foreground_height / image.height)
    foreground = image.resize((round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS)
    border = ImageOps.expand(foreground, border=5, fill=(224, 216, 188))
    shadow = Image.new("RGBA", (border.width + 34, border.height + 34), (0, 0, 0, 0))
    shadow.paste((0, 0, 0, 145), (17, 17, 17 + border.width, 17 + border.height))
    shadow = shadow.filter(ImageFilter.GaussianBlur(15))
    x = round((SIZE[0] - border.width) * position)
    x = max(30, min(x, SIZE[0] - border.width - 30))
    y = (SIZE[1] - border.height) // 2
    canvas.alpha_composite(shadow, (x - 17, y - 17))
    canvas.alpha_composite(border.convert("RGBA"), (x, y))
    target_path = target if isinstance(target, Path) else OUT / target
    target_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(target_path, quality=96)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    contain_on_blur(APPROVED / "KZ_001_Nikolai_Kozyrev_1959.png", "ORIG01_KOZYREV_FULL_WIDE.png")
    contain_on_blur(APPROVED / "KZ_001_Nikolai_Kozyrev_1959.png", "ORIG02_KOZYREV_FACE_AND_MOON_WIDE.png",
                    crop=(45, 0, 855, 560), foreground_height=1270)
    contain_on_blur(DOWNLOADS / "Kaznacheev_portrait.jpg", "ORIG03_KAZNACHEEV_FULL_WIDE.png",
                    position=0.28, foreground_height=1340)
    contain_on_blur(APPROVED / "KZ_003_Kozyrev_mirrors_modern_photo_2014.jpg", "ORIG04_MIRROR_2014_FULL_WIDE.png",
                    foreground_height=1340)
    contain_on_blur(APPROVED / "KZ_003_Kozyrev_mirrors_modern_photo_2014.jpg", "ORIG05_MIRROR_2014_DETAIL_WIDE.png",
                    crop=(0, 0, 540, 570), foreground_height=1260)
    contain_on_blur(APPROVED / "KZ_002_Kozyrev_mirror_apparatus_drawing_1996.jpg", "ORIG06_PATENT_DRAWING_FULL_WIDE.png",
                    foreground_height=1330)
    contain_on_blur(APPROVED / "KZ_004_Pulkovo_big_refractor.jpg", "ORIG07_REFRACTOR_FULL_WIDE.png",
                    position=0.62, foreground_height=1340, monochrome=True)
    contain_on_blur(APPROVED / "KZ_006_Pulkovo_26inch_refractor.jpg", "ORIG08_REFRACTOR_WIDE_SOURCE.png",
                    foreground_height=1280, monochrome=True)
    contain_on_blur(APPROVED / "KZ_005_Pulkovo_Observatory_1855.jpg", "ORIG09_OBSERVATORY_1855_WIDE.png",
                    foreground_height=1240, monochrome=True)
    page1 = Image.open(SRC / "PATENT_PAGE_01.png")
    page2 = Image.open(SRC / "PATENT_PAGE_02.png")
    page3 = Image.open(SRC / "PATENT_PAGE_03.png")
    page4 = Image.open(SRC / "PATENT_PAGE_04.png")
    contain_on_blur(SRC / "PATENT_PAGE_01.png", "ORIG10_PATENT_PAGE1_FULL_WIDE.png", foreground_height=1360)
    contain_on_blur(SRC / "PATENT_PAGE_01.png", "ORIG11_PATENT_HEADER_WIDE.png",
                    crop=(170, 80, page1.width - 150, 1160), foreground_height=1280)
    contain_on_blur(SRC / "PATENT_PAGE_01.png", "ORIG12_PATENT_FIGURE1_WIDE.png",
                    crop=(1020, 1210, 1710, 2380), foreground_height=1280)
    contain_on_blur(SRC / "PATENT_PAGE_03.png", "ORIG13_PATENT_DIMENSIONS_TEXT_WIDE.png",
                    crop=(1010, 720, 1820, 1510), foreground_height=1240)
    contain_on_blur(SRC / "PATENT_PAGE_02.png", "ORIG17_PATENT_PAGE2_FULL_WIDE.png",
                    foreground_height=1360)
    contain_on_blur(SRC / "PATENT_PAGE_04.png", "ORIG18_PATENT_PAGE4_FULL_WIDE.png",
                    foreground_height=1360)
    contain_on_blur(COMMONS / "KZ_WC_01_HORIZONTAL_BIG_G2PF_2015.jpg",
                    "ORIG14_COMMONS_HORIZONTAL_APPARATUS_WIDE.png", foreground_height=1260)
    contain_on_blur(COMMONS / "KZ_WC_02_BIG_S1_2015.jpg",
                    "ORIG15_COMMONS_PARTICIPANT_INSIDE_WIDE.png", position=0.46, foreground_height=1340)
    contain_on_blur(COMMONS / "KZ_WC_04_PATENT_APPARATUS_1992.gif",
                    "ORIG16_COMMONS_PATENT_APPARATUS_WIDE.png", foreground_height=1320)
    judges = Image.open(ADDITIONS / "IMG93_INDEPENDENT_JUDGES.png")
    contain_on_blur(ADDITIONS / "IMG93_INDEPENDENT_JUDGES.png",
                    ADDITIONS / "IMG93B_TARGET_POOL_DETAIL.png",
                    crop=(0, 315, judges.width, judges.height), foreground_height=1200)
    print(f"Created 18 manually framed composites in {OUT}")


if __name__ == "__main__":
    main()
