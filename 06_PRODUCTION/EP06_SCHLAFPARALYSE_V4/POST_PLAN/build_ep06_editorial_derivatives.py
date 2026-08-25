#!/usr/bin/env python3
"""EP06 - die 13 redaktionellen Ableitungen SHOT11 bis SHOT36 bauen.

`VOICE_EP06/SEMANTIC_DERIVATIVE_BATCH.md` fuehrt diese Shots als
`EDITORIAL_CROP_OR_DETAIL`: deterministische Ausschnitte aus vorhandenen
Quellen, nie neu erzeugte Bilder. Jeder Ausschnitt muss den im Batch genannten
neuen Anker tragen, nicht nur naeher an dasselbe Motiv heranfahren.

Geschnitten wird immer aus der **Rohquelle**, nicht aus dem bereits gerahmten
ORIG-Derivat - sonst schnitte man den abgedunkelten Hintergrund mit.

Mehrere EP06-Quellen sind klein (Fogo-Dorf 640x421, NHLBI 475x592). Ein enger
Crop daraus waere bei 1080p Matsch. Das Upscale-Gate weitet den Ausschnitt
darum so lange, bis MAX_UPSCALE haelt; reicht auch die Vollansicht nicht, steht
das Motiv kleiner im Rahmen statt aufgeblasen.

    python 06_PRODUCTION/EP06_SCHLAFPARALYSE_V4/POST_PLAN/build_ep06_editorial_derivatives.py
"""
from __future__ import annotations

import csv
import subprocess
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

Image.MAX_IMAGE_PIXELS = None

HERE = Path(__file__).resolve().parent
EPISODE = HERE.parent
ROOT = EPISODE.parents[1]
ASSETS = EPISODE / "IMAGE_GENERATION_KIT" / "02_ASSETS"
PHASE2 = ROOT / "SCHLAFPARALYSE_ASSETS_PHASE2" / "EP06"
CACHE = EPISODE / "ORIGINAL_DERIVATIVES" / "_raster_cache"
OUT = EPISODE / "EDITORIAL_DERIVATIVES"
QA = OUT / "QA_CONTACT_SHEETS"

SIZE = (2560, 1440)
INSET = (2240, 1260)
MAX_UPSCALE = 2.4
UA = "NOESIS-production/1.0 (contact: info@iqprinceps.de)"
R_FULL = "FULL"

# SHOT -> (Quelle, Region als Anteil der Quelle, Commons-Name fuer SVG)
# Die Region traegt den neuen Anker aus dem Batch; sie ist kein zweiter Zoom
# auf denselben Bildinhalt.
SPECS: dict[str, tuple[str, object, str | None]] = {
    # Hirnstamm: der Ausschnitt zeigt Pons und Medulla, wo die Hemmung sitzt.
    "SHOT11_HIRNSTAMM_HEMMUNG.png": (
        "ORIG017_Brainstem_Anatomy", (0.30, 0.34, 0.86, 0.92), None),
    # Schlafstoerungskontext: die Symptomspalte, nicht die ganze Figur.
    "SHOT13_SCHLAFSTORUNGSKONTEXT.png": (
        "ORIG023_Sleep_Deprivation", (0.02, 0.10, 0.52, 0.86),
        "Effects_of_sleep_deprivation.svg"),
    # Mischzustand: Hypothalamus/SCN-Bereich als Taktgeber.
    "SHOT15_NEUROPHYSIOLOGISCHER_MISCHZUSTAND.png": (
        "ORIG019_Circadian_Rhythm_NIH", (0.16, 0.32, 0.72, 0.90), None),
    # Uebergang ins Labor: die REM-Spitzen rechts im Hypnogramm.
    "SHOT16_UBERGANG_INS_LABOR.png": (
        "ORIG018_Sleep_Cycle_Hypnogram", (0.46, 0.04, 0.99, 0.96),
        "Hypro_zyklus_1_en_103.svg"),
    "SHOT17_MESSBARER_ZUSTAND.png": (
        "EP06_Sleep_Studies_NHLBI_Polysomnography", R_FULL, None),
    "SHOT18_MUSKELHEMMUNG_MESSKONTEXT.png": (
        "EP06_64_Channel_EEG_Cap", (0.20, 0.10, 0.80, 0.78), None),
    "SHOT20_KORPERLICHER_RAHMEN.png": (
        "EP06_REM_Polysomnography_30sec", (0.02, 0.04, 0.58, 0.96), None),
    "SHOT21_SUBJEKTIVE_WIRKLICHKEIT_MESSBARER_RAHMEN.png": (
        "EP06_Sleep_EEG_Stage_1_PSG", R_FULL, None),
    # Alarmsystem: der Amygdala-Bereich im limbischen Diagramm.
    "SHOT24_ALARMSYSTEM.png": (
        "ORIG021_Limbic_System", (0.14, 0.40, 0.74, 0.96), None),
    "SHOT29_ALLTAGSOBJEKT_KORPERLICHER_RAHMEN.png": (
        "EP06_Sleep_EEG_Stage_2_PSG", R_FULL, None),
    "SHOT34_TRADITION_ORT.png": (
        "EP06_Fogo_Island_Newfoundland_fishing_village_2002", R_FULL, None),
    # Seekarte 9697x14974: hier ist ein enger Ausschnitt tatsaechlich moeglich.
    "SHOT35_FOGO_ARCHIVANKER.png": (
        "EP06_Fogo_Island_to_Cape_Bonavista_Admiralty_Chart_1873",
        (0.10, 0.06, 0.62, 0.40), None),
    "SHOT36_BELASTBARER_KORPERLICHER_STAND.png": (
        "EP06_Simplified_Sleep_Phases", R_FULL, None),
}


