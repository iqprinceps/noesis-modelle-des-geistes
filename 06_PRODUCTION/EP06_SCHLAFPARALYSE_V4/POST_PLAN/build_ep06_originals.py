#!/usr/bin/env python3
"""EP06 - Originalquellen ORIG017 bis ORIG027 als 16:9-Editorexporte bauen.

Drei Quellensorten laufen hier zusammen:

* frisch geladene Wikimedia-Dateien (PNG, JPG, SVG, GIF),
* zwei Belege, die bereits fuer EP07 beschafft wurden und dieselbe
  gemeinfreie Vorlage betreffen (Salem 1876, Bridget-Bishop-Akte),
* zwei Positionen, fuer die es keine freie Quelle gibt.

SVG wird nicht lokal gerastert - dafuer fehlt auf dieser Maschine die
Cairo-Bibliothek. Stattdessen liefert der Thumbnail-Dienst von Wikimedia
Commons eine hochaufgeloeste PNG-Fassung derselben Datei. GIF-Frames holt
ffmpeg.

Fuer ORIG024 und ORIG025 existiert keine gesicherte freie Quelle. Sie werden
nicht durch ein beliebiges Stimmungsbild ersetzt, sondern durch eine
Quellenkarte, die die Luecke benennt - ein Dorm-Foto ohne Provenienz waere
genau der Beleg, den der Claims-Lock verbietet.

    python 06_PRODUCTION/EP06_SCHLAFPARALYSE_V4/POST_PLAN/build_ep06_originals.py
"""
from __future__ import annotations

import csv
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

Image.MAX_IMAGE_PIXELS = None

HERE = Path(__file__).resolve().parent
EPISODE = HERE.parent
ROOT = EPISODE.parents[1]
ASSETS = ROOT / "SCHLAFPARALYSE_ASSETS_PHASE2" / "EP06"
EP07_ASSETS = ROOT / "06_PRODUCTION" / "EP07_SCHLAFPARALYSE_V4" / "IMAGE_GENERATION_KIT" / "02_ASSETS"
OUT = EPISODE / "ORIGINAL_DERIVATIVES"
QA = OUT / "QA_CONTACT_SHEETS"
CACHE = OUT / "_raster_cache"

SIZE = (2560, 1440)
INSET = (2240, 1260)
MAX_UPSCALE = 2.4
UA = "NOESIS-production/1.0 (contact: info@iqprinceps.de)"

# Zielname -> (Quelldatei-Fragment, Commons-Dateiname fuer SVG-Rasterung)
SOURCES: dict[str, tuple[str, str | None]] = {
    "ORIG017_BRAINSTEM_ANATOMY.png": ("ORIG017_Brainstem_Anatomy", None),
    "ORIG018_SLEEP_CYCLE_HYPNOGRAM.png": ("ORIG018_Sleep_Cycle_Hypnogram",
                                          "Hypro_zyklus_1_en_103.svg"),
    "ORIG019_CIRCADIAN_RHYTHM_NIH.png": ("ORIG019_Circadian_Rhythm_NIH", None),
    "ORIG020_EEG_62_CHANNEL_CC0.png": ("ORIG020_EEG_62_Channel",
                                       "EEG_time_series_62_channels.svg"),
    "ORIG021_AMYGDALA_ANIMATION.png": ("ORIG021_Limbic_System", None),
    "ORIG022_OBE_ICON.png": ("ORIG022_OBE_Icon",
                             "Noun-Out_Of_Body_Experience_197585.svg"),
    "ORIG023_SLEEP_DEPRIVATION.png": ("ORIG023_Sleep_Deprivation",
                                      "Effects_of_sleep_deprivation.svg"),
}

# Zwei SVG-Assets liegen im Kit selbst und brauchen ebenfalls ein Rasterderivat,
# sonst findet der Schnitt sie nicht.
KIT_SVG = {
    "EP06_Fogo_Island_Cape_Freels_map.png": "EP06_Fogo_Island_Cape_Freels_map.svg",
    "EP06_EEG_Cap_Icon.png": "EP06_EEG_Cap_Icon.svg",
}

