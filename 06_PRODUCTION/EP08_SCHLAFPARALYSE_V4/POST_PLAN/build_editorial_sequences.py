#!/usr/bin/env python3
"""EP08 - die 22 EDITORIAL_BUILD-Cues als kurze Ebenensequenzen bauen.

Im Sync-Plan stehen diese Cues als `EDITORIAL_BUILD` mit der Regel
`EDITORIAL_LAYER_MOTION only; opacity/focus/reveal, camera locked`. Sie sind
keine Einzelbilder, sondern kurze Montagen aus zwei bis drei bereits
freigegebenen Assets.

Bewegung entsteht ausschliesslich durch Schnitt und Deckkraft. Es gibt keinen
Zoom und keine Kamerafahrt - der Renderer erkennt die Ergebnisse als `VIDEO`
und setzt dafuer `NATIVE_CLIP_NO_EXTERNAL_CAMERA`, legt also auch spaeter keine
Fahrt darueber.

Aufruf aus dem Repository-Root:
    python 06_PRODUCTION/EP08_SCHLAFPARALYSE_V4/POST_PLAN/build_editorial_sequences.py
"""
from __future__ import annotations

import csv
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EPISODE = HERE.parent
ROOT = EPISODE.parents[1]
PLAN = HERE / "EP08_VOICE_VISUAL_SYNC_PLAN.csv"
OUT = EPISODE / "EDITORIAL_SEQUENCES"
QA = OUT / "QA_FRAMES"

W, H, FPS = 1920, 1080, 24
DUR = 3.5
BG = "#080B10"

# Ersatz fuer nicht beschaffbare Belege: die Quellenkarten aus
# tools/build_schlafparalyse_source_cards.py.
SUBSTITUTES = {
    # EDIT015 stellt medizinischen Befund gegen Internetbericht. Zwei Textkarten
    # nebeneinander waeren eine Textwand; die Karte traegt den Befund, das Bild
    # traegt die Berichtslage.
    "SRC_MISSING_DPH_MEDICAL_SOURCE_DETAIL": "SOURCE_CARDS/SRC053_DPH_MEDICAL_STATEMENT.png",
    "SRC_MISSING_DPH_MEDICAL_SOURCE_FULL": "SOURCE_CARDS/SRC053_DPH_MEDICAL_STATEMENT.png",
    "SRC_MISSING_ANON_FORUM": "IMG021_MULTIPLE_CAUSES_SAME_SILHOUETTE",
    "SRC_MISSING_ANON_HAT_FORUM": "SOURCE_CARDS/SRC055_HAT_REPORTS_EVIDENCE_STATUS.png",
    "SRC_MISSING_WEB_ARCHIVE_RESULTS_FULL": "SOURCE_CARDS/SRC056_WEB_ARCHIVE_STATUS.png",
    "SRC_MISSING_PERIOD_FORUM_CAPTURE": "SOURCE_CARDS/SRC057_PERIOD_FORUM_STATUS.png",
    "SRC_MISSING_NIGHTMARE_BIBLIOGRAPHY": "SOURCE_CARDS/SRC058_NIGHTMARE_BIBLIOGRAPHY.png",
    "SRC_MISSING_NIGHTMARE_LICENSED_KEYART": "SOURCE_CARDS/SRC058_NIGHTMARE_BIBLIOGRAPHY.png",
    "SRC_MISSING_MCNALLY_CLANCY_PAPER_PAGE": "SOURCE_CARDS/SRC052_MCNALLY_CLANCY_BIBLIOGRAPHY.png",
    "EDIT011_HARVARD_RESEARCH_TITLE": "SOURCE_CARDS/SRC051_HARVARD_RESEARCH_TITLE.png",
}

# Montageart je Cue. Abgeleitet aus der `edit_note` des Plans; wo dort nichts
# steht, entscheidet die Anzahl der Quellen.
#   hardcut  - harte Schnitte, jede Quelle steht still
#   reveal   - Grundbild, zweite Ebene blendet auf
#   split    - zwei gleichwertige Spalten, zweite erscheint
#   hold     - eine Quelle, ruhiger Ausklang ins Dunkel
MODES = {
    "EDIT001_LATE_NIGHT_SIGNAL_COLLAGE": "hardcut",
    "EDIT002_MESSAGE_COUNTER_MATERIAL": "hardcut",
    "EDIT003_FAX_TO_CRT_HARDCUTS": "hardcut",
    "EDIT004_NAMELESS_SIGNAL_NETWORK": "reveal",
    "EDIT005_QUESTION_THRESHOLD": "hold",
    "EDIT006_DRAWING_NAME_SEQUENCE": "reveal",
    "EDIT007_BLANK_SKETCH_TO_SHADOW": "reveal",
    "EDIT008_UFO_ARCHIVE_CHRONOLOGY": "hardcut",
    "EDIT009_VESTIBULAR_LAYER_REVEAL": "reveal",
    "EDIT010_REALITY_CAUSE_SPLIT": "split",
    "EDIT011_HARVARD_RESEARCH_TITLE": "hold",
    "EDIT012_MEMORY_LAYER_COMPOSITE": "hold",
    "EDIT013_MEMORY_TO_BRIM_BRIDGE": "reveal",
    "EDIT014_HAT_VARIATION_SEQUENCE": "hardcut",
    "EDIT015_EVIDENCE_BOUNDARY": "split",
    "EDIT016_SKETCH_CONVERGENCE": "reveal",
    "EDIT017_SEARCH_SEQUENCE": "hardcut",
    "EDIT018_PATTERN_MEME_EQUAL_SPLIT": "split",
    "EDIT019_BODY_STORY_THRESHOLD": "reveal",
    "EDIT020_FEEDBACK_PREVIEW": "reveal",
    "EDIT021_SIX_LAYER_LOOP_SETUP": "hardcut",
    "EDIT022_FILM_IMAGE_SPREAD": "split",
    "EDIT023_GLOBAL_NODE_REVEAL": "hold",
}


