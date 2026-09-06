#!/usr/bin/env python3
"""Render the four EP13 teaser shorts at 1080x1920.

Motion comes from the shared engine in tools/smooth_still_motion.py, told to
supersample vertically so the zoompan window shares the delivery aspect. The
episode's own renderer learned the rest of this the hard way and the same rules
apply here: a linear ramp is not used, amplitude scales with the shot length,
clips are never looped inside a shot, and documents hold still.

Each short binds its fourteen beats to a state list. English and German share the
picture, because both scripts were written to the same beats; the narration and
the end card differ.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import pathlib
import re
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from smooth_still_motion import ENGINE_VERSION, eased_zoompan_filter  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
STILLS = ROOT / "tmp" / "imagegen" / "ep13_short_vertical"
PLATES = ROOT / "tmp" / "imagegen" / "ep13_short_plates"
CARDS = ROOT / "tmp" / "imagegen" / "ep13_short_cards"
CLIPS = ROOT / "tmp" / "video" / "ep13_veo"
WORK = ROOT / "tmp" / "render" / "ep13_shorts"

W, H, FPS = 1080, 1920, 30
SUPERSAMPLE = (4320, 7680)
ZOOM_PER_SECOND = 0.017 / 4.5
ZOOM_MIN, ZOOM_MAX = 0.012, 0.026
FADE, BG, CRF = 0.14, "#0B0A0C", 18
WORKERS = 3

# A short is watched with a thumb on the screen; a document that has to be read
# holds still, and so does anything under a third of a second.
LOCKED = {"OR07_NEWSPAPER_1917", "OR04_CHILDREN_1917"}
MIN_MOVE_SECONDS = 0.35

# A short is watched at speed. A beat that holds one picture for more than this
# reads as a stall, so it is split in two and the second half gets its own frame
# from the teaser's reserve list.
SPLIT_OVER = 4.6

# beat -> state, fourteen each. The same list serves both languages.
TEASER_A = [
    "OR01_CROWN_BULLET", "SH03_SQUARE_CROWD_1981", "SH04_HOSPITAL_WINDOW",
    "SHORT_CLIP02_ENVELOPE_LIFTED", "SB08_ENVELOPE_IN_DARK", "OR02_JOHN_XXIII",
    "SH07_HAND_WRITING_1944", "SH06_TWO_CHAIRS_EMPTY", "SH09_MAN_ALONE_THINKING",
    "SB09_EMPTY_CHAIR_QUESTION", "SH10_FIGURE_IN_WHITE_TALL", "SH12_PILGRIM_CANDLES_TALL",
    "SHORT_CLIP01_CROWN_PUSH", "CARD",
]
RESERVE_A = ["SH02_BULLET_MACRO", "SH05_ENVELOPE_UPRIGHT", "SH08_ARCHIVE_SHAFT",
             "OR04_CHILDREN_1917", "SH11_CROWN_EMBER_VISION", "OR06_CROWNED_STATUE",
             "SH01_CROWN_TALL", "SB03_CALENDAR_YEARS"]

TEASER_B = [
    "SHORT_CLIP03_DOOR_CLOSING", "SB02_WOMAN_AT_WINDOW", "SB03_CALENDAR_YEARS",
    "SB04_TELEPHONE_UNANSWERED", "OR02_JOHN_XXIII", "SB05_LOCKED_DOOR_CORRIDOR",
    "SB07_CROWD_WAITING_TALL", "SB06_NEWSPAPERS_PILED", "SHORT_CLIP04_DUST_IN_SHAFT",
    "OR07_NEWSPAPER_1917", "SH03_SQUARE_CROWD_1981", "SB09_EMPTY_CHAIR_QUESTION",
    "OR01_CROWN_BULLET", "CARD",
]

RESERVE_B = ["SB08_ENVELOPE_IN_DARK", "SH08_ARCHIVE_SHAFT", "OR04_CHILDREN_1917",
             "SH05_ENVELOPE_UPRIGHT", "SH12_PILGRIM_CANDLES_TALL", "SH02_BULLET_MACRO",
             "OR06_CROWNED_STATUE", "SH04_HOSPITAL_WINDOW"]

SHORTS = {
    "en1": {"root": ROOT / "07_ENGLISH_PRODUCTION" / "EP13_VATICAN_01_SHORTS" / "S01_BULLET_IN_CROWN",
            "stem": "EP13_S01_EN", "states": TEASER_A, "reserve": RESERVE_A, "card": "EN_S01"},
    "en2": {"root": ROOT / "07_ENGLISH_PRODUCTION" / "EP13_VATICAN_01_SHORTS" / "S02_THE_SILENCE",
            "stem": "EP13_S02_EN", "states": TEASER_B, "reserve": RESERVE_B, "card": "EN_S02"},
    "de1": {"root": ROOT / "08_GERMAN_PRODUCTION" / "EP13_VATIKAN_01_SHORTS" / "S01_KUGEL_IN_KRONE",
            "stem": "EP13_S01_DE", "states": TEASER_A, "reserve": RESERVE_A, "card": "DE_S01"},
    "de2": {"root": ROOT / "08_GERMAN_PRODUCTION" / "EP13_VATIKAN_01_SHORTS" / "S02_DAS_SCHWEIGEN",
            "stem": "EP13_S02_DE", "states": TEASER_B, "reserve": RESERVE_B, "card": "DE_S02"},
}


def run(args, timeout=None):
    p = subprocess.run(args, text=True, capture_output=True, timeout=timeout)
    if p.returncode:
        raise RuntimeError((p.stderr or p.stdout)[-3000:])
    return p.stdout


def probe(path, entries):
    return run(["ffprobe", "-v", "error", "-show_entries", entries,
                "-of", "csv=p=0", str(path)]).strip()


def resolve(state, card_key):
    if state == "CARD":
        return CARDS / f"EP13_SHORTCARD_{card_key}.png"
    for folder, suffix in ((CLIPS, ".mp4"), (STILLS, ".png"), (PLATES, ".png")):
        p = folder / (state + suffix)
        if p.is_file():
            return p
        p = folder / ("EP13_" + state + suffix)
        if p.is_file():
            return p
    return None


def beats(cfg):
    """Word-range beats from the forced alignment, one per script paragraph."""
    align = json.loads((cfg["root"] / "02_VOICE" / f"{cfg['stem']}_ALIGNMENT.json")
                       .read_text(encoding="utf-8"))
    words = [w for w in align["words"] if w["text"].strip()]
    script = next((cfg["root"] / "01_SCRIPT").glob("VOICE_SCRIPT_*.txt"))
    blocks = [b.strip() for b in re.split(r"\n\s*\n", script.read_text(encoding="utf-8")) if b.strip()]
    out, cursor = [], 0
    for i, b in enumerate(blocks, 1):
        n = len(re.findall(r"[\w']+", b.casefold(), re.UNICODE))
        seg = words[cursor:cursor + n]
        if not seg:
            break
        out.append({"beat": i, "start": round(seg[0]["start"], 3),
                    "end": round(seg[-1]["end"], 3), "text": b.replace("\n", " ")})
        cursor += n
    voice = cfg["root"] / "02_VOICE" / f"{cfg['stem']}_VO_MASTER.wav"
    total = float(probe(voice, "format=duration"))
    for k in range(len(out) - 1):
        out[k]["end"] = out[k + 1]["start"]
    out[-1]["end"] = total
    for s in out:
        s["dur"] = round(s["end"] - s["start"], 3)
    return out


def fades(dur, first, last):
    fi = f",fade=t=in:st=0:d={FADE:.3f}:color={BG}" if first else ""
    fo = f",fade=t=out:st={max(0, dur - FADE):.3f}:d={FADE:.3f}:color={BG}" if last else ""
    return fi + fo


def filter_for(src, state, dur, first, last):
    if src.suffix.lower() == ".mp4":
        srcdur = float(probe(src, "format=duration"))
        fit = ""
        if dur > srcdur * 1.02:
            ratio = min(1.35, dur / srcdur)
            fit = f",setpts={ratio:.6f}*PTS"
            if dur > srcdur * 1.35:
                fit += f",tpad=stop_mode=clone:stop_duration={dur - srcdur * 1.35:.3f}"
        return (f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"
                f"{fit},fps={FPS},format=yuv420p" + fades(dur, first, last))
    if state == "CARD" or state in LOCKED or dur < MIN_MOVE_SECONDS:
        return (f"scale={W}:{H}:force_original_aspect_ratio=decrease:flags=lanczos,"
                f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black,fps={FPS},"
                f"trim=duration={dur:.6f},setpts=PTS-STARTPTS,format=yuv420p"
                + fades(dur, first, last))
    amount = min(ZOOM_MAX, max(ZOOM_MIN, ZOOM_PER_SECOND * dur))
    return eased_zoompan_filter(duration=dur, fps=FPS, width=W, height=H,
                                zoom_amount=amount, background="black",
                                supersample=SUPERSAMPLE) + fades(dur, first, last)


def render_one(item):
    key, i, shot, state, src, total = item
    segs = WORK / key / "segments"
    segs.mkdir(parents=True, exist_ok=True)
    out = segs / f"{i + 1:03d}_{state[:40]}.mp4"
    vf = filter_for(src, state, shot["dur"], i == 0, i == total - 1)
    args = ["ffmpeg", "-y", "-loglevel", "error"]
    args += ["-i", str(src), "-an"] if src.suffix.lower() == ".mp4" else ["-loop", "1", "-i", str(src)]
    args += ["-vf", vf, "-c:v", "libx264", "-preset", "medium", "-crf", str(CRF),
             "-pix_fmt", "yuv420p", "-frames:v", str(max(1, round(shot["dur"] * FPS))), str(out)]
    run(args, timeout=1800)
    return key, out, state, shot["dur"]


def build(key):
    cfg = SHORTS[key]
    shots = beats(cfg)
    states = cfg["states"]
    if len(shots) != len(states):
        sys.exit(f"{key}: {len(shots)} beats but {len(states)} states")
    # split the long beats before anything is rendered
    plan, spare = [], list(cfg["reserve"])
    for shot, state in zip(shots, states):
        if shot["dur"] > SPLIT_OVER and state != "CARD" and spare:
            half = round(shot["dur"] / 2, 3)
            extra = spare.pop(0)
            plan.append(({**shot, "dur": half, "end": shot["start"] + half}, state))
            plan.append(({"beat": shot["beat"], "start": shot["start"] + half,
                          "end": shot["end"], "dur": round(shot["dur"] - half, 3),
                          "text": shot["text"]}, extra))
        else:
            plan.append((shot, state))
    jobs = []
    for i, (shot, state) in enumerate(plan):
        src = resolve(state, cfg["card"])
        if src is None:
            sys.exit(f"{key}: cannot resolve {state}")
        jobs.append((key, i, shot, state, src, len(plan)))
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as pool:
        for _, out, state, dur in pool.map(render_one, jobs):
            print(f"  {key}  {dur:5.2f}s  {state[:40]}", flush=True)
    segs = sorted((WORK / key / "segments").glob("*.mp4"),
                  key=lambda p: int(p.name.split("_")[0]))
    lst = WORK / key / "concat.txt"
    lst.write_text("\n".join(f"file '{p.as_posix()}'" for p in segs) + "\n", encoding="utf-8")
    picture = WORK / key / f"{cfg['stem']}_PICTURE.mp4"
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", str(lst), "-c", "copy", str(picture)], timeout=1800)
    print(f"  {key}  picture {probe(picture, 'format=duration')}s")
    return picture


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--which", default="en1,en2,de1,de2")
    a = ap.parse_args()
    print(f"engine v{ENGINE_VERSION}, {W}x{H}, supersample {SUPERSAMPLE[0]}x{SUPERSAMPLE[1]}")
    for key in [k.strip() for k in a.which.split(",") if k.strip()]:
        build(key)


if __name__ == "__main__":
    main()
