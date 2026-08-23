#!/usr/bin/env python3
"""Render individualized EP04A/EP04B audio stems and trim generator headroom.

The underlying synthesis generator may create working headroom after the VO.
This wrapper trims all delivered WAV stems to the actual rendered VO-master
length from stem_report.json. Endscreen/atmosphere duration is then chosen in
the edit and is not encoded as a hard episode duration.

Usage:
    python tools/ep04ab_audio_render.py EP04A
    python tools/ep04ab_audio_render.py EP04B
"""

from __future__ import annotations

import json
import subprocess
import sys
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROD = {
    "EP04A": ROOT / "PRODUCTION_SUMMARY" / "EP04A_JUNG_KUNDALINI_V5",
    "EP04B": ROOT / "PRODUCTION_SUMMARY" / "EP04B_CHAKRA_GENEALOGIE_V5",
}
CHUNK_FRAMES = 48000 * 4


def trim_wav(path: Path, seconds: float) -> None:
    tmp = path.with_suffix(path.suffix + ".trimtmp")
    with wave.open(str(path), "rb") as src:
        params = src.getparams()
        frames_left = min(src.getnframes(), int(round(seconds * src.getframerate())))
        with wave.open(str(tmp), "wb") as dst:
            dst.setparams(params)
            while frames_left > 0:
                take = min(CHUNK_FRAMES, frames_left)
                data = src.readframes(take)
                if not data:
                    break
                dst.writeframes(data)
                frames_left -= take
    tmp.replace(path)


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1].upper() not in PROD:
        raise SystemExit("Usage: python tools/ep04ab_audio_render.py EP04A|EP04B")
    profile = sys.argv[1].upper()
    prod = PROD[profile]
    report_path = prod / "voice" / "master" / "stem_report.json"
    if not report_path.is_file():
        raise SystemExit(
            f"Missing {report_path}\nRun `python tools/ep04ab_voice.py {profile} all` first."
        )

    subprocess.run(
        [sys.executable, str(ROOT / "tools" / "ep04ab_audio_stems.py"), profile],
        check=True,
    )

    report = json.loads(report_path.read_text(encoding="utf-8"))
    vo_duration = float(report["duration"])
    out = prod / "audio" / "stems"
    wavs = sorted(out.glob("*.wav"))
    if not wavs:
        raise SystemExit(f"No generated WAV stems found in {out}")
    for path in wavs:
        trim_wav(path, vo_duration)
        print(f"trimmed {path.name} -> {vo_duration:.3f}s")

    manifest_path = out / "audio_stem_manifest.json"
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        manifest = {}
    manifest.update({
        "episode": profile,
        "delivered_duration_seconds": round(vo_duration, 3),
        "duration_basis": "actual VO master from voice/master/stem_report.json",
        "postroll_rule": "No hard postroll is baked into delivered stems; extend/loop/fade in edit as the episode needs.",
        "files": [p.name for p in wavs],
    })
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
