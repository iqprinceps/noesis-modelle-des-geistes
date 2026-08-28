#!/usr/bin/env python3
"""Independent Scribe transcription and objective metrics for two EP01 auditions."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from difflib import SequenceMatcher
from pathlib import Path

from elevenlabs.client import ElevenLabs


ROOT = Path(__file__).resolve().parents[2]
EP = ROOT / "EP01_KOZYREV"
AUD = EP / "02_VOICE" / "auditions"
CLI_TOOLS = Path(r"C:\Users\iQPrinceps\Documents\Codex\NOESIS Channel\tools")


def load_key() -> str:
    sys.path.insert(0, str(CLI_TOOLS))
    from elevenlabs_cli import _load_key  # type: ignore

    return str(_load_key())


def words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.casefold())


def duration(path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    return float(result.stdout.strip())


def as_dict(value) -> dict:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if hasattr(value, "dict"):
        return value.dict()
    return json.loads(value.json())


def main() -> int:
    expected_text = (AUD / "AUDITION_TEXT.txt").read_text(encoding="utf-8").strip()
    expected = words(expected_text)
    client = ElevenLabs(api_key=load_key())
    results = []
    for audio in sorted(AUD.glob("EP01_AUDITION_*.mp3")):
        with audio.open("rb") as stream:
            response = client.speech_to_text.convert(
                model_id="scribe_v2",
                file=stream,
                language_code="en",
                tag_audio_events=False,
                diarize=False,
                timestamps_granularity="word",
                seed=82601,
                keyterms=["Kozyrev", "Nikolai Kozyrev", "Vlail Kaznacheev", "Alexander Trofimov"],
            )
        raw = as_dict(response)
        transcript = str(raw.get("text", ""))
        heard = words(transcript)
        matcher = SequenceMatcher(None, expected, heard, autojunk=False)
        result = {
            "candidate": audio.stem,
            "duration_seconds": round(duration(audio), 3),
            "word_count": len(expected),
            "estimated_wpm": round(len(expected) / duration(audio) * 60, 1),
            "scribe_similarity": round(matcher.ratio(), 6),
            "transcript": transcript,
            "transcription": raw,
        }
        results.append(result)
        (AUD / f"{audio.stem}_SCRIBE.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(json.dumps({k: result[k] for k in result if k != "transcription"}, ensure_ascii=False))

    report = {
        "purpose": "short identical-text audition comparison before single full master",
        "expected_text": expected_text,
        "results": results,
        "selection_rule": "Prefer intelligibility and investigative naturalness; use speed only as a tiebreaker.",
    }
    (AUD / "AUDITION_QA.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
