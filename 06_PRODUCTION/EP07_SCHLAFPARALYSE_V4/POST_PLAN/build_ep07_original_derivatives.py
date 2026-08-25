#!/usr/bin/env python3
"""EP07 — Originalquellen zu statischen 16:9-Editorexporten ableiten.

Ableitung der 47 `DERIVE_STATIC_FRAME`-Cues aus `EP07_VOICE_VISUAL_SYNC.csv`.
Analog zu `EP08_SCHLAFPARALYSE_V4/POST_PLAN/build_original_expansions.py`, aber
mit drei Erweiterungen, die EP07 zwingend braucht:

1. Master-Upgrade: einige Quellen in `02_ASSETS` sind deutlich kleiner als eine
   bereits vorhandene, identische Fassung an anderer Stelle im Repo. Der
   Registry-Schritt waehlt die hoechstaufgeloeste Fassung *derselben* Vorlage.
   Verschiedene Werke werden nie getauscht (Fuseli 1781 bleibt 1781).
2. Region-Map: mehrere Exporte aus einem Master muessen verschiedene Bildareale
   zeigen, sonst entstehen identische Frames. Jede Ableitung hat eine explizite,
   benannte Region.
3. Upscale-Gate: ein Crop, der ueber MAX_UPSCALE hinaus hochskaliert werden
   muesste, wird so lange geweitet, bis er das Limit haelt. Reicht auch die
   Vollansicht nicht, wird das Motiv kleiner in den Rahmen gesetzt statt
   matschig aufgeblasen. Jede Entscheidung steht im Manifest.

Aufruf aus dem Repository-Root:
    python tools/../06_PRODUCTION/EP07_SCHLAFPARALYSE_V4/POST_PLAN/build_ep07_original_derivatives.py
"""
from __future__ import annotations

import csv
import os
from pathlib import Path

import fitz
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

Image.MAX_IMAGE_PIXELS = None

HERE = Path(__file__).resolve().parent
EPISODE = HERE.parent
ROOT = EPISODE.parents[1]
PLAN = EPISODE / "EP07_VOICE_VISUAL_SYNC.csv"
ASSETS = EPISODE / "IMAGE_GENERATION_KIT" / "02_ASSETS"
OUT = EPISODE / "ORIGINAL_DERIVATIVES"
QA = OUT / "QA_CONTACT_SHEETS"

SIZE = (2560, 1440)
# Ein 16:9-Ausschnitt darf hoechstens um diesen Faktor hochskaliert werden.
# Darueber wird die Kante sichtbar weich, und ein Beleg, den niemand lesen kann,
# belegt nichts mehr.
MAX_UPSCALE = 2.2
# Innenmass der Vollansicht; der Rest ist abgedunkelter Hintergrund.
INSET = (2240, 1260)

# Zusaetzliche Suchorte fuer hoeher aufgeloeste Fassungen derselben Vorlage.
UPGRADE_ROOTS = [
    ROOT / "04_ASSETS" / "SCHLAFPARALYSE",
    ROOT / "SCHLAFPARALYSE_ASSETS_PHASE2",
    ROOT / "03_EPISODEN" / "TYPE_B" / "SCHLAFPARALYSE_ASSETS_PHASE2",
]

# Dateiname-Fragmente, die dieselbe Vorlage bezeichnen. Nur hier eingetragene
# Paare werden getauscht; alles andere bleibt beim Master aus dem Plan.
UPGRADE_KEYS = {
    "EP07_Abildgaard_Nightmare_1800": ("abildgaard", "1800"),
    "EP07_Fuseli_The_Nightmare_1781": ("fuseli", "1781"),
    "EP07_Queen_of_the_Night_Burney_Relief": ("queen_of_the_night",),
    "EP07_Salem_Village_1692_map_Upham_1866": ("salem_village", "map"),
    "EP07_Witchcraft_at_Salem_Village_1876": ("witchcraft_at_salem",),
    "EP07_Examination_of_a_Witch_Matteson_1853": ("matteson",),
    "EP07_Malleus_1494_Bull_Innocent_VIII_Wellcome": ("malleus", "1494"),
}

# Eigenstaendige Detailaufnahmen: fuer diese Ableitungen existiert eine echte
# separate Aufnahme, die jedem Crop aus der Gesamtansicht ueberlegen ist.
DEDICATED_SOURCE = {
    ("EP07_Queen_of_the_Night_Burney_Relief", "face_detail"): "EP07_Burney_Relief_bust_detail.jpg",
    ("EP07_Queen_of_the_Night_Burney_Relief", "talons_detail"): "EP07_Burney_Relief_lions_talons_detail.jpg",
    ("EP07_Sleep_Studies_NHLBI_Polysomnography", "sensor_detail"): "EP07_Polysomnography_sensor_connections.jpg",
}

