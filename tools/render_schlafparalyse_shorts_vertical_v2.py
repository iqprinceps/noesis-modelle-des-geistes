#!/usr/bin/env python3
"""Render the six Shorts edge-to-edge from native 9:16 assets, without Ken Burns motion."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from render_schlafparalyse_shorts import build_ass, duration, make_bed, run


ROOT = Path(__file__).resolve().parents[1]
PROD = ROOT / "06_PRODUCTION" / "SCHLAFPARALYSE_SHORTS_V1"
# Veo 3.1 returns native 24 fps. Keeping the complete timeline at 24 fps avoids
# cadence duplicates and the small motion judder produced by 24-to-30 conversion.
W, H, FPS = 1080, 1920, 24

SHORTS = {
    "SP06A_ATEM": {"hook": "DU ERSTICKST NICHT", "cta": "Mehr: Schlafparalyse EP06"},
    "SP06B_RUECKENLAGE": {"hook": "RÜCKENLAGE?", "cta": "Mehr: Schlafparalyse EP06"},
    "SP07A_ALBTRAUMWORT": {"hook": "ALBTRAUM WAR EIN WESEN", "cta": "Mehr: Schlafparalyse EP07"},
    "SP07B_SALEM_ZEUGE": {"hook": "DER UNSICHTBARE ZEUGE", "cta": "Mehr: Schlafparalyse EP07"},
    "SP08A_HAT_MAN_HUT": {"hook": "WARUM DER HUT?", "cta": "Mehr: Schlafparalyse EP08"},
    "SP08B_UNSICHTBARE_PERSON": {"hook": "EINE PERSON AUS DEM NICHTS", "cta": "Mehr: Schlafparalyse EP08"},
}


def add_hook(ass: Path, hook: str) -> None:
    text = ass.read_text(encoding="utf-8-sig")
    hook_style = (
        "Style: Hook,Arial Black,58,&H00F5F2EB,&H00F5F2EB,&H00101014,&H98000000,"
        "-1,0,0,0,100,100,0,0,3,4,0,8,64,64,105,1\n"
    )
    text = text.replace("Style: CTA,", hook_style + "Style: CTA,", 1)
    marker = "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    safe = hook.replace("\\", "").replace("{", "(").replace("}", ")")
    event = f"Dialogue: 2,0:00:00.00,0:00:01.75,Hook,,0,0,0,,{safe}\n"
    text = text.replace(marker, marker + event, 1)
    ass.write_text(text, encoding="utf-8-sig")


def encode_still(source: Path, output: Path, seconds: float) -> None:
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-loop", "1", "-framerate", str(FPS), "-i", str(source),
        "-vf", (
            f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,"
            f"crop={W}:{H},setsar=1,fps={FPS},format=yuv420p"
        ),
        "-t", f"{seconds:.6f}", "-an", "-c:v", "libx264", "-preset", "veryfast",
        "-crf", "18", "-r", str(FPS), str(output),
    ])


def encode_veo(source: Path, output: Path, seconds: float) -> None:
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(source),
        "-vf", (
            f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,"
            f"crop={W}:{H},setsar=1,fps={FPS},format=yuv420p"
        ),
        "-t", f"{seconds:.6f}", "-an", "-c:v", "libx264", "-preset", "veryfast",
        "-crf", "18", "-r", str(FPS), str(output),
    ])


def ffprobe(path: Path) -> dict:
    output = run([
        "ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)
    ])
    return json.loads(output)


def render(job: str, spec: dict, no_veo: bool = False) -> dict:
    folder = PROD / job
    assets = folder / "assets_vertical_v2"
    stills = [assets / f"SHOT{number:02d}.png" for number in range(1, 8)]
    missing = [str(path) for path in stills if not path.is_file()]
    veo = folder / "veo_vertical_v2" / "CLIP01.mp4"
    if not no_veo and not veo.is_file():
        missing.append(str(veo))
    if missing:
        raise FileNotFoundError("Missing sources:\n" + "\n".join(missing))

    voice = folder / "voice" / f"{job}_GEORGE.mp3"
    total = duration(voice) + 0.45
    veo_seconds = min(6.0, duration(veo)) if not no_veo else 0.0
    still_seconds = (total - veo_seconds) / len(stills)
    timeline: list[tuple[str, Path, float]] = []
    for index, source in enumerate(stills, 1):
        timeline.append(("still", source, still_seconds))
        if index == 4 and veo_seconds:
            timeline.append(("veo", veo, veo_seconds))

    work = folder / "render_vertical_v2"
    segments = work / "segments"
    segments.mkdir(parents=True, exist_ok=True)
    segment_paths = []
    for index, (kind, source, seconds) in enumerate(timeline, 1):
        output = segments / f"{index:02d}_{kind}.mp4"
        if kind == "veo":
            encode_veo(source, output, seconds)
        else:
            encode_still(source, output, seconds)
        segment_paths.append(output)

    concat = work / "concat.txt"
    concat.write_text(
        "\n".join(f"file '{path.as_posix()}'" for path in segment_paths) + "\n",
        encoding="utf-8",
    )
    visual = work / "visual_edge_to_edge.mp4"
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0",
        "-i", str(concat), "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
        "-pix_fmt", "yuv420p", "-r", str(FPS), "-an", str(visual),
    ])

    captions = build_ass(job, spec["cta"], total)
    add_hook(captions, spec["hook"])
    captioned = work / "captioned.mp4"
    relative_ass = captions.relative_to(ROOT).as_posix().replace(":", "\\:")
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(visual),
        "-vf", f"ass='{relative_ass}'", "-an", "-c:v", "libx264", "-preset", "veryfast",
        "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS), str(captioned),
    ])

    bed = work / "soundbed.wav"
    make_bed(total, bed)
    final_dir = folder / "final_vertical_v2"
    final_dir.mkdir(parents=True, exist_ok=True)
    final = final_dir / f"{job}_FINAL_VERTICAL_V2.mp4"
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(captioned),
        "-i", str(voice), "-i", str(bed), "-filter_complex",
        f"[1:a]adelay=220|220,apad=whole_dur={total:.3f},pan=stereo|c0=c0|c1=c0,asplit=2[voice][key];"
        "[2:a][key]sidechaincompress=threshold=0.018:ratio=7:attack=12:release=300[duck];"
        "[voice][duck]amix=inputs=2:normalize=0:duration=first,"
        f"atrim=0:{total:.3f},aresample=192000,alimiter=limit=.89,aresample=48000,"
        "loudnorm=I=-14:TP=-1.5:LRA=10[a]",
        "-map", "0:v:0", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k",
        "-ar", "48000", "-ac", "2", "-t", f"{total:.3f}", "-movflags", "+faststart", str(final),
    ])

    contact = final_dir / f"{job}_CONTACT_SHEET.jpg"
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(final),
        "-vf", "fps=1/5,scale=216:384,tile=5x2", "-frames:v", "1", "-q:v", "2", str(contact),
    ])
    black_log = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(final), "-vf", "blackdetect=d=0.08:pix_th=0.02", "-an", "-f", "null", "-"],
        cwd=ROOT, capture_output=True, text=True,
    ).stderr
    black_events = [line.strip() for line in black_log.splitlines() if "black_start:" in line]
    report = {
        "file": str(final),
        "duration": round(duration(final), 3),
        "resolution": f"{W}x{H}",
        "fps": FPS,
        "layout": "native 9:16 edge-to-edge",
        "camera_motion": "none on stills; locked-camera Veo motion only",
        "stills": len(stills),
        "veo_clips": 0 if no_veo else 1,
        "voice": "George",
        "voice_id": "JBFqnCBsd6RMkjVDRZzb",
        "blackdetect_events": black_events,
        "contact_sheet": str(contact),
        "probe": ffprobe(final),
    }
    (final_dir / "QA_REPORT.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", choices=tuple(SHORTS))
    parser.add_argument("--no-veo", action="store_true")
    args = parser.parse_args()
    report = {}
    for job, spec in SHORTS.items():
        if args.only and job != args.only:
            continue
        print(f"RENDER {job}", flush=True)
        report[job] = render(job, spec, no_veo=args.no_veo)
        print(json.dumps({key: value for key, value in report[job].items() if key != "probe"}, ensure_ascii=False), flush=True)
    destination = PROD / "FINAL_QA_VERTICAL_V2.json"
    existing = json.loads(destination.read_text(encoding="utf-8")) if destination.is_file() else {}
    existing.update(report)
    destination.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