def run(args: list[str]) -> None:
    p = subprocess.run(args, text=True, capture_output=True)
    if p.returncode:
        raise RuntimeError((p.stderr or p.stdout)[-3000:])


def find(fragment: str) -> Path | None:
    for root in (ASSETS, PHASE2):
        if not root.exists():
            continue
        for p in sorted(root.rglob("*")):
            if p.is_file() and fragment in p.name and not p.name.endswith(".txt"):
                return p
    return None


def fetch_svg_raster(commons_name: str, dest: Path) -> Path:
    if dest.is_file():
        return dest
    url = (f"https://commons.wikimedia.org/wiki/Special:FilePath/"
           f"{urllib.parse.quote(commons_name)}?width=3000")
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(req, timeout=120) as res:
        dest.write_bytes(res.read())
    return dest


def load(path: Path, commons: str | None) -> Image.Image:
    if path.suffix.lower() == ".svg":
        if not commons:
            raise SystemExit(f"SVG ohne Commons-Namen: {path}")
        path = fetch_svg_raster(commons, CACHE / f"{path.stem}.png")
    if path.suffix.lower() == ".gif":
        frame = CACHE / f"{path.stem}.png"
        if not frame.is_file():
            frame.parent.mkdir(parents=True, exist_ok=True)
            run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                 "-i", str(path), "-frames:v", "1", str(frame)])
        path = frame
    with Image.open(path) as src:
        if src.mode in ("RGBA", "LA", "P"):
            src = src.convert("RGBA")
            flat = Image.new("RGBA", src.size, (247, 244, 236, 255))
            flat.alpha_composite(src)
            return flat.convert("RGB")
        return src.convert("RGB")


def widen_to_limit(src: Image.Image, box):
    w, h = src.size
    l, t, r, b = box
    cx, cy = (l + r) / 2, (t + b) / 2
    widened = False
    step = 1.0
    ratio = SIZE[0] / SIZE[1]
    for _ in range(40):
        hw, hh = (r - l) / 2 * step, (b - t) / 2 * step
        nl, nt = max(0.0, cx - hw), max(0.0, cy - hh)
        nr, nb = min(1.0, cx + hw), min(1.0, cy + hh)
        px = (round(nl * w), round(nt * h), round(nr * w), round(nb * h))
        cw, ch = px[2] - px[0], px[3] - px[1]
        if cw < 8 or ch < 8:
            break
        if cw / ch > ratio:
            ew, eh = ch * ratio, ch
        else:
            ew, eh = cw, cw / ratio
        up = max(SIZE[0] / ew, SIZE[1] / eh)
        if up <= MAX_UPSCALE or (nl <= 0 and nt <= 0 and nr >= 1 and nb >= 1):
            return px, up, widened
        step *= 1.08
        widened = True
    return (0, 0, w, h), MAX_UPSCALE, True