# Region je (Master-Stamm, Suffix): (links, oben, rechts, unten) als Anteil des
# Quellbilds, plus PDF-Seite (0-basiert) fuer mehrseitige Dokumente.
# "FULL" bedeutet Vollansicht im Rahmen, kein Crop.
R_FULL = "FULL"
REGIONS: dict[tuple[str, str], object] = {
    # --- Richard Coman, Zeugenaussage gegen Bridget Bishop, 1692 (2 Seiten) ---
    # Ein Gerichtsprotokoll liest sich von oben nach unten; die Ableitungen
    # laufen deshalb als Baender ueber die Seite statt als Mittenzoom.
    ("EP07_Richard_Coman_Testimony_v_Bridget_Bishop_1692", "p1_full"): (R_FULL, 0),
    ("EP07_Richard_Coman_Testimony_v_Bridget_Bishop_1692", "p1_name_and_opening"): ((0.06, 0.08, 0.94, 0.34), 0),
    ("EP07_Richard_Coman_Testimony_v_Bridget_Bishop_1692", "p1_pressure_passage"): ((0.06, 0.30, 0.94, 0.56), 0),
    ("EP07_Richard_Coman_Testimony_v_Bridget_Bishop_1692", "p1_cannot_speak_nor_stir"): ((0.06, 0.50, 0.94, 0.76), 0),
    ("EP07_Richard_Coman_Testimony_v_Bridget_Bishop_1692", "p2_signature_and_oath"): ((0.06, 0.58, 0.94, 0.92), 1),
    ("EP07_Richard_Coman_Testimony_v_Bridget_Bishop_1692", "p1_full_return"): (R_FULL, 0),
    # --- Bridget Bishop, Verhoerprotokoll 1692 ---
    ("EP07_Bridget_Bishop_Examination_1692", "p1_full"): (R_FULL, 0),
    ("EP07_Bridget_Bishop_Examination_1692", "p1_heading_date"): ((0.06, 0.05, 0.94, 0.27), 0),
    ("EP07_Bridget_Bishop_Examination_1692", "p1_signature_detail"): ((0.06, 0.62, 0.94, 0.92), 0),
    # --- Malleus Maleficarum, Wellcome-Digitalisat 1928 ---
    ("EP07_Malleus_Maleficarum_1928_Wellcome", "p1_title_and_metadata"): (R_FULL, 0),
    ("EP07_Malleus_Maleficarum_1928_Wellcome", "editor_selected_relevant_passage"): ((0.10, 0.18, 0.90, 0.62), 30),
    # --- Papstbulle Innozenz VIII., 1494 ---
    ("EP07_Malleus_1494_Bull_Innocent_VIII_Wellcome", "full_page"): (R_FULL, 0),
    ("EP07_Malleus_1494_Bull_Innocent_VIII_Wellcome", "title_detail"): ((0.08, 0.06, 0.92, 0.30), 0),
    # --- Fuseli, The Nightmare, 1781 ---
    # Querformat 3013x2442: Frau links/mittig liegend, Inkubus auf der Brust,
    # Pferdekopf links oben aus dem Vorhang.
    ("EP07_Fuseli_The_Nightmare_1781", "full_painting"): (R_FULL, 0),
    ("EP07_Fuseli_The_Nightmare_1781", "woman_detail"): ((0.26, 0.38, 0.86, 0.94), 0),
    ("EP07_Fuseli_The_Nightmare_1781", "incubus_detail"): ((0.34, 0.14, 0.72, 0.60), 0),
    ("EP07_Fuseli_The_Nightmare_1781", "horse_detail"): ((0.02, 0.06, 0.40, 0.52), 0),
    ("EP07_Fuseli_The_Nightmare_1781", "full_return"): (R_FULL, 0),
    # --- Abildgaard, Nachtmahr, 1800 ---
    ("EP07_Abildgaard_Nightmare_1800", "full_painting"): (R_FULL, 0),
    ("EP07_Abildgaard_Nightmare_1800", "figure_detail"): ((0.30, 0.26, 0.86, 0.84), 0),
    ("EP07_Abildgaard_Nightmare_1800", "pressure_detail"): ((0.20, 0.40, 0.68, 0.88), 0),
    ("EP07_Abildgaard_Nightmare_1800", "full_return"): (R_FULL, 0),
    # --- Burney Relief / Queen of the Night ---
    ("EP07_Queen_of_the_Night_Burney_Relief", "full_object"): (R_FULL, 0),
    ("EP07_Queen_of_the_Night_Burney_Relief", "face_detail"): (R_FULL, 0),
    ("EP07_Queen_of_the_Night_Burney_Relief", "talons_detail"): (R_FULL, 0),
    # --- Salem Village Karte, Upham 1866 ---
    ("EP07_Salem_Village_1692_map_Upham_1866", "full_map"): (R_FULL, 0),
    ("EP07_Salem_Village_1692_map_Upham_1866", "map_edge_detail"): ((0.52, 0.44, 0.98, 0.94), 0),
    ("EP07_Salem_Village_1692_map_Upham_1866", "full_return"): (R_FULL, 0),
    # --- Spaetere Darstellungen der Prozesse ---
    ("EP07_Witchcraft_at_Salem_Village_1876", "full_later_depiction"): (R_FULL, 0),
    ("EP07_Witchcraft_at_Salem_Village_1876", "crowd_detail_later_depiction"): ((0.44, 0.16, 0.98, 0.78), 0),
    ("EP07_Witchcraft_at_Salem_Village_1876", "full_return_later_depiction"): (R_FULL, 0),
    ("EP07_Trial_George_Jacobs_Salem_LOC", "full_later_depiction"): (R_FULL, 0),
    ("EP07_Trial_George_Jacobs_Salem_LOC", "court_detail_later_depiction"): ((0.06, 0.18, 0.60, 0.82), 0),
    ("EP07_Examination_of_a_Witch_Matteson_1853", "full_painting_later_depiction"): (R_FULL, 0),
    # --- Bridget Bishop, Bildquellen ---
    ("EP07_Bridget_Bishop_lithograph", "full_portrait"): (R_FULL, 0),
    ("EP07_Bridget_Bishop_lithograph", "portrait_return"): (R_FULL, 0),
    ("EP07_Bridget_Bishop_execution_archive_scan", "full_scan"): (R_FULL, 0),
    ("EP07_Proctors_Ledge_Memorial", "full_context"): (R_FULL, 0),
    # --- Aussereuropaeische Traditionen ---
    ("EP07_Jinn_from_Ali_manuscript", "full_manuscript"): (R_FULL, 0),
    ("EP07_Jinn_from_Ali_manuscript", "figure_detail"): ((0.28, 0.02, 0.76, 0.98), 0),
    ("EP07_Kunisada_The_Ghost", "full_print"): (R_FULL, 0),
    ("EP07_Yoshitoshi_Shoki", "full_print"): (R_FULL, 0),
    # --- Schlaflabor ---
    ("EP07_REM_Polysomnography_30sec", "full_trace"): (R_FULL, 0),
    ("EP07_REM_Polysomnography_30sec", "rem_segment_detail"): ((0.04, 0.06, 0.56, 0.94), 0),
    ("EP07_REM_Polysomnography_30sec", "micro_arousal_detail"): ((0.46, 0.06, 0.98, 0.94), 0),
    ("EP07_Sleep_Studies_NHLBI_Polysomnography", "full_photo"): (R_FULL, 0),
    ("EP07_Sleep_Studies_NHLBI_Polysomnography", "sensor_detail"): (R_FULL, 0),
}

