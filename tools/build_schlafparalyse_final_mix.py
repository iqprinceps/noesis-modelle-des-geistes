#!/usr/bin/env python3
"""Finalmix aus VO, Musikbett und SFX bauen (EP06-EP08).

Setzt den Mix-Lock aus den Sounddesign-Plaenen um:

    VO        etwa -18 LUFS, bleibt immer Vordergrund
    Musikbett etwa -30 LUFS, weich gegen die Stimme geduckt
    SFX       12-18 dB unter der Stimme
    Finalmix  -14 LUFS +/- 0,5, True Peak <= -0,8 dBTP
    Delivery  Stereo, 48 kHz

Die Ducking-Kette benutzt `sidechaincompress` mit der Stimme als Steuersignal.
Damit senkt sich das Bett nur dort, wo George wirklich spricht, statt pauschal
leise zu liegen - sonst waere es in den Pausen unhoerbar und unter der Stimme
trotzdem im Weg.

    python tools/build_schlafparalyse_final_mix.py EP08
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FOLDERS = {
    "EP06": "EP06_SCHLAFPARALYSE_V4",
    "EP07": "EP07_SCHLAFPARALYSE_V4",
    "EP08": "EP08_SCHLAFPARALYSE_V4",
}

# Pegel der einzelnen Quellen vor dem Summieren, relativ zur Stimme.
MUSIC_DB = -12.0     # Bett unter der Stimme; Rest macht das Ducking
SFX_DB = -15.0       # Mitte des im Plan genannten Bereichs 12-18 dB
TARGET_I = -14.0
TARGET_TP = -0.8


def run(args: list[str], capture: bool = False) -> str:
    p = subprocess.run(args, text=True, capture_output=capture)
    if p.returncode:
        raise RuntimeError((p.stderr or p.stdout or "failed")[-6000:])
    return (p.stdout or "") + (p.stderr or "")


def dur(p: Path) -> float:
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                      "-of", "csv=p=0", str(p)], True).strip())


def loudness(p: Path) -> dict:
    out = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(p),
               "-af", f"loudnorm=I={TARGET_I}:TP={TARGET_TP}:LRA=9:print_format=json",
               "-f", "null", "-"], True)
    return json.loads(re.findall(r'\{\s*"input_i".*?\}', out, re.S)[-1])


def build(ep: str) -> None:
    prod = ROOT / "06_PRODUCTION" / FOLDERS[ep]
    voice = prod / "voice" / "master" / f"{FOLDERS[ep]}_VO_MASTER.wav"
    stems = prod / "audio" / "stems"
    if not voice.is_file():
        raise SystemExit(f"VO-Master fehlt: {voice}")

    music = stems / f"{ep}_MX_MASTER.wav"
    sfx = sorted(q for q in stems.glob(f"{ep}_SFX_*.wav"))
    if not music.is_file():
        raise SystemExit(f"Musikmaster fehlt: {music}")
    if not sfx:
        raise SystemExit(f"Keine SFX-Stems in {stems}")

    length = dur(voice)
    out_dir = prod / "audio"
    premix = out_dir / f"{ep}_premix.wav"
    final = out_dir / f"{ep}_final_MIX.wav"

    inputs = ["-i", str(voice), "-i", str(music)] + [x for q in sfx for x in ("-i", str(q))]

    # SFX zu einer Ebene summieren, dann Musik und SFX getrennt gegen die
    # Stimme ducken und alles auf Master-Laenge begrenzen.
    sfx_labels = "".join(f"[{i + 2}:a]" for i in range(len(sfx)))
    chain = (
        f"[0:a]aformat=channel_layouts=stereo,asplit=3[vo][dm][ds];"
        f"[1:a]aformat=channel_layouts=stereo,volume={MUSIC_DB}dB[mus];"
        f"{sfx_labels}amix=inputs={len(sfx)}:normalize=0,"
        f"aformat=channel_layouts=stereo,volume={SFX_DB}dB[sfxsum];"
        # Bett staerker ducken als die Effekte: die Stimme fuehrt, die Effekte
        # duerfen als Detail knapp darunter stehen bleiben.
        f"[mus][dm]sidechaincompress=threshold=0.05:ratio=6:attack=25:release=380[musduck];"
        f"[sfxsum][ds]sidechaincompress=threshold=0.10:ratio=3:attack=15:release=260[sfxduck];"
        f"[vo][musduck][sfxduck]amix=inputs=3:normalize=0:duration=first,"
        f"atrim=0:{length:.3f},alimiter=limit=0.94,"
        f"aformat=sample_fmts=s32:sample_rates=48000:channel_layouts=stereo[out]"
    )
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *inputs,
         "-filter_complex", chain, "-map", "[out]", "-c:a", "pcm_s24le", str(premix)])

    st = loudness(premix)
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(premix),
         "-af", (f"loudnorm=I={TARGET_I}:TP={TARGET_TP}:LRA=9:"
                 f"measured_I={st['input_i']}:measured_TP={st['input_tp']}:"
                 f"measured_LRA={st['input_lra']}:measured_thresh={st['input_thresh']}:"
                 f"offset={st['target_offset']}:linear=true"),
         "-ar", "48000", "-ac", "2", "-c:a", "pcm_s24le", str(final)])

    check = loudness(final)
    print(f"{ep} Finalmix: {final.relative_to(ROOT)}")
    print(f"  Laenge      {dur(final):.2f}s")
    print(f"  Integriert  {float(check['input_i']):.2f} LUFS   (Ziel {TARGET_I} +/- 0,5)")
    print(f"  True Peak   {float(check['input_tp']):.2f} dBTP   (Ziel <= {TARGET_TP})")
    print(f"  LRA         {float(check['input_lra']):.2f}")
    print(f"  Quellen     VO + Musikmaster + {len(sfx)} SFX-Stems")
    premix.unlink(missing_ok=True)


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in FOLDERS:
        raise SystemExit(f"Aufruf: build_schlafparalyse_final_mix.py <{'|'.join(FOLDERS)}>")
    build(sys.argv[1])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
