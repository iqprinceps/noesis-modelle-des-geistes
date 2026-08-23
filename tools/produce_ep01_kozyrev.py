#!/usr/bin/env python3
"""Build the aligned voice, audio mix, timeline and final EP01 Kozyrev video."""

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
import unicodedata
import uuid
from urllib.error import HTTPError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent.parent
EP = ROOT / "03_EPISODEN" / "TYPE_A" / "EP01_KOZYREV"
PROD = ROOT / "06_PRODUCTION" / "EP01_KOZYREV"
VOICE_TEXT = EP / "VOICE_SCRIPT_CLEAN.txt"
CUES = EP / "VISUAL_CUE_SHEET.csv"
RAW_VOICE = PROD / "voice" / "raw" / "EP01_KOZYREV_HELMUT_v2_8min.mp3"
VOICE_MASTER = PROD / "voice" / "master" / "EP01_KOZYREV_VO_MASTER_48k24_mono.wav"
ALIGNMENT = PROD / "voice" / "alignment" / "EP01_KOZYREV_alignment.json"
TIMELINE = PROD / "timeline" / "EP01_KOZYREV_timeline.json"
SRT = PROD / "captions" / "EP01_KOZYREV_de.srt"
SELECTED = ROOT / "05_GENERATED" / "EP01_KOZYREV" / "01_SELECTED"
CARDS = ROOT / "05_GENERATED" / "EP01_KOZYREV"
APPROVED = ROOT / "04_ASSETS" / "02_CURATED" / "EP01_KOZYREV" / "APPROVED"
AUDIO = PROD / "audio"
SEGMENTS = PROD / "render" / "segments"
FINAL = PROD / "render" / "final"
FPS = 30
END_HOLD = 2.5


def run(args: list[str], *, capture: bool = False) -> str:
    result = subprocess.run(args, text=True, capture_output=capture)
    if result.returncode:
        raise RuntimeError((result.stderr or result.stdout or "command failed")[-5000:])
    return (result.stdout or "") + (result.stderr or "")


def duration(path: Path) -> float:
    return float(run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "csv=p=0", str(path),
    ], capture=True).strip())


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def multipart(audio: Path, text: str) -> tuple[bytes, str]:
    boundary = "----KOZYREV" + uuid.uuid4().hex
    parts = [
        f"--{boundary}\r\n".encode(),
        b'Content-Disposition: form-data; name="text"\r\n\r\n',
        text.encode("utf-8"), b"\r\n",
        f"--{boundary}\r\n".encode(),
        f'Content-Disposition: form-data; name="file"; filename="{audio.name}"\r\n'.encode(),
        (b"Content-Type: audio/wav\r\n\r\n" if audio.suffix.casefold() == ".wav" else b"Content-Type: audio/mpeg\r\n\r\n"),
        audio.read_bytes(), b"\r\n",
        f"--{boundary}--\r\n".encode(),
    ]
    return b"".join(parts), boundary


