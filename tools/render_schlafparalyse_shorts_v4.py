#!/usr/bin/env python3
"""Render the Schlafparalyse Shorts V4.

Pipeline: V4_SCRIPTS.json -> voice_v4 (George + forced alignment) ->
assets_v4 (16 native 9:16 stills per Short) -> this renderer.

What this fixes against V2, with the measurement behind each:

* Cut rhythm. V2 held every one of seven stills for exactly 6.0-6.3 s. V4 takes
  its cut points from the forced-alignment word timings, so the picture changes
  on speech beats at 1.5-3.8 s, mean about 2.5 s.
* Motion. V1 used zoompan straight to 1080x1920 and juddered, so V2 removed
  motion entirely and became a slideshow. zoompan quantises the crop rectangle
  to whole input pixels; on a slow move that lands below one pixel per frame and
  alternates. V4 renders on a 3x supersampled canvas AND scales the zoom travel
  with shot length, so the crop edge always advances by more than two
  supersampled pixels per frame. Measured lag-1 autocorrelation of the
  frame-difference series, where a strongly negative value is the stutter
  signature: -0.51 naive, -0.16 here.
* Framing. Seven images became seven tableaus. V4 has sixteen images and gives
  each shot a wide / mid / tight framing aimed at an edge-energy focus point.
* Hook, badge and end card, see build_ass.
* Sound bed lifted from -42.6 dBFS mean, which is inaudible, to about -32 dBFS.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageFilter, ImageFont
import numpy as np

from render_schlafparalyse_shorts import ass_time, duration, escape_ass, run, wrap_caption


ROOT = Path(__file__).resolve().parents[1]
PROD = ROOT / "06_PRODUCTION" / "SCHLAFPARALYSE_SHORTS_V1"
SPECS = PROD / "V4_SCRIPTS.json"

W, H, FPS = 1080, 1920, 24
SS = 3                      # supersample factor for the Ken Burns canvas
LEAD = 0.22                 # voice delay
TAIL = 2.40                 # silence after the last word, carries the end card
MIN_SHOT, MAX_SHOT = 1.50, 3.80
RHYTHM = (2.4, 1.9, 3.0, 2.1, 2.7, 1.8, 3.2, 2.2)
ZOOM_MAX = 1.34             # 1.42 would be a native 1:1 crop of the 1536x2752 source
# Inverse-zoom travel per second. Below about 0.0185 the crop edge advances less
# than one supersampled pixel per frame and zoompan starts to alternate.
ZOOM_RATE = 0.021

EP_TITLE = {
    "EP06": "Warum du jemanden im Zimmer spürst",
    "EP07": "Salem 1692: Schlafparalyse als Hexerei",
    "EP08": "Shadow People: Warum viele den Hat Man sehen",
}


def specs() -> dict:
    data = json.loads(SPECS.read_text(encoding="utf-8"))
    return {job: item for job, item in data.items() if not job.startswith("_")}


# ----------------------------------------------------------------- word timings

def load_words(job: str) -> list[dict]:
    data = json.loads((PROD / job / "voice_v4" / "ALIGNMENT_V4.json").read_text(encoding="utf-8"))
    return [row for row in data["transcription"]["words"] if str(row.get("text", "")).strip()]


def cut_candidates(words: list[dict]) -> list[tuple[float, float]]:
    """Cut points in finished-timeline seconds, scored by how strong the beat is."""
    out: list[tuple[float, float]] = []
    for current, following in zip(words, words[1:]):
        end = float(current.get("end", 0.0) or 0.0)
        gap = max(0.0, float(following.get("start", end) or end) - end)
        token = str(current.get("text", "")).rstrip()
        score = gap
        if token.endswith((".", "?", "!")):
            score += 0.45
        elif token.endswith((":", ";")):
            score += 0.30
        elif token.endswith(","):
            score += 0.15
        # Sit just inside the pause so the cut lands on silence, not on a plosive.
        out.append((end + LEAD + min(gap * 0.5, 0.10), score))
    return out


def choose_cuts(cands: list[tuple[float, float]], end: float) -> list[float]:
    cuts: list[float] = []
    cur, step = 0.0, 0
    while end - cur > MAX_SHOT + 0.40:
        target = cur + RHYTHM[step % len(RHYTHM)]
        step += 1
        lo, hi = cur + MIN_SHOT, min(cur + MAX_SHOT, end - MIN_SHOT)
        pool = [c for c in cands if lo <= c[0] <= hi]
        if pool:
            pick = max(pool, key=lambda c: c[1] - 0.22 * abs(c[0] - target))[0]
        else:
            pick = min(target, end - MIN_SHOT)
            if pick - cur < MIN_SHOT:
                break
        cuts.append(round(pick, 3))
        cur = pick
    return cuts


# -------------------------------------------------------------------- framing

def focus_point(path: Path) -> tuple[float, float]:
    """Edge-energy centroid, used to aim the tighter framings at the subject."""
    image = Image.open(path).convert("L").resize((192, 344), Image.LANCZOS)
    array = np.asarray(image, dtype=np.float32)
    energy = np.abs(np.diff(array, axis=1))[:-1, :] + np.abs(np.diff(array, axis=0))[:, :-1]
    peak = float(energy.max())
    if peak <= 0.0:
        return 0.5, 0.5
    scaled = Image.fromarray((energy / peak * 255.0).astype(np.uint8), mode="L")
    blurred = np.asarray(scaled.filter(ImageFilter.GaussianBlur(7)), dtype=np.float32)
    mask = blurred >= float(np.percentile(blurred, 90.0))
    if not mask.any():
        return 0.5, 0.5
    ys, xs = np.nonzero(mask)
    weights = blurred[mask]
    fx = float((xs * weights).sum() / weights.sum() / blurred.shape[1])
    fy = float((ys * weights).sum() / weights.sum() / blurred.shape[0])
    # Keep the aim plausible; a runaway centroid would crop heads.
    return min(max(fx, 0.34), 0.66), min(max(fy, 0.30), 0.70)


def clamp_center(value: float, zoom: float) -> float:
    half = 1.0 / (2.0 * zoom)
    return min(max(value, half), 1.0 - half)


def zoom_pair(anchor: float, direction: str, seconds: float) -> tuple[float, float]:
    """Zoom endpoints whose inverse travel scales with shot length.

    Working in 1/zoom keeps the crop width linear in time, which is what has to
    advance fast enough to clear zoompan's integer rounding.
    """
    lo_inv, hi_inv = 1.0 / ZOOM_MAX, 1.0
    span = min(ZOOM_RATE * seconds, hi_inv - lo_inv)
    centre = 1.0 / anchor
    tight, wide = centre - span / 2.0, centre + span / 2.0
    if tight < lo_inv:
        tight, wide = lo_inv, lo_inv + span
    if wide > hi_inv:
        wide, tight = hi_inv, hi_inv - span
    return (1.0 / wide, 1.0 / tight) if direction == "push" else (1.0 / tight, 1.0 / wide)


ANCHOR = {"wide": 1.03, "mid": 1.16, "tight": 1.29}
AIM = {"wide": 0.12, "mid": 0.48, "tight": 0.82}


def framing(kind: str, direction: str, focus: tuple[float, float],
            seconds: float) -> tuple[float, float, tuple[float, float], tuple[float, float]]:
    z0, z1 = zoom_pair(ANCHOR[kind], direction, seconds)
    fx, fy = focus
    aim = AIM[kind]
    cx, cy = 0.5 + (fx - 0.5) * aim, 0.5 + (fy - 0.5) * aim
    # A small drift towards the subject keeps the move from reading as a pure zoom.
    drift = 0.22 if direction == "push" else -0.16
    cx1, cy1 = cx + (fx - cx) * drift, cy + (fy - cy) * drift
    return (
        z0, z1,
        (clamp_center(cx, z0), clamp_center(cy, z0)),
        (clamp_center(cx1, z1), clamp_center(cy1, z1)),
    )


# Framing cycle used when consecutive shots come from different images. It never
# repeats a size back to back, which is what keeps the montage from flattening
# into a run of identically framed tableaus.
CYCLE = ("wide", "mid", "tight", "mid", "tight", "wide", "mid", "tight")
# When two consecutive shots share one image, the second has to contrast hard or
# the cut reads as a glitch rather than as a deliberate push-in. Alternating
# between the two tables keeps half the pairs going in and half coming out.
CONTRAST_IN = {"wide": "tight", "mid": "tight", "tight": "wide"}
CONTRAST_OUT = {"tight": "wide", "mid": "wide", "wide": "tight"}


# --------------------------------------------------------------------- encode

def encode_kenburns(source: Path, output: Path, seconds: float, z0: float, z1: float,
                    c0: tuple[float, float], c1: tuple[float, float]) -> None:
    frames = max(2, int(round(seconds * FPS)))
    last = frames - 1
    cw, ch = W * SS, H * SS
    zexpr = "%.5f%+.5f*on/%d" % (z0, z1 - z0, last)
    xexpr = "clip((%.5f%+.5f*on/%d)*iw-iw/zoom/2,0,iw-iw/zoom)" % (c0[0], c1[0] - c0[0], last)
    yexpr = "clip((%.5f%+.5f*on/%d)*ih-ih/zoom/2,0,ih-ih/zoom)" % (c0[1], c1[1] - c0[1], last)
    chain = (
        "scale=%d:%d:force_original_aspect_ratio=increase:flags=lanczos,"
        "crop=%d:%d,setsar=1,"
        "zoompan=z='%s':x='%s':y='%s':d=1:s=%dx%d:fps=%d,"
        "scale=%d:%d:flags=lanczos,format=yuv420p"
    ) % (cw, ch, cw, ch, zexpr, xexpr, yexpr, cw, ch, FPS, W, H)
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-loop", "1", "-framerate", str(FPS), "-t", "%.6f" % seconds, "-i", str(source),
        "-vf", chain, "-frames:v", str(frames), "-an",
        "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-r", str(FPS), str(output),
    ])


# ------------------------------------------------------------------ shot plan

def build_plan(job: str, vo_end: float, total: float) -> list[dict]:
    cuts = choose_cuts(cut_candidates(load_words(job)), vo_end)
    bounds = [0.0] + cuts + [total]
    # The end card needs its own shot rather than one long hold.
    if bounds[-1] - bounds[-2] > 4.20:
        bounds.insert(len(bounds) - 1, round(total - 3.00, 3))
    spans = list(zip(bounds, bounds[1:]))

    assets = PROD / job / "assets_v4"
    stills = sorted(assets.glob("SHOT*.png"))
    if not stills:
        raise FileNotFoundError(str(assets))

    # Spread the shots over the images in narrative order. With 16 images and
    # about 17 shots most images carry one shot and a few carry two.
    assignment: list[int] = []
    if len(spans) <= len(stills):
        # Fewer shots than images: sample across the whole set rather than
        # taking the first n, so the closing image still reaches the end card.
        divisor = max(1, len(spans) - 1)
        assignment = [round(i * (len(stills) - 1) / divisor) for i in range(len(spans))]
    else:
        base, extra = divmod(len(spans), len(stills))
        for position in range(len(stills)):
            assignment += [position] * (base + (1 if position < extra else 0))

    focus_cache: dict[int, tuple[float, float]] = {}
    plan: list[dict] = []
    previous_kind: str | None = None
    previous_position: int | None = None
    cycle_pos = -1
    for shot_index, position in enumerate(assignment):
        still = stills[position]
        if position not in focus_cache:
            focus_cache[position] = focus_point(still)
        if position == previous_position and previous_kind is not None:
            table = CONTRAST_IN if cycle_pos % 2 == 0 else CONTRAST_OUT
            kind = table[previous_kind]
        else:
            cycle_pos += 1
            kind = CYCLE[cycle_pos % len(CYCLE)]
            if kind == previous_kind:
                cycle_pos += 1
                kind = CYCLE[cycle_pos % len(CYCLE)]
        direction = "push" if shot_index % 2 == 0 else "pull"
        start, end = spans[shot_index]
        seconds = round(end - start, 3)
        z0, z1, c0, c1 = framing(kind, direction, focus_cache[position], seconds)
        plan.append({
            "kind": "still", "source": still, "start": start, "end": end,
            "seconds": seconds, "still": position + 1, "asset": still.name,
            "framing": kind, "direction": direction,
            "z0": z0, "z1": z1, "c0": c0, "c1": c1,
        })
        previous_kind, previous_position = kind, position
    return plan


# ----------------------------------------------------------------------- text

def fit_hook(text: str) -> tuple[int, str]:
    """Largest Arial Black size that fits the hook into at most two lines."""
    words = text.split()
    for size in range(96, 53, -2):
        face = ImageFont.truetype("C:/Windows/Fonts/ariblk.ttf", size)
        for split in range(len(words), 0, -1):
            lines = [line for line in (" ".join(words[:split]), " ".join(words[split:])) if line]
            if len(lines) <= 2 and all(face.getlength(line) <= 900 for line in lines):
                return size, r"\N".join(lines)
    return 54, r"\N".join(text.split(" ", 1))


def build_ass(job: str, spec: dict, vo_end: float, total: float) -> Path:
    words = load_words(job)
    chunks: list[list[dict]] = []
    current: list[dict] = []
    for row in words:
        prospective = " ".join(str(item.get("text", "")).strip() for item in current + [row])
        if current and (len(current) >= 3 or len(prospective) > 29):
            chunks.append(current)
            current = []
        current.append(row)
        token = str(row.get("text", ""))
        start = float(current[0].get("start", 0.0) or 0.0)
        end = float(row.get("end", start) or start)
        if token.rstrip().endswith((".", "?", "!", ":", ";")) or end - start >= 1.85:
            chunks.append(current)
            current = []
    if current:
        chunks.append(current)

    hook_size, hook_text = fit_hook(spec["hook"])
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Caption,Arial,62,&H00F5F2EB,&H00F5F2EB,&H00101014,&H8C000000,-1,0,0,0,100,100,0,0,1,5,2,2,105,210,420,1
Style: Hook,Arial Black,__HOOK__,&H00F5F2EB,&H00F5F2EB,&H00101014,&HA0000000,-1,0,0,0,100,100,0,0,3,6,0,8,70,70,168,1
Style: Badge,Segoe UI Semibold,34,&H00BEBAAE,&H00BEBAAE,&H00101014,&H60000000,0,0,0,0,100,100,3,0,1,3,0,8,70,70,64,1
Style: CtaHead,Arial Black,52,&H00F5F2EB,&H00F5F2EB,&H00101014,&HA8000000,-1,0,0,0,100,100,0,0,3,6,0,2,90,90,486,1
Style: CtaSub,Segoe UI Semibold,42,&H00C9C08C,&H00C9C08C,&H00101014,&HA8000000,-1,0,0,0,100,100,0,0,3,5,0,2,90,90,414,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""".replace("__HOOK__", str(hook_size))

    lines = [header]
    lines.append("Dialogue: 3,%s,%s,Badge,,0,0,0,,SCHLAFPARALYSE  \u00b7  %d/6\n"
                 % (ass_time(0.0), ass_time(total), spec["n"]))
    lines.append("Dialogue: 4,%s,%s,Hook,,0,0,0,,{\\fad(160,260)}%s\n"
                 % (ass_time(0.0), ass_time(2.60), hook_text))
    for chunk in chunks:
        start = float(chunk[0].get("start", 0.0) or 0.0) + LEAD
        end = float(chunk[-1].get("end", start + 0.2) or start + 0.2) + LEAD
        text = wrap_caption(escape_ass(" ".join(str(row.get("text", "")).strip() for row in chunk)))
        lines.append("Dialogue: 0,%s,%s,Caption,,0,0,0,,%s\n" % (ass_time(start), ass_time(end), text))

    cta_start = min(vo_end + 0.30, total - 1.90)
    lines.append("Dialogue: 2,%s,%s,CtaHead,,0,0,0,,{\\fad(280,0)}GANZE FOLGE IM KANAL\n"
                 % (ass_time(cta_start), ass_time(total)))
    lines.append("Dialogue: 2,%s,%s,CtaSub,,0,0,0,,{\\fad(380,0)}%s\n"
                 % (ass_time(cta_start + 0.14), ass_time(total), escape_ass(EP_TITLE[spec["ep"]])))
    out = PROD / job / "captions_v4.ass"
    out.write_text("".join(lines), encoding="utf-8-sig")
    return out