# Rueckkehr-Shots duerfen nicht pixelgleich mit ihrer Erstverwendung sein.
# Sie bekommen einen minimal engeren Rahmen; derselbe Beleg, anderes Bild.
RETURN_TIGHTEN = 0.94


def is_return(suffix: str) -> bool:
    return suffix.endswith("_return") or "_return_" in suffix


def load_source(path: Path, page: int = 0) -> Image.Image:
    """Vorlage laden. PDF-Seiten werden so gerendert, dass die kurze Kante
    mindestens 2600 px hat - darunter waere Handschrift nicht mehr lesbar."""
    if path.suffix.lower() == ".pdf":
        doc = fitz.open(path)
        page = min(page, doc.page_count - 1)
        pg = doc.load_page(page)
        zoom = max(3.0, 2600 / min(pg.rect.width, pg.rect.height))
        pix = pg.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
        image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        doc.close()
        return image
    with Image.open(path) as src:
        return src.convert("RGB")


def widen_to_limit(src: Image.Image, box: tuple[float, float, float, float]
                   ) -> tuple[tuple[int, int, int, int], float, bool]:
    """Crop-Box in Pixel liefern, notfalls geweitet, bis MAX_UPSCALE haelt.

    Rueckgabe: (Box, effektiver Upscale, wurde geweitet).
    """
    w, h = src.size
    l, t, r, b = box
    cx, cy = (l + r) / 2, (t + b) / 2
    widened = False
    scale_step = 1.0
    for _ in range(40):
        hw = (r - l) / 2 * scale_step
        hh = (b - t) / 2 * scale_step
        nl, nt = max(0.0, cx - hw), max(0.0, cy - hh)
        nr, nb = min(1.0, cx + hw), min(1.0, cy + hh)
        px = (round(nl * w), round(nt * h), round(nr * w), round(nb * h))
        cw, ch = px[2] - px[0], px[3] - px[1]
        if cw < 8 or ch < 8:
            break
        # Der Crop wird spaeter auf 16:9 beschnitten; die bindende Kante ist die,
        # die nach dem Zuschnitt uebrig bleibt.
        target_ratio = SIZE[0] / SIZE[1]
        if cw / ch > target_ratio:
            eff_w, eff_h = ch * target_ratio, ch
        else:
            eff_w, eff_h = cw, cw / target_ratio
        upscale = max(SIZE[0] / eff_w, SIZE[1] / eff_h)
        if upscale <= MAX_UPSCALE or (nl <= 0 and nt <= 0 and nr >= 1 and nb >= 1):
            return px, upscale, widened
        scale_step *= 1.08
        widened = True
    w_px = (0, 0, w, h)
    return w_px, MAX_UPSCALE, True


