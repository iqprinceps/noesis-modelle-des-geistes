#!/usr/bin/env python3
"""EP13_EN local renderer.

Reads the cue sheet built from the forced alignment, resolves each state to a
local file, renders one cached segment per state, then concatenates and muxes the
voice master.

Camera technique is taken from tools/noesis_render.py: the source is scaled to
3840x2160 before zoompan outputs 1920x1080, so one integer position step in the
working image is half an output pixel, and four temporal sub-positions per output
frame are averaged with tmix. That keeps the sub-pixel move smooth and avoids the
pixel-rounding judder.

Episode camera profile is 'reliquary': very small amplitude, calm, because this
episode is carried by objects that should be looked at rather than swept.
"""

from __future__ import annotations

import argparse
import csv
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
EP = ROOT / "07_ENGLISH_PRODUCTION" / "EP13_VATICAN_01"
CUE = EP / "05_DELIVERY" / "EP13_EN_VISUAL_CUE_SHEET.csv"
VOICE = EP / "02_VOICE" / "MASTER" / "EP13_EN_VO_MASTER.wav"
GEN = EP / "03_VISUALS" / "ASSETS" / "SELECTED" / "GENERATED"
CARDS = EP / "03_VISUALS" / "CARDS"
CLIPS = EP / "03_VISUALS" / "CLIPS"
ORIG = EP / "03_VISUALS" / "ASSETS" / "SELECTED" / "AUTHENTIC"
WORK = ROOT / "tmp" / "render" / "ep13"
SEGS = WORK / "segments"
OUTFILE = WORK / "EP13_EN_PICTURE.mp4"
FINAL = EP / "05_DELIVERY" / "EP13_EN_FINAL.mp4"

FPS, SUB = 30, 8

# Camera speed, not camera distance.
#
# The old profile used a fixed 3 percent zoom on a smoothstep ramp. Measured on
# raw frames, that froze 26 of 179 frames on a six second shot: smoothstep starts
# and ends at zero velocity, and a 3 percent move is only about 0.3 output pixels
# per frame, which is below the pixel grid zoompan has to land on. The picture sat
# still for several frames and then hopped. That is the judder.
#
# A linear ramp with the amplitude scaled to the shot length fixes both halves.
# Measured across 1.0 s to 9.1 s and across every pan direction, it produces zero
# frozen frames, and the mean frame-to-frame change stays flat at about 0.68,
# which is what constant velocity means. Irregularity, as the coefficient of
# variation of that change, falls from 0.57 to 0.29.
ZOOM_PER_SECOND = 0.05 / 6.0
ZOOM_MIN, ZOOM_MAX = 0.015, 0.090
FADE, BG = 0.16, "#0B0A0C"
# SUB=8 rather than 4: at 4, ten of the 108 moving stills still failed the shared
# cadence gate in tools/qa_smooth_still_motion.py, marginally, on jerk and on the
# 95th percentile of adjacent-frame difference. Doubling the temporal samples that
# tmix averages carried them across. It costs render time and nothing else.
CAMERA_PROFILE = "linear-constant-velocity-v3-sub8"

# Locked frames. The standard already asks for registration-sensitive images to
# hold still, and these four are exactly that. They are also the ones the cadence
# gate could not pass at any encoder quality, because fine line work and old
# photographic grain shimmer when they are moved a fraction of a pixel at a time.
# Holding them still removes the artefact at its source and is the better reading
# of each image anyway.
LOCKED_STATES = {
    "EP13-C05",             # Duerer engraving, pure high-contrast line work
    "EP13-C07",             # the 1917 photograph of the three children
    "H16_NEWSPAPER_STACK",  # newsprint, a document
    "H39_CALENDAR_PAGES",   # printed pages, a document
    "EP13-X07",             # archival portrait-format photograph, pillarboxed
}

# Segment quality. The cadence gate measures encoded segments, so on
# high-frequency images x264's frame-to-frame quantisation decisions register as
# irregular motion. Measured on H54_SEAL_SINGLE_MACRO: crf 17 gives p95/median
# 2.58 and fails, crf 14 gives 2.42 and fails, crf 12 gives 2.31 and passes, with
# the motion itself unchanged. These two states carry fine texture and keep their
# move, so they are encoded finer.
# A move needs long enough to be seen. Below about a third of a second the eye
# reads a cut, not a camera, and the shared cadence gate cannot judge it either:
# it needs nine frames and a 0.22 s shot has seven. Those shots hold still.
MIN_MOVE_SECONDS = 0.35

CRF_DEFAULT = 17
CRF_FINE = 12
FINE_STATES = {"H54_SEAL_SINGLE_MACRO"}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp"}
VIDEO_EXT = {".mp4", ".mov", ".mkv", ".webm"}