def align() -> None:
    alignment_audio = VOICE_MASTER if VOICE_MASTER.is_file() else RAW_VOICE
    if not alignment_audio.is_file():
        raise FileNotFoundError(alignment_audio)
    noesis_tools = Path(r"C:\Users\iQPrinceps\Documents\Codex\NOESIS Channel\tools")
    sys.path.insert(0, str(noesis_tools))
    from elevenlabs_cli import _load_key  # type: ignore

    text = VOICE_TEXT.read_text(encoding="utf-8").strip()
    body, boundary = multipart(alignment_audio, text)
    request = Request(
        "https://api.elevenlabs.io/v1/forced-alignment",
        data=body,
        headers={
            "xi-api-key": _load_key(),
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=300) as response:
            result = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise RuntimeError(f"ElevenLabs alignment HTTP {exc.code}: {exc.read().decode(errors='replace')}")
    result["source_text"] = text
    result["audio"] = str(alignment_audio.resolve())
    result["audio_sha256"] = sha256(alignment_audio)
    ALIGNMENT.parent.mkdir(parents=True, exist_ok=True)
    ALIGNMENT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Alignment: {ALIGNMENT}")


def normalized_with_map(text: str) -> tuple[str, list[int]]:
    out: list[str] = []
    mapping: list[int] = []
    pending_space = False
    for index, char in enumerate(text):
        decomposed = unicodedata.normalize("NFKD", char.casefold())
        emitted = False
        for item in decomposed:
            if unicodedata.combining(item):
                continue
            if item.isalnum():
                if pending_space and out and out[-1] != " ":
                    out.append(" ")
                    mapping.append(index)
                pending_space = False
                out.append(item)
                mapping.append(index)
                emitted = True
        if not emitted:
            pending_space = True
    return "".join(out).strip(), mapping[:len("".join(out).strip())]


def normalized(text: str) -> str:
    return normalized_with_map(text)[0]


def original_asset(row: dict[str, str]) -> Path:
    concept = row["visual_concept"].casefold()
    kind = row["visual_type"]
    if kind == "ORIGINAL_PORTRAIT" or "portrait" in concept:
        return APPROVED / "KZ_001_Nikolai_Kozyrev_1959.png"
    if "observatory" in concept or "refractor" in concept:
        return APPROVED / "KZ_004_Pulkovo_big_refractor.jpg"
    if "drawing" in concept:
        return APPROVED / "KZ_002_Kozyrev_mirror_apparatus_drawing_1996.jpg"
    return APPROVED / "KZ_003_Kozyrev_mirrors_modern_photo_2014.jpg"


def resolve_visual(row: dict[str, str], previous: Path | None) -> Path:
    # An explicit editor asset is a manual override and must win over a stale
    # generation id left in an older cue sheet revision.
    if row.get("editor_asset"):
        relative = row["editor_asset"].split(";")[0].strip().replace("/", "\\")
        path = CARDS / relative
    elif row.get("generation_id"):
        path = SELECTED / f"{row['generation_id']}.png"
    elif row["visual_type"].startswith("ORIGINAL"):
        path = original_asset(row)
    elif row["visual_type"] == "HOLD_PREVIOUS" and previous:
        path = previous
    else:
        path = previous or CARDS / "03_EDITOR_CARDS" / "CARD01_PATENT_EVIDENCE.png"
    if not path.is_file():
        raise FileNotFoundError(f"Visual missing for {row['cue_id']}: {path}")
    return path


def build_timeline() -> list[dict]:
    alignment = json.loads(ALIGNMENT.read_text(encoding="utf-8"))
    text = alignment["source_text"]
    chars = alignment["characters"]
    norm_text, mapping = normalized_with_map(text)
    rows = list(csv.DictReader(CUES.open(encoding="utf-8-sig", newline="")))
    starts: list[float] = []
    search_from = 0
    for i, row in enumerate(rows):
        needle = normalized(row["voice_anchor_start"])
        pos = norm_text.find(needle, max(0, search_from - 80))
        if pos < 0:
            raise RuntimeError(f"Cue anchor not found: {row['cue_id']} / {needle}")
        original_index = mapping[pos]
        while original_index < len(chars) and chars[original_index]["text"].isspace():
            original_index += 1
        starts.append(float(chars[original_index]["start"]))
        search_from = pos + max(1, len(needle))
    starts[0] = 0.0
    total = duration(Path(alignment["audio"])) + END_HOLD
    result: list[dict] = []
    previous: Path | None = None
    for index, row in enumerate(rows):
        path = resolve_visual(row, previous)
        previous = path
        start = starts[index]
        end = starts[index + 1] if index + 1 < len(starts) else total
        if end <= start:
            raise RuntimeError(f"Non-positive cue: {row['cue_id']} {start}..{end}")
        result.append({
            **row,
            "start": round(start, 3),
            "end": round(end, 3),
            "duration": round(end - start, 3),
            "visual": str(path.resolve()),
        })
    TIMELINE.parent.mkdir(parents=True, exist_ok=True)
    TIMELINE.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Timeline: {len(result)} cues, {total:.3f}s -> {TIMELINE}")
    return result


def split_reference_stems() -> None:
    alignment = json.loads(ALIGNMENT.read_text(encoding="utf-8"))
    full_text = alignment["source_text"]
    chars = alignment["characters"]
    stems = json.loads((PROD / "voice" / "stems.json").read_text(encoding="utf-8"))
    ranges = []
    cursor = 0
    for stem in stems:
        stem_text = Path(stem["text_file"]).read_text(encoding="utf-8").strip()
        start_index = full_text.find(stem_text, cursor)
        if start_index < 0:
            raise RuntimeError(f"Stem text not found: {stem['id']}")
        end_index = start_index + len(stem_text) - 1
        first = next(i for i in range(start_index, end_index + 1) if not full_text[i].isspace())
        last = next(i for i in range(end_index, start_index - 1, -1) if not full_text[i].isspace())
        ranges.append({**stem, "speech_start": float(chars[first]["start"]), "speech_end": float(chars[last]["end"])})
        cursor = end_index + 1
    boundaries = [0.0]
    for left, right in zip(ranges, ranges[1:]):
        boundaries.append((left["speech_end"] + right["speech_start"]) / 2)
    boundaries.append(duration(RAW_VOICE))
    stem_dir = PROD / "voice" / "master" / "stems"
    stem_dir.mkdir(parents=True, exist_ok=True)
    concat_lines = []
    for index, stem in enumerate(ranges):
        start, end = boundaries[index], boundaries[index + 1]
        target = stem_dir / f"{stem['id']}.wav"
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{start:.6f}",
             "-to", f"{end:.6f}", "-i", str(RAW_VOICE), "-ar", "48000", "-ac", "1",
             "-c:a", "pcm_s24le", str(target)])
        stem.update({"file": str(target.resolve()), "start": round(start, 3), "end": round(end, 3),
                     "duration": round(duration(target), 3), "sha256": sha256(target)})
        concat_lines.append(f"file '{target.as_posix()}'")
    concat = PROD / "voice" / "master" / "concat.txt"
    concat.write_text("\n".join(concat_lines) + "\n", encoding="utf-8")
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", str(concat), "-c:a", "pcm_s24le", str(VOICE_MASTER)])
    report = {"source": str(RAW_VOICE.resolve()), "master": str(VOICE_MASTER.resolve()),
              "duration": duration(VOICE_MASTER), "stems": ranges}
    (PROD / "voice" / "master" / "stem_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Split {len(ranges)} stems -> {VOICE_MASTER}")


