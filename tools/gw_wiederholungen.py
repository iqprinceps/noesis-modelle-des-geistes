#!/usr/bin/env python3
"""Prueft eine Timeline auf nicht-zusammenhaengende Bildwiederholungen.

    python tools/gw_wiederholungen.py 06_PRODUCTION/EP0X_.../timeline/..._timeline.json
    python tools/gw_wiederholungen.py --legacy-strict <timeline.json>

Direkt benachbarte Eintraege mit demselben Asset gelten als ein kontinuierlicher
Block. Kehrt das Asset nach einem anderen Bild zurueck, ist das ein Fehler.
Die frueheren EP02-V7-Mengenwerte werden nur mit --legacy-strict geprueft.
"""

from __future__ import annotations

import collections
import hashlib
import json
import os
import sys
from pathlib import Path

from PIL import Image

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ZIEL_EINZELBILDER = 85
MAX_WIEDERHOLUNG = 4


def basename(p: str) -> str:
    return os.path.basename(p.replace("\\", "/"))


def resolve_visual(raw: str, timeline: Path) -> Path | None:
    path = Path(raw)
    candidates = [path] if path.is_absolute() else [Path.cwd() / path, timeline.parent / path]
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    return None


def average_hash(path: Path, size: int = 16) -> int:
    with Image.open(path) as image:
        resized = image.convert("L").resize((size, size))
        getter = getattr(resized, "get_flattened_data", None)
        pixels = list(getter() if getter else resized.getdata())
    mean = sum(pixels) / len(pixels)
    value = 0
    for pixel in pixels:
        value = (value << 1) | int(pixel >= mean)
    return value


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    legacy_strict = "--legacy-strict" in sys.argv
    paths = [arg for arg in sys.argv[1:] if not arg.startswith("--")]
    if len(paths) != 1:
        print(__doc__)
        return 2
    timeline = Path(paths[0]).resolve()
    rows = json.loads(timeline.read_text(encoding="utf-8"))
    namen = [basename(r["visual"]) for r in rows]
    zaehler = collections.Counter(namen)
    dauer = sum(r["duration"] for r in rows)

    blocks: list[dict[str, object]] = []
    for row, name in zip(rows, namen):
        duration = float(row["duration"])
        if blocks and blocks[-1]["name"] == name:
            blocks[-1]["duration"] = float(blocks[-1]["duration"]) + duration
            blocks[-1]["entries"] = int(blocks[-1]["entries"]) + 1
        else:
            blocks.append({"name": name, "duration": duration, "entries": 1})
    runs = [str(block["name"]) for block in blocks]
    run_counts = collections.Counter(runs)
    returns = {name: count for name, count in run_counts.items() if count > 1}

    print(f"{len(rows)} Timeline-Einträge · {len(runs)} visuelle Blöcke · {dauer/60:.0f}:{dauer%60:04.1f} · "
          f"Ø {dauer/len(rows):.2f}s\n")

    einzel = len(zaehler)
    hoechste = max(zaehler.values())
    print(f"Einzelbilder: {einzel}  (EP02-V7-Vergleich: {ZIEL_EINZELBILDER}, keine Mindestmenge)")
    print(f"Höchste Zeilennutzung: {hoechste}×")

    print("\n— Nicht-zusammenhängende Returns (HARD FAIL) —")
    if not returns:
        print("  0  ✓")
    for name, count in sorted(returns.items(), key=lambda item: (-item[1], item[0])):
        print(f"  {count} Blöcke  {name}")

    long_holds = [block for block in blocks if float(block["duration"]) >= 8.0]
    print("\n— Lange visuelle Holds (Review ab 8 s; ca. 10 s seltene Oberkante) —")
    if not long_holds:
        print("  0  ✓")
    for block in sorted(long_holds, key=lambda item: float(item["duration"]), reverse=True):
        marker = "  ← >10 s begründen oder neu bebildern" if float(block["duration"]) > 10.0 else ""
        print(f"  {float(block['duration']):5.2f}s  {block['name']}{marker}")

    print("\n— Mehrfach genutzt —")
    for name, n in zaehler.most_common():
        if n < 2:
            break
        szenen = [r["scene"] for r in rows if basename(r["visual"]) == name]
        doppelt = [s for s, c in collections.Counter(szenen).items() if c > 1]
        flag = "  ← zweimal im selben Akt" if doppelt else ""
        print(f"  {n}×  {name:<48} {sorted(set(szenen))}{flag}")

    # Catch identical or nearly identical stills hidden behind new filenames.
    image_ext = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}
    resolved: dict[str, Path] = {}
    for row in rows:
        name = basename(row["visual"])
        path = resolve_visual(row["visual"], timeline)
        if name not in resolved and path and path.suffix.lower() in image_ext:
            resolved[name] = path

    sha_groups: dict[str, list[str]] = collections.defaultdict(list)
    perceptual: dict[str, int] = {}
    for name, path in resolved.items():
        sha_groups[hashlib.sha256(path.read_bytes()).hexdigest()].append(name)
        try:
            perceptual[name] = average_hash(path)
        except Exception as exc:
            print(f"  WARN Hash nicht lesbar: {name}: {exc}")

    exact_duplicates = [sorted(names) for names in sha_groups.values() if len(set(names)) > 1]
    near_duplicates: list[tuple[str, str, int]] = []
    perceptual_names = sorted(perceptual)
    for i, left in enumerate(perceptual_names):
        for right in perceptual_names[i + 1:]:
            if any(left in group and right in group for group in exact_duplicates):
                continue
            distance = (perceptual[left] ^ perceptual[right]).bit_count()
            if distance <= 6:
                near_duplicates.append((left, right, distance))

    print("\n— Duplikate unter anderem Dateinamen (HARD FAIL) —")
    if not exact_duplicates:
        print("  0  ✓")
    for group in exact_duplicates:
        print("  " + " = ".join(group))

    print("\n— Visuell nahe Duplikate (manueller Review erforderlich) —")
    if not near_duplicates:
        print("  0  ✓")
    for left, right, distance in near_duplicates:
        print(f"  d={distance:02d}  {left}  ~  {right}")

    print("\n— Verteilung —")
    art = collections.Counter()
    for r in rows:
        v = r["visual"].replace("\\", "/")
        if r.get("kind") == "VIDEO":
            art["Bewegtbild"] += r["duration"]
        elif "/cards/" in v:
            art["Karte"] += r["duration"]
        elif "/documents/" in v or "reference_package" in v:
            art["Dokument"] += r["duration"]
        elif "AI_FINAL" in v or "/generated/" in v:
            art["Rekonstruktion"] += r["duration"]
        else:
            art["sonstiges"] += r["duration"]
    for k, v in art.most_common():
        print(f"  {k:<16}{v:6.1f}s  {100*v/dauer:4.1f} %")

    # Average hashes intentionally over-report similarly laid-out documents.
    # They are review candidates; asset returns and byte-identical copies are hard failures.
    no_return_errors = len(returns) + len(exact_duplicates)
    legacy_errors = int(einzel < ZIEL_EINZELBILDER) + int(hoechste > MAX_WIEDERHOLUNG)
    if legacy_strict:
        errors = no_return_errors + legacy_errors
        print(f"\nLEGACY-STRICT: {'BESTANDEN' if not errors else str(errors) + ' Punkte offen'}")
        return 0 if not errors else 1

    print(f"\nNO-RETURN-QA: {'BESTANDEN' if not no_return_errors else str(no_return_errors) + ' Wiederholungsprobleme'}")
    return 0 if not no_return_errors else 1


if __name__ == "__main__":
    sys.exit(main())
