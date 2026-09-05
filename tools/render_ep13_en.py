#!/usr/bin/env python3
"""EP13_EN local renderer.

Motion comes from tools/smooth_still_motion.py, the shared engine the visual
standard requires and the one EP07 uses. This script previously carried its own
zoompan implementation, which the standard forbids in as many words, and it
juddered: measured on the delivered master, the per-frame step of a moving still
averaged 0.31 px with a standard deviation of 0.34, swinging between 0.05 and
1.21 px. The engine supersamples to 7680x4320 rather than 3840x2160, so its
position quantum is a quarter of an output pixel instead of a half.

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
import concurrent.futures
import csv
import json
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from smooth_still_motion import ENGINE_VERSION, eased_zoompan_filter  # noqa: E402

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

FPS = 30
WORKERS = 3   # 7680x4320 buffers are large and only ~5 GB of RAM is free here

# Amplitude, matched to EP07, which is the channel reference for motion that does
# not judder. Measured with the shared engine on one still, the evenness of the
# per-frame step improves as the amplitude grows: 1.16 at zoom 0.017, 0.94 at
# 0.023, 0.71 at 0.043, 0.58 at 0.070. EP07 nevertheless reads as clean at 0.017,
# because at 0.087 px per frame the move is too small for its unevenness to be
# seen at all.
#
# So there are two safe places and a bad one between them. Small enough that the
# motion is subliminal, or fast enough that the steps are as even as this pipeline
# gets. EP13 sat in the middle at 0.043: visible enough to notice, uneven enough
# to stutter. It now uses EP07's range, 0.010 to 0.023 scaled by shot length.
ZOOM_PER_SECOND = 0.017 / 4.5
ZOOM_MIN, ZOOM_MAX = 0.010, 0.023
FADE, BG = 0.16, "#0B0A0C"

# Locked frames. The standard asks registration-sensitive images to hold still,
# and fine line work or old photographic grain shimmers when moved a fraction of
# a pixel per frame. Each of these is an image to look at, not travel across.
LOCKED_STATES = {
    "EP13-C05",             # Duerer engraving, pure high-contrast line work
    "EP13-C07",             # the 1917 photograph of the three children
    "H16_NEWSPAPER_STACK",  # newsprint, a document
    "H39_CALENDAR_PAGES",   # printed pages, a document
    "EP13-X07",             # archival portrait-format photograph
    "H50_THREE_READERS_TABLE",  # three sheets of dense hand, a document to read
}

# Below about a third of a second the eye reads a cut, not a camera.
MIN_MOVE_SECONDS = 0.35

# A held end screen after the narration. YouTube places its subscribe badge and
# next-video thumbnail over the last seconds of a film and needs somewhere to put
# them; the episode previously ended 1.3 s after the closing line, which left no
# room at all. The card keeps its right half bare for exactly that.
OUTRO_SECONDS = 20.0
OUTRO_STATE = "CARD11_END_SCREEN"

CRF = 17
COMPOSED = WORK / "composed"   # 16:9 blurred-background plates, see compose()

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


def compose(src: pathlib.Path) -> pathlib.Path:
    """Return a 16:9 plate for a source that is not already 16:9.

    The shared motion engine letterboxes to black. This channel fills the sides
    with a blurred, darkened copy of the picture instead, so the plate is built
    once here and the engine then sees an ordinary 16:9 image.
    """
    if not contain_needed(src):
        return src
    COMPOSED.mkdir(parents=True, exist_ok=True)
    out = COMPOSED / (src.stem + ".png")
    if out.is_file() and out.stat().st_mtime_ns >= src.stat().st_mtime_ns:
        return out
    vf = ("split=2[fg][bg];"
          "[bg]scale=3840:2160:force_original_aspect_ratio=increase,crop=3840:2160,"
          "gblur=sigma=56,eq=brightness=-0.24[back];"
          "[fg]scale=3840:2160:force_original_aspect_ratio=decrease:flags=lanczos[front];"
          "[back][front]overlay=(W-w)/2:(H-h)/2")
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-vf", vf,
         "-frames:v", "1", str(out)], True, timeout=300)
    return out


def fades(dur_s, first, last):
    fi = f",fade=t=in:st=0:d={FADE:.3f}:color={BG}" if first else ""
    fo = f",fade=t=out:st={max(0, dur_s - FADE):.3f}:d={FADE:.3f}:color={BG}" if last else ""
    return fi + fo


def locked_filter(dur_s, first, last):
    """A held frame: fit to 1920x1080 and do not move it."""
    return (f"scale=1920:1080:force_original_aspect_ratio=decrease:flags=lanczos,"
            f"pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black,fps={FPS},"
            f"trim=duration={dur_s:.6f},setpts=PTS-STARTPTS,format=yuv420p"
            + fades(dur_s, first, last))


def moving_filter(i, dur_s, first, last):
    """The shared engine. Direction rotates; amplitude tracks the shot length."""
    amount = min(ZOOM_MAX, max(ZOOM_MIN, ZOOM_PER_SECOND * dur_s))
    biases = [(0.5, 0.5), (0.2, 0.5), (0.5, 0.5), (0.5, 0.2),
              (0.5, 0.5), (0.8, 0.5), (0.5, 0.5), (0.5, 0.8)]
    x_bias, y_bias = biases[i % len(biases)]
    return eased_zoompan_filter(duration=dur_s, fps=FPS, width=1920, height=1080,
                                x_bias=x_bias, y_bias=y_bias, zoom_amount=amount,
                                background="black") + fades(dur_s, first, last)


def clip_filter(path, dur_s, first, last):
    """Fit a clip to its shot without ever replaying it.

    A clip shorter than its shot used to be looped, so CLIP09 played its first
    1.2 seconds a second time and the action visibly restarted. A clip is a
    performance: it may be slowed a little to fill the gap, and past that it
    holds on its last frame, but it never begins again.
    """
    src = float(probe(path, "format=duration"))
    fit = ""
    if dur_s > src * 1.02:
        ratio = dur_s / src
        if ratio <= 1.35:
            fit = f",setpts={ratio:.6f}*PTS"          # slow slightly to fit
        else:
            fit = (f",setpts={1.35:.6f}*PTS,"          # slow to the limit, then hold
                   f"tpad=stop_mode=clone:stop_duration={dur_s - src * 1.35:.3f}")
    return (f"scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080"
            f"{fit},fps={FPS},format=yuv420p" + fades(dur_s, first, last))


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
        end = duration(VOICE)
        shots[-1]["end"] = end
        shots[-1]["dur"] = round(end - shots[-1]["start"], 3)
        shots.append({"state": OUTRO_STATE, "start": end, "end": end + OUTRO_SECONDS,
                      "dur": OUTRO_SECONDS, "beat": "outro",
                      "text": "end screen hold, no narration"})
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


def render_one(job):
    i, s, total = job
    out = SEGS / f"{i + 1:03d}_{s['state'][:44]}.mp4"
    src = resolve(s["state"])
    first, last = i == 0, i == total - 1
    if src.suffix.lower() in VIDEO_EXT:
        vf = clip_filter(src, s["dur"], first, last)
        args = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(src),
                "-an", "-vf", vf]
    else:
        plate = compose(src)
        locked = ("CARD" in s["state"].upper() or s["state"] in LOCKED_STATES
                  or s["dur"] < MIN_MOVE_SECONDS)
        vf = (locked_filter(s["dur"], first, last) if locked
              else moving_filter(i, s["dur"], first, last))
        args = ["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", str(plate),
                "-t", f"{s['dur']:.3f}", "-vf", vf]
    args += ["-c:v", "libx264", "-preset", "medium", "-crf", str(CRF),
             "-pix_fmt", "yuv420p", "-frames:v", str(max(1, round(s["dur"] * FPS))),
             str(out)]
    run(args, True, timeout=3600)
    return i, s, out


def fingerprint(i, s, total):
    src = resolve(s["state"])
    return {"src": str(src), "mtime": src.stat().st_mtime_ns, "dur": s["dur"],
            "first": i == 0, "last": i == total - 1, "crf": CRF,
            "engine": ENGINE_VERSION, "path": "smooth_still_motion"}


def cmd_render(only=None):
    shots = load_shots()
    missing = [s for s in shots if resolve(s["state"]) is None]
    if missing:
        sys.exit("unresolved states: " + ", ".join(s["state"] for s in missing[:20]))
    SEGS.mkdir(parents=True, exist_ok=True)
    cache_path = WORK / "segment_cache.json"
    cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.is_file() else {}
    total = len(shots)
    todo = []
    for i, s in enumerate(shots):
        if only and only not in s["state"]:
            continue
        out = SEGS / f"{i + 1:03d}_{s['state'][:44]}.mp4"
        if out.is_file() and cache.get(out.name) == fingerprint(i, s, total):
            continue
        todo.append((i, s, total))
    print(f"  {len(todo)} of {total} segments to render on {WORKERS} workers", flush=True)
    done = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as pool:
        for i, s, out in pool.map(render_one, todo):
            cache[out.name] = fingerprint(i, s, total)
            done += 1
            print(f"  {done:3d}/{len(todo)}  {s['dur']:5.2f}s  {s['state'][:52]}", flush=True)
            cache_path.write_text(json.dumps(cache, indent=1), encoding="utf-8")
    cache_path.write_text(json.dumps(cache, indent=1), encoding="utf-8")
    print(f"segments in {SEGS}")


def cmd_status():
    """How far along the render is. Safe to run while one is in progress."""
    import datetime
    shots = load_shots()
    total = len(shots)
    cache_path = WORK / "segment_cache.json"
    cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.is_file() else {}
    done, stale, missing, newest = [], [], [], 0.0
    for i, s in enumerate(shots):
        name = f"{i + 1:03d}_{s['state'][:44]}.mp4"
        f = SEGS / name
        if not f.is_file():
            missing.append((i + 1, s))
        elif cache.get(name) == fingerprint(i, s, total):
            done.append((i + 1, s))
            newest = max(newest, f.stat().st_mtime)
        else:
            stale.append((i + 1, s))

    open_ = stale + missing
    pct = 100.0 * len(done) / total
    bar = "#" * int(pct / 2.5) + "." * (40 - int(pct / 2.5))
    print("")
    print("EP13_EN  segment render")
    print(f"  [{bar}] {pct:5.1f}%")
    print(f"  fertig      {len(done):3d} / {total}")
    print(f"  offen       {len(open_):3d}   ({len(missing)} fehlen, {len(stale)} veraltet)")
    if newest:
        age = (datetime.datetime.now().timestamp() - newest) / 60
        print(f"  zuletzt     vor {age:.1f} min geschrieben")
        if open_ and age < 10 and len(done) > 3:
            first = min(f.stat().st_mtime for f in SEGS.glob("*.mp4")
                        if datetime.datetime.now().timestamp() - f.stat().st_mtime < 36000)
            rate = (newest - first) / max(1, len(done) - 1)
            eta = len(open_) * rate / 60
            print(f"  Tempo       {rate:.0f}s pro Segment  ->  noch ca. {eta:.0f} min")
    secs_done = sum(s["dur"] for _, s in done)
    print(f"  Material    {secs_done / 60:.1f} von {sum(s['dur'] for s in shots) / 60:.1f} min")
    if open_:
        print("")
        print("  noch offen:")
        for n, s in open_[:15]:
            print(f"    {n:3d}  {s['dur']:5.2f}s  {s['state'][:48]}")
        if len(open_) > 15:
            print(f"    ... und {len(open_) - 15} weitere")
    else:
        print("")
        print("  alle Segmente aktuell.")
    for label, path in (("Bild", OUTFILE), ("Master", FINAL)):
        if path.is_file():
            age = (datetime.datetime.now().timestamp() - path.stat().st_mtime) / 60
            print(f"  {label:10s} {duration(path):7.2f}s  {path.stat().st_size / 1048576:6.0f} MiB"
                  f"  vor {age:.0f} min")
        else:
            print(f"  {label:10s} noch nicht gebaut")
    return not open_


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
    ap.add_argument("command", choices=["doctor", "render", "final", "all", "status"])
    ap.add_argument("--only", default=None)
    a = ap.parse_args()
    if a.command == "status":
        sys.exit(0 if cmd_status() else 1)
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