def master_generated_stems() -> None:
    raw_dir = PROD / "voice" / "raw_stems"
    stems = json.loads((PROD / "voice" / "stems.json").read_text(encoding="utf-8"))
    master_dir = PROD / "voice" / "master"
    stem_dir = master_dir / "stems"
    stem_dir.mkdir(parents=True, exist_ok=True)
    gaps = [0.45, 0.55, 0.45, 0.45, 0.55, 0.60, 0.65]
    concat_lines: list[str] = []
    report = []
    for index, stem in enumerate(stems):
        source = raw_dir / f"{stem['id']}.mp3"
        if not source.is_file():
            raise FileNotFoundError(source)
        target = stem_dir / f"{stem['id']}.wav"
        normalize_audio(source, target, -18.0, -2.0, 1)
        concat_lines.append(f"file '{target.as_posix()}'")
        report.append({"id": stem["id"], "file": str(target.resolve()),
                       "duration": round(duration(target), 3), "sha256": sha256(target)})
        if index < len(gaps):
            gap = master_dir / f"gap_{index + 1:02d}.wav"
            run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i",
                 f"anullsrc=r=48000:cl=mono:d={gaps[index]}", "-c:a", "pcm_s24le", str(gap)])
            concat_lines.append(f"file '{gap.as_posix()}'")
    concat = master_dir / "concat.txt"
    concat.write_text("\n".join(concat_lines) + "\n", encoding="utf-8")
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", str(concat), "-c:a", "pcm_s24le", str(VOICE_MASTER)])
    payload = {"master": str(VOICE_MASTER.resolve()), "duration": round(duration(VOICE_MASTER), 3),
               "gaps": gaps, "stems": report}
    (master_dir / "stem_report.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


def srt_time(value: float) -> str:
    ms = int(round(value * 1000))
    h, rem = divmod(ms, 3_600_000)
    m, rem = divmod(rem, 60_000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def build_srt() -> None:
    data = json.loads(ALIGNMENT.read_text(encoding="utf-8"))
    chars = data["characters"]
    text = data["source_text"]
    spans = []
    for match in re.finditer(r"[^.!?]+[.!?]+|[^.!?]+$", text, re.S):
        sentence = re.sub(r"\s+", " ", match.group()).strip()
        if not sentence:
            continue
        first = next(i for i in range(match.start(), match.end()) if not text[i].isspace())
        last = next(i for i in range(match.end() - 1, match.start() - 1, -1) if not text[i].isspace())
        start, end = float(chars[first]["start"]), float(chars[last]["end"])
        words = sentence.split()
        if len(words) <= 13:
            spans.append((start, end, sentence))
        else:
            midpoint = len(words) // 2
            split_phrase = " ".join(words[:midpoint])
            split_char = text.find(split_phrase, match.start()) + len(split_phrase)
            split_time = float(chars[min(split_char, len(chars) - 1)]["end"])
            spans.append((start, split_time, " ".join(words[:midpoint])))
            spans.append((split_time, end, " ".join(words[midpoint:])))
    lines = []
    for index, (start, end, sentence) in enumerate(spans, 1):
        lines.extend([str(index), f"{srt_time(start)} --> {srt_time(end)}", sentence, ""])
    SRT.parent.mkdir(parents=True, exist_ok=True)
    SRT.write_text("\n".join(lines), encoding="utf-8-sig")
    print(f"Captions: {len(spans)} -> {SRT}")


def loudness(path: Path, target: float, peak: float, lra: float = 7.0) -> dict:
    output = run([
        "ffmpeg", "-hide_banner", "-nostats", "-i", str(path),
        "-af", f"loudnorm=I={target}:TP={peak}:LRA={lra}:print_format=json",
        "-f", "null", "-",
    ], capture=True)
    matches = re.findall(r'\{\s*"input_i".*?\}', output, re.S)
    return json.loads(matches[-1])


def normalize_audio(source: Path, target: Path, integrated: float, peak: float, channels: int) -> dict:
    stats = loudness(source, integrated, peak)
    filt = (
        f"loudnorm=I={integrated}:TP={peak}:LRA=7:"
        f"measured_I={stats['input_i']}:measured_TP={stats['input_tp']}:"
        f"measured_LRA={stats['input_lra']}:measured_thresh={stats['input_thresh']}:"
        f"offset={stats['target_offset']}:linear=true"
    )
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(source),
         "-af", filt, "-ac", str(channels), "-ar", "48000", "-c:a", "pcm_s24le", str(target)])
    return loudness(target, integrated, peak)


