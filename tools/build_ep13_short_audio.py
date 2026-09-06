#!/usr/bin/env python3
"""Mix and master the four EP13 teaser shorts.

The bed is taken from the episode's own score rather than synthesised again, so a
teaser sounds like the film it points at. Each short draws from a different part
of the score, matched to what the teaser is about: the object texture for the
crown, the held texture for the silence.

Loudness follows the episode's finding: alimiter cannot see inter-sample peaks,
so it runs oversampled or the master stalls short of the target.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
WORK = ROOT / "tmp" / "render" / "ep13_shorts"
SCORE_EN = ROOT / "07_ENGLISH_PRODUCTION" / "EP13_VATICAN_01" / "04_AUDIO" / "stems" / "EP13_MX_SCORE.wav"
SFX_EN = ROOT / "07_ENGLISH_PRODUCTION" / "EP13_VATICAN_01" / "04_AUDIO" / "stems" / "EP13_SFX_BED.wav"

SHORTS = {
    "en1": (ROOT / "07_ENGLISH_PRODUCTION" / "EP13_VATICAN_01_SHORTS" / "S01_BULLET_IN_CROWN",
            "EP13_S01_EN", 372.0),
    "en2": (ROOT / "07_ENGLISH_PRODUCTION" / "EP13_VATICAN_01_SHORTS" / "S02_THE_SILENCE",
            "EP13_S02_EN", 116.0),
    "de1": (ROOT / "08_GERMAN_PRODUCTION" / "EP13_VATIKAN_01_SHORTS" / "S01_KUGEL_IN_KRONE",
            "EP13_S01_DE", 372.0),
    "de2": (ROOT / "08_GERMAN_PRODUCTION" / "EP13_VATIKAN_01_SHORTS" / "S02_DAS_SCHWEIGEN",
            "EP13_S02_DE", 116.0),
}


def run(args, timeout=None):
    p = subprocess.run(args, text=True, capture_output=True, timeout=timeout)
    if p.returncode:
        raise RuntimeError((p.stderr or p.stdout)[-3000:])
    return p.stdout


def probe(path, entries):
    return run(["ffprobe", "-v", "error", "-show_entries", entries,
                "-of", "csv=p=0", str(path)]).strip()


def measure(path):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af",
                          "loudnorm=I=-14:TP=-1:print_format=json", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    return json.loads(re.search(r"\{[^{}]*input_i[^{}]*\}", out, re.S).group())


def build(key):
    root, stem, score_at = SHORTS[key]
    voice = root / "02_VOICE" / f"{stem}_VO_MASTER.wav"
    picture = WORK / key / f"{stem}_PICTURE.mp4"
    for label, p in (("voice", voice), ("picture", picture)):
        if not p.is_file():
            sys.exit(f"{key}: missing {label}: {p}")
    total = float(probe(voice, "format=duration"))
    tmp = WORK / key
    mix = tmp / f"{stem}_MIX.wav"

    # voice, plus a slice of the episode score and effects bed ducked under it
    graph = (
        f"[0:a]aresample=48000,highpass=f=72,lowpass=f=15200[vo];"
        f"[1:a]atrim=start={score_at}:duration={total + 1:.3f},asetpts=PTS-STARTPTS,"
        f"volume=0.30,afade=t=in:st=0:d=1.2,afade=t=out:st={max(0, total - 2.4):.3f}:d=2.4[mx];"
        f"[2:a]atrim=start={score_at}:duration={total + 1:.3f},asetpts=PTS-STARTPTS,"
        f"volume=0.26[sx];"
        f"[mx][sx]amix=inputs=2:normalize=0[bed];"
        f"[bed][vo]sidechaincompress=threshold=0.02:ratio=7:attack=10:release=240[duck];"
        f"[vo][duck]amix=inputs=2:normalize=0:duration=first,"
        f"atrim=0:{total:.3f},asetpts=PTS-STARTPTS[out]"
    )
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(voice), "-i", str(SCORE_EN),
         "-i", str(SFX_EN), "-filter_complex", graph, "-map", "[out]",
         "-ar", "48000", "-ac", "1", "-c:a", "pcm_s24le", str(mix)], timeout=900)

    gain = -14.0 - float(measure(mix)["input_i"])
    norm = tmp / f"{stem}_NORM.wav"
    li = tp = 0.0
    for _ in range(10):
        chain = (f"volume={gain:.2f}dB,aresample=192000:resampler=soxr:precision=28,"
                 f"alimiter=limit=0.80:attack=4:release=70:level=disabled,"
                 f"aresample=48000:resampler=soxr:precision=28")
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mix), "-af", chain,
             "-ar", "48000", "-ac", "1", "-c:a", "pcm_s24le", str(norm)], timeout=900)
        a = measure(norm)
        li, tp = float(a["input_i"]), float(a["input_tp"])
        if abs(li + 14.0) <= 0.3 and tp <= -1.0:
            break
        gain += min(1.0, -14.0 - li) if tp <= -1.0 else -0.4

    final = root / "05_OUTPUT" / f"{stem}_MASTER_1080x1920.mp4"
    final.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(picture), "-i", str(norm),
         "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-shortest", "-movflags", "+faststart", str(final)], timeout=1800)
    size = final.stat().st_size / 1048576
    print(f"{key}: {probe(final, 'format=duration')}s  {li:.1f} LUFS  {tp:.1f} dBTP  "
          f"{size:.0f} MiB -> {final.name}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--which", default="en1,en2,de1,de2")
    a = ap.parse_args()
    for key in [k.strip() for k in a.which.split(",") if k.strip()]:
        build(key)


if __name__ == "__main__":
    main()
