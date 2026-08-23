#!/usr/bin/env python3
"""Prepare scene-based ElevenLabs narration inputs for EP02 Gateway."""

from __future__ import annotations

import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent.parent
PROD = ROOT / "06_PRODUCTION" / "EP02_GATEWAY"
SCRIPT = PROD / "03_DREHBUCH_PRODUKTIONSFASSUNG.md"
CLEAN = PROD / "04_VOICE_SCRIPT_CLEAN.txt"
VOICE = PROD / "voice"

# The scene windows are editorial targets from the approved 12-minute structure.
SCENE_WINDOWS = [50.0, 75.0, 90.0, 105.0, 110.0, 115.0, 110.0, 65.0]
# Helmut remains the series voice. Per-scene tempo follows the actual narrative density.
SCENE_SPEEDS = [1.05, 1.16, 1.13, 0.88, 0.90, 0.86, 0.92, 0.96]


def slug(title: str) -> str:
    value = title.upper().replace("Ä", "AE").replace("Ö", "OE").replace("Ü", "UE").replace("ß", "SS")
    return re.sub(r"[^A-Z0-9]+", "_", value).strip("_")


def scenes() -> list[tuple[str, str]]:
    result: list[tuple[str, str]] = []
    title: str | None = None
    collecting = False
    paragraphs: list[str] = []

    def close() -> None:
        if title and paragraphs:
            result.append((title, "\n\n".join(paragraphs).strip()))

    for line in SCRIPT.read_text(encoding="utf-8").splitlines():
        if line.startswith("## Szene "):
            close()
            title = line.split(" |", 1)[0].split(" - ", 1)[-1].strip()
            collecting = False
            paragraphs = []
        elif line.strip() == "### Voiceover":
            collecting = True
        elif line.startswith("## ") or line.startswith("### "):
            collecting = False
        elif collecting and line.strip():
            paragraphs.append(line.strip())
    close()
    return result


def tts_text(text: str) -> str:
    """Resolve abbreviations, years and English terminology for German narration."""
    replacements = [
        ("9. Juni 1983", "neunten Juni neunzehnhundertdreiundachtzig"),
        ("1983", "neunzehnhundertdreiundachtzig"),
        ("1993", "neunzehnhundertdreiundneunzig"),
        ("2019", "zweitausendneunzehn"),
        ("2023", "zweitausenddreiundzwanzig"),
        ("Wayne M. McDonnell", "Wäin Em Mak-Donnell"),
        ("McDonnells", "Mak-Donnells"),
        ("McDonnell", "Mak-Donnell"),
        ("Robert A. Monroe", "Robert Ei Monroe"),
        ("Hemi-Sync", "Hemmi-Sink"),
        ("EEG-Muster", "E E G Muster"),
        ("Frequency-Following Response", "Frequency Following Response"),
        ("Focus 10", "Focus zehn"),
        ("Focus 12", "Focus zwölf"),
        ("Focus 15", "Focus fünfzehn"),
        ("Focus 21", "Focus einundzwanzig"),
        ("400 Hertz", "vierhundert Hertz"),
        ("410", "vierhundertzehn"),
        ("10 Hertz", "zehn Hertz"),
        ("22 Studien", "zweiundzwanzig Studien"),
        ("fünf Prozent", "fünf Prozent"),
        ("CIA", "C I A"),
        ("U.S. Army", "U S Army"),
        ("US-Patent", "U S Patent"),
    ]
    for source, spoken in replacements:
        text = text.replace(source, spoken)
    return text


def main() -> int:
    parts = scenes()
    if len(parts) != 8:
        raise RuntimeError(f"Expected 8 scenes, found {len(parts)}")
    reconstructed = "\n\n".join(text for _, text in parts).strip()
    clean = CLEAN.read_text(encoding="utf-8").strip()
    if reconstructed != clean:
        raise RuntimeError("Scene extraction no longer matches 04_VOICE_SCRIPT_CLEAN.txt exactly")

    source = VOICE / "source"
    raw = VOICE / "raw_stems"
    source.mkdir(parents=True, exist_ok=True)
    raw.mkdir(parents=True, exist_ok=True)
    stems: list[dict] = []
    for index, ((title, text), target, speed) in enumerate(zip(parts, SCENE_WINDOWS, SCENE_SPEEDS), 1):
        stem_id = f"EP02_VO_{index:02d}_{slug(title)}"
        path = source / f"{stem_id}.txt"
        spoken = tts_text(text)
        path.write_text(spoken + "\n", encoding="utf-8")
        stems.append({
            "id": stem_id,
            "scene": f"S{index}",
            "title": title,
            "text_file": str(path.resolve()),
            "clean_text": text,
            "target_duration": target,
            "speed": speed,
            "characters": len(spoken),
            "words": len(re.findall(r"\b[\w-]+\b", text, flags=re.UNICODE)),
        })

    batch = {
        "voice": "TUKJhQmz3RPYBNAgC5A1",
        "model": "eleven_multilingual_v2",
        "settings": {
            "stability": 0.58,
            "similarity_boost": 0.80,
            "style": 0.03,
            "speed": 1.0,
            "use_speaker_boost": True,
        },
        "seed": 2402,
        "output_format": "mp3_44100_128",
        "output_dir": str(raw.resolve()),
        "stems": [
            {"id": row["id"], "text_file": row["text_file"], "settings": {"speed": row["speed"]}}
            for row in stems
        ],
    }
    VOICE.mkdir(parents=True, exist_ok=True)
    (VOICE / "stems.json").write_text(json.dumps(stems, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (VOICE / "voice_batch.json").write_text(json.dumps(batch, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Prepared {len(stems)} stems / {sum(row['words'] for row in stems)} words / 720 seconds")
    print(VOICE / "voice_batch.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
