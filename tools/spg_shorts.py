#!/usr/bin/env python3
"""EP01A Die Spiegel — zwei eigenstaendige Shorts, 1080x1920.

Uebernimmt alles, was heute an der Folge gelernt wurde:

* Ueberabtastung auf 3840x6826 vor `zoompan` und vier Zwischenschritte je
  Ausgabebild. Ohne das laeuft die Fahrt in ganzen Pixeln und zappelt — bei
  Shorts faellt das noch mehr auf, weil das Bild auf dem Telefon groesser ist
  als ein 16:9-Video.
* Strecke nach Shotdauer, weiche Enden.
* Ein Bild je Satz, kein Bild zweimal.
* Untertitel eingebrannt: der groesste Teil des Shorts-Publikums sieht ohne
  Ton. Zwei Zeilen, Wort fuer Wort aus dem Forced Alignment, damit sie auf
  der Stimme sitzen und nicht daneben.
* Der Hook steht in den ersten Sekunden im Bild, nicht nur auf der Tonspur.

    python tools/spg_shorts.py ton
    python tools/spg_shorts.py alle
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import uuid
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
PROD = ROOT / "06_PRODUCTION" / "EP01A_SPIEGEL" / "shorts"
VIS = PROD / "visuals"
RAW = PROD / "voice" / "raw_stems"
WERK = PROD / "werk"
FINAL = PROD / "final"

W, H = 1080, 1920
SW, SH = 3840, 6826            # Ueberabtastung fuer zoompan
SUB = 4                        # Zwischenschritte je Ausgabebild
FPS = 30
GRUND = "#0A1428"
VOR, NACH = 0.30, 1.60         # Vorlauf und Nachlauf auf der Tonspur

# Verweis auf die Folge, gleicher Wortlaut in beiden Shorts
ABSPANN = "DIE GANZE FOLGE\nauf dem Kanal"


def run(args, capture=False):
    p = subprocess.run(args, text=True, capture_output=capture)
    if p.returncode:
        raise RuntimeError((p.stderr or p.stdout or "failed")[-6000:])
    return (p.stdout or "") + (p.stderr or "")


def dur(p: Path) -> float:
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                      "-of", "csv=p=0", str(p)], True).strip())


def v(n): return str((VIS / f"{n}.png").resolve())


# Anker sind Satzanfaenge aus der Reinschrift. Das Bild haengt am Text, nicht
# an einer Sekundenzahl — wird die Stimme neu erzeugt, wandert es mit.
SHORTS = {
    "SHORT_A_DER_STUHL": {
        "titel": "Der Stuhl",
        "hook": "NACH VIER\nMINUTEN",
        "marke": "NOESIS  ·  MODELLE DES GEISTES",
        "shots": [
            ("Du sitzt auf einem Stuhl aus Metall.", "sh_a01_stuhl"),
            ("Um dich herum steht eine Spirale", "sh_a02_setzen"),
            ("Sie schließt sich hinter dir", "sh_a03_spalt"),
            ("Das Licht geht aus.", "sh_a04_licht_aus"),
            ("Nach etwa vier Minuten beginnt es.", "sh_a05_schimmern"),
            ("Dann Farbe.", "sh_a06_farbe"),
            ("Ringe, die sich ineinanderschieben.", "sh_a07_ringe"),
            ("Der Raum ist vollständig dunkel.", "sh_a04_licht_aus"),
            ("Nach zehn Minuten werden daraus Bilder.", "sh_a08_zimmer"),
            ("Ein Gesicht, das dich ansieht.", "sh_a09_gesicht"),
            ("Und irgendwann verlierst du das Gefühl", "sh_a10_uhr"),
            ("Als die Tür aufgeht", "sh_a11_tuer"),
            ("Diese Anlage steht in Nowosibirsk.", "sh_a12_anlage"),
            ("Und keiner von denen", "sh_a01_stuhl"),
        ],
    },
    "SHORT_B_DER_VERSUCH": {
        "titel": "Der Versuch",
        "hook": "DREITAUSEND\nKILOMETER",
        "marke": "NOESIS  ·  MODELLE DES GEISTES",
        "shots": [
            ("Dreitausend Kilometer nördlich", "sh_b01_dikson"),
            ("Eine Siedlung am Rand des Nordpolarmeers.", "sh_b02_karte"),
            ("1990 bringen sowjetische Forscher", "sh_b03_verladung"),
            ("Ihre Überlegung", "sh_b04_aufbau"),
            ("Zu einer festgelegten Minute", "sh_b06_sender"),
            ("Einen Kreis.", "sh_b05_symbolkarte"),
            ("Zur selben Minute sitzen irgendwo", "sh_b07_kuechentisch"),
            ("und zeichnen auf, was bei ihnen ankommt", "sh_b08_empfaenger"),
            ("Koordiniert über Kurzwelle", "sh_b09_kurzwelle"),
            ("Nach Angaben der Beteiligten", "sh_b10_zeitung"),
            ("Der Versuch heißt Aurora Borealis.", "sh_b12_polarlicht"),
            ("Die Auswertung meldet auffällige", "sh_b11_blaetter"),
            ("Alle Auswertungen stammen bis heute", "sh_b04_aufbau"),
        ],
    },
}


# ------------------------------------------------------------------- Ton

def multipart(audio: Path, text: str):
    b = "----SPGS" + uuid.uuid4().hex
    parts = [f"--{b}\r\n".encode(),
             b'Content-Disposition: form-data; name="text"\r\n\r\n', text.encode(), b"\r\n",
             f"--{b}\r\n".encode(),
             f'Content-Disposition: form-data; name="file"; filename="{audio.name}"\r\n'.encode(),
             b"Content-Type: audio/wav\r\n\r\n", audio.read_bytes(), b"\r\n",
             f"--{b}--\r\n".encode()]
    return b"".join(parts), b


def ton():
    """Stimme auf -18 LUFS, Vorlauf und Nachlauf, dann Forced Alignment."""
    sys.path.insert(0, r"C:\Users\iQPrinceps\Documents\Codex\NOESIS Channel\tools")
    from elevenlabs_cli import _load_key  # type: ignore

    WERK.mkdir(parents=True, exist_ok=True)
    for name in SHORTS:
        roh = RAW / f"{name}.mp3"
        stimme = WERK / f"{name}_voice.wav"
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(roh),
             "-af", (f"loudnorm=I=-18:TP=-1.5:LRA=9,"
                     f"adelay={int(VOR * 1000)}|{int(VOR * 1000)},"
                     f"apad=pad_dur={NACH}"),
             "-ar", "48000", "-ac", "2", "-c:a", "pcm_s24le", str(stimme)])

        rein = (PROD / f"{name}_CLEAN.txt").read_text(encoding="utf-8").strip()
        body, b = multipart(stimme, rein)
        req = Request("https://api.elevenlabs.io/v1/forced-alignment", data=body,
                      headers={"xi-api-key": _load_key(),
                               "Content-Type": f"multipart/form-data; boundary={b}",
                               "Accept": "application/json"}, method="POST")
        try:
            with urlopen(req, timeout=600) as res:
                data = json.loads(res.read().decode())
        except HTTPError as e:
            raise SystemExit(f"Alignment HTTP {e.code}: "
                             f"{e.read().decode(errors='replace')[:600]}")
        data["source_text"] = rein
        (WERK / f"{name}_alignment.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"{name:22s} {dur(stimme):5.2f}s  "
              f"{len(data.get('words', []))} Woerter ausgerichtet")


# -------------------------------------------------------------- Zeitachse

def worte(name: str) -> list[dict]:
    d = json.loads((WERK / f"{name}_alignment.json").read_text(encoding="utf-8"))
    return [w for w in d["words"] if w.get("text", "").strip()]


def zeitachse(name: str) -> dict:
    kurz = SHORTS[name]
    ws = worte(name)
    laenge = dur(WERK / f"{name}_voice.wav")

    def zeit_von(anker: str) -> float:
        """Startzeit des Ankers, gesucht ueber die Wortfolge."""
        ziel = [t.lower().strip(".,:;!?„“\"") for t in anker.split()]
        folge = [w["text"].lower().strip(".,:;!?„“\"") for w in ws]
        for i in range(len(folge) - len(ziel) + 1):
            if folge[i:i + len(ziel)] == ziel:
                return float(ws[i]["start"])
        raise SystemExit(f"{name}: Anker nicht gefunden: {anker!r}")

    starts = [zeit_von(a) for a, _ in kurz["shots"]]
    shots = []
    for i, ((anker, bild), t0) in enumerate(zip(kurz["shots"], starts)):
        t1 = starts[i + 1] if i + 1 < len(starts) else laenge
        shots.append({"i": i, "anker": anker, "visual": v(bild), "name": bild,
                      "start": round(t0, 3), "duration": round(t1 - t0, 3)})

    # Untertitel: zwei Zeilen, an Satzgrenzen und Laenge gebrochen
    bloecke, zeile, start = [], [], None
    for w in ws:
        if start is None:
            start = float(w["start"])
        zeile.append(w)
        text = " ".join(x["text"] for x in zeile).strip()
        satzende = w["text"].strip().endswith((".", "!", "?", ":"))
        if satzende or len(text) >= 42:
            bloecke.append({"start": round(start, 3),
                            "end": round(float(w["end"]), 3), "text": text})
            zeile, start = [], None
    if zeile:
        bloecke.append({"start": round(start, 3),
                        "end": round(float(zeile[-1]["end"]), 3),
                        "text": " ".join(x["text"] for x in zeile).strip()})

    tl = {"name": name, "titel": kurz["titel"], "hook": kurz["hook"],
          "marke": kurz["marke"], "duration": round(laenge, 3),
          "shots": shots, "captions": bloecke}
    (WERK / f"{name}_timeline.json").write_text(
        json.dumps(tl, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    eindeutig = len({s["name"] for s in shots})
    print(f"{name:22s} {laenge:5.2f}s  {len(shots)} Shots, {eindeutig} Motive, "
          f"{len(bloecke)} Untertitel")
    return tl


# ----------------------------------------------------------------- Bild

def kamera(i: int, shot: dict) -> str:
    """Wie in der Folge: ueberabgetastet, Zwischenschritte, weiche Enden."""
    frames = max(1, math.ceil(shot["duration"] * FPS)) * SUB
    lin = f"(on/{frames})"
    p = f"(0.6*{lin}+0.4*({lin}*{lin}*(3-2*{lin})))"
    tempo = min(1.55, max(0.50, shot["duration"] / 3.6))
    tempo_quer = min(1.0, tempo)
    mitte_x, mitte_y = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    unten = "(ih-ih/zoom)"

    def hoch(rueck=False):
        a = 0.5 - tempo_quer / 2 if not rueck else 0.5 + tempo_quer / 2
        b = tempo_quer if not rueck else -tempo_quer
        return f"{unten}*({a:.4f}+{b:.4f}*{p})"

    # Im Hochformat traegt die senkrechte Fahrt; ein Seitenschwenk hat kaum
    # Weg, weil das Bild nur 1080 breit ist.
    bewegungen = [
        (1.03, 0.15, mitte_x, mitte_y),          # hinein
        (1.13, 0.0, mitte_x, hoch(True)),        # nach oben
        (1.18, -0.15, mitte_x, mitte_y),         # heraus
        (1.13, 0.0, mitte_x, hoch()),            # nach unten
    ]
    z0, dz, x, y = bewegungen[i % len(bewegungen)]
    z1 = min(1.30, max(1.005, z0 + dz * tempo))
    zexpr = f"{z0:.4f}+({z1 - z0:.4f})*{p}"
    return (f"scale={SW}:{SH}:force_original_aspect_ratio=increase,crop={SW}:{SH},"
            f"loop=loop=-1:size=1:start=0,fps={FPS * SUB},"
            f"zoompan=z='{zexpr}':x='{x}':y='{y}':d=1:s={W}x{H}:fps={FPS * SUB},"
            f"tmix=frames={SUB}:weights='1 1 1 1',fps={FPS},"
            f"eq=contrast=1.03:saturation=1.04,unsharp=5:5:.24:5:5:0,format=yuv420p")


def ass(tl: dict) -> Path:
    """Untertitel, Hook und Markenzeile in einer Spur."""
    def t(x: float) -> str:
        cs = round(x * 100)
        h, r = divmod(cs, 360000)
        m, r = divmod(r, 6000)
        s, cs = divmod(r, 100)
        return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

    kopf = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Unter,Arial,74,&H00F0E8D2,&H00140A04,&H96140A04,-1,0,0,0,100,100,0,0,1,5,3,2,70,70,300,1
Style: Hook,Arial Black,128,&H00D2E8F0,&H00120A04,&H00120A04,-1,0,0,0,100,100,2,0,1,9,5,5,60,60,0,1
Style: Marke,Arial,34,&H008FA0A8,&H00140A04,&H00140A04,-1,0,0,0,100,100,6,0,1,3,0,7,64,64,86,1
Style: Ende,Arial,62,&H00F0E8D2,&H00120A04,&H00120A04,-1,0,0,0,100,100,2,0,3,26,0,5,80,80,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    zeilen = []
    ende = tl["duration"]

    # Markenzeile durchgehend oben
    zeilen.append(f"Dialogue: 0,{t(0)},{t(ende)},Marke,,0,0,0,,{tl['marke']}")

    # Hook in den ersten Sekunden, mittig, mit kurzer Blende
    hook = tl["hook"].replace("\n", r"\N")
    zeilen.append(
        f"Dialogue: 1,{t(0.15)},{t(3.20)},Hook,,0,0,0,,"
        r"{\fad(180,260)\pos(" + f"{W // 2},{int(H * 0.30)}" + r")}" + hook)

    # Untertitel
    for c in tl["captions"]:
        text = c["text"].replace("\n", " ")
        if len(text) > 26:
            worte_ = text.split()
            mitte = len(worte_) // 2
            best, diff = mitte, 1e9
            for k in range(1, len(worte_)):
                d = abs(len(" ".join(worte_[:k])) - len(" ".join(worte_[k:])))
                if d < diff:
                    best, diff = k, d
            text = " ".join(worte_[:best]) + r"\N" + " ".join(worte_[best:])
        zeilen.append(f"Dialogue: 2,{t(c['start'])},{t(c['end'])},Unter,,0,0,0,,{text}")

    # Abspann in der letzten Sekunde
    zeilen.append(
        f"Dialogue: 3,{t(max(0, ende - 1.9))},{t(ende)},Ende,,0,0,0,,"
        r"{\fad(240,200)\pos(" + f"{W // 2},{int(H * 0.50)}" + r")}"
        + ABSPANN.replace("\n", r"\N"))

    p = WERK / f"{tl['name']}_untertitel.ass"
    p.write_text(kopf + "\n".join(zeilen) + "\n", encoding="utf-8")
    return p


def bett(name: str, laenge: float) -> Path:
    """Ruhiges Bett unter der Stimme, Eigensynthese wie in der Folge."""
    ziel = WERK / f"{name}_bett.wav"
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-f", "lavfi", "-i", f"aevalsrc=0.06*sin(2*PI*55*t):d={laenge:.3f}:s=48000",
         "-f", "lavfi", "-i", f"aevalsrc=0.03*sin(2*PI*110.5*t):d={laenge:.3f}:s=48000",
         "-f", "lavfi", "-i", f"anoisesrc=d={laenge:.3f}:c=brown:a=0.020:r=48000",
         "-filter_complex",
         "[0:a][1:a][2:a]amix=inputs=3:normalize=0,"
         "highpass=f=42,lowpass=f=2600,"
         f"afade=t=in:st=0:d=1.2,afade=t=out:st={max(0, laenge - 1.6):.3f}:d=1.6,"
         "aformat=channel_layouts=stereo",
         "-c:a", "pcm_s24le", str(ziel)])
    return ziel


def rendern(name: str, force: bool = False):
    tl = json.loads((WERK / f"{name}_timeline.json").read_text(encoding="utf-8"))
    seg = WERK / name / "segmente"
    seg.mkdir(parents=True, exist_ok=True)
    FINAL.mkdir(parents=True, exist_ok=True)

    offen = []
    for s in tl["shots"]:
        ziel = seg / f"{s['i'] + 1:03d}.mp4"
        if ziel.exists() and not force:
            try:
                dur(ziel)
                continue
            except RuntimeError:
                ziel.unlink()
        offen.append((s, ziel))

    def bauen(auftrag):
        s, ziel = auftrag
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
             "-i", s["visual"],
             "-sws_flags", "lanczos+accurate_rnd+full_chroma_int",
             "-t", f"{s['duration']:.3f}", "-vf", kamera(s["i"], s),
             "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
             "-pix_fmt", "yuv420p", "-r", str(FPS), str(ziel)])
        return s

    if offen:
        arbeiter = max(1, min(4, (os.cpu_count() or 4) // 2 + 1))
        print(f"  {len(offen)} Segmente, {arbeiter} parallel")
        with cf.ThreadPoolExecutor(max_workers=arbeiter) as pool:
            for s in pool.map(bauen, offen):
                print(f"    {s['i'] + 1:02d}  {s['duration']:5.2f}s  {s['name']}",
                      flush=True)

    liste = WERK / f"{name}_concat.txt"
    liste.write_text("\n".join(
        f"file '{(seg / f'{s["i"] + 1:03d}.mp4').as_posix()}'" for s in tl["shots"]
    ) + "\n", encoding="utf-8")
    stumm = WERK / f"{name}_stumm.mp4"
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat",
         "-safe", "0", "-i", str(liste), "-c", "copy", str(stumm)])

    untertitel = ass(tl)
    stimme = WERK / f"{name}_voice.wav"
    musik = bett(name, tl["duration"])
    ziel = FINAL / f"EP01A_{name}_9x16.mp4"

    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-i", str(stumm), "-i", str(stimme), "-i", str(musik),
         "-filter_complex",
         # Der Doppelpunkt nach dem Laufwerksbuchstaben ist fuer den
         # Filtergraphen ein Argumenttrenner und muss maskiert werden.
         (f"[0:v]ass='{untertitel.as_posix().replace(':', chr(92) + ':')}'[v];"
          "[1:a]asplit=2[vox][key];"
          "[2:a][key]sidechaincompress=threshold=0.05:ratio=7:attack=8:release=380[duck];"
          "[vox][duck]amix=inputs=2:normalize=0,"
          "loudnorm=I=-14:TP=-1.0:LRA=9,aformat=channel_layouts=stereo[a]"),
         "-map", "[v]", "-map", "[a]",
         "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
         "-r", str(FPS), "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
         "-movflags", "+faststart", str(ziel)])
    print(f"  fertig: {ziel.name}  {dur(ziel):.2f}s")
    return ziel


def qa(name: str):
    ziel = FINAL / f"EP01A_{name}_9x16.mp4"
    tl = json.loads((WERK / f"{name}_timeline.json").read_text(encoding="utf-8"))
    vs = json.loads(run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                         "-show_entries", "stream=width,height,r_frame_rate,codec_name,pix_fmt",
                         "-of", "json", str(ziel)], True))["streams"][0]
    aus = json.loads(run(["ffprobe", "-v", "error", "-select_streams", "a:0",
                          "-show_entries", "stream=codec_name,sample_rate,channels",
                          "-of", "json", str(ziel)], True))["streams"][0]
    out = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(ziel),
               "-af", "loudnorm=I=-14:TP=-1.0:LRA=9:print_format=json",
               "-f", "null", "-"], True)
    laut = json.loads(re.findall(r'\{\s*"input_i".*?\}', out, re.S)[-1])

    d = dur(ziel)
    eindeutig = len({s["name"] for s in tl["shots"]})
    pruef = {
        "1080x1920": vs["width"] == W and vs["height"] == H,
        "h264_yuv420p": vs["codec_name"] == "h264" and vs["pix_fmt"] == "yuv420p",
        "30fps": vs["r_frame_rate"] == "30/1",
        "aac_48k_stereo": (aus["codec_name"] == "aac"
                           and int(aus["sample_rate"]) == 48000 and aus["channels"] == 2),
        "unter_3_minuten": d <= 180.0,
        "dauer_stimmt": abs(d - tl["duration"]) < 0.6,
        "mind_10_motive": eindeutig >= 10,
        "untertitel_vorhanden": len(tl["captions"]) >= 12,
        "loudness": abs(float(laut["input_i"]) + 14.0) <= 1.0,
        "peak": float(laut["input_tp"]) <= -0.8,
    }
    bericht = {"file": str(ziel.resolve()), "duration": round(d, 3),
               "shots": len(tl["shots"]), "unique_visuals": eindeutig,
               "captions": len(tl["captions"]),
               "loudness_lufs": round(float(laut["input_i"]), 2),
               "true_peak_dbtp": round(float(laut["input_tp"]), 2),
               "sha256": hashlib.sha256(ziel.read_bytes()).hexdigest(),
               "checks": pruef}
    (FINAL / f"EP01A_{name}_QA.json").write_text(
        json.dumps(bericht, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(ziel),
         "-vf", f"fps=1/{max(2, d / 12):.2f},scale=216:384,tile=6x2",
         "-frames:v", "1", "-q:v", "3",
         str(FINAL / f"EP01A_{name}_KONTAKTBOGEN.jpg")])
    print(f"\n{name}  {d:.2f}s  {len(tl['shots'])} Shots  {eindeutig} Motive  "
          f"{bericht['loudness_lufs']} LUFS  TP {bericht['true_peak_dbtp']}")
    for k, ok in pruef.items():
        print(f"    {'OK  ' if ok else 'FEHL'}  {k}")
    if not all(pruef.values()):
        raise SystemExit("QA fehlgeschlagen: "
                         + ", ".join(k for k, o in pruef.items() if not o))


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("befehl", choices=("ton", "zeitachse", "render", "qa", "alle"))
    ap.add_argument("--nur", default="")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    namen = [n for n in SHORTS if not args.nur or n == args.nur]

    if args.befehl in ("ton", "alle"):
        ton()
    if args.befehl in ("zeitachse", "render", "qa", "alle"):
        for n in namen:
            zeitachse(n)
    if args.befehl in ("render", "alle"):
        for n in namen:
            print(f"\n{n}")
            rendern(n, args.force)
    if args.befehl in ("qa", "alle"):
        for n in namen:
            qa(n)


if __name__ == "__main__":
    main()
