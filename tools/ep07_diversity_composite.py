#!/usr/bin/env python3
"""Finalize EP07 diversity redesign with source-faithful archival inserts."""

from __future__ import annotations

import pathlib
import shutil

from PIL import Image, ImageDraw


ROOT = pathlib.Path(__file__).resolve().parent.parent
KIT = ROOT / "06_PRODUCTION" / "EP07_SCHLAFPARALYSE_V4" / "IMAGE_GENERATION_KIT"
ASSETS = KIT / "02_ASSETS"
RAW = ROOT / "tmp" / "imagegen" / "ep07_diversity_raw"
QA = ROOT / "tmp" / "imagegen" / "ep07_diversity_qa"
COMAN = ROOT / "tmp" / "pdfs" / "ep07" / "Richard_Coman_page1.png"


def copy_raw() -> None:
    QA.mkdir(parents=True, exist_ok=True)
    for source in RAW.glob("*.png"):
        if not source.name.startswith("_"):
            shutil.copy2(source, QA / source.name)


def fit_inside(image: Image.Image, width: int, height: int) -> Image.Image:
    result = image.convert("RGB").copy()
    result.thumbnail((width, height), Image.Resampling.LANCZOS)
    return result


def insert(base: Image.Image, source: Image.Image, box: tuple[int, int, int, int],
           matte: int = 18, light: bool = False) -> None:
    x, y, width, height = box
    draw = ImageDraw.Draw(base)
    fill = (218, 207, 187) if light else (27, 25, 23)
    line = (160, 142, 115) if light else (89, 78, 63)
    draw.rounded_rectangle(
        (x - matte, y - matte, x + width + matte, y + height + matte),
        radius=10,
        fill=fill,
        outline=line,
        width=6,
    )
    fitted = fit_inside(source, width, height)
    base.paste(fitted, (x + (width - fitted.width) // 2, y + (height - fitted.height) // 2))


def save(name: str, base: Image.Image) -> None:
    base.save(QA / name, format="PNG", optimize=False)


def coman_page() -> Image.Image:
    # Preserve the full historical sheet while removing capture-room margins.
    return Image.open(COMAN).convert("RGB").crop((545, 70, 1450, 1320))


def fix_img003() -> None:
    name = "IMG003_PRIVATE_NIGHT_TO_COURT.png"
    base = Image.open(RAW / name).convert("RGB")
    insert(base, coman_page(), (125, 115, 610, 1120))
    court = Image.open(ASSETS / "EP07_Witchcraft_at_Salem_Village_1876.jpg")
    insert(base, court, (1740, 120, 860, 650))
    save(name, base)


def fix_img007() -> None:
    name = "IMG007_MARA_INCUBUS_KANASHIBARI_BASE.png"
    base = Image.open(RAW / name).convert("RGB")
    insert(base, Image.open(ASSETS / "EP07_Jinn_from_Ali_manuscript.png"),
           (250, 540, 650, 360), light=True)
    insert(base, Image.open(ASSETS / "EP07_Kunisada_The_Ghost.jpg"),
           (1110, 230, 520, 970), light=True)
    insert(base, Image.open(ASSETS / "EP07_Yoshitoshi_Shoki.jpg"),
           (1940, 210, 500, 1000), light=True)
    save(name, base)


def fix_img019() -> None:
    name = "IMG019_SALEM_LOOP_RETURN.png"
    base = Image.open(RAW / name).convert("RGB")
    insert(base, coman_page(), (110, 160, 560, 1050))
    court = Image.open(ASSETS / "EP07_Witchcraft_at_Salem_Village_1876.jpg")
    insert(base, court, (1040, 95, 920, 650))
    bishop = Image.open(ASSETS / "EP07_Bridget_Bishop_lithograph.jpg")
    insert(base, bishop, (2150, 260, 410, 720))
    save(name, base)


def fix_shot02() -> None:
    name = "SHOT02_MANY_NAMES_PAPER_LAYERS.png"
    base = Image.open(RAW / name).convert("RGB")
    insert(base, Image.open(ASSETS / "EP07_Jinn_from_Ali_manuscript.png"),
           (300, 690, 560, 315), light=True)
    insert(base, Image.open(ASSETS / "EP07_Kunisada_The_Ghost.jpg"),
           (1580, 405, 380, 650), light=True)
    insert(base, Image.open(ASSETS / "EP07_Yoshitoshi_Shoki.jpg"),
           (2110, 430, 370, 660), light=True)
    save(name, base)


def main() -> None:
    copy_raw()
    fix_img003()
    fix_img007()
    fix_img019()
    fix_shot02()
    print(f"EP07 diversity QA: {len(list(QA.glob('*.png')))} PNGs in {QA}")


if __name__ == "__main__":
    main()
