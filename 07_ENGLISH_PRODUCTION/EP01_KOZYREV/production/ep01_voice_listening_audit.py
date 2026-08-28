#!/usr/bin/env python3
"""Independent listening-focused QA for the existing EP01 voice only.

This sends small, already-rendered listening samples to Vertex Gemini for an
auditory performance review.  It never generates speech or images, never logs
credentials, and stores only the compact structured verdict.
"""

from __future__ import annotations

import base64
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import requests


MODEL = "gemini-2.5-flash"
ROOT = Path(__file__).resolve().parents[3]
EP = ROOT / "07_ENGLISH_PRODUCTION" / "EP01_KOZYREV"
SAMPLES = EP / "02_VOICE" / "qa" / "listening_samples"
OUTPUT = EP / "02_VOICE" / "qa" / "EP01_EN_LISTENING_AUDIT.json"


def token() -> str:
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


def audio_part(path: Path) -> dict:
    return {
        "inlineData": {
            "mimeType": "audio/ogg",
            "data": base64.b64encode(path.read_bytes()).decode("ascii"),
        }
    }


def main() -> int:
    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project:
        raise SystemExit("GOOGLE_CLOUD_PROJECT is not set")
    ordered = [
        ("AUDITION_A", SAMPLES / "AUDITION_A.opus"),
        ("AUDITION_B", SAMPLES / "AUDITION_B.opus"),
        ("MASTER_HOOK", SAMPLES / "MASTER_HOOK.opus"),
        ("MASTER_THEORIES", SAMPLES / "MASTER_THEORIES.opus"),
        ("MASTER_BLIND_TEST", SAMPLES / "MASTER_BLIND_TEST.opus"),
        ("MASTER_CONCLUSION", SAMPLES / "MASTER_CONCLUSION.opus"),
    ]
    missing = [str(path) for _, path in ordered if not path.exists()]
    if missing:
        raise SystemExit("Missing listening samples: " + ", ".join(missing))

    prompt = """You are performing an auditory QA of English documentary narration for a serious mystery/science YouTube episode. Listen to all six labeled clips in order. Do not judge transcript accuracy; judge what a viewer hears: naturalness, pace, pauses, emphasis, tension, mystic atmosphere without melodrama, pronunciation, edit joins, fatigue, artifacts, and retention. Auditions A and B contain identical text; say which performance is stronger. The four MASTER clips sample the selected full master at the hook, theory section, blind-test explanation, and conclusion. A pickup is justified only for a clearly localized audible performance defect; do not request stylistic re-recording merely from preference. Return compact JSON using the requested schema."""
    parts: list[dict] = [{"text": prompt}]
    for label, path in ordered:
        parts.append({"text": f"NEXT AUDIO LABEL: {label}"})
        parts.append(audio_part(path))

    schema = {
        "type": "OBJECT",
        "properties": {
            "audition_preference": {"type": "STRING"},
            "audition_reason": {"type": "STRING"},
            "master_overall_verdict": {"type": "STRING", "enum": ["PASS", "PASS_WITH_PICKUP", "FAIL"]},
            "naturalness": {"type": "STRING"},
            "pace_and_pauses": {"type": "STRING"},
            "tension_and_atmosphere": {"type": "STRING"},
            "pronunciation": {"type": "STRING"},
            "edit_joins_and_artifacts": {"type": "STRING"},
            "retention": {"type": "STRING"},
            "localized_defects": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "sample": {"type": "STRING"},
                        "approx_seconds_within_sample": {"type": "STRING"},
                        "defect": {"type": "STRING"},
                        "pickup_required": {"type": "BOOLEAN"},
                    },
                    "required": ["sample", "approx_seconds_within_sample", "defect", "pickup_required"],
                },
            },
            "pickup_decision": {"type": "STRING"},
        },
        "required": [
            "audition_preference",
            "audition_reason",
            "master_overall_verdict",
            "naturalness",
            "pace_and_pauses",
            "tension_and_atmosphere",
            "pronunciation",
            "edit_joins_and_artifacts",
            "retention",
            "localized_defects",
            "pickup_decision",
        ],
    }
    url = (
        f"https://aiplatform.googleapis.com/v1/projects/{project}/locations/global/"
        f"publishers/google/models/{MODEL}:generateContent"
    )
    response = requests.post(
        url,
        headers={"Authorization": f"Bearer {token()}", "Content-Type": "application/json"},
        json={
            "contents": [{"role": "USER", "parts": parts}],
            "generationConfig": {
                "temperature": 0.1,
                "responseMimeType": "application/json",
                "responseSchema": schema,
            },
        },
        timeout=240,
    )
    if response.status_code >= 400:
        raise SystemExit(f"Listening audit failed: HTTP {response.status_code}")
    data = response.json()
    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        verdict = json.loads(text)
    except (KeyError, IndexError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Listening audit returned no valid structured verdict: {exc}")
    record = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "reviewer": "Vertex Gemini auditory review",
        "model": MODEL,
        "input_samples": [label for label, _ in ordered],
        "scope": "performance listening only; source and transcript accuracy audited separately",
        "verdict": verdict,
    }
    OUTPUT.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(verdict, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