def run(args: list[str]) -> None:
    p = subprocess.run(args, text=True, capture_output=True)
    if p.returncode:
        raise RuntimeError((p.stderr or p.stdout)[-4000:])


def build_index() -> dict[str, Path]:
    index: dict[str, Path] = {}
    for p in EPISODE.rglob("*"):
        if p.suffix.lower() not in (".png", ".jpg", ".jpeg", ".webp"):
            continue
        if "QA_CONTACT" in str(p) or "QA_FRAMES" in str(p):
            continue
        index.setdefault(p.stem, p)
    return index


def resolve(token: str, index: dict[str, Path]) -> Path | None:
    token = re.sub(r"\.(png|jpg|jpeg)$", "", token.strip())
    if token in SUBSTITUTES:
        # Ein Ersatz kann ein Pfad relativ zur Episode sein (Quellenkarte) oder
        # der blosse Dateistamm eines vorhandenen Motivs.
        sub = SUBSTITUTES[token]
        q = EPISODE / sub
        if q.is_file():
            return q
        token = re.sub(r"\.(png|jpg|jpeg)$", "", Path(sub).name)
    if token in index:
        return index[token]
    hits = sorted(k for k in index if k.startswith(token + "_"))
    return index[hits[0]] if hits else None


def is_card(path: Path) -> bool:
    """Karten und Quellenkarten tragen Satz und duerfen nie beschnitten werden."""
    # Der Pfad entscheidet. Ein Praefixtest auf "SRC05" wuerde SRC050 mitnehmen -
    # das ist eine Originalableitung (Modemdetail), keine Karte.
    s = path.as_posix().upper()
    return "SOURCE_CARDS" in s or "/CARDS/" in s or path.stem.upper().startswith("CARD")


def scale_chain(label: str) -> str:
    """Quelle formatfuellend auf 1920x1080, ohne Verzerrung."""
    return (f"scale={W}:{H}:force_original_aspect_ratio=increase,"
            f"crop={W}:{H},setsar=1,format=rgba[{label}]")


def build_hardcut(sources: list[Path], out: Path) -> None:
    """Gleich lange harte Schnitte. Jede Quelle steht absolut still."""
    n = len(sources)
    seg = DUR / n
    inputs: list[str] = []
    for q in sources:
        inputs += ["-loop", "1", "-t", f"{seg:.3f}", "-i", str(q)]
    chains = [f"[{i}:v]scale={W}:{H}:force_original_aspect_ratio=increase,"
              f"crop={W}:{H},setsar=1,fps={FPS}[v{i}]" for i in range(n)]
    concat = "".join(f"[v{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0[out]"
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *inputs,
         "-filter_complex", ";".join(chains) + ";" + concat,
         "-map", "[out]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
         "-pix_fmt", "yuv420p", "-r", str(FPS), str(out)])


def build_reveal(sources: list[Path], out: Path) -> None:
    """Grundbild steht; die zweite Ebene blendet in der Mitte auf."""
    base, layer = sources[0], sources[1]
    fade_start = DUR * 0.38
    fade_len = DUR * 0.30
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-loop", "1", "-t", f"{DUR:.3f}", "-i", str(base),
         "-loop", "1", "-t", f"{DUR:.3f}", "-i", str(layer),
         "-filter_complex",
         f"[0:v]{scale_chain('b')};"
         f"[1:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
         f"setsar=1,format=rgba,"
         f"fade=t=in:st={fade_start:.3f}:d={fade_len:.3f}:alpha=1[l];"
         f"[b][l]overlay=0:0:format=auto,fps={FPS},format=yuv420p[out]",
         "-map", "[out]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
         "-pix_fmt", "yuv420p", "-r", str(FPS), str(out)])


