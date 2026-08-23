#!/usr/bin/env python3
"""EP01 Kozyrev V2 — Voice-Master bauen und ausrichten.

Abgeleitet von `tools/gw_v7_voice.py` (EP02 Gateway V7); die Vorlage bleibt
unveraendert.

Baut aus den acht George-Stems den durchgehenden VO-Master (gleiche
Bauweise wie EP02 V7: Vorlauf, Stems auf -18 LUFS, Pausen dazwischen, Nachlauf)
und holt dann das Forced Alignment gegen die Reinschrift.

Das Alignment laeuft ausdruecklich gegen `07_VOICE_SCRIPT_CLEAN_V2.txt`,
nicht gegen die Sprechtexte: die Reinschrift traegt die richtige
Orthografie, und genau an ihr haengen spaeter Untertitel und Bildanker.
"""

from __future__ import annotations

import json
import hashlib
import subprocess
import sys
import uuid
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
PROD = ROOT / "06_PRODUCTION" / "EP01_KOZYREV_V2"
CLEAN = PROD / "07_VOICE_SCRIPT_CLEAN_V2.txt"
BATCH = PROD / "voice" / "voice_batch.json"
RAW = PROD / "voice" / "raw_stems"
MDIR = PROD / "voice" / "master"
MASTER = MDIR / "EP01_KOZYREV_V2_VO_MASTER.wav"
ALIGNMENT = PROD / "voice" / "alignment" / "EP01_KOZYREV_V2_alignment.json"

PRE, GAP, TAIL = 0.35, 0.65, 2.2


def run(args, capture=False):
    p = subprocess.run(args, text=True, capture_output=capture)
    if p.returncode:
        raise RuntimeError((p.stderr or p.stdout or "failed")[-6000:])
    return (p.stdout or "") + (p.stderr or "")


def dur(p: Path) -> float:
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                      "-of", "csv=p=0", str(p)], True).strip())


def loudness(p: Path, i=-18.0, tp=-2.0) -> dict:
    import re
    out = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(p),
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


def build_master():
    batch = json.loads(BATCH.read_text(encoding="utf-8"))
    sdir = MDIR / "stems"
    sdir.mkdir(parents=True, exist_ok=True)
    lines, report = [], []

    pre = MDIR / "pre.wav"
    silence(pre, PRE)
    lines.append(f"file '{pre.as_posix()}'")

    stems = batch["stems"]
    for i, stem in enumerate(stems):
        src = RAW / f"{stem['id']}.mp3"
        if not src.is_file():
            raise SystemExit(f"Stem fehlt: {src}")
        dst = sdir / f"{stem['id']}.wav"
        normalize(src, dst)
        lines.append(f"file '{dst.as_posix()}'")
        report.append({"id": stem["id"], "duration": round(dur(dst), 3)})
        print(f"  {stem['id'][10:]:<24} {dur(dst):7.2f}s")
        if i < len(stems) - 1:
            gap = MDIR / f"gap_{i+1:02d}.wav"
            silence(gap, GAP)
            lines.append(f"file '{gap.as_posix()}'")

    tail = MDIR / "tail.wav"
    silence(tail, TAIL)
    lines.append(f"file '{tail.as_posix()}'")

    concat = MDIR / "concat.txt"
    concat.write_text("\n".join(lines) + "\n", encoding="utf-8")
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat",
         "-safe", "0", "-i", str(concat), "-c:a", "pcm_s24le", str(MASTER)])
    total = dur(MASTER)
    (MDIR / "stem_report.json").write_text(json.dumps({
        "duration": round(total, 3), "voice": batch["voice"],
        "voice_name": batch.get("voice_name"), "settings": batch["settings"],
        "stems": report}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nMaster: {total:.2f}s  ({int(total//60)}:{total%60:04.1f})")
    return total


def multipart(audio: Path, text: str):
    b = "----KZV2" + uuid.uuid4().hex
    parts = [f"--{b}\r\n".encode(),
             b'Content-Disposition: form-data; name="text"\r\n\r\n', text.encode(), b"\r\n",
             f"--{b}\r\n".encode(),
             f'Content-Disposition: form-data; name="file"; filename="{audio.name}"\r\n'.encode(),
             b"Content-Type: audio/wav\r\n\r\n", audio.read_bytes(), b"\r\n",
             f"--{b}--\r\n".encode()]
    return b"".join(parts), b


def align():
    sys.path.insert(0, r"C:\Users\iQPrinceps\Documents\Codex\NOESIS Channel\tools")
    from elevenlabs_cli import _load_key  # type: ignore
    text = CLEAN.read_text(encoding="utf-8").strip()
    body, b = multipart(MASTER, text)
    req = Request("https://api.elevenlabs.io/v1/forced-alignment", data=body,
                  headers={"xi-api-key": _load_key(),
                           "Content-Type": f"multipart/form-data; boundary={b}",
                           "Accept": "application/json"}, method="POST")
    try:
        with urlopen(req, timeout=600) as res:
            data = json.loads(res.read().decode())
    except HTTPError as e:
        raise SystemExit(f"Alignment HTTP {e.code}: {e.read().decode(errors='replace')[:800]}")
    data.update({"source_text": text, "audio": str(MASTER.resolve()),
                 "audio_sha256": hashlib.sha256(MASTER.read_bytes()).hexdigest()})
    ALIGNMENT.parent.mkdir(parents=True, exist_ok=True)
    ALIGNMENT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Alignment: {len(data['characters'])} Zeichen -> {ALIGNMENT.name}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd in ("master", "all"):
        build_master()
    if cmd in ("align", "all"):
        align()
