from __future__ import annotations

import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "EP08_SPRECHERFASSUNG_GEORGE_FINAL.md"
SOURCE_DIR = ROOT / "source"
SYNC_PLAN = ROOT.parent / "POST_PLAN" / "EP08_VOICE_VISUAL_SYNC_PLAN.csv"

CUE_RANGES = {
    1: "V001-V005", 2: "V006-V009", 3: "V010-V014", 4: "V015-V020",
    5: "V021-V026", 6: "V027-V032", 7: "V033-V039",
    8: "V040-V045", 9: "V046-V051", 10: "V052-V057",
    11: "V058-V061", 12: "V062-V065", 13: "V066-V070", 14: "V071-V074",
    15: "V075-V080", 16: "V081-V085", 17: "V086-V091", 18: "V092-V096",
    19: "V097-V105", 20: "V106-V115",
    21: "V116-V121", 22: "V122-V128", 23: "V129-V135",
    24: "V136-V139", 25: "V140-V144", 26: "V145-V147", 27: "V148-V150",
}

PERFORMANCE = {
    1: "Nachtstudio nüchtern eröffnen; Datum nicht pathetisch setzen",
    2: "Silhouetten fließend aufzählen; kein Horrorflüstern",
    3: "Zahl klar tragen; Infrastruktur als eigentlichen Wendepunkt setzen",
    4: "Fragen wirklich stellen, nicht wie Schlussfolgerungen lesen",
    5: "Begriff sachlich einführen; Heidi Hollis nicht als Erfinderin behaupten",
    6: "Erklärend, aber offen; keine Identitätsbehauptung",
    7: "Direkte Du-Passage nah und ruhig; Schlussfrage offen halten",
    8: "Popkultur als Kontext, nicht als Spottfolie",
    9: "Körperliche Details glaubwürdig, ohne Trailersteigerung",
    10: "Das Wort real hörbar prüfen; drei Fragen nicht künstlich trennen",
    11: "Mack fair und nüchtern darstellen",
    12: "Forschung zugänglich; kleine menschliche Reaktion auf interessanter",
    13: "Fließend erklären; Gedächtnis nicht mechanisch klingen lassen",
    14: "Lüge oder Raumschiff trocken; Übergang zum Hut langsam zuspitzen",
    15: "Hutrand als visuelles Detail, nicht als Monsterenthüllung",
    16: "Medizinisch sachlich; Diphenhydramin sauber artikulieren",
    17: "Dreifaches Vielleicht gleichwertig, ohne Scheingewissheit",
    18: "Gedanken ruhig landen lassen",
    19: "Publikumsfrage direkt und unaufdringlich; Muster oder Meme klar",
    20: "Falle als Erkenntnis, nicht als Gotcha-Moment",
    21: "Filmtitel neutral; keine Werbe- oder Rezensionstonlage",
    22: "Schleife etwas zügiger, aber verständlich",
    23: "Globales Gedächtnis als zweite Wendung tragen",
    24: "Rückblick rhythmisch; Begriffslisten zusammenhängend lesen",
    25: "Keine Debunking-Haltung; Aussage bewusst begrenzen",
    26: "Viergliedrigen Kreis klar, ruhig und gleichmäßig lesen",
    27: "Nach Upload kurz denken; Schluss leiser und näher",
}


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\wÄÖÜäöüß]+(?:[-’][\wÄÖÜäöüß]+)*\b", text, re.UNICODE))


def resolved_cue_ranges() -> dict[int, str]:
    if not SYNC_PLAN.exists():
        return CUE_RANGES
    grouped: dict[int, list[int]] = {}
    with SYNC_PLAN.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            take_number = int(row["take_id"].rsplit("_", 1)[-1])
            cue_number = int(row["cue_id"][1:])
            grouped.setdefault(take_number, []).append(cue_number)
    if set(grouped) != set(range(1, 28)):
        return CUE_RANGES
    return {
        number: f"V{min(cues):03d}-V{max(cues):03d}"
        for number, cues in grouped.items()
    }