def build_audio() -> None:
    AUDIO.mkdir(parents=True, exist_ok=True)
    voice = AUDIO / "EP01_voice_48k24_mono_-18LUFS.wav"
    source_voice = VOICE_MASTER if VOICE_MASTER.exists() else RAW_VOICE
    voice_stats = normalize_audio(source_voice, voice, -18.0, -2.0, 1)
    total = duration(source_voice) + END_HOLD
    drone = (
        "aevalsrc="
        "0.095*sin(2*PI*43.65*t+0.08*sin(2*PI*t/37))"
        "+0.040*sin(2*PI*65.41*t+0.09*sin(2*PI*t/53))"
        "+0.018*sin(2*PI*87.31*t+0.05*sin(2*PI*t/79))"
        f":s=48000:d={total}"
    )
    noise = f"anoisesrc=color=pink:amplitude=0.038:r=48000:d={total}"
    bed_raw = AUDIO / "EP01_original_ambient_raw.wav"
    bed = AUDIO / "EP01_original_ambient_-34LUFS.wav"
    filt = (
        "[0:a]lowpass=f=540,aecho=0.8:0.45:1300|2600:0.06|0.025,"
        "volume='0.74+0.06*sin(2*PI*t/91)':eval=frame[d];"
        "[1:a]highpass=f=240,lowpass=f=2800,volume=0.12[n];"
        "[d][n]amix=inputs=2:weights='1 0.14':normalize=0,alimiter=limit=0.9[out]"
    )
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-f", "lavfi", "-i", drone, "-f", "lavfi", "-i", noise,
         "-filter_complex", filt, "-map", "[out]", "-ac", "2", "-ar", "48000",
         "-c:a", "pcm_s24le", str(bed_raw)])
    bed_stats = normalize_audio(bed_raw, bed, -34.0, -4.0, 2)
    premix = AUDIO / "EP01_mix_premaster.wav"
    final = AUDIO / "EP01_final_mix_48k24_stereo_-14LUFS.wav"
    mix = (
        f"[0:a]apad=pad_dur={END_HOLD},atrim=0:{total},pan=stereo|c0=c0|c1=c0[voice];"
        "[1:a][voice]sidechaincompress=threshold=0.020:ratio=6:attack=35:release=650[ducked];"
        "[voice][ducked]amix=inputs=2:weights='1 1':normalize=0,alimiter=limit=0.94[out]"
    )
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(voice), "-i", str(bed),
         "-filter_complex", mix, "-map", "[out]", "-ac", "2", "-ar", "48000",
         "-c:a", "pcm_s24le", str(premix)])
    final_stats = normalize_audio(premix, final, -14.0, -1.0, 2)
    report = {
        "duration": round(total, 3), "voice": str(voice.resolve()), "voice_verify": voice_stats,
        "bed": str(bed.resolve()), "bed_verify": bed_stats,
        "final": str(final.resolve()), "final_verify": final_stats,
        "rights": "Original procedural synthesis; no samples or third-party music.",
    }
    (AUDIO / "audio_mix_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


def camera_filter(index: int, row: dict) -> str:
    frames = max(1, int(math.ceil(float(row["duration"]) * FPS)))
    if row["editor_asset"]:
        increment = 0.000025
    elif row["visual_type"].startswith("ORIGINAL"):
        increment = 0.00011
    else:
        increment = 0.000075
    direction = index % 4
    if direction == 0:
        x, y = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    elif direction == 1:
        x, y = "(iw-iw/zoom)*on/%d" % frames, "ih/2-(ih/zoom/2)"
    elif direction == 2:
        x, y = "iw/2-(iw/zoom/2)", "(ih-ih/zoom)*on/%d" % frames
    else:
        x, y = "(iw-iw/zoom)*(1-on/%d)" % frames, "ih/2-(ih/zoom/2)"
    return (
        "scale=1920:1080:force_original_aspect_ratio=increase,"
        "crop=1920:1080,"
        f"zoompan=z='min(zoom+{increment:.6f},1.055)':x='{x}':y='{y}':d=1:s=1920x1080:fps={FPS},"
        "eq=contrast=1.025:saturation=0.94,unsharp=5:5:0.25:5:5:0.0,format=yuv420p"
    )


def motion_filter() -> str:
    """Normalize documentary motion assets without applying a still-image zoom."""
    return (
        "scale=1920:1080:force_original_aspect_ratio=increase,"
        "crop=1920:1080,"
        "eq=contrast=1.015:saturation=0.96,format=yuv420p"
    )


def render(*, limit: int | None = None, force: bool = False) -> None:
    rows = json.loads(TIMELINE.read_text(encoding="utf-8"))
    if limit:
        rows = rows[:limit]
    SEGMENTS.mkdir(parents=True, exist_ok=True)
    for index, row in enumerate(rows):
        target = SEGMENTS / f"{index + 1:03d}_{row['cue_id']}.mp4"
        if target.exists() and not force:
            continue
        print(f"Render {index + 1:03d}/{len(rows):03d} {row['cue_id']} {row['duration']:.3f}s", flush=True)
        visual = Path(row["visual"])
        is_motion = visual.suffix.casefold() in {".mp4", ".mov", ".m4v", ".webm", ".mkv"}
        input_args = (["-stream_loop", "-1", "-i", str(visual)] if is_motion else
                      ["-loop", "1", "-framerate", str(FPS), "-i", str(visual)])
        run([
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            *input_args,
            "-t", f"{float(row['duration']):.3f}",
            "-vf", motion_filter() if is_motion else camera_filter(index, row),
            "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
            "-pix_fmt", "yuv420p", "-r", str(FPS), str(target),
        ])
    if limit:
        print(f"Test render complete: {limit} segments")
        return
    concat = PROD / "render" / "concat.txt"
    segment_paths = [SEGMENTS / f"{i + 1:03d}_{row['cue_id']}.mp4" for i, row in enumerate(rows)]
    concat.write_text("\n".join(f"file '{path.as_posix()}'" for path in segment_paths) + "\n", encoding="utf-8")
    silent = PROD / "render" / "EP01_KOZYREV_picture_lock_silent.mp4"
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", str(concat), "-c", "copy", str(silent)])
    FINAL.mkdir(parents=True, exist_ok=True)
    output = FINAL / "EP01_KOZYREV_FINAL_1080p.mp4"
    mix = AUDIO / "EP01_final_mix_48k24_stereo_-14LUFS.wav"
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(silent), "-i", str(mix),
         "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-af", "volume=-0.4dB",
         "-c:a", "aac", "-b:a", "320k",
         "-ar", "48000", "-movflags", "+faststart", "-shortest", str(output)])
    print(f"Final: {output}")


