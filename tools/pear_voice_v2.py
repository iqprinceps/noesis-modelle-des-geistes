#!/usr/bin/env python3
"""EP03 PEAR V2 — Einzelne Voice-Stems generieren.

Generiert jeden Stem einzeln, damit bei Fehlern einzelne ersetzt werden können.
Nutzt die gleichen Einstellungen wie die bestehende Pipeline.

Nutzung:
    python tools/pear_voice_v2.py                    # Alle fehlenden Stems
    python tools/pear_voice_v2.py --only EP03_V2_01_PARADOXON  # Nur einen
    python tools/pear_voice_v2.py --force             # Alle neu generieren
    python tools/pear_voice_v2.py --master            # Master bauen
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = Path(__file__).resolve().parents[1]
NOESIS = ROOT.parent / "NOESIS Channel"
PROD = ROOT / "06_PRODUCTION" / "EP03_PEAR"

# V2 Pfade
BATCH_V2 = PROD / "voice" / "voice_batch_v2.json"
RAW_STEMS = PROD / "voice" / "raw_stems"
STEMS_DIR = PROD / "voice" / "master" / "stems_v2"
MASTER = PROD / "voice" / "master" / "EP03_V2_VO_MASTER.wav"
VOICE_OUT = PROD / "audio" / "EP03_V2_voice_-18LUFS.wav"

# Pausen zwischen Stems
PRE = 0.35
GAP = 0.65
TAIL = 2.2


def run(args, capture=False):
    p = subprocess.run(args, text=True, capture_output=capture)
    if p.returncode:
        raise RuntimeError((p.stderr or p.stdout or "failed")[-8000:])
    return (p.stdout or "") + (p.stderr or "")


def dur(path: Path) -> float:
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                      "-of", "csv=p=0", str(path)], True).strip())


def loudness(path: Path, i=-18.0, tp=-2.0) -> dict:
    import re
    out = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path),
               "-af", f"loudnorm=I={i}:TP={tp}:LRA=7:print_format=json",
               "-f", "null", "-"], True)
    return json.loads(re.findall(r'\{\s*"input_i".*?\}', out, re.S)[-1])


def normalize(src: Path, dst: Path, i=-18.0, tp=-2.0):
    st = loudness(src, i, tp)
    dst.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(src),
         "-af", (f"loudnorm=I={i}:TP={tp}:LRA=7:measured_I={st['input_i']}:"
                 f"measured_TP={st['input_tp']}:measured_LRA={st['input_lra']}:"
                 f"measured_thresh={st['input_thresh']}:offset={st['target_offset']}:linear=true"),
         "-ac", "1", "-ar", "48000", "-c:a", "pcm_s24le", str(dst)])


def silence(path: Path, seconds: float):
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "lavfi",
         "-i", f"anullsrc=r=48000:cl=mono:d={seconds}", "-c:a", "pcm_s24le", str(path)])


def generate_single_stem(stem_id: str, text: str, voice_id: str, settings: dict,
                         model: str = "eleven_multilingual_v2", seed: int = 2402) -> dict:
    """Generiert einen einzelnen Stem über ElevenLabs API."""
    sys.path.insert(0, str(NOESIS / "tools"))
    from elevenlabs_cli import _generate, _resolve_voice
    
    voice = _resolve_voice(voice_id)
    output = RAW_STEMS / f"{stem_id}.mp3"
    
    result = _generate(
        voice=voice,
        text=text,
        output=output,
        model=model,
        stability=settings["stability"],
        similarity=settings["similarity_boost"],
        style=settings["style"],
        speed=settings["speed"],
        speaker_boost=settings["use_speaker_boost"],
        output_format="mp3_44100_128",
        seed=seed,
    )
    
    return result


def generate_all_stems(force: bool = False, only: list[str] = None, workers: int = 1):
    """Generiert alle fehlenden Stems."""
    batch = json.loads(BATCH_V2.read_text(encoding="utf-8"))
    voice_id = batch["voice"]
    settings = batch["settings"]
    model = batch.get("model", "eleven_multilingual_v2")
    seed = batch.get("seed", 2402)
    
    RAW_STEMS.mkdir(parents=True, exist_ok=True)
    
    # Prüfe welche Stems fehlen
    stems_to_generate = []
    for stem in batch["stems"]:
        stem_id = stem["id"]
        output = RAW_STEMS / f"{stem_id}.mp3"
        
        if only and stem_id not in only:
            continue
        
        if output.exists() and not force:
            print(f"  {stem_id:35} vorhanden")
            continue
        
        text_file = Path(stem["text_file"])
        if not text_file.exists():
            print(f"  {stem_id:35} FEHLT (Textdatei)")
            continue
        
        text = text_file.read_text(encoding="utf-8").strip()
        stems_to_generate.append({
            "id": stem_id,
            "text": text,
            "text_file": text_file,
        })
    
    if not stems_to_generate:
        print("  Alle Stems vorhanden.")
        return
    
    print(f"\n  Generiere {len(stems_to_generate)} Stems...")
    print(f"  Voice: {voice_id}")
    print(f"  Model: {model}")
    print(f"  Seed: {seed}")
    
    # Generiere Stems
    results = []
    errors = 0
    
    for i, stem in enumerate(stems_to_generate, 1):
        stem_id = stem["id"]
        print(f"\n  [{i}/{len(stems_to_generate)}] {stem_id}")
        print(f"    Text: {stem['text'][:80]}...")
        
        try:
            result = generate_single_stem(
                stem_id=stem_id,
                text=stem["text"],
                voice_id=voice_id,
                settings=settings,
                model=model,
                seed=seed,
            )
            results.append({"status": "ok", "id": stem_id, "file": result["file"]})
            print(f"    OK: {result['file']}")
            print(f"    Dauer: {result['characters']} Zeichen")
            
            # Pause zwischen Stems
            if i < len(stems_to_generate):
                time.sleep(1)
                
        except Exception as e:
            results.append({"status": "error", "id": stem_id, "error": str(e)[:200]})
            print(f"    FEHLER: {str(e)[:200]}")
            errors += 1
    
    # Zusammenfassung
    print(f"\n  {'='*60}")
    print(f"  Fertig: {len(stems_to_generate) - errors} von {len(stems_to_generate)} erfolgreich")
    if errors > 0:
        print(f"  Fehler: {errors}")
        print(f"  Fehlende Stems mit --force oder --only neu generieren")


def build_master():
    """Baut den Voice-Master aus den einzelnen Stems."""
    print("\n  Baue Voice Master...")
    
    batch = json.loads(BATCH_V2.read_text(encoding="utf-8"))
    STEMS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Prüfe ob alle Stems vorhanden
    missing = []
    for stem in batch["stems"]:
        src = RAW_STEMS / f"{stem['id']}.mp3"
        if not src.exists():
            missing.append(stem["id"])
    
    if missing:
        print(f"  WARNUNG: {len(missing)} Stems fehlen:")
        for m in missing:
            print(f"    - {m}")
        print(f"  Erst alle Stems generieren, dann Master bauen.")
        return
    
    # Concat-Datei erstellen
    lines = []
    
    # Vorlauf
    pre = STEMS_DIR / "pre.wav"
    silence(pre, PRE)
    lines.append(f"file '{pre.as_posix()}'")
    
    # Stems
    for i, stem in enumerate(batch["stems"]):
        src = RAW_STEMS / f"{stem['id']}.mp3"
        
        # Normalisieren
        dst = STEMS_DIR / f"{stem['id']}.wav"
        if not dst.exists():
            print(f"    Normalisiere {stem['id']}...")
            normalize(src, dst)
        
        lines.append(f"file '{dst.as_posix()}'")
        
        # Dauer anzeigen
        d = dur(dst)
        print(f"    {stem['id']:35} {d:7.2f}s")
        
        # Pause zwischen Stems
        if i < len(batch["stems"]) - 1:
            gap = STEMS_DIR / f"gap_{i+1:02d}.wav"
            if not gap.exists():
                silence(gap, GAP)
            lines.append(f"file '{gap.as_posix()}'")
    
    # Nachlauf
    tail = STEMS_DIR / "tail.wav"
    silence(tail, TAIL)
    lines.append(f"file '{tail.as_posix()}'")
    
    # Concat
    concat_file = STEMS_DIR / "concat.txt"
    concat_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    
    # Master erstellen
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-f", "concat", "-safe", "0", "-i", str(concat_file),
         "-c:a", "pcm_s24le", str(MASTER)])
    
    # Producer Voice
    import shutil
    shutil.copy2(MASTER, VOICE_OUT)
    
    # Report
    total = dur(MASTER)
    print(f"\n  Master: {total:.2f}s ({int(total//60)}:{total%60:04.1f})")
    print(f"  Datei: {MASTER}")
    print(f"  Producer: {VOICE_OUT}")
    
    # Stem Report
    stem_report = {
        "duration": round(total, 3),
        "voice": batch["voice"],
        "voice_name": batch.get("voice_name"),
        "settings": batch["settings"],
        "stems": []
    }
    
    for stem in batch["stems"]:
        dst = STEMS_DIR / f"{stem['id']}.wav"
        if dst.exists():
            d = dur(dst)
            stem_report["stems"].append({
                "id": stem["id"],
                "duration": round(d, 3)
            })
    
    report_file = PROD / "voice" / "master" / "stem_report_v2.json"
    report_file.write_text(json.dumps(stem_report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"  Report: {report_file}")


def main():
    ap = argparse.ArgumentParser(description="EP03 PEAR V2 Voice Generation")
    ap.add_argument("--force", action="store_true", help="Alle neu generieren")
    ap.add_argument("--only", nargs="*", help="Nur diese Stem-IDs")
    ap.add_argument("--master", action="store_true", help="Nur Master bauen")
    ap.add_argument("--workers", type=int, default=1, help="Parallele Worker")
    args = ap.parse_args()
    
    if args.master:
        build_master()
    else:
        generate_all_stems(force=args.force, only=args.only, workers=args.workers)
        build_master()


if __name__ == "__main__":
    main()
