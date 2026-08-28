#!/usr/bin/env python3
"""VO-Master und Forced Alignment fuer EP06-EP08 im 06_PRODUCTION-Layout.

`tools/schlafparalyse_voice.py` erwartet die aeltere PRODUCTION_SUMMARY-Ablage
und einen Batch, den es dort nicht mehr gibt. Die Sprechertakes, Batchdateien
und Reinschriften liegen inzwischen unter `06_PRODUCTION/<Episode>/VOICE_<EP>/`.

Ablauf je Episode:
1. Stems auf -18 LUFS normalisieren (True Peak <= -2 dBTP),
2. Vorlauf, feste Pausen und Nachlauf einsetzen, zum Master concaten,
3. Master zusaetzlich als Producer-Spur unter `audio/` ablegen,
4. Forced Alignment gegen die **Reinschrift** holen - sie traegt die richtige
   Orthografie, und an ihr haengen spaeter Bildanker und Untertitel.

    python tools/schlafparalyse_voice_v5.py EP08 all
    python tools/schlafparalyse_voice_v5.py EP08 master
    python tools/schlafparalyse_voice_v5.py EP08 align
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
import subprocess
import sys
import uuid
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
CLI_TOOLS = Path(r"C:\Users\iQPrinceps\Documents\Codex\NOESIS Channel\tools")

# Vorlauf, Pause zwischen den Takes, Nachlauf. Jeder normalisierte Take bekommt
# zusaetzlich einen kurzen digitalen Ruheauslauf. Dadurch endet kein Wort direkt
# an einer Dateigrenze (einige ElevenLabs-MP3s hatten nur 10-50 ms Reserve).
# Die sichtbare Gesamttpause bleibt 0,65 s: 0,12 s im Take plus 0,53 s Gap.
PRE, BOUNDARY_PAD, GAP, TAIL = 0.35, 0.12, 0.53, 2.2

EPISODES = {
    "EP06": dict(dir="EP06_SCHLAFPARALYSE_V4", voice="VOICE_EP06",
                 batch="voice_batch.json", clean="EP06_VOICE_SCRIPT_CLEAN.txt",
                 plan="VOICE_EP06/sync/EP06_VOICE_VISUAL_SYNC.csv",
                 take_col="take_id", act_col="act"),
    "EP07": dict(dir="EP07_SCHLAFPARALYSE_V4", voice="VOICE_EP07",
                 batch="voice_batch.json", clean="EP07_VOICE_SCRIPT_CLEAN.txt",
                 plan="EP07_VOICE_VISUAL_SYNC.csv",
                 take_col="take_id", act_col="section"),
    "EP08": dict(dir="EP08_SCHLAFPARALYSE_V4", voice="VOICE_EP08",
                 batch="voice_batch.json", clean="EP08_SPRECHTEXT_CLEAN.txt",
                 plan="POST_PLAN/EP08_VOICE_VISUAL_SYNC_PLAN.csv",
                 take_col="take_id", act_col="act"),
}


def run(args: list[str], capture: bool = False) -> str:
    p = subprocess.run(args, text=True, capture_output=capture)
    if p.returncode:
        raise RuntimeError((p.stderr or p.stdout or "failed")[-6000:])
    return (p.stdout or "") + (p.stderr or "")


def dur(p: Path) -> float:
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                      "-of", "csv=p=0", str(p)], True).strip())


def loudness(p: Path, i: float = -18.0, tp: float = -2.0) -> dict:
    out = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(p),
               "-af", f"loudnorm=I={i}:TP={tp}:LRA=7:print_format=json",
               "-f", "null", "-"], True)
    return json.loads(re.findall(r'\{\s*"input_i".*?\}', out, re.S)[-1])


def normalize(src: Path, dst: Path, i: float = -18.0, tp: float = -2.0) -> None:
    st = loudness(src, i, tp)
    dst.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(src),
         "-af", (f"loudnorm=I={i}:TP={tp}:LRA=7:measured_I={st['input_i']}:"
                 f"measured_TP={st['input_tp']}:measured_LRA={st['input_lra']}:"
                 f"measured_thresh={st['input_thresh']}:offset={st['target_offset']}:"
                 f"linear=true,apad=pad_dur={BOUNDARY_PAD}"),
         "-ac", "1", "-ar", "48000", "-c:a", "pcm_s24le", str(dst)])


def silence(path: Path, seconds: float) -> None:
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "lavfi",
         "-i", f"anullsrc=r=48000:cl=mono:d={seconds}", "-c:a", "pcm_s24le", str(path)])


def normalise_alignment(data: dict) -> dict:
    """Antwort der Forced-Alignment-API auf das Schema des Renderers bringen.

    Die API liefert `characters` inzwischen als Liste von Objekten
    (`{text, start, end}`). `tools/noesis_render.py` erwartet in seinem ersten
    Zweig dagegen eine Liste von Einzelzeichen plus zwei parallele Zeitarrays.

    Ohne diese Umformung faellt der Renderer auf `words` zurueck. Dort setzt
    seine Heuristik vor jedes Wort ein Leerzeichen - die Wortliste enthaelt aber
    bereits eigene Leerzeicheneintraege. Der rekonstruierte Text bekommt dadurch
    doppelte Leerzeichen, keine Ankersuche trifft mehr, und saemtliche Cues
    rutschen auf Zeit 0.
    """
    chars = data.get("characters")
    if isinstance(chars, list) and chars and isinstance(chars[0], dict):
        data = dict(data)
        data["raw_characters"] = chars
        data["characters"] = [c.get("text", "") for c in chars]
        data["character_start_times_seconds"] = [float(c.get("start", 0)) for c in chars]
        data["character_end_times_seconds"] = [float(c.get("end", 0)) for c in chars]
    return data


class Episode:
    def __init__(self, ep: str) -> None:
        cfg = EPISODES[ep]
        self.ep = ep
        self.prod = ROOT / "06_PRODUCTION" / cfg["dir"]
        self.vdir = self.prod / cfg["voice"]
        self.raw = self.vdir / "raw_stems"
        self.batch = self.vdir / cfg["batch"]
        self.clean = self.vdir / cfg["clean"]
        self.mdir = self.prod / "voice" / "master"
        self.master = self.mdir / f"{cfg['dir']}_VO_MASTER.wav"
        self.producer = self.prod / "audio" / f"{ep}_voice_-18LUFS.wav"
        self.alignment = (self.prod / "voice" / "alignment"
                          / f"{cfg['dir']}_alignment.json")
        self.plan = self.prod / cfg["plan"]
        self.take_col, self.act_col = cfg["take_col"], cfg["act_col"]

    def act_of_take(self) -> dict[str, str]:
        """Take-ID auf Akt abbilden.

        `tools/build_schlafparalyse_audio_stems.py` leitet die Aktenergie aus
        dem Stem-Report ab und braucht dafuer je Take `section`, `start` und
        `end`. Die Zuordnung Take -> Akt steht im Sync-Plan.
        """
        mapping: dict[str, str] = {}
        if not self.plan.is_file():
            return mapping
        with self.plan.open(encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                mapping.setdefault(row[self.take_col].strip(), row[self.act_col].strip())
        return mapping

    def build_master(self) -> float:
        batch = json.loads(self.batch.read_text(encoding="utf-8"))
        sdir = self.mdir / "stems"
        sdir.mkdir(parents=True, exist_ok=True)
        lines: list[str] = []
        report: list[dict] = []
        acts = self.act_of_take()

        pre = self.mdir / "pre.wav"
        silence(pre, PRE)
        lines.append(f"file '{pre.as_posix()}'")

        stems = batch["stems"]
        cursor = PRE
        for i, stem in enumerate(stems):
            src = self.raw / f"{stem['id']}.mp3"
            if not src.is_file():
                raise SystemExit(f"Stem fehlt: {src}")
            dst = sdir / f"{stem['id']}.wav"
            normalize(src, dst)
            lines.append(f"file '{dst.as_posix()}'")
            d = dur(dst)
            # Take-ID im Plan ist der Stamm ohne den sprechenden Titelteil.
            take_key = "_".join(stem["id"].split("_")[:3])
            report.append({
                "id": stem["id"],
                "section": acts.get(stem["id"], acts.get(take_key, "")),
                "start": round(cursor, 3),
                "end": round(cursor + d, 3),
                "duration": round(d, 3),
            })
            print(f"  {stem['id']:<46} {d:7.2f}s  {report[-1]['section']}")
            cursor += d
            if i < len(stems) - 1:
                gap = self.mdir / f"gap_{i + 1:02d}.wav"
                silence(gap, GAP)
                lines.append(f"file '{gap.as_posix()}'")
                cursor += GAP

        tail = self.mdir / "tail.wav"
        silence(tail, TAIL)
        lines.append(f"file '{tail.as_posix()}'")

        concat = self.mdir / "concat.txt"
        concat.write_text("\n".join(lines) + "\n", encoding="utf-8")
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat",
             "-safe", "0", "-i", str(concat), "-c:a", "pcm_s24le", str(self.master)])

        total = dur(self.master)
        self.producer.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(self.master, self.producer)
        payload = json.dumps({
            "episode": self.ep, "duration": round(total, 3),
            "voice": batch["voice"], "voice_name": batch.get("voice_name"),
            "model": batch.get("model"), "settings": batch["settings"],
            "stems": report}, indent=2, ensure_ascii=False) + "\n"
        (self.mdir / "stem_report.json").write_text(payload, encoding="utf-8")
        # build_schlafparalyse_audio_stems.py sucht den Report unter
        # VOICE_<EP>/master/ und leitet daraus die Aktenergie ab.
        legacy = self.vdir / "master" / "stem_report.json"
        legacy.parent.mkdir(parents=True, exist_ok=True)
        legacy.write_text(payload, encoding="utf-8")
        print(f"\nMaster: {total:.2f}s  ({int(total // 60)}:{total % 60:04.1f})")
        return total

    def align(self) -> None:
        sys.path.insert(0, str(CLI_TOOLS))
        from elevenlabs_cli import _load_key  # type: ignore

        text = self.clean.read_text(encoding="utf-8").strip()
        boundary = "----NOESIS" + uuid.uuid4().hex
        body = b"".join([
            f"--{boundary}\r\n".encode(),
            b'Content-Disposition: form-data; name="text"\r\n\r\n', text.encode(), b"\r\n",
            f"--{boundary}\r\n".encode(),
            f'Content-Disposition: form-data; name="file"; '
            f'filename="{self.master.name}"\r\n'.encode(),
            b"Content-Type: audio/wav\r\n\r\n", self.master.read_bytes(), b"\r\n",
            f"--{boundary}--\r\n".encode(),
        ])
        req = Request("https://api.elevenlabs.io/v1/forced-alignment", data=body,
                      headers={"xi-api-key": _load_key(),
                               "Content-Type": f"multipart/form-data; boundary={boundary}",
                               "Accept": "application/json"}, method="POST")
        try:
            with urlopen(req, timeout=900) as res:
                data = json.loads(res.read().decode())
        except HTTPError as e:
            raise SystemExit(f"Alignment HTTP {e.code}: "
                             f"{e.read().decode(errors='replace')[:800]}")
        data = normalise_alignment(data)
        data.update({"source_text": text, "audio": str(self.master.resolve()),
                     "audio_sha256": hashlib.sha256(self.master.read_bytes()).hexdigest()})
        self.alignment.parent.mkdir(parents=True, exist_ok=True)
        self.alignment.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                                  encoding="utf-8")
        n = len(data.get("characters", data.get("words", [])))
        print(f"Alignment: {n} Einheiten -> {self.alignment.name}")


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] not in EPISODES:
        raise SystemExit(f"Aufruf: schlafparalyse_voice_v5.py <{'|'.join(EPISODES)}> "
                         f"[master|align|all]")
    ep = Episode(sys.argv[1])
    cmd = sys.argv[2] if len(sys.argv) > 2 else "all"
    if cmd in ("master", "all"):
        ep.build_master()
    if cmd in ("align", "all"):
        ep.align()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
