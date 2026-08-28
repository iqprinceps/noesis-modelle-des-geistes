#!/usr/bin/env python3
"""Render six standalone Schlafparalyse Shorts in the established NOESIS style.

Each Short uses a single continuous George read, ten unique visual sources,
word-timed captions from an independent transcription, and no internal audio
joins.  Generated triptychs are split into individual visual beats here.
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
PROD = ROOT / "06_PRODUCTION" / "SCHLAFPARALYSE_SHORTS_V1"
W, H, FPS = 1080, 1920, 30

EP06 = ROOT / "06_PRODUCTION" / "EP06_SCHLAFPARALYSE_V4"
EP07 = ROOT / "06_PRODUCTION" / "EP07_SCHLAFPARALYSE_V4"
EP08 = ROOT / "06_PRODUCTION" / "EP08_SCHLAFPARALYSE_V4"
G06 = EP06 / "IMAGE_GENERATION_KIT" / "03_GENERATED_OUTPUT" / "NanoBanana_2K_Series"
G07 = EP07 / "IMAGE_GENERATION_KIT" / "03_GENERATED_OUTPUT" / "NanoBanana_Pro_2K_Series"
G08 = EP08 / "IMAGE_GENERATION_KIT" / "03_GENERATED_OUTPUT"
O07 = EP07 / "ORIGINAL_DERIVATIVES"
O08 = EP08 / "ORIGINAL_EXPANSIONS"
A06 = EP06 / "IMAGE_GENERATION_KIT" / "02_ASSETS"


def panel(job: str, number: int) -> Path:
    return PROD / job / "assets" / f"{job}_PANEL{number:02d}.png"


SHORTS = {
    "SP06A_ATEM": {
        "hook": "DU ERSTICKST NICHT",
        "cta": "Mehr: Schlafparalyse EP06",
        "images": [
            panel("SP06A_ATEM", 1),
            G06 / "IMG005_CHEST_PRESSURE_CLOSE.png",
            G06 / "IMG009_REM_BODY_STILL.png",
            panel("SP06A_ATEM", 2),
            A06 / "EP06_Polysomnography_model_side.jpg",
            G06 / "IMG020_EEG_AWAKE_BODY_STILL_BASE.png",
            panel("SP06A_ATEM", 3),
            G06 / "IMG003_HAND_WILL_NOT_MOVE.png",
            G06 / "IMG025_ALARM_WITHOUT_CAUSE.png",
            G06 / "IMG019_RETURN_TO_BED_RECON.png",
        ],
    },
    "SP06B_RUECKENLAGE": {
        "hook": "RÜCKENLAGE?",
        "cta": "Mehr: Schlafparalyse EP06",
        "images": [
            panel("SP06B_RUECKENLAGE", 1),
            G06 / "IMG018_SLEEP_INTERRUPTION_CLOCK.png",
            G06 / "IMG017_SLEEP_LAB_WIDE_RECON.png",
            panel("SP06B_RUECKENLAGE", 2),
            G06 / "IMG015_VESTIBULAR_FLOAT.png",
            G06 / "IMG011_WAKE_BODY_LAG.png",
            panel("SP06B_RUECKENLAGE", 3),
            G06 / "IMG022_VIEWER_BEDROOM_TWO_STEPS.png",
            A06 / "EP06_Sleep_Studies_NHLBI_Polysomnography.jpg",
            G06 / "IMG023_BODY_OR_VISITOR_SPLIT_BASE.png",
        ],
    },
    "SP07A_ALBTRAUMWORT": {
        "hook": "ALBTRAUM WAR EIN WESEN",
        "cta": "Mehr: Schlafparalyse EP07",
        "images": [
            panel("SP07A_ALBTRAUMWORT", 1),
            G07 / "IMG009_MEDIEVAL_BEDROOM_EXPLANATION.png",
            G07 / "IMG005_NIGHTMARE_MOTIF_ROOM_BASE.png",
            panel("SP07A_ALBTRAUMWORT", 2),
            G07 / "IMG007_MARA_INCUBUS_KANASHIBARI_BASE.png",
            G07 / "SHOT02_MANY_NAMES_PAPER_LAYERS.png",
            panel("SP07A_ALBTRAUMWORT", 3),
            G07 / "IMG060_WORD_LAYERS_CTA_BG.png",
            G07 / "IMG039_GENERATIONS_OF_NIGHT_STORIES.png",
            O07 / "SRC_EP07_Fuseli_The_Nightmare_1781_full_painting.png",
        ],
    },
    "SP07B_SALEM_ZEUGE": {
        "hook": "DER UNSICHTBARE ZEUGE",
        "cta": "Mehr: Schlafparalyse EP07",
        "images": [
            panel("SP07B_SALEM_ZEUGE", 1),
            G07 / "IMG001_SALEM_BEDROOM_COMAN_RECON.png",
            G07 / "SHOT01_SALEM_EMPTY_BED.png",
            panel("SP07B_SALEM_ZEUGE", 2),
            G07 / "IMG003_PRIVATE_NIGHT_TO_COURT.png",
            G07 / "IMG004_BRIDGET_BISHOP_COURT_CONTEXT_RECON.png",
            panel("SP07B_SALEM_ZEUGE", 3),
            O07 / "SRC_EP07_Bridget_Bishop_lithograph_full_portrait.png",
            O07 / "SRC_EP07_Trial_George_Jacobs_Salem_LOC_full_later_depiction.png",
            G07 / "IMG050_PRIVATE_TO_PUBLIC_NETWORK.png",
        ],
    },
    "SP08A_HAT_MAN_HUT": {
        "hook": "WARUM DER HUT?",
        "cta": "Mehr: Schlafparalyse EP08",
        "images": [
            panel("SP08A_HAT_MAN_HUT", 1),
            G08 / "IMG017_HAT_MAN_FOOT_OF_BED.png",
            G08 / "IMG018_HAT_BRIM_MINIMAL.png",
            panel("SP08A_HAT_MAN_HUT", 2),
            G08 / "IMG019_HAT_MAN_AS_ROOM_GEOMETRY.png",
            G08 / "IMG021_MULTIPLE_CAUSES_SAME_SILHOUETTE.png",
            panel("SP08A_HAT_MAN_HUT", 3),
            G08 / "IMG022_INTERNET_SUPPLIES_HAT.png",
            G08 / "IMG023_PATTERN_OR_MEME_BASE.png",
            G08 / "IMG027_GLOBAL_VISUAL_MEMORY.png",
        ],
    },
    "SP08B_UNSICHTBARE_PERSON": {
        "hook": "EINE PERSON AUS DEM NICHTS",
        "cta": "Mehr: Schlafparalyse EP08",
        "images": [
            panel("SP08B_UNSICHTBARE_PERSON", 1),
            O08 / "SRC018_PSG_MODEL_SIDE_FULL.png",
            O08 / "SRC024_EEG_CAP_FULL.png",
            panel("SP08B_UNSICHTBARE_PERSON", 2),
            G08 / "IMG030_BRAIN_EXPERIENCE_STORY_EXPECTATION_BASE.png",
            G06 / "IMG023_BODY_OR_VISITOR_SPLIT_BASE.png",
            panel("SP08B_UNSICHTBARE_PERSON", 3),
            G08 / "IMG014_MEMORY_RECONSTRUCTION_LAYERS.png",
            G08 / "IMG031_HAT_MAN_DISSOLVES_INTO_PIXELS.png",
            G08 / "IMG012_TOUCH_WITHOUT_AGENT.png",
        ],
    },
}


def run(args: list[str]) -> str:
    result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError((result.stderr or result.stdout)[-5000:])
    return result.stdout + result.stderr


def duration(path: Path) -> float:
    return float(run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "csv=p=0", str(path),
    ]).strip())


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "ariblk.ttf" if bold else "seguisb.ttf"
    return ImageFont.truetype(f"C:/Windows/Fonts/{name}", size)


def split_triptych(job: str) -> None:
    assets = PROD / job / "assets"
    master = assets / f"{job.replace('_ATEM', '').replace('_RUECKENLAGE', '').replace('_ALBTRAUMWORT', '').replace('_SALEM_ZEUGE', '').replace('_HAT_MAN_HUT', '').replace('_UNSICHTBARE_PERSON', '')}_MASTER_TRIPTYCH.png"
    # Master names use the short ID prefix, which is simpler and explicit here.
    prefix = job.split("_")[0]
    master = assets / f"{prefix}_MASTER_TRIPTYCH.png"
    with Image.open(master).convert("RGB") as image:
        width, height = image.size
        if (width, height) != (941, 1672):
            raise ValueError(f"Unexpected triptych dimensions: {master} {image.size}")
        crops = ((0, 553), (560, 1112), (1119, 1672))
        for number, (top, bottom) in enumerate(crops, 1):
            image.crop((0, top, width, bottom)).save(panel(job, number), quality=96)


def vertical_frame(source: Path, target: Path, hook: str | None = None) -> None:
    with Image.open(source).convert("RGB") as image:
        bg_scale = max(W / image.width, H / image.height)
        bg = image.resize(
            (math.ceil(image.width * bg_scale), math.ceil(image.height * bg_scale)),
            Image.Resampling.LANCZOS,
        )
        left = (bg.width - W) // 2
        top = (bg.height - H) // 2
        bg = bg.crop((left, top, left + W, top + H)).filter(ImageFilter.GaussianBlur(32))
        bg = ImageEnhance.Brightness(bg).enhance(0.43)

        max_w, max_h = 1020, 1320
        fg_scale = min(max_w / image.width, max_h / image.height)
        fg = image.resize(
            (max(1, round(image.width * fg_scale)), max(1, round(image.height * fg_scale))),
            Image.Resampling.LANCZOS,
        )
        frame = bg.copy()
        x = (W - fg.width) // 2
        y = max(170, (H - fg.height) // 2 - 65)
        shadow = Image.new("RGBA", (fg.width + 50, fg.height + 50), (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow)
        sd.rounded_rectangle((25, 25, fg.width + 25, fg.height + 25), radius=18, fill=(0, 0, 0, 190))
        shadow = shadow.filter(ImageFilter.GaussianBlur(18))
        frame.paste(shadow.convert("RGB"), (x - 25, y - 25))
        frame.paste(fg, (x, y))

        if hook:
            overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            f = font(62, bold=True)
            while draw.textlength(hook, font=f) > 900 and f.size > 38:
                f = font(f.size - 2, bold=True)
            text_w = draw.textlength(hook, font=f)
            bx0 = (W - text_w) / 2 - 34
            by0 = 82
            draw.rounded_rectangle((bx0, by0, W - bx0, by0 + 104), radius=26, fill=(7, 10, 15, 225))
            draw.text(((W - text_w) / 2, by0 + 18), hook, font=f, fill=(245, 242, 235, 255))
            frame = Image.alpha_composite(frame.convert("RGBA"), overlay).convert("RGB")
        frame.save(target, quality=95)


def ass_time(seconds: float) -> str:
    seconds = max(0.0, seconds)
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours}:{minutes:02d}:{secs:05.2f}"


def escape_ass(text: str) -> str:
    return text.replace("\\", "").replace("{", "(").replace("}", ")")


def wrap_caption(text: str, limit: int = 24) -> str:
    """Insert an explicit ASS line break without producing one-word orphans."""
    words = text.split()
    if len(text) <= limit or len(words) < 2:
        return text
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if current and len(candidate) > limit:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    if len(lines) > 2:
        # Word groups are already short; balance an exceptional three-line case.
        midpoint = max(1, len(words) // 2)
        lines = [" ".join(words[:midpoint]), " ".join(words[midpoint:])]
    return r"\N".join(lines)


def build_ass(job: str, cta: str, total: float, audio_delay: float = 0.22) -> Path:
    qa = PROD / job / "voice" / "qa" / "SCRIBE_CONTENT_QA.json"
    data = json.loads(qa.read_text(encoding="utf-8"))
    words = [row for row in data["transcription"].get("words", []) if str(row.get("text", "")).strip()]
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
        stop = token.rstrip().endswith((".", "?", "!", ":", ";")) or end - start >= 1.85
        if stop:
            chunks.append(current)
            current = []
    if current:
        chunks.append(current)

    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Caption,Arial,62,&H00F5F2EB,&H00F5F2EB,&H00101014,&H8C000000,-1,0,0,0,100,100,0,0,1,5,2,2,105,210,420,1
Style: CTA,Segoe UI Semibold,42,&H00C7C28D,&H00C7C28D,&H00101014,&H9A000000,-1,0,0,0,100,100,0,0,1,4,1,8,80,210,170,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = [header]
    for chunk in chunks:
        start = float(chunk[0].get("start", 0.0) or 0.0) + audio_delay
        end = float(chunk[-1].get("end", start + 0.2) or start + 0.2) + audio_delay
        safe_text = escape_ass(" ".join(str(row.get("text", "")).strip() for row in chunk))
        words_text = wrap_caption(safe_text)
        lines.append(f"Dialogue: 0,{ass_time(start)},{ass_time(end)},Caption,,0,0,0,,{words_text}\n")
    cta_start = max(0.0, total - 2.8)
    lines.append(f"Dialogue: 1,{ass_time(cta_start)},{ass_time(total)},CTA,,0,0,0,,{escape_ass(cta)}\n")
    out = PROD / job / "captions.ass"
    out.write_text("".join(lines), encoding="utf-8-sig")
    return out


def make_bed(seconds: float, path: Path) -> None:
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "lavfi", "-i", f"sine=frequency=48:duration={seconds:.3f}",
        "-f", "lavfi", "-i", f"sine=frequency=73:duration={seconds:.3f}",
        "-f", "lavfi", "-i", f"anoisesrc=d={seconds:.3f}:c=brown:a=0.04",
        "-filter_complex",
        "[0:a]volume=0.11[a];[1:a]volume=0.045[b];[2:a]lowpass=f=460,volume=0.24[c];"
        "[a][b][c]amix=inputs=3:normalize=0,afade=t=in:st=0:d=1.2,"
        f"afade=t=out:st={max(0.0, seconds-1.4):.3f}:d=1.4[out]",
        "-map", "[out]", "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", str(path),
    ])


def render(job: str, spec: dict, reuse_visual: bool = False) -> dict:
    split_triptych(job)
    missing = [str(path) for path in spec["images"] if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing visual sources:\n" + "\n".join(missing))

    work = PROD / job / "render"
    frames = work / "frames"
    segments = work / "segments"
    frames.mkdir(parents=True, exist_ok=True)
    segments.mkdir(parents=True, exist_ok=True)
    voice = PROD / job / "voice" / f"{job}_GEORGE.mp3"
    total = duration(voice) + 0.45
    shot_dur = total / len(spec["images"])

    visual = work / "visual.mp4"
    if not (reuse_visual and visual.is_file()):
        segment_paths = []
        for index, source in enumerate(spec["images"]):
            frame = frames / f"{index:02d}.jpg"
            vertical_frame(source, frame, spec["hook"] if index == 0 else None)
            segment = segments / f"{index:02d}.mp4"
            frames_count = max(1, round(shot_dur * FPS))
            zoom_start = 1.0 + (index % 3) * 0.006
            zoom_delta = 0.045 if index % 2 == 0 else 0.032
            run([
                "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                "-framerate", str(FPS), "-loop", "1", "-i", str(frame),
                "-vf",
                f"scale=2160:3840,zoompan=z='{zoom_start:.4f}+{zoom_delta:.4f}*on/{frames_count}':"
                f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS},"
                "eq=contrast=1.025:saturation=0.98,format=yuv420p",
                "-t", f"{shot_dur:.5f}", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                "-r", str(FPS), str(segment),
            ])
            segment_paths.append(segment)

        concat = work / "concat.txt"
        concat.write_text("\n".join(f"file '{path.as_posix()}'" for path in segment_paths) + "\n", encoding="utf-8")
        run([
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-f", "concat", "-safe", "0", "-i", str(concat),
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
            "-pix_fmt", "yuv420p", "-r", str(FPS), "-an", str(visual),
        ])

    captions = build_ass(job, spec["cta"], total)
    captioned = work / "captioned.mp4"
    relative_ass = captions.relative_to(ROOT).as_posix().replace(":", "\\:")
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(visual), "-vf", f"ass='{relative_ass}'",
        "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
        "-pix_fmt", "yuv420p", "-r", str(FPS), str(captioned),
    ])

    bed = work / "soundbed.wav"
    make_bed(total, bed)
    final_dir = PROD / job / "final"
    final_dir.mkdir(parents=True, exist_ok=True)
    final = final_dir / f"{job}_FINAL.mp4"
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(captioned), "-i", str(voice), "-i", str(bed),
        "-filter_complex",
        f"[1:a]adelay=220|220,apad=whole_dur={total:.3f},pan=stereo|c0=c0|c1=c0,asplit=2[voice][key];"
        "[2:a][key]sidechaincompress=threshold=0.018:ratio=7:attack=12:release=300[duck];"
        "[voice][duck]amix=inputs=2:normalize=0:duration=first,"
        f"atrim=0:{total:.3f},aresample=192000,alimiter=limit=.89,aresample=48000,"
        "loudnorm=I=-14:TP=-1.5:LRA=10[a]",
        "-map", "0:v:0", "-map", "[a]", "-c:v", "copy",
        "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-ac", "2",
        "-t", f"{total:.3f}", "-movflags", "+faststart", str(final),
    ])
    return {
        "file": str(final),
        "duration": round(duration(final), 3),
        "resolution": f"{W}x{H}",
        "fps": FPS,
        "voice": "George",
        "voice_id": "JBFqnCBsd6RMkjVDRZzb",
        "continuous_voice_file": str(voice),
        "visual_sources": len(spec["images"]),
        "unique_visual_sources": len({str(path) for path in spec["images"]}),
        "captions": "word-timed from independent Scribe transcription",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", choices=tuple(SHORTS))
    parser.add_argument("--reuse-visual", action="store_true")
    args = parser.parse_args()
    report = {}
    for job, spec in SHORTS.items():
        if args.only and job != args.only:
            continue
        print(f"--- {job} ---", flush=True)
        report[job] = render(job, spec, reuse_visual=args.reuse_visual)
        print(json.dumps(report[job], ensure_ascii=False), flush=True)
    report_path = PROD / "FINAL_QA.json"
    existing = {}
    if report_path.is_file():
        existing = json.loads(report_path.read_text(encoding="utf-8"))
    existing.update(report)
    report_path.write_text(json.dumps(existing, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