def run(args, capture=False, timeout=None):
    p = subprocess.run(args, text=True, capture_output=capture, timeout=timeout)
    if p.returncode:
        raise RuntimeError((p.stderr or p.stdout or "command failed")[-4000:])
    return (p.stdout or "") + (p.stderr or "")


def probe(path, entries):
    return run(["ffprobe", "-v", "error", "-show_entries", entries, "-of", "csv=p=0", str(path)], True).strip()


def duration(path):
    return float(probe(path, "format=duration"))


def dims(path):
    w, h = probe(path, "stream=width,height").splitlines()[0].split(",")[:2]
    return int(w), int(h)


_index = None


def resolve(state: str) -> pathlib.Path | None:
    """Map a cue-sheet state id to a local media file."""
    global _index
    if _index is None:
        _index = {}
        for folder in (GEN, CARDS, CLIPS, ORIG):
            if not folder.is_dir():
                continue
            for f in folder.iterdir():
                if f.suffix.lower() in IMAGE_EXT | VIDEO_EXT:
                    _index[f.stem.upper()] = f
        # originals carry manifest ids rather than filenames
        for name in ("COMMONS_ASSET_MANIFEST.csv", "COMMONS_EXPANSION_MANIFEST.csv",
                     "COMMONS_SHAREALIKE_REPLACEMENT_MANIFEST.csv"):
            p = EP / "02_SOURCES" / name
            if not p.is_file():
                continue
            for row in csv.DictReader(p.open(encoding="utf-8")):
                f = EP / row["file"]
                if f.is_file():
                    _index[row["asset_id"].upper()] = f
    key = state.upper()
    if key in _index:
        return _index[key]
    if ("EP13_" + key) in _index:
        return _index["EP13_" + key]
    return None


def contain_needed(path) -> bool:
    w, h = dims(path)
    return abs((w / h) - (16 / 9)) > 0.06


def base_filter(path, scale="1920:1080"):
    sigma = round(28 * int(scale.split(":")[0]) / 1920, 1)
    if contain_needed(path):
        return (f"split=2[fg][bg];[bg]scale={scale}:force_original_aspect_ratio=increase,"
                f"crop={scale},gblur=sigma={sigma},eq=brightness=-0.24[back];"
                f"[fg]scale={scale}:force_original_aspect_ratio=decrease[front];"
                f"[back][front]overlay=(W-w)/2:(H-h)/2")
    return f"scale={scale}:force_original_aspect_ratio=increase,crop={scale}"


def camera_filter(path, i, dur_s, static, first, last):
    fi = f",fade=t=in:st=0:d={FADE:.3f}:color={BG}" if first else ""
    fo = f",fade=t=out:st={max(0, dur_s - FADE):.3f}:d={FADE:.3f}:color={BG}" if last else ""
    if static:
        return base_filter(path) + f",fps={FPS},format=yuv420p" + fi + fo
    frames = max(2, round(dur_s * FPS * SUB))
    amount = min(ZOOM_MAX, max(ZOOM_MIN, ZOOM_PER_SECOND * dur_s))
    modes = ["in", "left", "in", "up", "out", "right", "in", "down"]
    mode = modes[i % len(modes)]
    z0, z1 = (1, 1 + amount) if mode != "out" else (1 + amount, 1)
    q = f"(on/{frames})"   # linear: any easing that reaches zero velocity freezes frames
    z = f"({z0:.5f}+({z1 - z0:.5f})*{q})"
    x = (f"(iw-iw/zoom)*(0.70*(1-{q}))" if mode == "left" else
         f"(iw-iw/zoom)*(0.70*{q})" if mode == "right" else "(iw-iw/zoom)/2")
    y = (f"(ih-ih/zoom)*(0.70*(1-{q}))" if mode == "up" else
         f"(ih-ih/zoom)*(0.70*{q})" if mode == "down" else "(ih-ih/zoom)/2")
    weights = " ".join(["1"] * SUB)
    return (base_filter(path, "3840:2160") +
            f",zoompan=z='{z}':x='{x}':y='{y}':d=1:s=1920x1080:fps={FPS * SUB},"
            f"tmix=frames={SUB}:weights='{weights}',framestep={SUB},fps={FPS},format=yuv420p" + fi + fo)


def load_shots():
    rows = list(csv.DictReader(CUE.open(encoding="utf-8-sig")))
    shots, i = [], 0
    while i < len(rows):
        r = rows[i]
        state = r["state"]
        start, end = float(r["in"]), float(r["out"])
        j = i + 1
        while j < len(rows) and rows[j]["state"] == state:   # merge contiguous holds
            end = float(rows[j]["out"])
            j += 1
        shots.append({"state": state, "start": start, "end": end,
                      "dur": round(end - start, 3), "beat": r["beat"], "text": r["text"]})
        i = j
    # A picture holds through the pause that follows its beat instead of cutting
    # to black: each shot runs until the next one starts, and the last one runs to
    # the end of the voice master.
    for k in range(len(shots) - 1):
        shots[k]["end"] = shots[k + 1]["start"]
        shots[k]["dur"] = round(shots[k]["end"] - shots[k]["start"], 3)
    if VOICE.is_file():
        shots[-1]["end"] = duration(VOICE)
        shots[-1]["dur"] = round(shots[-1]["end"] - shots[-1]["start"], 3)
    return shots