def build_split(sources: list[Path], out: Path) -> None:
    """Zwei gleich breite Spalten. Die rechte erscheint, kein Gewinner."""
    left, right = sources[0], sources[1]
    half = W // 2
    fade_start = DUR * 0.30
    fade_len = DUR * 0.28
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-loop", "1", "-t", f"{DUR:.3f}", "-i", str(left),
         "-loop", "1", "-t", f"{DUR:.3f}", "-i", str(right),
         "-f", "lavfi", "-t", f"{DUR:.3f}", "-i", f"color=c={BG}:s={W}x{H}:r={FPS}",
         "-filter_complex",
         f"[0:v]scale={half}:{H}:force_original_aspect_ratio=increase,"
         f"crop={half}:{H},setsar=1[L];"
         f"[1:v]scale={half}:{H}:force_original_aspect_ratio=increase,"
         f"crop={half}:{H},setsar=1,format=rgba,"
         f"fade=t=in:st={fade_start:.3f}:d={fade_len:.3f}:alpha=1[R];"
         f"[2:v]format=rgba[bg];"
         f"[bg][L]overlay=0:0[s1];"
         f"[s1][R]overlay={half}:0:format=auto,"
         f"drawbox=x={half - 2}:y=0:w=4:h={H}:color={BG}@0.9:t=fill,"
         f"fps={FPS},format=yuv420p[out]",
         "-map", "[out]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
         "-pix_fmt", "yuv420p", "-r", str(FPS), str(out)])


def build_hold(sources: list[Path], out: Path) -> None:
    """Eine Quelle, ruhiger Ausklang. Kein Zoom, nur ein Abdunkeln am Ende."""
    src = sources[0]
    out_start = DUR * 0.72
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-loop", "1", "-t", f"{DUR:.3f}", "-i", str(src),
         "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                f"setsar=1,fade=t=out:st={out_start:.3f}:d={DUR - out_start:.3f}:"
                f"color={BG},fps={FPS},format=yuv420p",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
         "-pix_fmt", "yuv420p", "-r", str(FPS), str(out)])


BUILDERS = {"hardcut": build_hardcut, "reveal": build_reveal,
            "split": build_split, "hold": build_hold}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    QA.mkdir(parents=True, exist_ok=True)
    index = build_index()

    with PLAN.open(encoding="utf-8-sig", newline="") as handle:
        rows = [r for r in csv.DictReader(handle) if r["asset_status"] == "EDITORIAL_BUILD"]

    manifest: list[dict[str, str]] = []
    problems: list[str] = []

    for row in rows:
        name = row["visual_asset"]
        mode = MODES.get(name)
        if mode is None:
            problems.append(f"{name}: keine Montageart hinterlegt")
            continue

        tokens = [t for t in re.split(r"\+", row["base_asset_or_build"]) if t.strip()]
        resolved: list[Path] = []
        for tok in tokens:
            q = resolve(tok, index)
            if q is None:
                problems.append(f"{name}: Quelle nicht aufloesbar -> {tok.strip()}")
            else:
                resolved.append(q)
        if not resolved:
            continue
        # Karten sind Vollformat-Layouts mit Satzspiegel. In einer Splitspalte
        # wuerde die Haelfte der Schrift wegfallen, unter einer Reveal-Ebene
        # waere sie nicht mehr lesbar. Beteiligt sich eine Karte, wird hart
        # geschnitten - dann steht jede Karte einmal vollstaendig im Bild.
        if any(is_card(q) for q in resolved) and mode in ("split", "reveal"):
            mode = "hardcut"
        # Reveal und Split brauchen zwei Ebenen; faellt eine aus, wird gehalten.
        if mode in ("reveal", "split") and len(resolved) < 2:
            mode = "hold"
        if mode == "hardcut" and len(resolved) < 2:
            mode = "hold"

        out = OUT / f"{name}.mp4"
        BUILDERS[mode](resolved, out)
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(out),
             "-ss", f"{DUR / 2:.2f}", "-frames:v", "1", str(QA / f"{name}.jpg")])
        manifest.append({
            "filename": out.name,
            "cue_id": row["cue_id"],
            "act": row["act"],
            "mode": mode,
            "sources": " + ".join(q.name for q in resolved),
            "substituted": "yes" if any("SOURCE_CARDS" in str(q) for q in resolved) else "no",
            "duration_s": f"{DUR:.2f}",
            "resolution": f"{W}x{H}",
            "camera_rule": "NO_PAN_NO_ZOOM",
        })
        print(f"{mode:8s} {name}  <- {', '.join(q.name for q in resolved)}")

    with (OUT / "EP08_EDITORIAL_SEQUENCES_MANIFEST.csv").open(
            "w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(manifest[0].keys()))
        writer.writeheader()
        writer.writerows(manifest)

    print(f"\ncreated={len(manifest)}")
    if problems:
        print("\nOffen:")
        for p in problems:
            print("  ", p)
        sys.exit(1)


if __name__ == "__main__":
    main()