def qa() -> None:
    video = FINAL / "EP01_KOZYREV_FINAL_1080p.mp4"
    probe = json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(video)], capture=True))
    video_stream = next(s for s in probe["streams"] if s["codec_type"] == "video")
    audio_stream = next(s for s in probe["streams"] if s["codec_type"] == "audio")
    measured = loudness(video, -14.0, -1.0)
    report = {
        "file": str(video.resolve()), "sha256": sha256(video),
        "duration": float(probe["format"]["duration"]),
        "video": {k: video_stream.get(k) for k in ("codec_name", "width", "height", "pix_fmt", "r_frame_rate")},
        "audio": {k: audio_stream.get(k) for k in ("codec_name", "sample_rate", "channels", "bit_rate")},
        "loudness": measured,
        "checks": {
            "resolution_1080p": video_stream.get("width") == 1920 and video_stream.get("height") == 1080,
            "h264_yuv420p": video_stream.get("codec_name") == "h264" and video_stream.get("pix_fmt") == "yuv420p",
            "aac_stereo_48k": audio_stream.get("codec_name") == "aac" and audio_stream.get("sample_rate") == "48000" and audio_stream.get("channels") == 2,
            "duration_matches": abs(float(probe["format"]["duration"]) - (duration(VOICE_MASTER) + END_HOLD)) < 0.25,
            "loudness_near_minus14": abs(float(measured["input_i"]) + 14.0) <= 0.5,
            "true_peak_safe": float(measured["input_tp"]) <= -0.8,
        },
    }
    path = FINAL / "EP01_KOZYREV_QA.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not all(report["checks"].values()):
        raise RuntimeError("QA failed")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["align", "split", "master", "timeline", "srt", "audio", "render", "qa", "all"])
    parser.add_argument("--limit", type=int)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if args.command == "align" or (args.command == "all" and not ALIGNMENT.exists()):
        align()
    if args.command in ("split", "all"):
        split_reference_stems()
    if args.command in ("master", "all"):
        master_generated_stems()
    if args.command in ("timeline", "all"):
        build_timeline()
    if args.command in ("srt", "all"):
        build_srt()
    if args.command in ("audio", "all"):
        build_audio()
    if args.command in ("render", "all"):
        render(limit=args.limit, force=args.force)
    if args.command in ("qa", "all") and not args.limit:
        qa()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