# Belege, die schon fuer EP07 beschafft wurden. Dieselbe gemeinfreie Vorlage
# zweimal zu laden waere sinnlos; die Datei wird direkt weiterverwendet.
FROM_EP07 = {
    "ORIG026_SALEM_COURT_1876.png": "EP07_Witchcraft_at_Salem_Village_1876.jpg",
    "ORIG027_BRIDGET_BISHOP_RECORD.png": "EP07_Bridget_Bishop_execution_archive_scan.png",
}

# Positionen ohne freie Quelle. Text der Ersatzkarte.
GAPS = {
    "ORIG024_1960S_DORM_CONTEXT.png": dict(
        section="",
        title="Warum wir kein Originalzimmer zeigen",
        subtitle="Die Bilder dieser Szene sind Rekonstruktionen.",
        entries=[
            ("Sicher", "David Hufford beschrieb das Erlebnis später ausführlich."),
            ("Nicht vorhanden", "Vom Studentenzimmer aus dem Jahr 1963 gibt es "
                                "kein bekanntes Foto."),
            ("Darum", "Wir zeigen die Schilderung als Rekonstruktion — nicht als "
                      "historische Aufnahme."),
        ],
        status="REKONSTRUKTION",
        note="Die Szene folgt Huffords Bericht. Das gezeigte Zimmer ist nicht sein echtes Zimmer.",
        source="Einordnung zur Rekonstruktion · David Huffords Bericht"),
    "ORIG025_ORAL_HISTORY_RECORDER.png": dict(
        section="",
        title="Die Interviews sind belegt — das Gerät nicht",
        subtitle="Hufford zeichnete Gespräche auf. Das genaue Modell ist unbekannt.",
        entries=[
            ("Sicher", "Huffords Feldarbeit auf Neufundland stützt sich auf "
                       "aufgezeichnete Interviews."),
            ("Unbekannt", "Welches Aufnahmegerät er dabei benutzte, ist nicht "
                          "gesichert dokumentiert."),
            ("Darum", "Das Gerät im Bild steht nur für die Methode — nicht für ein "
                      "bestimmtes historisches Modell."),
        ],
        status="SYMBOLBILD",
        note="Die Interviewmethode ist belegt. Das konkrete Gerät bleibt offen.",
        source="Einordnung zur Feldforschung · David Hufford"),
}


def run(args: list[str]) -> None:
    p = subprocess.run(args, text=True, capture_output=True)
    if p.returncode:
        raise RuntimeError((p.stderr or p.stdout)[-3000:])


def find_source(fragment: str) -> Path | None:
    for p in ASSETS.rglob("*"):
        if p.is_file() and fragment in p.name:
            return p
    return None


def fetch_svg_raster(commons_name: str, dest: Path) -> Path:
    """Commons rendert SVG serverseitig als PNG; lokal fehlt Cairo."""
    if dest.is_file():
        return dest
    url = (f"https://commons.wikimedia.org/wiki/Special:FilePath/"
           f"{urllib.parse.quote(commons_name)}?width=3000")
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(req, timeout=120) as res:
        dest.write_bytes(res.read())
    return dest


def load(path: Path, commons_name: str | None) -> Image.Image:
    suffix = path.suffix.lower()
    if suffix == ".svg":
        if not commons_name:
            raise SystemExit(f"SVG ohne Commons-Namen: {path}")
        path = fetch_svg_raster(commons_name, CACHE / f"{path.stem}.png")
        suffix = ".png"
    if suffix == ".gif":
        frame = CACHE / f"{path.stem}.png"
        frame.parent.mkdir(parents=True, exist_ok=True)
        if not frame.is_file():
            # Erster Frame genuegt: die Karte nutzt das GIF als Anatomiekontext,
            # nicht als Animation.
            run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                 "-i", str(path), "-frames:v", "1", str(frame)])
        path = frame
    with Image.open(path) as src:
        if src.mode in ("RGBA", "LA", "P"):
            src = src.convert("RGBA")
            # Diagramme kommen oft transparent; auf Papierweiss setzen, sonst
            # steht schwarze Schrift spaeter auf schwarzem Grund.
            flat = Image.new("RGBA", src.size, (247, 244, 236, 255))
            flat.alpha_composite(src)
            return flat.convert("RGB")
        return src.convert("RGB")


