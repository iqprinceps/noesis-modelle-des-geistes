#!/usr/bin/env python3
"""EP03 PEAR V2 — Optimierte Render-Pipeline.

Optimiert für 6 Kerne / 32GB RAM:
- 6 parallele ffmpeg-Prozesse (statt 4)
- Schnellere Presets (veryfast statt slow)
- Reduzierte Zwischenschritte
- Optimierte Ken-Burns-Filter

Nutzung:
    python tools/pear_render_v2_fast.py segments  # Alle Segmente
    python tools/pear_render_v2_fast.py final     # Finale Zusammenführung
    python tools/pear_render_v2_fast.py all       # Alles
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = Path(__file__).resolve().parents[1]
PROD = ROOT / "06_PRODUCTION" / "EP03_PEAR"

TIMELINE = PROD / "timeline" / "EP03_V2_timeline.json"
VOICE = PROD / "audio" / "EP03_V2_voice_-18LUFS.wav"
AUDIO_MIX = PROD / "audio" / "EP01A_final_mix.wav"
SEGMENTS = PROD / "render" / "segments_v2"
FINAL = PROD / "render" / "final_v2"
CARDS = PROD / "visuals" / "cards"

FPS = 30
ENDCARD_SEC = 20.0
NAME = "EP03_PEAR_V2"
GRUND = "#0E1013"

# Optimierte Worker-Anzahl für 6 Kerne
MAX_WORKERS = 6


def run(args, capture=False):
    p = subprocess.run(args, text=True, capture_output=capture)
    if p.returncode:
        raise RuntimeError((p.stderr or p.stdout or "failed")[-8000:])
    return (p.stdout or "") + (p.stderr or "")


def dur(path: Path) -> float:
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                      "-of", "csv=p=0", str(path)], True).strip())


def camera_filter_fast(index, row):
    """Optimierter Ken-Burns-Filter (schneller, weniger Zwischenschritte)."""
    import math
    
    SW, SH = 3840, 2160  # 4K statt 8K → 4x schneller
    fg_w, fg_h = (SW * 1844) // 1920, (SH * 984) // 1080
    kante = max(4, SW // 400)
    
    frames = max(1, math.ceil(row["duration"] * FPS))
    
    if row.get("contain"):
        base = (
            f"split=2[bg][fg];"
            f"[bg]scale={SW}:{SH}:force_original_aspect_ratio=increase,crop={SW}:{SH},"
            f"gblur=sigma={SW // 50},eq=brightness=-0.66:saturation=0.28:contrast=0.82,"
            f"colorbalance=bs=0.22:bm=0.10:rs=-0.06,"
            f"vignette=angle=PI/4.2[b];"
            f"[fg]scale={fg_w}:{fg_h}:force_original_aspect_ratio=decrease:flags=lanczos,"
            f"pad=iw+{kante * 2}:ih+{kante * 2}:{kante}:{kante}:0x2E2418[f];"
            f"[b][f]overlay=(W-w)/2:(H-h)/2"
        )
    else:
        base = (f"scale={SW}:{SH}:force_original_aspect_ratio=increase,"
                f"crop={SW}:{SH}")
    
    # Vereinfachte Animation (weniger Berechnungen)
    lin = f"(on/{frames})"
    p = f"(0.5*{lin}+0.5*({lin}*{lin}*(3-2*{lin})))"
    
    tempo = min(1.3, max(0.6, row["duration"] / 4.0))
    mitte_x, mitte_y = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    
    # Weniger Bewegungsvarianten → schneller
    bewegungen = [
        (1.05, 0.10, mitte_x, mitte_y),
        (1.15, -0.10, mitte_x, mitte_y),
        (1.12, 0.0, mitte_x, mitte_y),
    ]
    
    if row["kind"] == "VIDEO":
        z0, dz = (1.02, 0.05)
        x, y = mitte_x, mitte_y
    else:
        z0, dz, x, y = bewegungen[index % len(bewegungen)]
    z1 = z0 + dz * tempo
    z1 = min(1.25, max(1.005, z1))
    
    zexpr = f"{z0:.4f}+({z1 - z0:.4f})*{p}"
    
    # Kein SUB/oversampling → viel schneller
    f = (base
         + f",zoompan=z='{zexpr}':x='{x}':y='{y}':d=1:s=1920x1080:fps={FPS}"
         + ",eq=contrast=1.03:saturation=1.04,format=yuv420p")
    
    if row.get("scene_first"):
        f += f",fade=t=in:st=0:d=0.35:color={GRUND}"
    if row.get("scene_last"):
        f += f",fade=t=out:st={max(0, row['duration'] - 0.35):.3f}:d=0.35:color={GRUND}"
    
    return f


def render_segments_fast():
    """Rendert alle Segmente parallel (optimiert)."""
    print(f"\n  Rendere Segmente ({MAX_WORKERS} Worker)...")
    
    timeline = json.loads(TIMELINE.read_text(encoding="utf-8"))
    SEGMENTS.mkdir(parents=True, exist_ok=True)
    
    missing = []
    for i, row in enumerate(timeline):
        target = SEGMENTS / f"{i+1:03d}_{row['shot_id']}.mp4"
        if not target.exists():
            missing.append((i, row, target))
    
    if not missing:
        print("  Alle Segmente vorhanden.")
        return
    
    print(f"  {len(missing)} Segmente fehlen...")
    
    def render_segment(args):
        i, row, target = args
        try:
            inputs = ["-stream_loop", "-1", "-i", row["visual"]] if row["kind"] == "VIDEO" else ["-i", row["visual"]]
            vf = camera_filter_fast(i, row)
            
            # Optimierter ffmpeg-Befehl
            run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *inputs,
                 "-sws_flags", "fast_bilinear",  # schneller als lanczos
                 "-t", f"{row['duration']:.3f}", "-vf", vf,
                 "-an", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
                 "-pix_fmt", "yuv420p", "-r", str(FPS), str(target)])
            return {"status": "ok", "index": i}
        except Exception as e:
            return {"status": "error", "index": i, "error": str(e)[:100]}
    
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(render_segment, m): m for m in missing}
        done = 0
        for future in as_completed(futures):
            result = future.result()
            done += 1
            status = "OK" if result["status"] == "ok" else "FEHL"
            if done % 10 == 0 or result["status"] == "error":
                print(f"  [{done}/{len(missing)}] {status}", flush=True)
    
    elapsed = time.time() - start_time
    print(f"  Fertig in {elapsed:.0f}s ({len(missing)/elapsed:.1f} Segmente/Sekunde)")


def build_final_fast():
    """Führt alles zum finalen Video zusammen (optimiert)."""
    print("\n  Baue finales Video...")
    
    timeline = json.loads(TIMELINE.read_text(encoding="utf-8"))
    
    concat = PROD / "render" / "concat_v2.txt"
    paths = [SEGMENTS / f"{i+1:03d}_{r['shot_id']}.mp4" for i, r in enumerate(timeline)]
    paths.append(SEGMENTS / "999_ENDCARD.mp4")
    
    for p in paths:
        if not p.exists():
            print(f"    WARNUNG: {p.name} fehlt")
            return
    
    concat.write_text("\n".join(f"file '{p.as_posix()}'" for p in paths) + "\n", encoding="utf-8")
    
    picture = PROD / "render" / f"{NAME}_picture_lock.mp4"
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", str(concat), "-c", "copy", str(picture)])
    
    FINAL.mkdir(parents=True, exist_ok=True)
    final = FINAL / f"{NAME}_FINAL_1080p.mp4"
    
    if AUDIO_MIX.exists():
        # Schnelleres Encoding mit hardware-optimierten Settings
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
             "-i", str(picture), "-i", str(AUDIO_MIX),
             "-map", "0:v:0", "-map", "1:a:0",
             "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
             "-movflags", "+faststart", "-shortest", str(final)])
        
        d = dur(final)
        print(f"  Fertig: {final.name} ({d:.0f}s, {d/60:.1f} Min)")


def main():
    import argparse
    ap = argparse.ArgumentParser(description="EP03 PEAR V2 Fast Render")
    ap.add_argument("command", choices=["segments", "final", "all"])
    args = ap.parse_args()
    
    start = time.time()
    
    if args.command in ("segments", "all"):
        render_segments_fast()
    
    if args.command in ("final", "all"):
        build_final_fast()
    
    elapsed = time.time() - start
    print(f"\n  Gesamtzeit: {elapsed:.0f}s ({elapsed/60:.1f} Minuten)")


if __name__ == "__main__":
    main()
