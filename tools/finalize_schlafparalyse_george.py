#!/usr/bin/env python3
"""Finalize natural George pickup batches for Schlafparalyse EP06-EP08.

This script never time-stretches speech.  It normalizes each approved pickup,
adds short natural pauses, creates a PCM24 master and optionally requests forced
alignment with the locally encrypted ElevenLabs account profile.

Generation remains a separate explicit step:
    python tools/run_ep04a_elevenlabs.py batch --batch-file <voice_batch.json> --execute

Then:
    python tools/finalize_schlafparalyse_george.py EP06 all
"""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import uuid
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
SHARED_CLI = Path.home() / "Documents" / "Codex" / "NOESIS Channel" / "tools" / "elevenlabs_cli.py"
PRODUCTION = ROOT / "06_PRODUCTION"
PROFILE = {
    "EP06": PRODUCTION / "EP06_SCHLAFPARALYSE_V4" / "VOICE_EP06",
    "EP07": PRODUCTION / "EP07_SCHLAFPARALYSE_V4" / "VOICE_EP07",
    "EP08": PRODUCTION / "EP08_SCHLAFPARALYSE_V4" / "VOICE_EP08",
}
PRE, TAKE_GAP, SECTION_GAP, TAIL = .35, .25, .65, 2.2


def run(args: list[str], capture=False) -> str:
    process = subprocess.run(args, text=True, capture_output=capture)
    if process.returncode:
        raise RuntimeError((process.stderr or process.stdout or "command failed")[-6000:])
    return (process.stdout or "") + (process.stderr or "")


def duration(path: Path) -> float:
    return float(run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "csv=p=0", str(path),
    ], True).strip())


def loudness(path: Path):
    output = run([
        "ffmpeg", "-hide_banner", "-nostats", "-i", str(path),
        "-af", "loudnorm=I=-18:TP=-2:LRA=7:print_format=json", "-f", "null", "-",
    ], True)
    matches = re.findall(r'\{\s*"input_i".*?\}', output, re.S)
    if not matches:
        raise RuntimeError(f"No loudness analysis for {path}")
    return json.loads(matches[-1])


def normalize(src: Path, dst: Path):
    stats = loudness(src)
    filt = (
        "loudnorm=I=-18:TP=-2:LRA=7:"
        f"measured_I={stats['input_i']}:measured_TP={stats['input_tp']}:"
        f"measured_LRA={stats['input_lra']}:measured_thresh={stats['input_thresh']}:"
        f"offset={stats['target_offset']}:linear=true"
    )
    dst.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(src),
         "-af", filt, "-ac", "1", "-ar", "48000", "-c:a", "pcm_s24le", str(dst)])


def silence(path: Path, seconds: float):
    path.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "lavfi",
         "-i", f"anullsrc=r=48000:cl=mono:d={seconds}", "-c:a", "pcm_s24le", str(path)])


def find_one(folder: Path, names: list[str]) -> Path:
    for name in names:
        candidate = folder / name
        if candidate.is_file():
            return candidate
    raise SystemExit(f"Missing one of {names} under {folder}")


def resolve_path(raw: str) -> Path:
    path = Path(raw)
    return path if path.is_absolute() else ROOT / path


def package(ep: str):
    voice = PROFILE[ep]
    batch = find_one(voice, ["voice_batch.json", f"{ep.lower()}_voice_batch.json", "voice_batch_v4.json"])
    clean = find_one(voice, [f"{ep}_VOICE_SCRIPT_CLEAN.txt", f"{ep}_SPRECHTEXT_CLEAN.txt"])
    manifest = voice / "take_manifest.csv"
    return voice, batch, clean, manifest


def section_map(manifest: Path):
    if not manifest.is_file():
        return {}
    with manifest.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    result = {}
    for row in rows:
        take_id = row.get("take_id") or row.get("id")
        section = row.get("act") or row.get("section") or ""
        if take_id:
            result[take_id] = section
    return result