def backdrop(src: Image.Image) -> Image.Image:
    bg = ImageOps.fit(src, SIZE, method=Image.Resampling.LANCZOS)
    bg = bg.filter(ImageFilter.GaussianBlur(52))
    bg = ImageEnhance.Color(bg).enhance(0.28)
    bg = ImageEnhance.Brightness(bg).enhance(0.34)
    navy = Image.new("RGB", SIZE, (8, 18, 38))
    return Image.blend(bg, navy, 0.44)


def full_frame(src: Image.Image, tighten: float = 1.0) -> tuple[Image.Image, float]:
    """Vollansicht mittig im Rahmen, Rest abgedunkelter Hintergrund."""
    bg = backdrop(src)
    max_w, max_h = int(INSET[0] * tighten), int(INSET[1] * tighten)
    scale = min(max_w / src.width, max_h / src.height)
    # Nie ueber das Upscale-Limit aufblasen: lieber kleiner im Rahmen stehen.
    scale = min(scale, MAX_UPSCALE)
    fg = src.resize((max(1, round(src.width * scale)), max(1, round(src.height * scale))),
                    Image.Resampling.LANCZOS)
    framed = Image.new("RGB", (fg.width + 12, fg.height + 12), (46, 36, 24))
    framed.paste(fg, (6, 6))
    bg.paste(framed, ((SIZE[0] - framed.width) // 2, (SIZE[1] - framed.height) // 2))
    return bg, scale


def crop_frame(src: Image.Image, box: tuple[float, float, float, float]
               ) -> tuple[Image.Image, float, bool]:
    px, upscale, widened = widen_to_limit(src, box)
    cut = src.crop(px)
    return ImageOps.fit(cut, SIZE, method=Image.Resampling.LANCZOS,
                        centering=(0.5, 0.5)), upscale, widened


def build_registry() -> dict[str, Path]:
    """Fuer jeden Master aus dem Plan die hoechstaufgeloeste Fassung derselben
    Vorlage suchen. Nur Treffer, die alle Schluesselfragmente enthalten."""
    upgrades: dict[str, Path] = {}
    candidates: list[tuple[str, int, Path]] = []
    for root in UPGRADE_ROOTS:
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if p.suffix.lower() not in (".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"):
                continue
            name = p.name.lower()
            for stem, keys in UPGRADE_KEYS.items():
                if all(k in name for k in keys):
                    try:
                        with Image.open(p) as im:
                            candidates.append((stem, im.size[0] * im.size[1], p))
                    except Exception:
                        pass
    for stem, px, p in candidates:
        base = ASSETS / f"{stem}.jpg"
        base_px = 0
        for ext in (".jpg", ".png", ".jpeg"):
            cand = ASSETS / f"{stem}{ext}"
            if cand.exists():
                try:
                    with Image.open(cand) as im:
                        base_px = im.size[0] * im.size[1]
                    base = cand
                except Exception:
                    pass
                break
        best = upgrades.get(stem)
        best_px = 0
        if best is not None:
            with Image.open(best) as im:
                best_px = im.size[0] * im.size[1]
        if px > max(base_px, best_px):
            upgrades[stem] = p
    return upgrades


def make_contact_sheets(files: list[Path]) -> None:
    QA.mkdir(parents=True, exist_ok=True)
    thumb = (480, 270)
    label_h = 54
    cols, rows = 4, 3
    font = ImageFont.load_default(size=20)
    for page, start in enumerate(range(0, len(files), cols * rows), 1):
        batch = files[start:start + cols * rows]
        sheet = Image.new("RGB", (cols * thumb[0], rows * (thumb[1] + label_h)), (12, 18, 30))
        draw = ImageDraw.Draw(sheet)
        for i, path in enumerate(batch):
            with Image.open(path) as image:
                frame = image.convert("RGB").resize(thumb, Image.Resampling.LANCZOS)
            x = (i % cols) * thumb[0]
            y = (i // cols) * (thumb[1] + label_h)
            sheet.paste(frame, (x, y))
            label = path.stem.replace("SRC_EP07_", "")
            if len(label) > 40:
                label = label[:39] + "…"
            draw.text((x + 8, y + thumb[1] + 9), label, fill=(236, 231, 215), font=font)
        sheet.save(QA / f"EP07_ORIGINAL_DERIVATIVES_{page:02d}.jpg", quality=91)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    registry = build_registry()
    if registry:
        print("Master-Upgrades:")
        for stem, p in sorted(registry.items()):
            with Image.open(p) as im:
                print(f"  {stem} -> {p.name} ({im.size[0]}x{im.size[1]})")

    with PLAN.open("r", encoding="utf-8-sig", newline="") as handle:
        plan = [r for r in csv.DictReader(handle) if r["asset_status"] == "DERIVE_STATIC_FRAME"]

    created: list[Path] = []
    manifest: list[dict[str, str]] = []
    seen: set[str] = set()
    cache: dict[tuple[Path, int], Image.Image] = {}
    unmapped: list[str] = []

    for row in plan:
        out_name = os.path.basename(row["asset_path"])
        if out_name in seen:
            continue
        seen.add(out_name)
        master = Path(row["source_master"])
        stem = master.stem
        suffix = row["asset_id"].replace(f"SRC_{stem}_", "")

        key = (stem, suffix)
        spec = REGIONS.get(key)
        if spec is None:
            unmapped.append(f"{stem} :: {suffix}")
            continue
        box, page = spec

        source_path = master
        note = "plan_master"
        dedicated = DEDICATED_SOURCE.get(key)
        if dedicated and (ASSETS / dedicated).exists():
            source_path = ASSETS / dedicated
            note = f"eigene Detailaufnahme: {dedicated}"
        elif stem in registry:
            source_path = registry[stem]
            note = f"hoeher aufgeloeste Fassung: {source_path.name}"

        ck = (source_path, page)
        if ck not in cache:
            cache[ck] = load_source(source_path, page)
        src = cache[ck]

        if box == R_FULL:
            tighten = RETURN_TIGHTEN if is_return(suffix) else 1.0
            image, scale = full_frame(src, tighten)
            view = "FULL_CONTAIN_STATIC"
            upscale, widened = scale, False
        else:
            image, upscale, widened = crop_frame(src, box)
            view = "SEMANTIC_CROP_STATIC"

        out_path = OUT / out_name
        image.save(out_path, compress_level=6)
        created.append(out_path)
        manifest.append({
            "filename": out_name,
            "cue_id": row["cue_id"],
            "section": row["section"],
            "source_file": source_path.name,
            "source_resolution": f"{src.width}x{src.height}",
            "source_note": note,
            "view": view,
            "region": "full" if box == R_FULL else ",".join(f"{v:.2f}" for v in box),
            "pdf_page": str(page + 1) if source_path.suffix.lower() == ".pdf" else "",
            "effective_upscale": f"{upscale:.2f}",
            "widened_for_quality": "yes" if widened else "no",
            "resolution": "2560x1440",
            "camera_rule": "NO_PAN_NO_ZOOM",
        })

    if unmapped:
        raise SystemExit("Ohne Region-Eintrag:\n  " + "\n  ".join(unmapped))

    with (OUT / "EP07_ORIGINAL_DERIVATIVES_MANIFEST.csv").open("w", encoding="utf-8-sig",
                                                               newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(manifest[0].keys()))
        writer.writeheader()
        writer.writerows(manifest)

    make_contact_sheets(created)
    soft = [m for m in manifest if float(m["effective_upscale"]) > MAX_UPSCALE - 0.01]
    print(f"\ncreated={len(created)}")
    print(f"geweitet fuer Qualitaet: {sum(1 for m in manifest if m['widened_for_quality'] == 'yes')}")
    if soft:
        print(f"am Upscale-Limit (Quelle klein): {len(soft)}")
        for m in soft:
            print(f"  {m['filename']}  <- {m['source_file']} {m['source_resolution']}")


if __name__ == "__main__":
    main()