def backdrop(src: Image.Image) -> Image.Image:
    bg = ImageOps.fit(src, SIZE, method=Image.Resampling.LANCZOS)
    bg = bg.filter(ImageFilter.GaussianBlur(52))
    bg = ImageEnhance.Color(bg).enhance(0.24)
    bg = ImageEnhance.Brightness(bg).enhance(0.30)
    navy = Image.new("RGB", SIZE, (9, 10, 13))
    return Image.blend(bg, navy, 0.52)


def full_frame(src: Image.Image) -> tuple[Image.Image, float]:
    bg = backdrop(src)
    scale = min(INSET[0] / src.width, INSET[1] / src.height, MAX_UPSCALE)
    fg = src.resize((max(1, round(src.width * scale)), max(1, round(src.height * scale))),
                    Image.Resampling.LANCZOS)
    framed = Image.new("RGB", (fg.width + 12, fg.height + 12), (46, 36, 24))
    framed.paste(fg, (6, 6))
    bg.paste(framed, ((SIZE[0] - framed.width) // 2, (SIZE[1] - framed.height) // 2))
    return bg, scale


def gap_card(spec: dict) -> Image.Image:
    sys.path.insert(0, str(ROOT / "tools"))
    from build_schlafparalyse_cards import (  # noqa: E402
        CORAL, MUTED, WHITE, PAPER, LINE, background, draw_wrapped, font,
        footer, header, rounded_panel, wrap,
    )
    image = background(CORAL)
    draw = ImageDraw.Draw(image, "RGBA")
    header(draw, "EP06", spec["section"], spec["title"], spec["subtitle"])
    left_x, right_x = 112, 1660
    y1 = 470
    y = y1 + 54
    heights = 54
    for _, value in spec["entries"]:
        heights += 38 + len(wrap(draw, value, font(33), right_x - left_x - 156)) * 43 + 26
    y2 = min(SIZE[1] - 150, y1 + max(heights + 34, 320))
    rounded_panel(draw, (left_x, y1, right_x - 60, y2), CORAL)
    for label, value in spec["entries"]:
        draw.text((left_x + 48, y), label.upper(), font=font(24, bold=True), fill=CORAL)
        y += 38
        y = draw_wrapped(draw, (left_x + 48, y), value, font(33), PAPER,
                         right_x - left_x - 156, 10)
        y += 26
    rounded_panel(draw, (right_x, y1, SIZE[0] - 112, y2), MUTED)
    draw.text((right_x + 44, y1 + 54), "KURZ GESAGT", font=font(24, bold=True), fill=MUTED)
    draw.line((right_x + 44, y1 + 112, SIZE[0] - 156, y1 + 112), fill=CORAL, width=8)
    ty = draw_wrapped(draw, (right_x + 44, y1 + 158), spec["status"], font(36, bold=True),
                      WHITE, SIZE[0] - 112 - right_x - 88, 8)
    draw.line((right_x + 44, ty + 26, SIZE[0] - 156, ty + 26), fill=LINE, width=2)
    draw_wrapped(draw, (right_x + 44, ty + 62), spec["note"], font(28), PAPER,
                 SIZE[0] - 112 - right_x - 88, 12)
    footer(draw, spec["source"])
    return image.convert("RGB")


def contact_sheets(files: list[Path]) -> None:
    QA.mkdir(parents=True, exist_ok=True)
    thumb, label_h, cols, rows = (480, 270), 54, 4, 3
    font_small = ImageFont.load_default(size=20)
    for page, start in enumerate(range(0, len(files), cols * rows), 1):
        batch = files[start:start + cols * rows]
        sheet = Image.new("RGB", (cols * thumb[0], rows * (thumb[1] + label_h)), (12, 14, 20))
        draw = ImageDraw.Draw(sheet)
        for i, path in enumerate(batch):
            with Image.open(path) as image:
                frame = image.convert("RGB").resize(thumb, Image.Resampling.LANCZOS)
            x, y = (i % cols) * thumb[0], (i // cols) * (thumb[1] + label_h)
            sheet.paste(frame, (x, y))
            draw.text((x + 8, y + thumb[1] + 9), path.stem[:40],
                      fill=(236, 231, 215), font=font_small)
        sheet.save(QA / f"EP06_ORIGINAL_DERIVATIVES_{page:02d}.jpg", quality=91)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    CACHE.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []
    manifest: list[dict[str, str]] = []

    for target, (fragment, commons) in SOURCES.items():
        src_path = find_source(fragment)
        if src_path is None:
            print(f"  FEHLT: {target} (kein Treffer fuer {fragment})")
            continue
        image, scale = full_frame(load(src_path, commons))
        out = OUT / target
        image.save(out, compress_level=6)
        created.append(out)
        manifest.append({"filename": target, "source_file": src_path.name,
                         "kind": "ORIGINAL_CONTAIN", "scale": f"{scale:.2f}",
                         "resolution": "2560x1440", "camera_rule": "NO_PAN_NO_ZOOM"})
        print(f"  {target}  <- {src_path.name}")

    for target, name in FROM_EP07.items():
        src_path = EP07_ASSETS / name
        if not src_path.is_file():
            print(f"  FEHLT: {target} ({name})")
            continue
        image, scale = full_frame(load(src_path, None))
        out = OUT / target
        image.save(out, compress_level=6)
        created.append(out)
        manifest.append({"filename": target, "source_file": name,
                         "kind": "ORIGINAL_CONTAIN_SHARED_WITH_EP07",
                         "scale": f"{scale:.2f}", "resolution": "2560x1440",
                         "camera_rule": "NO_PAN_NO_ZOOM"})
        print(f"  {target}  <- EP07/{name}")

    kit = EPISODE / "IMAGE_GENERATION_KIT" / "02_ASSETS"
    for target, name in KIT_SVG.items():
        src_path = kit / name
        if not src_path.is_file():
            print(f"  FEHLT: {target} ({name})")
            continue
        # Lokal fehlt Cairo; PIL kann SVG nicht lesen. Diese beiden Dateien
        # stammen nicht von Commons, werden also ueber ffmpeg gerastert.
        raster = CACHE / f"{src_path.stem}.png"
        if not raster.is_file():
            raster.parent.mkdir(parents=True, exist_ok=True)
            run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                 "-i", str(src_path), "-vf", "scale=2400:-1", str(raster)])
        image, scale = full_frame(load(raster, None))
        out = OUT / target
        image.save(out, compress_level=6)
        created.append(out)
        manifest.append({"filename": target, "source_file": name,
                         "kind": "KIT_SVG_RASTER", "scale": f"{scale:.2f}",
                         "resolution": "2560x1440", "camera_rule": "NO_PAN_NO_ZOOM"})
        print(f"  {target}  <- {name}")

    for target, spec in GAPS.items():
        out = OUT / target
        gap_card(spec).save(out, compress_level=6)
        created.append(out)
        manifest.append({"filename": target, "source_file": "-",
                         "kind": "GAP_SOURCE_CARD", "scale": "-",
                         "resolution": "2560x1440", "camera_rule": "STATIC_CARD"})
        print(f"  {target}  <- Quellenkarte (keine freie Quelle)")

    with (OUT / "EP06_ORIGINAL_DERIVATIVES_MANIFEST.csv").open(
            "w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(manifest[0].keys()))
        writer.writeheader()
        writer.writerows(manifest)
    contact_sheets(created)
    print(f"\ncreated={len(created)}")


if __name__ == "__main__":
    pass
    main()