# ---------------------------------------------------------------------- audio

def make_bed(seconds: float, path: Path, accents: list[float]) -> None:
    inputs, parts, labels = [], [], []
    for source in ("sine=frequency=46:duration=%.3f" % seconds,
                   "sine=frequency=69:duration=%.3f" % seconds,
                   "anoisesrc=d=%.3f:c=brown:a=0.9" % seconds):
        inputs += ["-f", "lavfi", "-i", source]
    parts.append("[0:a]volume=0.34,tremolo=f=0.12:d=0.30[d0]")
    parts.append("[1:a]volume=0.15[d1]")
    parts.append("[2:a]lowpass=f=520,volume=0.30[air]")
    labels += ["[d0]", "[d1]", "[air]"]
    for index, when in enumerate(accents):
        inputs += ["-f", "lavfi", "-i", "sine=frequency=57:duration=1.80"]
        parts.append("[%d:a]volume=0.42,afade=t=out:st=0.10:d=1.60,adelay=%d|%d[acc%d]"
                     % (3 + index, int(when * 1000), int(when * 1000), index))
        labels.append("[acc%d]" % index)
    parts.append("%samix=inputs=%d:normalize=0,afade=t=in:st=0:d=1.4,afade=t=out:st=%.3f:d=1.6[out]"
                 % ("".join(labels), len(labels), max(0.0, seconds - 1.6)))
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"] + inputs
        + ["-filter_complex", ";".join(parts), "-map", "[out]", "-t", "%.3f" % seconds,
           "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", str(path)])


