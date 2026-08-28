#!/usr/bin/env python3
"""Independent speech-content QA for Schlafparalyse EP06-EP08.

ElevenLabs forced alignment is useful for timing but it is constrained by the
authored transcript.  This check uses Scribe as an independent listener and
compares the recognized word stream with the clean script.  Insertions,
deletions and replacements are mapped back to audio time so boundary glitches
can be fixed without guessing.
"""
from __future__ import annotations

import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

from elevenlabs.client import ElevenLabs

ROOT = Path(__file__).resolve().parents[1]
CLI_TOOLS = Path(r"C:\Users\iQPrinceps\Documents\Codex\NOESIS Channel\tools")
CFG = {
    "EP06": ("EP06_SCHLAFPARALYSE_V4", "EP06_VOICE_SCRIPT_CLEAN.txt"),
    "EP07": ("EP07_SCHLAFPARALYSE_V4", "EP07_VOICE_SCRIPT_CLEAN.txt"),
    "EP08": ("EP08_SCHLAFPARALYSE_V4", "EP08_SPRECHTEXT_CLEAN.txt"),
}


def tokens(text: str) -> list[str]:
    return re.findall(r"[0-9a-zäöüß]+", text.casefold())


def load_key() -> str:
    sys.path.insert(0, str(CLI_TOOLS))
    from elevenlabs_cli import _load_key  # type: ignore
    return str(_load_key())


def as_dict(response) -> dict:
    if hasattr(response, "model_dump"):
        return response.model_dump(mode="json")
    if hasattr(response, "dict"):
        return response.dict()
    return json.loads(response.json())


def main() -> int:
    episodes = tuple(CFG) if len(sys.argv) < 2 or sys.argv[1] == "all" else (sys.argv[1],)
    client = ElevenLabs(api_key=load_key())
    for ep in episodes:
        folder, clean_name = CFG[ep]
        prod = ROOT / "06_PRODUCTION" / folder
        master = prod / "voice" / "master" / f"{folder}_VO_MASTER.wav"
        clean = prod / f"VOICE_{ep}" / clean_name
        with master.open("rb") as audio:
            response = client.speech_to_text.convert(
                model_id="scribe_v2", file=audio, language_code="de",
                tag_audio_events=False, diarize=False,
                timestamps_granularity="word", seed=60826,
                keyterms=["Schlafparalyse", "Hufford", "Salem", "Shadow People", "Hat Man"],
            )
        raw = as_dict(response)
        expected = tokens(clean.read_text(encoding="utf-8"))
        word_rows = [w for w in raw.get("words", []) if str(w.get("text", "")).strip()]
        actual = tokens(" ".join(str(w.get("text", "")) for w in word_rows))
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
                "heard_context": [w.get("text") for w in around],
            })
        report = {
            "episode": ep,
            "purpose": "independent speech-to-text transition/content QA",
            "model": "scribe_v2",
            "expected_words": len(expected),
            "heard_words": len(actual),
            "sequence_similarity": round(matcher.ratio(), 6),
            "issues": issues,
            "transcription": raw,
        }
        out = prod / "voice" / "qa" / f"{ep}_SCRIBE_CONTENT_QA.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"{ep}: similarity={matcher.ratio():.5f}, issues={len(issues)} -> {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
