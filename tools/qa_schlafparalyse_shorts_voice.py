#!/usr/bin/env python3
"""Independent content QA for the six Schlafparalyse Short narrations."""
from __future__ import annotations

import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

from elevenlabs.client import ElevenLabs

ROOT = Path(__file__).resolve().parents[1]
PROD = ROOT / "06_PRODUCTION" / "SCHLAFPARALYSE_SHORTS_V1"
CLI_TOOLS = Path(r"C:\Users\iQPrinceps\Documents\Codex\NOESIS Channel\tools")
JOBS = (
    "SP06A_ATEM",
    "SP06B_RUECKENLAGE",
    "SP07A_ALBTRAUMWORT",
    "SP07B_SALEM_ZEUGE",
    "SP08A_HAT_MAN_HUT",
    "SP08B_UNSICHTBARE_PERSON",
)


def tokens(text: str) -> list[str]:
    return re.findall(r"[0-9a-zäöüß]+", text.casefold())


def as_dict(response) -> dict:
    if hasattr(response, "model_dump"):
        return response.model_dump(mode="json")
    if hasattr(response, "dict"):
        return response.dict()
    return json.loads(response.json())


def main() -> int:
    sys.path.insert(0, str(CLI_TOOLS))
    from elevenlabs_cli import _load_key  # type: ignore

    client = ElevenLabs(api_key=str(_load_key()))
    failed = False
    for job in JOBS:
        folder = PROD / job
        audio_path = folder / "voice" / f"{job}_GEORGE.mp3"
        script_path = folder / "narration.txt"
        with audio_path.open("rb") as audio:
            response = client.speech_to_text.convert(
                model_id="scribe_v2",
                file=audio,
                language_code="de",
                tag_audio_events=False,
                diarize=False,
                timestamps_granularity="word",
                seed=60826,
                keyterms=[
                    "Schlafparalyse", "Zwerchfell", "Märe", "Mara", "Mahr",
                    "spectral evidence", "Bridget Bishop", "Hat Man",
                    "temporoparietal",
                ],
            )
        raw = as_dict(response)
        expected = tokens(script_path.read_text(encoding="utf-8"))
        word_rows = [
            word for word in raw.get("words", [])
            if str(word.get("text", "")).strip()
        ]
        actual = tokens(" ".join(str(word.get("text", "")) for word in word_rows))
        matcher = SequenceMatcher(None, expected, actual, autojunk=False)
        issues = []
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                continue
            around = word_rows[max(0, j1 - 3):min(len(word_rows), j2 + 3)]
            issues.append({
                "type": tag,
                "expected": expected[i1:i2],
                "heard": actual[j1:j2],
                "audio_start": around[0].get("start") if around else None,
                "audio_end": around[-1].get("end") if around else None,
                "heard_context": [word.get("text") for word in around],
            })
        similarity = matcher.ratio()
        failed |= similarity < 0.94
        report = {
            "job": job,
            "purpose": "independent speech-to-text content and transition QA",
            "voice": "George",
            "voice_id": "JBFqnCBsd6RMkjVDRZzb",
            "model": "scribe_v2",
            "expected_words": len(expected),
            "heard_words": len(actual),
            "sequence_similarity": round(similarity, 6),
            "issues": issues,
            "transcription": raw,
        }
        out = folder / "voice" / "qa" / "SCRIBE_CONTENT_QA.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"{job}: similarity={similarity:.5f}, issues={len(issues)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