def build_master(ep: str):
    voice, batch_path, clean, manifest = package(ep)
    batch = json.loads(batch_path.read_text(encoding="utf-8"))
    raw = resolve_path(batch.get("output_dir", str(voice / "raw_stems")))
    master_dir = voice / "master"
    stems_dir = master_dir / "stems"
    sections = section_map(manifest)
    concat_lines, report_rows = [], []
    cursor = 0.0

    pre = master_dir / "pre.wav"
    silence(pre, PRE)
    concat_lines.append(f"file '{pre.as_posix()}'")
    cursor += PRE

    items = batch.get("stems", [])
    if not items:
        raise SystemExit(f"No stems in {batch_path}")
    for index, item in enumerate(items):
        take_id = item["id"]
        src = raw / f"{take_id}.mp3"
        if not src.is_file():
            raise SystemExit(
                f"Missing raw take: {src}\nRun the documented batch command only after the account has enough credits."
            )
        dst = stems_dir / f"{take_id}.wav"
        normalize(src, dst)
        seconds = duration(dst)
        start, end = cursor, cursor + seconds
        concat_lines.append(f"file '{dst.as_posix()}'")
        section = sections.get(take_id, "")
        next_section = sections.get(items[index+1]["id"], section) if index+1 < len(items) else section
        gap = 0.0 if index+1 == len(items) else (SECTION_GAP if next_section != section else TAKE_GAP)
        report_rows.append({
            "id": take_id, "section": section, "duration": round(seconds, 3),
            "start": round(start, 3), "end": round(end, 3), "gap_after": round(gap, 3),
        })
        cursor = end
        if gap:
            gap_file = master_dir / f"gap_{index+1:02d}.wav"
            silence(gap_file, gap)
            concat_lines.append(f"file '{gap_file.as_posix()}'")
            cursor += gap

    tail = master_dir / "tail.wav"
    silence(tail, TAIL)
    concat_lines.append(f"file '{tail.as_posix()}'")
    concat = master_dir / "concat.txt"
    concat.write_text("\n".join(concat_lines)+"\n", encoding="utf-8")
    master = master_dir / f"{ep}_SCHLAFPARALYSE_GEORGE_MASTER.wav"
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat",
         "-safe", "0", "-i", str(concat), "-c:a", "pcm_s24le", str(master)])
    total = duration(master)
    report = {
        "episode": ep, "duration": round(total, 3), "master_duration": round(total, 3),
        "voice": batch.get("voice"), "voice_name": batch.get("voice_name", "George"),
        "model": batch.get("model"), "settings": batch.get("settings"), "seed": batch.get("seed"),
        "pause_policy": {"pre": PRE, "same_section": TAKE_GAP, "new_section": SECTION_GAP, "tail": TAIL},
        "clean_transcript": str(clean.resolve()), "stems": report_rows,
    }
    (master_dir / "stem_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8"
    )
    print(f"{ep}: {len(report_rows)} takes, {total:.2f}s -> {master}")
    return master, clean


def load_key():
    if not SHARED_CLI.is_file():
        raise SystemExit(f"Shared ElevenLabs CLI missing: {SHARED_CLI}")
    spec = importlib.util.spec_from_file_location("noesis_elevenlabs_cli", SHARED_CLI)
    if spec is None or spec.loader is None:
        raise SystemExit("Could not load encrypted ElevenLabs profile")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return str(module._load_key())


def multipart(audio: Path, text: str):
    boundary = "----SCHLAF" + uuid.uuid4().hex
    parts = [
        f"--{boundary}\r\n".encode(),
        b'Content-Disposition: form-data; name="text"\r\n\r\n', text.encode(), b"\r\n",
        f"--{boundary}\r\n".encode(),
        f'Content-Disposition: form-data; name="file"; filename="{audio.name}"\r\n'.encode(),
        b"Content-Type: audio/wav\r\n\r\n", audio.read_bytes(), b"\r\n",
        f"--{boundary}--\r\n".encode(),
    ]
    return b"".join(parts), boundary


def align(ep: str):
    voice, _, clean, _ = package(ep)
    master = voice / "master" / f"{ep}_SCHLAFPARALYSE_GEORGE_MASTER.wav"
    if not master.is_file():
        raise SystemExit(f"Missing master: {master}")
    text = clean.read_text(encoding="utf-8").strip()
    body, boundary = multipart(master, text)
    request = Request(
        "https://api.elevenlabs.io/v1/forced-alignment", data=body,
        headers={"xi-api-key": load_key(), "Content-Type": f"multipart/form-data; boundary={boundary}",
                 "Accept": "application/json"}, method="POST",
    )
    try:
        with urlopen(request, timeout=600) as response:
            data = json.loads(response.read().decode())
    except HTTPError as exc:
        raise SystemExit(f"Alignment HTTP {exc.code}: {exc.read().decode(errors='replace')[:1000]}")
    data.update({"episode": ep, "source_text": text, "audio": str(master.resolve()),
                 "audio_sha256": hashlib.sha256(master.read_bytes()).hexdigest()})
    output = voice / "alignment" / f"{ep}_SCHLAFPARALYSE_GEORGE_ALIGNMENT.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(f"{ep}: alignment -> {output}")


def main():
    if len(sys.argv) < 2 or sys.argv[1].upper() not in PROFILE:
        raise SystemExit("Usage: python tools/finalize_schlafparalyse_george.py EP06|EP07|EP08 [master|align|all]")
    ep = sys.argv[1].upper()
    command = sys.argv[2].lower() if len(sys.argv) > 2 else "all"
    if command not in {"master", "align", "all"}:
        raise SystemExit("Command must be master, align or all")
    if command in {"master", "all"}:
        build_master(ep)
    if command in {"align", "all"}:
        align(ep)


if __name__ == "__main__":
    main()
