#!/usr/bin/env python3
"""EP03 PEAR V2 — Render mit 6 Workers."""

import json
import sys
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pear_render_v2 import camera_filter, run, dur, FPS, GRUND

PROD = Path(__file__).resolve().parents[1] / "06_PRODUCTION" / "EP03_PEAR"
TIMELINE = PROD / "timeline" / "EP03_V2_timeline.json"
SEGMENTS = PROD / "render" / "segments_v2"
CARDS = PROD / "visuals" / "cards"
ENDCARD_SEC = 20.0


def render_segment(args):
    i, row, target = args
    try:
        if row["kind"] == "VIDEO":
            inputs = ["-stream_loop", "-1", "-i", row["visual"]]
        else:
            inputs = ["-i", row["visual"]]
        
        vf = camera_filter(i, row)
        
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *inputs,
             "-sws_flags", "lanczos+accurate_rnd+full_chroma_int",
             "-t", str(row["duration"]), "-vf", vf,
             "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
             "-pix_fmt", "yuv420p", "-r", str(FPS), str(target)])
        return {"status": "ok", "index": i}
    except Exception as e:
        return {"status": "error", "index": i, "error": str(e)[:100]}


def main():
    timeline = json.loads(TIMELINE.read_text(encoding="utf-8"))
    SEGMENTS.mkdir(parents=True, exist_ok=True)
    
    # Check which segments are missing
    tasks = []
    for i, row in enumerate(timeline):
        target = SEGMENTS / f"{i+1:03d}_{row['shot_id']}.mp4"
        if not target.exists():
            tasks.append((i, row, target))
    
    if not tasks:
        print("Alle Segmente vorhanden.")
        return
    
    print(f"Rendere {len(tasks)} Segmente mit 6 Workers...")
    
    start = time.time()
    
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(render_segment, t): t for t in tasks}
        done = 0
        errors = 0
        for future in as_completed(futures):
            result = future.result()
            done += 1
            if result["status"] == "error":
                errors += 1
                print(f"  FEHLER Segment {result['index']+1}: {result['error']}")
            elif done % 20 == 0:
                print(f"  [{done}/{len(tasks)}]", flush=True)
    
    elapsed = time.time() - start
    print(f"Fertig in {elapsed:.0f}s ({len(tasks)/elapsed:.1f} Segmente/Sekunde)")
    if errors:
        print(f"  {errors} Fehler!")
    
    # Render endcard
    endcard = SEGMENTS / "999_ENDCARD.mp4"
    if not endcard.exists():
        print("Rendere Endcard...")
        endcard_src = CARDS / "PE_V2_ENDCARD.png"
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
             "-loop", "1", "-framerate", str(FPS), "-i", str(endcard_src),
             "-t", str(ENDCARD_SEC),
             "-vf", f"scale=1920:1080,fade=t=in:st=0:d=0.6,fade=t=out:st={ENDCARD_SEC-1.2:.2f}:d=1.2,format=yuv420p",
             "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
             "-pix_fmt", "yuv420p", "-r", str(FPS), str(endcard)])
        print("Endcard fertig.")


if __name__ == "__main__":
    main()
