#!/usr/bin/env python3
"""EP07 archival-source fidelity and generated-text cleanup pass.

This script does not invent historical content. It places the original source
photographs into the already generated 16:9 documentary layouts and softens
generated placeholder writing where a prompt explicitly requires unreadable text.
"""

from __future__ import annotations

import pathlib
import shutil

from PIL import Image, ImageDraw, ImageFilter


ROOT = pathlib.Path(__file__).resolve().parent.parent
KIT = ROOT / "06_PRODUCTION" / "EP07_SCHLAFPARALYSE_V4" / "IMAGE_GENERATION_KIT"
ASSETS = KIT / "02_ASSETS"
RAW = ROOT / "tmp" / "imagegen" / "ep07_vertex_raw"
QA = ROOT / "tmp" / "imagegen" / "ep07_vertex_qa"
COMAN = ROOT / "tmp" / "pdfs" / "ep07" / "Richard_Coman_page1.png"


def copy_raw() -> None:
    QA.mkdir(parents=True, exist_ok=True)
    for source in RAW.glob("*.png"):
        if source.name.startswith("_"):
            continue
        shutil.copy2(source, QA / source.name)


def fit_inside(image: Image.Image, width: int, height: int) -> Image.Image:
    copy = image.copy().convert("RGB")
    copy.thumbnail((width, height), Image.Resampling.LANCZOS)
    return copy


def framed_insert(base: Image.Image, source: Image.Image, box: tuple[int, int, int, int],
                  matte: int = 28, frame: int = 8) -> None:
    x, y, width, height = box
    draw = ImageDraw.Draw(base)
    draw.rounded_rectangle(
        (x - matte, y - matte, x + width + matte, y + height + matte),
        radius=12,
        fill=(24, 23, 22),
        outline=(72, 66, 59),
        width=frame,
    )
    fitted = fit_inside(source, width, height)
    px = x + (width - fitted.width) // 2
    py = y + (height - fitted.height) // 2
    base.paste(fitted, (px, py))


def save(name: str, image: Image.Image) -> None:
    image.save(QA / name, format="PNG", optimize=False)


def fix_img003() -> None:
    name = "IMG003_PRIVATE_NIGHT_TO_COURT.png"
    base = Image.open(RAW / name).convert("RGB")
    source = Image.open(COMAN).convert("RGB")
    # Crop only the neutral capture margin. The complete paper and color ruler remain.
    source = source.crop((545, 70, 1450, 1320))
    framed_insert(base, source, (1870, 150, 720, 1220), matte=24)
    save(name, base)


def fix_img005() -> None:
    name = "IMG005_NIGHTMARE_MOTIF_ROOM_BASE.png"
    base = Image.open(RAW / name).convert("RGB")
    source = Image.open(ASSETS / "EP07_Fuseli_The_Nightmare_1781.jpg").convert("RGB")
    framed_insert(base, source, (815, 205, 1120, 1010), matte=22)
    save(name, base)


def fix_img008() -> None:
    name = "IMG008_BURNEY_RELIEF_SOURCE_ROOM.png"
    base = Image.open(RAW / name).convert("RGB")
    source = Image.open(ASSETS / "EP07_Queen_of_the_Night_Burney_Relief.jpg").convert("RGB")
    framed_insert(base, source, (900, 115, 950, 1310), matte=26)
    save(name, base)


def fix_img019() -> None:
    name = "IMG019_SALEM_LOOP_RETURN.png"
    base = Image.open(RAW / name).convert("RGB")
    document = Image.open(COMAN).convert("RGB").crop((545, 70, 1450, 1320))
    lithograph = Image.open(ASSETS / "EP07_Bridget_Bishop_lithograph.jpg").convert("RGB")
    framed_insert(base, document, (80, 145, 720, 1200), matte=22)
    framed_insert(base, lithograph, (2120, 260, 500, 900), matte=22)
    save(name, base)


def blur_region(name: str, box: tuple[int, int, int, int], radius: float) -> None:
    base = Image.open(QA / name).convert("RGB")
    region = base.crop(box).filter(ImageFilter.GaussianBlur(radius=radius))
    base.paste(region, box[:2])
    save(name, base)


def lift_midtones(name: str, gamma: float = 0.72, floor: int = 5) -> None:
    base = Image.open(QA / name).convert("RGB")
    lut = [min(255, round(floor + (255 - floor) * ((value / 255) ** gamma))) for value in range(256)]
    save(name, base.point(lut * 3))


def fix_shot04() -> None:
    name = "SHOT04_FUSELI_TO_SCREEN_TRANSITION.png"
    base = Image.open(RAW / name).convert("RGB")
    source = Image.open(ASSETS / "EP07_Fuseli_The_Nightmare_1781.jpg").convert("RGB")
    framed_insert(base, source, (95, 165, 1330, 1080), matte=18)
    # Keep the early monitor and window shapes, but make all generated UI text unreadable.
    screen = (1770, 600, 2335, 1065)
    region = base.crop(screen).filter(ImageFilter.GaussianBlur(radius=18))
    base.paste(region, screen[:2])
    save(name, base)


def main() -> None:
    copy_raw()
    fix_img003()
    fix_img005()
    fix_img008()
    fix_img019()
    fix_shot04()
    blur_region("IMG020_MEDIA_SPEED_HANDOFF.png", (1640, 290, 2505, 1010), 18)
    blur_region("SHOT03_CASSETTE_NOTEBOOK_MACRO.png", (1450, 300, 2752, 1120), 10)
    lift_midtones("IMG001_SALEM_BEDROOM_COMAN_RECON.png")
    lift_midtones("IMG005_NIGHTMARE_MOTIF_ROOM_BASE.png", gamma=0.85, floor=4)
    print(f"QA outputs: {len(list(QA.glob('*.png')))} in {QA}")


if __name__ == "__main__":
    main()