def backdrop(src: Image.Image) -> Image.Image:
    bg = ImageOps.fit(src, SIZE, method=Image.Resampling.LANCZOS)
    bg = bg.filter(ImageFilter.GaussianBlur(52))
    bg = ImageEnhance.Color(bg).enhance(0.24)
    bg = ImageEnhance.Brightness(bg).enhance(0.30)
    return Image.blend(bg, Image.new("RGB", SIZE, (9, 10, 13)), 0.52)


def full_frame(src: Image.Image):
    bg = backdrop(src)
    scale = min(INSET[0] / src.width, INSET[1] / src.height, MAX_UPSCALE)
    fg = src.resize((max(1, round(src.width * scale)), max(1, round(src.height * scale))),
                    Image.Resampling.LANCZOS)
    framed = Image.new("RGB", (fg.width + 12, fg.height + 12), (46, 36, 24))
    framed.paste(fg, (6, 6))
    bg.paste(framed, ((SIZE[0] - framed.width) // 2, (SIZE[1] - framed.height) // 2))
    return bg, scale


def contact_sheets(files: list[Path]) -> None:
    QA.mkdir(parents=True, exist_ok=True)
    thumb, label_h, cols, rows = (480, 270), 54, 4, 3
    font = ImageFont.load_default(size=18)
    for page, start in enumerate(range(0, len(files), cols * rows), 1):
        batch = files[start:start + cols * rows]
        sheet = Image.new("RGB", (cols * thumb[0], rows * (thumb[1] + label_h)), (12, 14, 20))
        draw = ImageDraw.Draw(sheet)
        for i, path in enumerate(batch):
            with Image.open(path) as im:
                sheet.paste(im.convert("RGB").resize(thumb, Image.Resampling.LANCZOS),
                            ((i % cols) * thumb[0], (i // cols) * (thumb[1] + label_h)))
            draw.text(((i % cols) * thumb[0] + 8,
                       (i // cols) * (thumb[1] + label_h) + thumb[1] + 9),
                      path.stem[:42], fill=(236, 231, 215), font=font)
        sheet.save(QA / f"EP06_EDITORIAL_DERIVATIVES_{page:02d}.jpg", quality=91)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []
    manifest: list[dict[str, str]] = []
    for target, (fragment, box, commons) in SPECS.items():
        src_path = find(fragment)
        if src_path is None:
            print(f"  FEHLT: {target} (keine Quelle fuer {fragment})")
            continue
        src = load(src_path, commons)
        if box == R_FULL:
            image, scale = full_frame(src)
            view, up, widened = "FULL_CONTAIN_STATIC", scale, False
        else:
            px, up, widened = widen_to_limit(src, box)
            image = ImageOps.fit(src.crop(px), SIZE, method=Image.Resampling.LANCZOS,
                                 centering=(0.5, 0.5))
            view = "EDITORIAL_CROP_STATIC"
        out = OUT / target
        image.save(out, compress_level=6)
        created.append(out)
        manifest.append({
            "filename": target, "source_file": src_path.name,
            "source_resolution": f"{src.width}x{src.height}", "view": view,
            "region": "full" if box == R_FULL else ",".join(f"{v:.2f}" for v in box),
            "effective_upscale": f"{up:.2f}",
            "widened_for_quality": "yes" if widened else "no",
            "resolution": "2560x1440", "camera_rule": "NO_PAN_NO_ZOOM",
        })
        flag = "  (geweitet)" if widened else ""
        print(f"  {target:52s} <- {src_path.name[:38]}{flag}")

    with (OUT / "EP06_EDITORIAL_DERIVATIVES_MANIFEST.csv").open(
            "w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(manifest[0].keys()))
        writer.writeheader()
        writer.writerows(manifest)
    contact_sheets(created)
    print(f"\ncreated={len(created)}")


if __name__ == "__main__":
    main()
