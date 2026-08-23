#!/usr/bin/env python3
"""Prepare maintainable scene stems and an ElevenLabs batch for EP01."""

from __future__ import annotations

import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent.parent
EP = ROOT / "03_EPISODEN" / "TYPE_A" / "EP01_KOZYREV"
PROD = ROOT / "06_PRODUCTION" / "EP01_KOZYREV" / "voice"
SCRIPT = EP / "VOICE_SCRIPT_FINAL.md"
CLEAN = EP / "VOICE_SCRIPT_CLEAN.txt"


def slug(title: str) -> str:
    value = title.upper().replace("Ä", "AE").replace("Ö", "OE").replace("Ü", "UE").replace("ß", "SS")
    return re.sub(r"[^A-Z0-9]+", "_", value).strip("_")


def scenes() -> list[tuple[str, str]]:
    result: list[tuple[str, str]] = []
    title: str | None = None
    paragraphs: list[str] = []

    def close() -> None:
        if title and paragraphs:
            result.append((title, "\n\n".join(paragraphs).strip()))

    for line in SCRIPT.read_text(encoding="utf-8").splitlines():
        if line.startswith("## Szene "):
            close()
            title = line.split("–", 1)[-1].strip()
            paragraphs = []
        elif title and line.strip() and not line.strip().startswith("["):
            paragraphs.append(line.strip())
    close()
    return result


def tts_text(text: str) -> str:
    """Make years, measurements and Russian names unambiguous for German TTS."""
    replacements = [
        ("bis zu 2,80 Metern", "bis zu zwei Meter achtzig"),
        ("einer Breite von 1,20 Metern", "einer Breite von einem Meter zwanzig"),
        ("2,80 Meter", "zwei Meter achtzig"),
        ("1996", "neunzehnhundertsechsundneunzig"),
        ("1983", "neunzehnhundertdreiundachtzig"),
        ("Nikolai Alexandrowitsch Kozyrev", "Nikolai Alexandrowitsch Kósyreff"),
        ("Kozyrevs", "Kósyreffs"),
        ("Kozyrev", "Kósyreff"),
        ("Vlail Kaznacheev", "Wla-íl Kas-na-tsché-jef"),
        ("Kaznacheev", "Kas-na-tsché-jef"),
        ("Trofimov", "Tra-fí-moff"),
    ]
    for source, spoken in replacements:
        text = text.replace(source, spoken)
    return text


def main() -> int:
    parts = scenes()
    reconstructed = "\n\n".join(text for _, text in parts).strip()
    clean = CLEAN.read_text(encoding="utf-8").strip()
    if reconstructed != clean:
        raise RuntimeError("Scene extraction no longer matches VOICE_SCRIPT_CLEAN.txt exactly")

    source = PROD / "source"
    raw = PROD / "raw_stems"
    source.mkdir(parents=True, exist_ok=True)
    stems = []
    for index, (title, text) in enumerate(parts, 1):
        stem_id = f"EP01_VO_{index:02d}_{slug(title)}"
        path = source / f"{stem_id}.txt"
        spoken = tts_text(text)
        path.write_text(spoken + "\n", encoding="utf-8")
        stems.append({
            "id": stem_id,
            "title": title,
            "text_file": str(path.resolve()),
            "characters": len(spoken),
            "words": len(re.findall(r"\b[\w-]+\b", text, flags=re.UNICODE)),
        })

    batch = {
        "voice": "TUKJhQmz3RPYBNAgC5A1",
        "model": "eleven_multilingual_v2",
        "settings": {
            "stability": 0.56,
            "similarity_boost": 0.80,
            "style": 0.04,
            "speed": 1.13,
            "use_speaker_boost": True,
        },
        "seed": 2402,
        "output_format": "mp3_44100_128",
        "output_dir": str(raw.resolve()),
        "stems": [{"id": row["id"], "text_file": row["text_file"]} for row in stems],
    }
    PROD.mkdir(parents=True, exist_ok=True)
    (PROD / "stems.json").write_text(json.dumps(stems, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (PROD / "voice_batch.json").write_text(json.dumps(batch, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Prepared {len(stems)} scene stems / {sum(row['words'] for row in stems)} words")
    print(PROD / "voice_batch.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
