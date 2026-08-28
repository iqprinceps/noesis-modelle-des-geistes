#!/usr/bin/env python3
"""Transcribe three critical windows from the final mixed EP02 master."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from difflib import SequenceMatcher
from pathlib import Path

from elevenlabs.client import ElevenLabs

ROOT = Path(__file__).resolve().parents[1]
EP = ROOT / "07_ENGLISH_PRODUCTION" / "EP02_GATEWAY"
MASTER = EP / "06_RENDER" / "EP02_GATEWAY_EN_REVIEW_MASTER_1080P.mp4"
ALIGNMENT = EP / "04_VOICE" / "ALIGNMENT" / "GW_EN_VO_ALIGNMENT.json"
OUT = EP / "03_VISUALS" / "QA" / "AUDIO_PROBES"
REPORT = EP / "03_VISUALS" / "QA" / "GW_EN_MIXED_SPEECH_QA.json"
CLI_TOOLS = Path(r"C:\Users\iQPrinceps\Documents\Codex\NOESIS Channel\tools")
PROBES = {
    "hook": (0.0, 32.0),
    "dense_music_sfx": (299.0, 324.0),
    "closing": (455.0, 481.0),
}


def tokens(text: str) -> list[str]:
    return re.findall(r"[0-9a-z]+", text.casefold())


def as_dict(value) -> dict:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if hasattr(value, "dict"):
        return value.dict()
    return json.loads(value.json())


def main() -> int:
    sys.path.insert(0, str(CLI_TOOLS))
    from elevenlabs_cli import _load_key  # type: ignore

    alignment = json.loads(ALIGNMENT.read_text(encoding="utf-8"))
    client = ElevenLabs(api_key=str(_load_key()))
    OUT.mkdir(parents=True, exist_ok=True)
    results = []
    for name, (start, end) in PROBES.items():
        audio = OUT / f"GW_EN_MIX_PROBE_{name.upper()}.wav"
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", str(start),
            "-to", str(end), "-i", str(MASTER), "-map", "0:a:0", "-ar", "48000", "-ac", "2",
            "-c:a", "pcm_s16le", str(audio),
        ], check=True)
        expected_text = "".join(
            str(word["text"]) for word in alignment["words"]
            if word.get("start") is not None and word.get("end") is not None
            and float(word["end"]) > start and float(word["start"]) < end
        ).strip()
        with audio.open("rb") as handle:
            response = client.speech_to_text.convert(
                model_id="scribe_v2", file=handle, language_code="en",
                tag_audio_events=False, diarize=False, timestamps_granularity="word",
                seed=260826, keyterms=["McDonnell", "Monroe", "Recommendation H", "non-corporeal", "Gateway"],
            )
        raw = as_dict(response)
        heard_text = str(raw.get("text", ""))
        similarity = SequenceMatcher(None, tokens(expected_text), tokens(heard_text), autojunk=False).ratio()
        results.append({
            "name": name, "range_seconds": [start, end], "audio_file": audio.name,
            "expected_text": expected_text, "heard_text": heard_text,
            "sequence_similarity": round(similarity, 6),
            "status": "PASS" if similarity >= 0.94 else "FAIL",
        })
        print(name, round(similarity, 6))
    report = {
        "purpose": "speech intelligibility check on the actual final stereo mix, not the isolated voice master",
        "model": "scribe_v2", "probes": results,
        "status": "PASS" if all(row["status"] == "PASS" for row in results) else "FAIL",
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if report["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
