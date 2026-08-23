#!/usr/bin/env python3
"""Produce the complete 12-minute EP02 Gateway longform master."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import uuid
from urllib.error import HTTPError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent.parent
PROD = ROOT / "06_PRODUCTION" / "EP02_GATEWAY"
VOICE_TEXT = PROD / "04_VOICE_SCRIPT_CLEAN.txt"
SHOTLIST = PROD / "05_SHOTLIST_LONGFORM.csv"
VOICE_MASTER = PROD / "voice" / "master" / "EP02_GATEWAY_VO_MASTER_48k24_mono.wav"
ALIGNMENT = PROD / "voice" / "alignment" / "EP02_GATEWAY_alignment.json"
TIMELINE = PROD / "timeline" / "EP02_GATEWAY_timeline.json"
SRT = PROD / "captions" / "EP02_GATEWAY_de.srt"
AUDIO = PROD / "audio"
SEGMENTS = PROD / "render" / "segments"
FINAL = PROD / "render" / "final"
FPS = 30
TOTAL = 720.0


def run(args: list[str], *, capture: bool = False) -> str:
    result = subprocess.run(args, text=True, capture_output=capture)
    if result.returncode:
        raise RuntimeError((result.stderr or result.stdout or "command failed")[-7000:])
    return (result.stdout or "") + (result.stderr or "")


def duration(path: Path) -> float:
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                      "-of", "csv=p=0", str(path)], capture=True).strip())


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_time(value: str) -> float:
    parts = [float(x) for x in value.split(":")]
    if len(parts) == 2:
        return parts[0] * 60 + parts[1]
    return parts[0] * 3600 + parts[1] * 60 + parts[2]


def loudness(path: Path, target: float = -14.0, peak: float = -1.0, lra: float = 7.0) -> dict:
    output = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af",
                  f"loudnorm=I={target}:TP={peak}:LRA={lra}:print_format=json",
                  "-f", "null", "-"], capture=True)
    matches = re.findall(r'\{\s*"input_i".*?\}', output, re.S)
    return json.loads(matches[-1])


def normalize_audio(source: Path, target: Path, integrated: float, peak: float, channels: int) -> dict:
    stats = loudness(source, integrated, peak)
    filt = (f"loudnorm=I={integrated}:TP={peak}:LRA=7:"
            f"measured_I={stats['input_i']}:measured_TP={stats['input_tp']}:"
            f"measured_LRA={stats['input_lra']}:measured_thresh={stats['input_thresh']}:"
            f"offset={stats['target_offset']}:linear=true")
    target.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(source),
         "-af", filt, "-ac", str(channels), "-ar", "48000", "-c:a", "pcm_s24le", str(target)])
    return loudness(target, integrated, peak)


def master_voice() -> None:
    stems = json.loads((PROD / "voice" / "stems.json").read_text(encoding="utf-8"))
    raw_dir = PROD / "voice" / "raw_stems"
    master_dir = PROD / "voice" / "master"
    stem_dir = master_dir / "stems"
    master_dir.mkdir(parents=True, exist_ok=True)
    stem_dir.mkdir(parents=True, exist_ok=True)
    concat_lines: list[str] = []
    report: list[dict] = []
    for index, stem in enumerate(stems):
        source = raw_dir / f"{stem['id']}.mp3"
        if not source.is_file():
            raise FileNotFoundError(source)
        normalized = stem_dir / f"{stem['id']}_normalized.wav"
        normalize_audio(source, normalized, -18.0, -2.0, 1)
        current = duration(normalized)
        target_window = float(stem["target_duration"])
        pre = 0.35 if index else 0.55
        desired_speech = target_window - pre - 1.15
        factor = current / desired_speech
        # Keep delivery natural. Only intervene when the stem would not fit or leaves a large dead zone.
        factor = min(1.16, max(0.88, factor))
        fitted = stem_dir / f"{stem['id']}.wav"
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(normalized),
             "-af", f"atempo={factor:.6f}", "-ar", "48000", "-ac", "1", "-c:a", "pcm_s24le", str(fitted)])
        fitted_duration = duration(fitted)
        if fitted_duration > target_window - pre - 0.25:
            emergency = fitted_duration / (target_window - pre - 0.35)
            temp = fitted.with_name(fitted.stem + "_fit.wav")
            run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(fitted),
                 "-af", f"atempo={emergency:.6f}", "-ar", "48000", "-ac", "1", "-c:a", "pcm_s24le", str(temp)])
            fitted = temp
            fitted_duration = duration(fitted)
            factor *= emergency
        post = max(0.25, target_window - pre - fitted_duration)
        for kind, seconds in (("pre", pre),):
            gap = master_dir / f"{index + 1:02d}_{kind}.wav"
            run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i",
                 f"anullsrc=r=48000:cl=mono:d={seconds:.6f}", "-c:a", "pcm_s24le", str(gap)])
            concat_lines.append(f"file '{gap.as_posix()}'")
        concat_lines.append(f"file '{fitted.as_posix()}'")
        gap = master_dir / f"{index + 1:02d}_post.wav"
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i",
             f"anullsrc=r=48000:cl=mono:d={post:.6f}", "-c:a", "pcm_s24le", str(gap)])
        concat_lines.append(f"file '{gap.as_posix()}'")
        report.append({"scene": stem["scene"], "source_seconds": round(current, 3),
                       "fitted_seconds": round(fitted_duration, 3), "atempo": round(factor, 4),
                       "pre_gap": pre, "post_gap": round(post, 3), "window": target_window})
    concat = master_dir / "concat.txt"
    concat.write_text("\n".join(concat_lines) + "\n", encoding="utf-8")
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", str(concat), "-t", f"{TOTAL:.3f}", "-c:a", "pcm_s24le", str(VOICE_MASTER)])
    payload = {"master": str(VOICE_MASTER.resolve()), "duration": round(duration(VOICE_MASTER), 3),
               "method": "scene-window fit with bounded atempo and explicit chapter pauses", "scenes": report}
    (master_dir / "stem_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def multipart(audio: Path, text: str) -> tuple[bytes, str]:
    boundary = "----GATEWAY" + uuid.uuid4().hex
    parts = [f"--{boundary}\r\n".encode(), b'Content-Disposition: form-data; name="text"\r\n\r\n',
             text.encode("utf-8"), b"\r\n", f"--{boundary}\r\n".encode(),
             f'Content-Disposition: form-data; name="file"; filename="{audio.name}"\r\n'.encode(),
             b"Content-Type: audio/wav\r\n\r\n", audio.read_bytes(), b"\r\n",
             f"--{boundary}--\r\n".encode()]
    return b"".join(parts), boundary


def align() -> None:
    sys.path.insert(0, r"C:\Users\iQPrinceps\Documents\Codex\NOESIS Channel\tools")
    from elevenlabs_cli import _load_key  # type: ignore
    text = VOICE_TEXT.read_text(encoding="utf-8").strip()
    body, boundary = multipart(VOICE_MASTER, text)
    request = Request("https://api.elevenlabs.io/v1/forced-alignment", data=body,
                      headers={"xi-api-key": _load_key(), "Content-Type": f"multipart/form-data; boundary={boundary}",
                               "Accept": "application/json"}, method="POST")
    try:
        with urlopen(request, timeout=300) as response:
            result = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise RuntimeError(f"ElevenLabs alignment HTTP {exc.code}: {exc.read().decode(errors='replace')}")
    result.update({"source_text": text, "audio": str(VOICE_MASTER.resolve()), "audio_sha256": sha256(VOICE_MASTER)})
    ALIGNMENT.parent.mkdir(parents=True, exist_ok=True)
    ALIGNMENT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Alignment: {ALIGNMENT}")


def srt_time(value: float) -> str:
    ms = int(round(value * 1000)); h, rem = divmod(ms, 3_600_000); m, rem = divmod(rem, 60_000); s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def build_srt() -> None:
    data = json.loads(ALIGNMENT.read_text(encoding="utf-8")); chars = data["characters"]; text = data["source_text"]
    spans: list[tuple[float, float, str]] = []
    # Protect periods that are not sentence boundaries while preserving indices.
    protected = text.replace("U.S.", "U§S§")
    protected = re.sub(r"(?<=\b[A-Z])\.(?=\s+[A-ZÄÖÜ])", "§", protected)
    protected = re.sub(r"\b(\d{1,2})\.(?=\s+(?:Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember))", r"\1§", protected)
    for match in re.finditer(r"[^.!?]+[.!?]+|[^.!?]+$", protected, re.S):
        original = text[match.start():match.end()]
        sentence = re.sub(r"\s+", " ", original).strip()
        if not sentence: continue
        first = next(i for i in range(match.start(), match.end()) if not text[i].isspace())
        last = next(i for i in range(match.end() - 1, match.start() - 1, -1) if not text[i].isspace())
        start, end = float(chars[first]["start"]), float(chars[last]["end"])
        words = sentence.split()
        chunks = [words] if len(words) <= 12 else [words[:len(words)//2], words[len(words)//2:]]
        cursor = start
        for chunk_index, chunk in enumerate(chunks):
            chunk_end = end if chunk_index == len(chunks) - 1 else start + (end - start) * len(chunk) / len(words)
            spans.append((cursor, chunk_end, " ".join(chunk))); cursor = chunk_end
    SRT.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    for index, (start, end, sentence) in enumerate(spans, 1):
        lines += [str(index), f"{srt_time(start)} --> {srt_time(end)}", sentence, ""]
    SRT.write_text("\n".join(lines), encoding="utf-8-sig")
    print(f"Captions: {len(spans)} -> {SRT}")


def resolve_visual(value: str) -> Path:
    normalized = value.replace("/", "\\")
    if normalized.startswith(("04_ASSETS\\", "05_GENERATED\\", "06_PRODUCTION\\")):
        path = ROOT / normalized
    else:
        path = PROD / normalized
    if path.suffix.casefold() == ".svg":
        path = PROD / "qa_renders" / f"{path.stem}.png"
    if path.suffix.casefold() == ".pdf":
        # The approved PDF's opening page is already available as a checked,
        # lossless crop in the episode reference package.
        path = PROD / "reference_package" / "GW_REPORT_PDF01_HEADER.png"
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.resolve()


def build_timeline() -> list[dict]:
    rows = list(csv.DictReader(SHOTLIST.open(encoding="utf-8-sig", newline="")))
    result = []
    for row in rows:
        start, end = parse_time(row["start"]), parse_time(row["end"])
        if end <= start: raise RuntimeError(f"Bad shot duration: {row['shot_id']}")
        result.append({**row, "start_seconds": start, "end_seconds": end, "duration": end - start,
                       "visual": str(resolve_visual(row["visual_path_or_id"]))})
    if abs(result[0]["start_seconds"]) > .001 or abs(result[-1]["end_seconds"] - TOTAL) > .001:
        raise RuntimeError("Shotlist must cover exactly 00:00-12:00")
    for left, right in zip(result, result[1:]):
        if abs(left["end_seconds"] - right["start_seconds"]) > .001:
            raise RuntimeError(f"Timeline gap/overlap: {left['shot_id']} -> {right['shot_id']}")
    TIMELINE.parent.mkdir(parents=True, exist_ok=True)
    TIMELINE.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Timeline: {len(result)} shots / {TOTAL:.0f}s -> {TIMELINE}")
    return result


def build_audio() -> None:
    AUDIO.mkdir(parents=True, exist_ok=True)
    voice = AUDIO / "EP02_voice_48k24_mono_-18LUFS.wav"
    voice_stats = normalize_audio(VOICE_MASTER, voice, -18.0, -2.0, 1)
    # Original Gateway-specific ambient: restrained stereo tone offset, low drone and filtered air.
    left = ("0.038*sin(2*PI*55*t+0.10*sin(2*PI*t/43))"
            "+0.022*sin(2*PI*82.41*t+0.06*sin(2*PI*t/67))")
    right = ("0.038*sin(2*PI*63*t+0.10*sin(2*PI*t/47))"
             "+0.022*sin(2*PI*82.41*t+0.06*sin(2*PI*t/71))")
    tonal = f"aevalsrc='{left}|{right}':s=48000:d={TOTAL}"
    noise = f"anoisesrc=color=pink:amplitude=0.028:r=48000:d={TOTAL}"
    raw = AUDIO / "EP02_original_ambient_raw.wav"; bed = AUDIO / "EP02_original_ambient_-34LUFS.wav"
    filt = ("[0:a]lowpass=f=520,aecho=0.8:0.45:1100|2300:0.045|0.018,"
            "volume='0.72+0.05*sin(2*PI*t/97)':eval=frame[t];"
            "[1:a]highpass=f=280,lowpass=f=3100,volume=0.10[n];"
            "[t][n]amix=inputs=2:weights='1 0.16':normalize=0,alimiter=limit=0.9[out]")
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i", tonal,
         "-f", "lavfi", "-i", noise, "-filter_complex", filt, "-map", "[out]", "-ac", "2", "-ar", "48000",
         "-c:a", "pcm_s24le", str(raw)])
    bed_stats = normalize_audio(raw, bed, -34.0, -4.0, 2)
    premix = AUDIO / "EP02_mix_premaster.wav"; final = AUDIO / "EP02_final_mix_48k24_stereo_-14LUFS.wav"
    mix = (f"[0:a]atrim=0:{TOTAL},pan=stereo|c0=c0|c1=c0,asplit=2[v_mix][v_sc];"
           "[1:a][v_sc]sidechaincompress=threshold=0.020:ratio=6:attack=35:release=700[d];"
           "[v_mix][d]amix=inputs=2:weights='1 1':normalize=0,afade=t=out:st=718.3:d=1.7,alimiter=limit=0.94[out]")
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(voice), "-i", str(bed),
         "-filter_complex", mix, "-map", "[out]", "-t", f"{TOTAL}", "-ac", "2", "-ar", "48000",
         "-c:a", "pcm_s24le", str(premix)])
    final_stats = normalize_audio(premix, final, -14.0, -1.0, 2)
    report = {"duration": TOTAL, "voice": str(voice.resolve()), "voice_verify": voice_stats,
              "bed": str(bed.resolve()), "bed_verify": bed_stats, "final": str(final.resolve()),
              "final_verify": final_stats, "rights": "Original procedural synthesis; no samples or third-party music."}
    (AUDIO / "audio_mix_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


def camera_filter(index: int, row: dict) -> str:
    frames = max(1, int(math.ceil(float(row["duration"]) * FPS)))
    increment = 0.000035 if row["visual_class"] == "EDITOR_GRAPHIC" else 0.000085
    action = row.get("editor_action", "").casefold()
    documentary_page = row["visual_class"] in {"ORIGINAL_DOCUMENT", "ORIGINAL_OPEN_ACCESS", "ORIGINAL_DIAGRAM"}
    keep_whole = documentary_page and any(token in action for token in (
        "full page", "full frame", "orientation", "whole page", "title and definition", "settle on page"
    ))
    direction = index % 4
    x = "iw/2-(iw/zoom/2)" if direction in (0, 2) else (f"(iw-iw/zoom)*on/{frames}" if direction == 1 else f"(iw-iw/zoom)*(1-on/{frames})")
    y = f"(ih-ih/zoom)*on/{frames}" if direction == 2 else "ih/2-(ih/zoom/2)"
    framing = ("scale=1720:970:force_original_aspect_ratio=decrease,"
               "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=#071113" if keep_whole else
               "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080")
    fade = ",fade=t=out:st=8:d=2:color=#071113" if row.get("shot_id") == "GW_LF_077" else ""
    return (framing + ","
            f"zoompan=z='min(zoom+{increment:.6f},1.055)':x='{x}':y='{y}':d=1:s=1920x1080:fps={FPS},"
            "eq=contrast=1.025:saturation=0.94,unsharp=5:5:0.22:5:5:0.0,format=yuv420p" + fade)


def ass_time(seconds: float) -> str:
    cs = int(round(seconds * 100)); h, rem = divmod(cs, 360000); m, rem = divmod(rem, 6000); s, cs = divmod(rem, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def ass_escape(text: str) -> str:
    return text.replace("\\", r"\\").replace("{", r"\{").replace("}", r"\}").replace("->", "→")


def build_graphics_ass(rows: list[dict]) -> Path:
    target = PROD / "render" / "EP02_GATEWAY_graphics.ass"; target.parent.mkdir(parents=True, exist_ok=True)
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Title,Arial,38,&H00F4F0E6,&H000000FF,&H90000000,&H70000000,-1,0,0,0,100,100,1,0,3,1,0,7,92,92,68,1
Style: Evidence,Arial,23,&H00FFFFFF,&H000000FF,&H70000000,&H9823211E,-1,0,0,0,100,100,1,0,3,1,0,9,80,80,64,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
    lines = [header]
    for row in rows:
        start, end = ass_time(row["start_seconds"] + 0.20), ass_time(max(row["start_seconds"] + .4, row["end_seconds"] - .20))
        if row.get("on_screen_text"):
            lines.append(f"Dialogue: 0,{start},{end},Title,,0,0,0,,{ass_escape(row['on_screen_text'])}\n")
        if row.get("evidence_label"):
            label = row["evidence_label"].replace("_", " ")
            lines.append(f"Dialogue: 0,{start},{end},Evidence,,0,0,0,,{ass_escape(label)}\n")
    target.write_text("".join(lines), encoding="utf-8-sig")
    return target


def render(*, limit: int | None = None, force: bool = False, shot: str | None = None) -> None:
    rows = json.loads(TIMELINE.read_text(encoding="utf-8"))
    indexed = list(enumerate(rows))
    if shot:
        indexed = [(index, row) for index, row in indexed if row["shot_id"] == shot]
        if not indexed: raise RuntimeError(f"Unknown shot: {shot}")
    elif limit:
        indexed = indexed[:limit]
    SEGMENTS.mkdir(parents=True, exist_ok=True)
    for display_index, (index, row) in enumerate(indexed, 1):
        target = SEGMENTS / f"{index + 1:03d}_{row['shot_id']}.mp4"
        if target.exists() and not force: continue
        print(f"Render {display_index:03d}/{len(indexed):03d} {row['shot_id']} {row['duration']:.1f}s", flush=True)
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-loop", "1", "-framerate", str(FPS),
             "-i", row["visual"], "-t", f"{row['duration']:.3f}", "-vf", camera_filter(index, row), "-an",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p", "-r", str(FPS), str(target)])
    if limit and not shot:
        print(f"Test render complete: {limit} segments"); return
    concat = PROD / "render" / "concat.txt"
    paths = [SEGMENTS / f"{i + 1:03d}_{row['shot_id']}.mp4" for i, row in enumerate(rows)]
    concat.write_text("\n".join(f"file '{p.as_posix()}'" for p in paths) + "\n", encoding="utf-8")
    silent = PROD / "render" / "EP02_GATEWAY_picture_lock_silent.mp4"
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(concat), "-c", "copy", str(silent)])
    ass = build_graphics_ass(rows); mix = AUDIO / "EP02_final_mix_48k24_stereo_-14LUFS.wav"
    FINAL.mkdir(parents=True, exist_ok=True); output = FINAL / "EP02_GATEWAY_FINAL_1080p.mp4"
    ass_filter = "ass='" + str(ass).replace("\\", "/").replace(":", r"\:") + "'"
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(silent), "-i", str(mix),
         "-map", "0:v:0", "-map", "1:a:0", "-vf", ass_filter, "-c:v", "libx264", "-preset", "slow", "-crf", "18",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart",
         "-t", f"{TOTAL}", str(output)])
    print(f"Final: {output}")


def qa() -> None:
    video = FINAL / "EP02_GATEWAY_FINAL_1080p.mp4"
    probe = json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(video)], capture=True))
    vs = next(s for s in probe["streams"] if s["codec_type"] == "video"); aud = next(s for s in probe["streams"] if s["codec_type"] == "audio")
    measured = loudness(video); timeline = json.loads(TIMELINE.read_text(encoding="utf-8"))
    checks = {"resolution_1080p": vs.get("width") == 1920 and vs.get("height") == 1080,
              "h264_yuv420p": vs.get("codec_name") == "h264" and vs.get("pix_fmt") == "yuv420p",
              "aac_stereo_48k": aud.get("codec_name") == "aac" and aud.get("sample_rate") == "48000" and aud.get("channels") == 2,
              "duration_12min": abs(float(probe["format"]["duration"]) - TOTAL) < .25,
              "timeline_77_shots": len(timeline) == 77,
              "loudness_near_minus14": abs(float(measured["input_i"]) + 14.0) <= .5,
              "true_peak_safe": float(measured["input_tp"]) <= -.8,
              "captions_present": SRT.is_file() and SRT.stat().st_size > 1000}
    report = {"file": str(video.resolve()), "sha256": sha256(video), "bytes": video.stat().st_size,
              "duration": float(probe["format"]["duration"]),
              "video": {k: vs.get(k) for k in ("codec_name", "width", "height", "pix_fmt", "r_frame_rate", "bit_rate")},
              "audio": {k: aud.get(k) for k in ("codec_name", "sample_rate", "channels", "bit_rate")},
              "loudness": measured, "checks": checks}
    path = FINAL / "EP02_GATEWAY_QA.json"; path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    contact = FINAL / "EP02_GATEWAY_CONTACT_SHEET.jpg"
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(video), "-vf",
         "fps=1/60,scale=480:270,tile=4x3", "-frames:v", "1", "-q:v", "2", str(contact)])
    print(json.dumps(report, indent=2))
    if not all(checks.values()): raise RuntimeError("QA failed")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["master", "align", "srt", "timeline", "audio", "render", "qa", "all"])
    parser.add_argument("--limit", type=int); parser.add_argument("--shot"); parser.add_argument("--force", action="store_true"); args = parser.parse_args()
    if args.command in ("master", "all"): master_voice()
    if args.command in ("align", "all"): align()
    if args.command in ("srt", "all"): build_srt()
    if args.command in ("timeline", "all"): build_timeline()
    if args.command in ("audio", "all"): build_audio()
    if args.command in ("render", "all"): render(limit=args.limit, force=args.force, shot=args.shot)
    if args.command in ("qa", "all") and not args.limit: qa()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
