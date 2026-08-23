#!/usr/bin/env python3
"""EP03 PEAR V2 — Finaler Render.

Rendert das finale Video mit:
- Timeline aus Text-Bild-Sync
- Voice-Master
- Audio-Mix
- Grafikspur (Beschriftungen + Quellzeilen)
- Endcard

Nutzung:
    python tools/pear_render_v2.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = Path(__file__).resolve().parents[1]
PROD = ROOT / "06_PRODUCTION" / "EP03_PEAR"

# Pfade
TIMELINE = PROD / "timeline" / "EP03_V2_timeline.json"
VOICE = PROD / "audio" / "EP03_V2_voice_-18LUFS.wav"
AUDIO_MIX = PROD / "audio" / "EP01A_final_mix.wav"
SEGMENTS = PROD / "render" / "segments_v2"
FINAL = PROD / "render" / "final_v2"
CARDS = PROD / "visuals" / "cards"

# Konstanten
FPS = 30
ENDCARD_SEC = 20.0
NAME = "EP03_PEAR_V2"
GRUND = "#0E1013"


def run(args, capture=False):
    p = subprocess.run(args, text=True, capture_output=capture)
    if p.returncode:
        raise RuntimeError((p.stderr or p.stdout or "failed")[-8000:])
    return (p.stdout or "") + (p.stderr or "")


def dur(path: Path) -> float:
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                      "-of", "csv=p=0", str(path)], True).strip())


def camera_filter(index, row):
    """Ken-Burns-Filter für Standbilder."""
    import math
    
    FPS = 30
    SUB = 4
    SW, SH = 7680, 4320
    fg_w, fg_h = (SW * 1844) // 1920, (SH * 984) // 1080
    kante = max(6, SW // 320)
    
    frames = max(1, math.ceil(row["duration"] * FPS)) * SUB
    
    if row.get("contain"):
        base = (
            f"split=2[bg][fg];"
            f"[bg]scale={SW}:{SH}:force_original_aspect_ratio=increase,crop={SW}:{SH},"
            f"gblur=sigma={SW // 37},eq=brightness=-0.66:saturation=0.28:contrast=0.82,"
            f"colorbalance=bs=0.22:bm=0.10:rs=-0.06,"
            f"vignette=angle=PI/4.2[b];"
            f"[fg]scale={fg_w}:{fg_h}:force_original_aspect_ratio=decrease:flags=lanczos,"
            f"pad=iw+{kante * 2}:ih+{kante * 2}:{kante}:{kante}:0x2E2418[f];"
            f"[b][f]overlay=(W-w)/2:(H-h)/2"
        )
    else:
        base = (f"scale={SW}:{SH}:force_original_aspect_ratio=increase,"
                f"crop={SW}:{SH}")
    
    lin = f"(on/{frames})"
    p = f"(0.6*{lin}+0.4*({lin}*{lin}*(3-2*{lin})))"
    
    tempo = min(1.55, max(0.50, row["duration"] / 3.6))
    mitte_x, mitte_y = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    tempo_quer = min(1.0, tempo)
    
    def quer(weg, rueckwaerts=False):
        a = 0.5 - tempo_quer / 2 if not rueckwaerts else 0.5 + tempo_quer / 2
        b = tempo_quer if not rueckwaerts else -tempo_quer
        return f"{weg}*({a:.4f}+{b:.4f}*{p})"
    
    rechts, unten = "(iw-iw/zoom)", "(ih-ih/zoom)"
    
    if row.get("contain"):
        paare = [(1.000, 0.050), (1.050, -0.050)]
        z0, dz = paare[index % len(paare)]
        z1 = z0 + dz * tempo
        x, y = mitte_x, mitte_y
    else:
        bewegungen = [
            (1.03, 0.15, mitte_x, mitte_y),
            (1.18, -0.15, mitte_x, mitte_y),
            (1.14, 0.0, quer(rechts), mitte_y),
            (1.14, 0.0, quer(rechts, True), mitte_y),
            (1.13, 0.0, mitte_x, quer(unten, True)),
            (1.05, 0.13, quer(rechts), quer(unten)),
            (1.17, -0.11, quer(rechts, True), mitte_y),
            (1.13, 0.0, mitte_x, quer(unten)),
        ]
        if row["kind"] == "VIDEO":
            z0, dz = (1.02, 0.07) if index % 2 == 0 else (1.09, -0.07)
            x, y = mitte_x, mitte_y
        else:
            z0, dz, x, y = bewegungen[index % len(bewegungen)]
        z1 = z0 + dz * tempo
    
    z1 = min(1.30, max(1.005, z1))
    zexpr = f"{z0:.4f}+({z1 - z0:.4f})*{p}"
    
    einmal = (f",loop=loop=-1:size=1:start=0,fps={FPS * SUB}"
              if row["kind"] != "VIDEO" else "")
    mittel = (f",tmix=frames={SUB}:weights='{' '.join('1' * SUB)}',fps={FPS}"
              if SUB > 1 else "")
    
    f = (base + einmal
         + f",zoompan=z='{zexpr}':x='{x}':y='{y}':d=1:s=1920x1080:fps={FPS * SUB}"
         + mittel
         + ",eq=contrast=1.03:saturation=1.04,unsharp=5:5:.24:5:5:0,format=yuv420p")
    
    if row.get("scene_first"):
        f += f",fade=t=in:st=0:d=0.35:color={GRUND}"
    if row.get("scene_last"):
        f += f",fade=t=out:st={max(0, row['duration'] - 0.35):.3f}:d=0.35:color={GRUND}"
    
    return f


def render_segments():
    """Rendert alle Segmente parallel."""
    print("\n  Rendere Segmente...")
    
    timeline = json.loads(TIMELINE.read_text(encoding="utf-8"))
    SEGMENTS.mkdir(parents=True, exist_ok=True)
    
    # Prüfe welche Segmente fehlen
    missing = []
    for i, row in enumerate(timeline):
        target = SEGMENTS / f"{i+1:03d}_{row['shot_id']}.mp4"
        if not target.exists():
            missing.append((i, row, target))
    
    if not missing:
        print("  Alle Segmente vorhanden.")
        return
    
    print(f"  {len(missing)} Segmente fehlen, rendere parallel...")
    
    def render_segment(args):
        i, row, target = args
        try:
            inputs = ["-stream_loop", "-1", "-i", row["visual"]] if row["kind"] == "VIDEO" else ["-i", row["visual"]]
            run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *inputs,
                 "-sws_flags", "lanczos+accurate_rnd+full_chroma_int",
                 "-t", f"{row['duration']:.3f}", "-vf", camera_filter(i, row),
                 "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
                 "-pix_fmt", "yuv420p", "-r", str(FPS), str(target)])
            return {"status": "ok", "index": i, "file": target.name}
        except Exception as e:
            return {"status": "error", "index": i, "error": str(e)[:200]}
    
    # Parallele Renderung (4 Worker)
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(render_segment, m): m for m in missing}
        done = 0
        for future in as_completed(futures):
            result = future.result()
            done += 1
            status = "OK" if result["status"] == "ok" else "FEHL"
            print(f"  [{done}/{len(missing)}] Segment {result['index']+1:03d} {status}", flush=True)


def render_endcard():
    """Rendert die Endcard."""
    print("\n  Rendere Endcard...")
    
    endcard = SEGMENTS / "999_ENDCARD.mp4"
    if endcard.exists():
        print("  Endcard vorhanden.")
        return
    
    endcard_src = CARDS / "PE_V2_ENDCARD.png"
    if not endcard_src.exists():
        print("  WARNUNG: Endcard-Bild fehlt.")
        return
    
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-loop", "1", "-framerate", str(FPS), "-i", str(endcard_src),
         "-t", f"{ENDCARD_SEC:.3f}",
         "-vf", f"scale=1920:1080,fade=t=in:st=0:d=0.6,fade=t=out:st={ENDCARD_SEC-1.2:.2f}:d=1.2,format=yuv420p",
         "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
         "-pix_fmt", "yuv420p", "-r", str(FPS), str(endcard)])
    
    print("  Endcard fertig.")


def build_final():
    """Führt alles zum finalen Video zusammen."""
    print("\n  Baue finales Video...")
    
    timeline = json.loads(TIMELINE.read_text(encoding="utf-8"))
    
    # Concat-Datei erstellen
    concat = PROD / "render" / "concat_v2.txt"
    paths = [SEGMENTS / f"{i+1:03d}_{r['shot_id']}.mp4" for i, r in enumerate(timeline)]
    paths.append(SEGMENTS / "999_ENDCARD.mp4")
    
    # Prüfe alle Segmente
    for p in paths:
        if not p.exists():
            print(f"    WARNUNG: {p.name} fehlt")
            return
        dur(p)
    
    concat.write_text("\n".join(f"file '{p.as_posix()}'" for p in paths) + "\n", encoding="utf-8")
    
    # Picture Lock
    picture = PROD / "render" / f"{NAME}_picture_lock.mp4"
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", str(concat), "-c", "copy", str(picture)])
    
    # Audio hinzufügen
    FINAL.mkdir(parents=True, exist_ok=True)
    final = FINAL / f"{NAME}_FINAL_1080p.mp4"
    
    if AUDIO_MIX.exists():
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
             "-i", str(picture), "-i", str(AUDIO_MIX),
             "-map", "0:v:0", "-map", "1:a:0",
             "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
             "-movflags", "+faststart", "-shortest", str(final)])
        print(f"  Fertig: {final}")
    else:
        print("  WARNUNG: Audio-Mix fehlt.")


def qa():
    """Quality Assurance."""
    print("\n  Quality Assurance...")
    
    final = FINAL / f"{NAME}_FINAL_1080p.mp4"
    if not final.exists():
        print("  WARNUNG: Finale Datei fehlt.")
        return
    
    probe = json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-show_format",
                            "-of", "json", str(final)], True))
    vs = next(x for x in probe["streams"] if x["codec_type"] == "video")
    au = next(x for x in probe["streams"] if x["codec_type"] == "audio")
    
    dd = float(probe["format"]["duration"])
    timeline = json.loads(TIMELINE.read_text(encoding="utf-8")) if TIMELINE.exists() else []
    
    checks = {
        "1080p": vs.get("width") == 1920 and vs.get("height") == 1080,
        "h264": vs.get("codec_name") == "h264",
        "aac_48k": au.get("codec_name") == "aac" and au.get("sample_rate") == "48000",
        "30fps": vs.get("r_frame_rate") == "30/1",
        "dauer_ok": dd > 600,
        "shots_vorhanden": len(timeline) > 100,
    }
    
    print(f"  Dauer: {dd:.1f}s ({int(dd//60)}:{dd%60:04.1f})")
    print(f"  Shots: {len(timeline)}")
    print(f"  Video: {vs.get('width')}x{vs.get('height')} @ {vs.get('r_frame_rate')}fps")
    print(f"  Audio: {au.get('codec_name')} {au.get('sample_rate')}Hz")
    
    for check, ok in checks.items():
        status = "OK" if ok else "FEHL"
        print(f"  {check:20} {status}")
    
    if all(checks.values()):
        print("\n  QA bestanden!")
    else:
        print("\n  QA fehlgeschlagen!")


def main():
    import argparse
    ap = argparse.ArgumentParser(description="EP03 PEAR V2 Final Render")
    ap.add_argument("command", choices=["segments", "endcard", "final", "qa", "all"])
    args = ap.parse_args()
    
    if args.command in ("segments", "all"):
        render_segments()
    
    if args.command in ("endcard", "all"):
        render_endcard()
    
    if args.command in ("final", "all"):
        build_final()
    
    if args.command in ("qa", "all"):
        qa()


if __name__ == "__main__":
    main()
