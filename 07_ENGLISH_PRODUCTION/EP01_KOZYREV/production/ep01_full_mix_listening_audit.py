#!/usr/bin/env python3
"""One-pass Vertex auditory review of the complete 7:14 EP01 final mix."""

from __future__ import annotations

import base64
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import requests


MODEL = "gemini-2.5-flash"
EP = Path(__file__).resolve().parents[1]
MIX = EP / "07_REVIEW/audio/EP01_EN_KOZYREV_FINAL_MIX.wav"
LISTENING = EP / "05_QA/FULL_MIX_LISTENING"
OPUS = LISTENING / "EP01_EN_KOZYREV_FULL_MIX_48K.opus"
OUTPUT = EP / "05_QA/FULL_MIX_LISTENING_AUDIT.json"


def access_token() -> str:
    gcloud = os.environ.get(
        "GCLOUD_CMD",
        r"C:\Users\iQPrinceps\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd",
    )
    return subprocess.run(
        [gcloud, "auth", "application-default", "print-access-token"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def main() -> int:
    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project:
        raise SystemExit("GOOGLE_CLOUD_PROJECT is not set")
    LISTENING.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(MIX),
        "-c:a", "libopus", "-b:a", "48k", "-vbr", "on", str(OPUS),
    ], check=True)
    prompt = """Listen to the attached complete 7 minute 14 second English documentary mix from beginning to end. This is the final continuous mix, not samples. Judge only what a first-time viewer hears: narration naturalness, name pronunciation, pace, pauses, hook tension, micro-hooks, fatigue, edit joins, glitches, silence/dropouts, score and sound-design balance, whether the restrained mysterious atmosphere supports rather than masks the voice, and the strength of the closing impulse. Distinguish a clearly localized defect requiring a pickup or remix from mere taste. Return concise JSON. For any localized issue give an approximate absolute timestamp; otherwise return an empty issues list."""
    schema = {
        "type": "OBJECT",
        "properties": {
            "listened_complete_stream": {"type": "BOOLEAN"},
            "overall_verdict": {"type": "STRING", "enum": ["PASS", "PASS_WITH_FIX", "FAIL"]},
            "naturalness_and_pronunciation": {"type": "STRING"},
            "pace_hook_and_retention": {"type": "STRING"},
            "score_sfx_voice_balance": {"type": "STRING"},
            "edit_joins_artifacts_dropouts": {"type": "STRING"},
            "closing_impulse": {"type": "STRING"},
            "localized_issues": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "timestamp": {"type": "STRING"},
                        "issue": {"type": "STRING"},
                        "required_action": {"type": "STRING"},
                    },
                    "required": ["timestamp", "issue", "required_action"],
                },
            },
            "pickup_or_remix_decision": {"type": "STRING"},
        },
        "required": [
            "listened_complete_stream", "overall_verdict", "naturalness_and_pronunciation",
            "pace_hook_and_retention", "score_sfx_voice_balance", "edit_joins_artifacts_dropouts",
            "closing_impulse", "localized_issues", "pickup_or_remix_decision",
        ],
    }
    url = f"https://aiplatform.googleapis.com/v1/projects/{project}/locations/global/publishers/google/models/{MODEL}:generateContent"
    response = requests.post(
        url,
        headers={"Authorization": f"Bearer {access_token()}", "Content-Type": "application/json"},
        json={
            "contents": [{"role": "USER", "parts": [
                {"text": prompt},
                {"inlineData": {"mimeType": "audio/ogg", "data": base64.b64encode(OPUS.read_bytes()).decode("ascii")}},
            ]}],
            "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json", "responseSchema": schema},
        },
        timeout=300,
    )
    if response.status_code >= 400:
        raise SystemExit(f"Full-mix listening audit failed once: HTTP {response.status_code}")
    try:
        verdict = json.loads(response.json()["candidates"][0]["content"]["parts"][0]["text"])
    except (KeyError, IndexError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Full-mix listening audit returned no valid structured verdict: {exc}")
    record = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "reviewer": "Vertex Gemini full-stream auditory review",
        "model": MODEL,
        "audio_file": OPUS.relative_to(EP).as_posix(),
        "duration_seconds": 434.632,
        "verdict": verdict,
    }
    OUTPUT.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(verdict, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