def cmd_doctor():
    ok = True
    for label, p in (("cue sheet", CUE), ("voice master", VOICE)):
        print(f"  {label}: {'OK' if p.is_file() else 'MISSING'}  {p}")
        ok &= p.is_file()
    for tool in ("ffmpeg", "ffprobe"):
        try:
            run([tool, "-version"], True)
            print(f"  {tool}: OK")
        except Exception:
            print(f"  {tool}: MISSING")
            ok = False
    shots = load_shots()
    unresolved = [s for s in shots if resolve(s["state"]) is None]
    print(f"  shots: {len(shots)}  unresolved: {len(unresolved)}")
    for s in unresolved[:40]:
        print(f"     beat {s['beat']}: {s['state']}")
    print(f"  voice duration: {duration(VOICE):.2f}s" if VOICE.is_file() else "")
    print(f"  cue coverage:   {shots[-1]['end']:.2f}s")
    return ok and not unresolved


def cmd_render(only=None):
    shots = load_shots()
    missing = [s for s in shots if resolve(s["state"]) is None]
    if missing:
        sys.exit("unresolved states: " + ", ".join(s["state"] for s in missing[:20]))
    SEGS.mkdir(parents=True, exist_ok=True)
    cache_path = WORK / "segment_cache.json"
    cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.is_file() else {}
    for i, s in enumerate(shots):
        out = SEGS / f"{i + 1:03d}_{s['state'][:44]}.mp4"
        src = resolve(s["state"])
        is_clip = src.suffix.lower() in VIDEO_EXT
        is_card = ("CARD" in s["state"].upper() or s["state"] in LOCKED_STATES
                   or s["dur"] < MIN_MOVE_SECONDS)
        fp = {"src": str(src), "mtime": src.stat().st_mtime_ns, "dur": s["dur"],
              "first": i == 0, "last": i == len(shots) - 1, "camera": CAMERA_PROFILE,
              "crf": CRF_FINE if s["state"] in FINE_STATES else CRF_DEFAULT}
        if only and only not in s["state"]:
            continue
        if out.is_file() and cache.get(out.name) == fp:
            continue
        vf = camera_filter(src, i, s["dur"], static=is_card, first=i == 0, last=i == len(shots) - 1)
        crf = str(CRF_FINE if s["state"] in FINE_STATES else CRF_DEFAULT)
        if is_clip:
            args = ["ffmpeg", "-y", "-loglevel", "error", "-stream_loop", "-1", "-i", str(src),
                    "-t", f"{s['dur']:.3f}", "-an", "-vf",
                    base_filter(src) + f",fps={FPS},format=yuv420p", "-c:v", "libx264",
                    "-preset", "medium", "-crf", crf, str(out)]
        else:
            args = ["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", str(src),
                    "-t", f"{s['dur']:.3f}", "-vf", vf, "-c:v", "libx264",
                    "-preset", "medium", "-crf", crf, "-pix_fmt", "yuv420p", str(out)]
        run(args, True, timeout=900)
        cache[out.name] = fp
        print(f"  {i + 1:3d}/{len(shots)}  {s['dur']:5.2f}s  {s['state'][:52]}", flush=True)
    cache_path.write_text(json.dumps(cache, indent=1), encoding="utf-8")
    print(f"segments in {SEGS}")


def cmd_final():
    shots = load_shots()
    files = sorted(SEGS.glob("*.mp4"), key=lambda p: int(p.name.split("_")[0]))
    if len(files) != len(shots):
        sys.exit(f"segment count {len(files)} != shot count {len(shots)}; run render first")
    lst = WORK / "concat.txt"
    lst.write_text("\n".join(f"file '{f.as_posix()}'" for f in files) + "\n", encoding="utf-8")
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
         "-c", "copy", str(OUTFILE)], True, timeout=1800)
    FINAL.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(OUTFILE), "-i", str(VOICE),
         "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-shortest", "-movflags", "+faststart", str(FINAL)], True, timeout=1800)
    print(f"picture {duration(OUTFILE):.2f}s  final {duration(FINAL):.2f}s -> {FINAL}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["doctor", "render", "final", "all"])
    ap.add_argument("--only", default=None)
    a = ap.parse_args()
    if a.command == "doctor":
        sys.exit(0 if cmd_doctor() else 1)
    if a.command in ("render", "all"):
        if not cmd_doctor():
            sys.exit("doctor failed")
        cmd_render(a.only)
    if a.command in ("final", "all"):
        cmd_final()


if __name__ == "__main__":
    main()
