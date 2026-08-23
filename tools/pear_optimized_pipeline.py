#!/usr/bin/env python3
"""EP03 PEAR V2 — Optimierte Production Pipeline.

Komplett optimiert für maximale Effizienz:
- Parallele Voice-Generierung (8 Stems gleichzeitig)
- Parallele Bildgenerierung (4 Workers)
- Optimierte Timeline mit vorgebauten Segmenten
- Effizientes Audio-Mixing
- Schneller Render mit parallelen Segmenten

Nutzung:
    python tools/pear_optimized_pipeline.py all      # Alles optimiert
    python tools/pear_optimized_pipeline.py voices   # Nur Voice
    python tools/pear_optimized_pipeline.py images   # Nur Bilder
    python tools/pear_optimized_pipeline.py render   # Nur Render
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = Path(__file__).resolve().parents[1]
NOESIS = ROOT.parent / "NOESIS Channel"
PROD = ROOT / "06_PRODUCTION" / "EP03_PEAR"

# V2 Pfade
CLEAN_V2 = PROD / "07_VOICE_SCRIPT_CLEAN_V2.txt"
BATCH_V2 = PROD / "voice" / "voice_batch_v2.json"
VOICE_V2 = PROD / "audio" / "EP03_V2_voice_-18LUFS.wav"
ALIGNMENT_V2 = PROD / "voice" / "alignment" / "EP03_V2_alignment.json"
TIMELINE_V2 = PROD / "timeline" / "EP03_V2_timeline.json"

# Output Pfade
AUDIO_V2 = PROD / "audio"
SEGMENTS_V2 = PROD / "render" / "segments_v2"
FINAL_V2 = PROD / "render" / "final_v2"
CARDS = PROD / "visuals" / "cards"
GEN = PROD / "visuals" / "generated"

# Konstanten
FPS = 30
ENDCARD_SEC = 20.0
NAME = "EP03_PEAR_V2"


def run(args, capture=False):
    p = subprocess.run(args, text=True, capture_output=capture)
    if p.returncode:
        raise RuntimeError((p.stderr or p.stdout or "failed")[-8000:])
    return (p.stdout or "") + (p.stderr or "")


def dur(path: Path) -> float:
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                      "-of", "csv=p=0", str(path)], True).strip())


# ================================================================ VOICE (Parallel)

def generate_voices_parallel():
    """Voice Stems parallel generieren."""
    print("\n" + "="*60)
    print("VOICE GENERATION (Parallel)")
    print("="*60)
    
    batch = json.loads(BATCH_V2.read_text(encoding="utf-8"))
    output_dir = Path(batch["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Prüfe welche Stems fehlen
    missing = []
    for stem in batch["stems"]:
        output = output_dir / f"{stem['id']}.mp3"
        if not output.exists():
            missing.append(stem)
    
    if not missing:
        print("  Alle Stems vorhanden.")
        return
    
    print(f"  {len(missing)} Stems fehlen, generiere parallel...")
    
    # Importiere ElevenLabs CLI
    sys.path.insert(0, str(NOESIS / "tools"))
    try:
        from elevenlabs_cli import generate_stems
    except ImportError:
        print("  WARNUNG: ElevenLabs CLI nicht verfügbar. Stems manuell generieren.")
        return
    
    # Parallele Generierung
    def generate_single_stem(stem):
        text_file = Path(stem["text_file"])
        text = text_file.read_text(encoding="utf-8").strip()
        output = output_dir / f"{stem['id']}.mp3"
        try:
            generate_stems(text, output, batch["voice"], batch["settings"])
            return {"status": "ok", "id": stem["id"], "file": output.name}
        except Exception as e:
            return {"status": "error", "id": stem["id"], "error": str(e)[:200]}
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(generate_single_stem, s): s for s in missing}
        for future in as_completed(futures):
            result = future.result()
            status = "OK" if result["status"] == "ok" else "FEHL"
            print(f"  {result['id']:30} {status}")


def build_voice_master():
    """Voice Master aus Stems bauen."""
    print("\n  Baue Voice Master...")
    
    batch = json.loads(BATCH_V2.read_text(encoding="utf-8"))
    stems_dir = PROD / "voice" / "master" / "stems_v2"
    stems_dir.mkdir(parents=True, exist_ok=True)
    
    # Concat-Datei erstellen
    lines = []
    for i, stem in enumerate(batch["stems"]):
        src = Path(batch["output_dir"]) / f"{stem['id']}.mp3"
        if not src.exists():
            print(f"    WARNUNG: {src.name} fehlt")
            continue
        
        # Normalisieren
        dst = stems_dir / f"{stem['id']}.wav"
        if not dst.exists():
            run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                 "-i", str(src), "-af", "loudnorm=I=-18:TP=-2:LRA=7",
                 "-ac", "1", "-ar", "48000", "-c:a", "pcm_s24le", str(dst)])
        
        lines.append(f"file '{dst.as_posix()}'")
        
        # Pause zwischen Stems
        if i < len(batch["stems"]) - 1:
            gap = stems_dir / f"gap_{i+1:02d}.wav"
            if not gap.exists():
                run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                     "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono:d=0.65",
                     "-c:a", "pcm_s24le", str(gap)])
            lines.append(f"file '{gap.as_posix()}'")
    
    # Concat
    concat_file = stems_dir / "concat.txt"
    concat_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    
    master = PROD / "voice" / "master" / "EP03_V2_VO_MASTER.wav"
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-f", "concat", "-safe", "0", "-i", str(concat_file),
         "-c:a", "pcm_s24le", str(master)])
    
    # Producer Voice
    producer = AUDIO_V2 / "EP03_V2_voice_-18LUFS.wav"
    import shutil
    shutil.copy2(master, producer)
    
    d = dur(master)
    print(f"  Voice Master: {d:.2f}s ({int(d//60)}:{d%60:04.1f})")
    return d


# ================================================================ IMAGES (Parallel)

def generate_images_parallel():
    """Alle Bilder parallel generieren."""
    print("\n" + "="*60)
    print("IMAGE GENERATION (Parallel)")
    print("="*60)
    
    # Hauptbilder
    print("\n  Generiere Hauptbilder (8 Stück)...")
    run([sys.executable, str(NOESIS / "tools" / "pear_parallel_images.py"),
         "--batch", "EP03_PEAR_V2.json", "--modell", "flash", "--workers", "4",
         "--varianten", "1", "--execute"])
    
    # Cards
    print("\n  Generiere Cards (5 Stück)...")
    run([sys.executable, str(NOESIS / "tools" / "pear_parallel_images.py"),
         "--batch", "EP03_PEAR_V2_CARDS.json", "--modell", "flash", "--workers", "3",
         "--varianten", "1", "--execute"])
    
    # Kopiere Ergebnisse
    print("\n  Kopiere Ergebnisse...")
    import shutil
    
    # Hauptbilder
    src_gen = NOESIS / "werkbank" / "EP03_PEAR_V2_generated"
    dst_gen = PROD / "visuals" / "generated"
    for f in src_gen.glob("*.png"):
        shutil.copy2(f, dst_gen / f.name)
    
    # Cards
    src_cards = NOESIS / "werkbank" / "EP03_PEAR_V2_cards"
    dst_cards = PROD / "visuals" / "cards"
    for f in src_cards.glob("*.png"):
        shutil.copy2(f, dst_cards / f.name)
    
    print("  Bilder kopiert.")


# ================================================================ TIMELINE

def build_timeline():
    """Timeline für V2 bauen."""
    print("\n" + "="*60)
    print("TIMELINE BUILD")
    print("="*60)
    
    if not ALIGNMENT_V2.exists():
        print("  WARNUNG: Alignment fehlt. Erst Voice generieren.")
        return
    
    # Importiere Timeline-Builder
    sys.path.insert(0, str(ROOT / "tools"))
    from pear_produce_v2 import build_timeline as build_v2_timeline
    build_v2_timeline()


# ================================================================ AUDIO

def build_audio():
    """Audio mischen."""
    print("\n" + "="*60)
    print("AUDIO MIX")
    print("="*60)
    
    sys.path.insert(0, str(ROOT / "tools"))
    from pear_produce import build_audio as build_audio_mix
    build_audio_mix()


# ================================================================ RENDER (Parallel Segments)

def render_parallel():
    """Video mit parallelen Segmenten rendern."""
    print("\n" + "="*60)
    print("VIDEO RENDER (Parallel Segments)")
    print("="*60)
    
    if not TIMELINE_V2.exists():
        print("  WARNUNG: Timeline fehlt.")
        return
    
    timeline = json.loads(TIMELINE_V2.read_text(encoding="utf-8"))
    SEGMENTS_V2.mkdir(parents=True, exist_ok=True)
    
    # Prüfe welche Segmente fehlen
    missing = []
    for i, row in enumerate(timeline):
        target = SEGMENTS_V2 / f"{i+1:03d}_{row['shot_id']}.mp4"
        if not target.exists():
            missing.append((i, row, target))
    
    if not missing:
        print("  Alle Segmente vorhanden.")
    else:
        print(f"  {len(missing)} Segmente fehlen, rendere parallel...")
        
        # Importiere Render-Funktionen
        sys.path.insert(0, str(ROOT / "tools"))
        from pear_produce import camera_filter
        
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
    
    # Endcard rendern
    endcard = SEGMENTS_V2 / "999_ENDCARD.mp4"
    if not endcard.exists():
        print("  Rendere Endcard...")
        endcard_src = CARDS / "PE_V2_ENDCARD.png"
        if endcard_src.exists():
            run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                 "-loop", "1", "-framerate", str(FPS), "-i", str(endcard_src),
                 "-t", f"{ENDCARD_SEC:.3f}",
                 "-vf", f"scale=1920:1080,fade=t=in:st=0:d=0.6,fade=t=out:st={ENDCARD_SEC-1.2:.2f}:d=1.2,format=yuv420p",
                 "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
                 "-pix_fmt", "yuv420p", "-r", str(FPS), str(endcard)])
    
    # Finale Zusammenführung
    print("  Führe finale Zusammenführung durch...")
    concat = PROD / "render" / "concat_v2.txt"
    paths = [SEGMENTS_V2 / f"{i+1:03d}_{r['shot_id']}.mp4" for i, r in enumerate(timeline)] + [endcard]
    
    # Prüfe alle Segmente
    for p in paths:
        if not p.exists():
            print(f"    WARNUNG: {p.name} fehlt")
            return
        dur(p)
    
    concat.write_text("\n".join(f"file '{p.as_posix()}'" for p in paths) + "\n", encoding="utf-8")
    
    picture = PROD / "render" / f"{NAME}_picture_lock.mp4"
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", str(concat), "-c", "copy", str(picture)])
    
    # Audio hinzufügen
    FINAL_V2.mkdir(parents=True, exist_ok=True)
    final = FINAL_V2 / f"{NAME}_FINAL_1080p.mp4"
    audio_mix = AUDIO_V2 / "EP01A_final_mix.wav"
    
    if audio_mix.exists():
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
             "-i", str(picture), "-i", str(audio_mix),
             "-map", "0:v:0", "-map", "1:a:0",
             "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
             "-movflags", "+faststart", "-shortest", str(final)])
        print(f"  Fertig: {final}")
    else:
        print("  WARNUNG: Audio-Mix fehlt.")


# ================================================================ QA

def qa():
    """Quality Assurance."""
    print("\n" + "="*60)
    print("QUALITY ASSURANCE")
    print("="*60)
    
    final = FINAL_V2 / f"{NAME}_FINAL_1080p.mp4"
    if not final.exists():
        print("  WARNUNG: Finale Datei fehlt.")
        return
    
    probe = json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-show_format",
                            "-of", "json", str(final)], True))
    vs = next(x for x in probe["streams"] if x["codec_type"] == "video")
    au = next(x for x in probe["streams"] if x["codec_type"] == "audio")
    
    dd = float(probe["format"]["duration"])
    timeline = json.loads(TIMELINE_V2.read_text(encoding="utf-8")) if TIMELINE_V2.exists() else []
    
    checks = {
        "1080p": vs.get("width") == 1920 and vs.get("height") == 1080,
        "h264": vs.get("codec_name") == "h264",
        "aac_48k": au.get("codec_name") == "aac" and au.get("sample_rate") == "48000",
        "30fps": vs.get("r_frame_rate") == "30/1",
        "dauer_ok": dd > 600,  # Mindestens 10 Minuten
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


# ================================================================ MAIN

def main():
    ap = argparse.ArgumentParser(description="EP03 PEAR V2 Optimized Pipeline")
    ap.add_argument("command", choices=["voices", "images", "timeline", "audio", 
                                        "render", "qa", "all"])
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    
    start_time = time.time()
    
    if args.command in ("voices", "all"):
        generate_voices_parallel()
        build_voice_master()
    
    if args.command in ("images", "all"):
        generate_images_parallel()
    
    if args.command in ("timeline", "all"):
        build_timeline()
    
    if args.command in ("audio", "all"):
        build_audio()
    
    if args.command in ("render", "all"):
        render_parallel()
    
    if args.command in ("qa", "all"):
        qa()
    
    elapsed = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"GESAMTZEIT: {elapsed:.0f}s ({elapsed/60:.1f} Minuten)")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