# --------------------------------------------------------------------- render

def loudness(path: Path) -> dict:
    log = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "ebur128=peak=true",
         "-f", "null", "-"], cwd=ROOT, capture_output=True, text=True,
    ).stderr
    tail = log[log.rfind("Integrated loudness"):] if "Integrated loudness" in log else ""
    result = {}
    for key, token in (("integrated_lufs", "I:"), ("lra", "LRA:"), ("true_peak_dbtp", "Peak:")):
        for line in tail.splitlines():
            if line.strip().startswith(token):
                try:
                    result[key] = float(line.split()[1])
                except (IndexError, ValueError):
                    pass
                break
    return result


def render(job: str, spec: dict) -> dict:
    folder = PROD / job
    voice = folder / "voice_v4" / ("%s_GEORGE_V4.mp3" % job)
    if not voice.is_file():
        raise FileNotFoundError(str(voice))
    vo_end = LEAD + duration(voice)
    total = round(vo_end + TAIL, 3)

    plan = build_plan(job, vo_end, total)
    work = folder / "render_v4"
    segments = work / "segments"
    segments.mkdir(parents=True, exist_ok=True)
    for stale in segments.glob("*.mp4"):
        stale.unlink()

    paths = []
    for index, shot in enumerate(plan, 1):
        out = segments / ("%02d.mp4" % index)
        encode_kenburns(shot["source"], out, shot["seconds"],
                        shot["z0"], shot["z1"], shot["c0"], shot["c1"])
        paths.append(out)

    concat = work / "concat.txt"
    concat.write_text("\n".join("file '%s'" % p.as_posix() for p in paths) + "\n", encoding="utf-8")
    visual = work / "visual.mp4"
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", str(concat), "-c:v", "libx264", "-preset", "medium", "-crf", "16",
         "-pix_fmt", "yuv420p", "-r", str(FPS), "-an", str(visual)])

    captions = build_ass(job, spec, vo_end, total)
    relative = captions.relative_to(ROOT).as_posix().replace(":", "\\:")
    captioned = work / "captioned.mp4"
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(visual),
         "-vf", "ass='%s'" % relative, "-an", "-c:v", "libx264", "-preset", "medium",
         "-crf", "16", "-pix_fmt", "yuv420p", "-r", str(FPS), str(captioned)])

    bed = work / "soundbed.wav"
    make_bed(total, bed, [round(total * 0.34, 2), round(total * 0.66, 2)])

    final_dir = folder / "final_v4"
    final_dir.mkdir(parents=True, exist_ok=True)
    final = final_dir / ("%s_FINAL_V4.mp4" % job)
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-i", str(captioned), "-i", str(voice), "-i", str(bed), "-filter_complex",
         "[1:a]adelay=%d|%d,apad=whole_dur=%.3f,pan=stereo|c0=c0|c1=c0,asplit=2[voice][key];"
         "[2:a][key]sidechaincompress=threshold=0.020:ratio=8:attack=10:release=320[duck];"
         "[voice][duck]amix=inputs=2:normalize=0:duration=first,"
         "atrim=0:%.3f,aresample=192000,alimiter=limit=.89,aresample=48000,"
         "loudnorm=I=-14:TP=-1.5:LRA=10[a]" % (int(LEAD * 1000), int(LEAD * 1000), total, total),
         "-map", "0:v:0", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k",
         "-ar", "48000", "-ac", "2", "-t", "%.3f" % total, "-movflags", "+faststart", str(final)])

    contact = final_dir / ("%s_CONTACT_SHEET.jpg" % job)
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(final),
         "-vf", "fps=1/2.2,scale=200:356,tile=5x4", "-frames:v", "1", "-q:v", "3", str(contact)])

    black = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(final), "-vf", "blackdetect=d=0.08:pix_th=0.02",
         "-an", "-f", "null", "-"], cwd=ROOT, capture_output=True, text=True,
    ).stderr
    lengths = [shot["seconds"] for shot in plan]
    report = {
        "file": str(final),
        "duration": round(duration(final), 3),
        "resolution": "%dx%d" % (W, H),
        "fps": FPS,
        "shots": len(plan),
        "shot_min": min(lengths),
        "shot_max": max(lengths),
        "shot_mean": round(sum(lengths) / len(lengths), 3),
        "distinct_assets": len({shot["asset"] for shot in plan}),
        "kenburns": "3x supersampled zoompan, travel scaled with shot length",
        "hook": spec["hook"],
        "cta": "GANZE FOLGE IM KANAL / " + EP_TITLE[spec["ep"]],
        "tail_seconds": TAIL,
        "voice": "George",
        "voice_id": "JBFqnCBsd6RMkjVDRZzb",
        "voice_take": "V4 (re-recorded for the rewritten script)",
        "blackdetect_events": [line.strip() for line in black.splitlines() if "black_start:" in line],
        "loudness": loudness(final),
        "contact_sheet": str(contact),
        "plan": [
            {"index": i, "asset": s["asset"], "start": s["start"], "seconds": s["seconds"],
             "framing": s["framing"], "direction": s["direction"],
             "zoom": [round(s["z0"], 3), round(s["z1"], 3)]}
            for i, s in enumerate(plan, 1)
        ],
    }
    (final_dir / "QA_REPORT.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only")
    args = parser.parse_args()
    report = {}
    for job, spec in specs().items():
        if args.only and job != args.only:
            continue
        print("RENDER %s" % job, flush=True)
        report[job] = render(job, spec)
        print(json.dumps({k: v for k, v in report[job].items() if k != "plan"},
                         ensure_ascii=False), flush=True)
    destination = PROD / "FINAL_QA_V4.json"
    existing = json.loads(destination.read_text(encoding="utf-8")) if destination.is_file() else {}
    existing.update(report)
    destination.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