def main() -> None:
    raw = SOURCE.read_text(encoding="utf-8")
    pattern = re.compile(
        r"^## TAKE (\d{3}) — (S\d) — ([^\n]+)\n\n(.*?)(?=^## TAKE|^## Endcard)",
        re.MULTILINE | re.DOTALL,
    )
    takes = []
    for match in pattern.finditer(raw):
        number = int(match.group(1))
        section = match.group(2)
        title = match.group(3).strip()
        text = re.sub(r"\s+", " ", match.group(4)).strip()
        takes.append((number, section, title, text))

    if [t[0] for t in takes] != list(range(1, 28)):
        raise RuntimeError("Expected exactly TAKE 001 through TAKE 027")

    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    cue_ranges = resolved_cue_ranges()
    manifest_rows = []
    clean_parts = []
    desired_source_files: set[str] = set()
    for number, section, title, text in takes:
        slug_source = (
            title.upper()
            .replace("Ä", "AE")
            .replace("Ö", "OE")
            .replace("Ü", "UE")
            .replace("ß", "SS")
        )
        slug = re.sub(r"[^A-Z0-9]+", "_", slug_source).strip("_")
        take_id = f"EP08_TAKE_{number:03d}_{slug}"
        source_name = f"{take_id}.txt"
        desired_source_files.add(source_name)
        (SOURCE_DIR / source_name).write_text(text + "\n", encoding="utf-8")
        words = word_count(text)
        manifest_rows.append(
            {
                "take_id": take_id,
                "section": section,
                "cue_range": cue_ranges[number],
                "word_count": words,
                "estimated_seconds_at_136_wpm": f"{words * 60 / 136:.1f}",
                "pickup_note": PERFORMANCE[number],
            }
        )
        clean_parts.append(text)

    for stale in SOURCE_DIR.glob("EP08_TAKE_*.txt"):
        if stale.name not in desired_source_files:
            stale.unlink()

    (ROOT / "EP08_SPRECHTEXT_CLEAN.txt").write_text("\n\n".join(clean_parts) + "\n", encoding="utf-8")
    with (ROOT / "take_manifest.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=manifest_rows[0].keys())
        writer.writeheader()
        writer.writerows(manifest_rows)

    voice_lock = {
        "episode": "EP08_SCHLAFPARALYSE_V4",
        "voice_name": "George",
        "voice_id": "JBFqnCBsd6RMkjVDRZzb",
        "model": "eleven_multilingual_v2",
        "stability": 0.58,
        "similarity_boost": 0.80,
        "style": 0.08,
        "speed": 1.06,
        "speaker_boost": True,
        "rule": "Never time-stretch. Regenerate only the failed take with this exact lock.",
    }
    (ROOT / "elevenlabs_voice_lock.json").write_text(
        json.dumps(voice_lock, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    voice_batch = {
        "voice": "JBFqnCBsd6RMkjVDRZzb",
        "voice_name": "George",
        "model": "eleven_multilingual_v2",
        "settings": {
            "stability": 0.58,
            "similarity_boost": 0.80,
            "style": 0.08,
            "speed": 1.06,
            "use_speaker_boost": True,
        },
        "seed": 2402,
        "output_format": "mp3_44100_128",
        "output_dir": "06_PRODUCTION/EP08_SCHLAFPARALYSE_V4/VOICE_EP08/raw_stems",
        "stems": [
            {
                "id": row["take_id"],
                "text_file": f"06_PRODUCTION/EP08_SCHLAFPARALYSE_V4/VOICE_EP08/source/{row['take_id']}.txt",
            }
            for row in manifest_rows
        ],
    }
    (ROOT / "voice_batch.json").write_text(
        json.dumps(voice_batch, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    total_words = sum(int(row["word_count"]) for row in manifest_rows)
    estimate = total_words * 60 / 136
    readme = f"""# EP08 — George-Voice-Paket

**Status:** Text und Pickup-Struktur bereit; Audio noch nicht erzeugt.  
**Umfang:** {len(takes)} Takes, {total_words} Wörter, reine Sprechzeit rechnerisch etwa {estimate / 60:.1f} Minuten beim Planwert 136 Wörter pro Minute. Der verbindliche Serienkorridor liegt bei 132–140 Wörtern pro Minute; reale Zeiten entstehen erst durch George und Forced Alignment.

- `EP08_SPRECHERFASSUNG_GEORGE_FINAL.md` ist die redaktionelle Quelle.
- `EP08_SPRECHTEXT_CLEAN.txt` ist die durchgehende Untertitel-/Alignment-Fassung.
- `source/` enthält genau einen vollständigen Gedanken pro Pickup-Datei.
- `take_manifest.csv` verbindet Takes mit den visuellen Cues V001–V150.
- `elevenlabs_voice_lock.json` hält den bereits etablierten George-Lock fest.
- `voice_batch.json` ist die vorbereitete, noch nicht ausgeführte 27-Take-Batchliste.

Nach der Voice-Erzeugung werden ausschließlich gemessene Wortzeiten in den Sync-Plan übernommen. Sprache wird nie beschleunigt oder zeitlich gestreckt.
"""
    (ROOT / "README.md").write_text(readme, encoding="utf-8")


if __name__ == "__main__":
    main()
