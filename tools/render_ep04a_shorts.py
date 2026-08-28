#!/usr/bin/env python3
"""Die drei EP04A-Shorts rendern: 1080x1920, eingebrannte Untertitel, SFX-Bett.

Die Schnittzeiten stammen aus den per silencedetect gemessenen Sprechpausen der
George-Takes, liegen also in den Atempausen und nicht mitten im Wort.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
S = ROOT / "06_PRODUCTION" / "JUNG_SERIES_V1" / "SHORTS_EP04A"
GEN, SRC, REFS = S / "images" / "generated", S / "images" / "quelle", S / "images" / "refs"
W, H, FPS, SUB = 1080, 1920, 30, 3
BG = "#0A0A0F"


def g(n): return GEN / f"{n}.png"
def q(n): return SRC / f"{n}.png"


SHORTS = {
    "S1": dict(
        title="Jung und die schwarze Schlange",
        endcard=("DIE GANZE GESCHICHTE", "Jung & Kundalini"),
        shots=[
            (0.00, 1.80, q("16_08_00 (4)"), "Eine große schwarze Schlange."),
            (1.80, 2.96, q("16_08_00 (3)"), "Eine Höhle."),
            (2.96, 5.20, g("S1_03_rote_sonne_unter_wasser"), "Eine rote Sonne unter Wasser."),
            (5.20, 7.50, g("S1_04_gestalten_im_gang"), "Gestalten, die ihm antworteten."),
            (7.50, 9.06, g("S1_05_notizbuch_1913"), "Das ist kein Roman."),
            (9.06, 11.30, g("S1_06_jung_schreibt_nacht"), "Das hat C. G. Jung aufgeschrieben."),
            (11.30, 12.73, q("16_25_28 (5)"), "Über sich selbst."),
            (12.73, 16.40, g("S3_12_karte_des_bewusstseins"),
             "Neunzehn Jahre später liegt eine\nindische Karte vor ihm."),
            (16.40, 19.58, g("S1_08_schlange_am_fuss_der_tafel"),
             "Unten, aufgerollt:\nwieder eine Schlange."),
            (19.58, 21.81, g("S1_09_jung_warnt_seminar"), "Und Jung warnt sein Publikum."),
            (21.81, 26.69, q("16_25_27 (4)"),
             "Wer damit herumspielt, könne sich\npsychisch in Gefahr bringen."),
            (26.69, 28.92, g("S1_12_schlange_und_karte"),
             "Dass seine Schlange Kundalini war,\nist bis heute nicht belegt."),
            (28.92, 35.67, g("S1_13_mann_vor_der_karte"),
             "Aber warum warnt ein Mann vor einem\nGelände, das seinem eigenen\nso ähnlich sieht?"),
        ]),
    "S2": dict(
        title="Der Psychiater, der sich vor sich selbst fürchtete",
        endcard=("WAS ER DORT FAND", "Die schwarze Schlange"),
        shots=[
            (0.00, 2.36, q("16_25_26 (1)"), "Mitten am Tag,\nim Zug durch die Schweiz,"),
            (2.36, 4.68, q("16_25_27 (2)"), "sieht ein Mann\nEuropa unter Wasser."),
            (4.68, 7.90, g("S2_03_truemmer_im_wasser"), "Gelbe Wellen. Trümmer. Tote."),
            (7.90, 9.64, q("16_25_27 (3)"), "Dann färbt sich das Meer rot."),
            (9.64, 11.52, q("16_25_28 (5)"), "Und die Vision kommt wieder."),
            (11.52, 13.31, g("S2_06_klinik_innen"), "Der Mann ist Psychiater."),
            (13.31, 17.06, g("S2_08_klinik_akte"),
             "Er kennt psychotische Zustände\naus seiner Arbeit an der Klinik."),
            (17.06, 19.94, q("16_25_27 (4)"), "Genau deshalb erschreckt ihn,\nwas er da sieht."),
            (19.94, 24.39, q("16_25_28 (7)"),
             "Später schreibt er, er habe sich von\neiner Psychose bedroht gefühlt."),
            (24.39, 26.67, q("16_25_28 (6)"), "Ein Jahr danach beginnt der Krieg."),
            (26.67, 30.14, g("S2_12_die_gefaehrliche_frage"),
             "Und C. G. Jung stellt sich\neine gefährliche Frage:"),
            (30.14, 32.86, g("S2_04_leeres_abteil"), "War daran wirklich alles nur privat?"),
            (32.86, 36.50, g("S2_09_geht_wieder_hinein"),
             "Er läuft nicht weg.\nEr geht absichtlich wieder hinein."),
        ]),
    "S3": dict(
        title="Zwei Sekunden, die alles verändern",
        endcard=("DIE PSYCHOLOGIE DAHINTER", "Jung & Kundalini"),
        shots=[
            (0.00, 1.87, g("S3_02_display_nur_ein_name"), "Eine Nachricht auf deinem Display."),
            (1.87, 3.06, q("16_33_02 (1)"), "Nur ein Name."),
            (3.06, 5.85, q("16_33_03 (2)"), "Und dein Körper ist schneller\nals dein Denken."),
            (5.85, 8.33, g("S3_05_kiefer_spannt"),
             "Der Brustkorb zieht sich zusammen.\nDer Kiefer spannt an."),
            (8.33, 10.13, q("16_33_03 (4)"), "Dein Finger liegt schon\nüber der Tastatur."),
            (10.13, 12.99, g("S3_11_ich_bin_diese_wut"),
             "In diesem Moment\nbeobachtest du Wut nicht."),
            (12.99, 16.09, q("16_33_03 (3)"), "Du bist wütend."),
            (16.09, 17.72, q("16_33_04 (5)"), "Dann passiert etwas Kleines.\nDu bemerkst es."),
            (17.72, 20.01, g("S3_08_zwei_sekunden"), "Du schreibst zwei Sekunden\nlang nichts."),
            (20.01, 21.49, g("S3_10_da_ist_wut"), "Die Wut ist noch da."),
            (21.49, 25.68, q("16_33_04 (6)"),
             "Aber nicht mehr: Ich bin diese Wut.\nSondern: Da ist Wut."),
            (25.68, 29.44, q("16_33_05 (7)"),
             "Genau diesen Übergang erkannte\nC. G. Jung in einer alten\nindischen Karte wieder."),
            (29.44, 39.38, g("S3_12_karte_des_bewusstseins"),
             "Nicht als Anatomie.\nSondern als Karte des Bewusstseins."),
        ]),
}


def run(args):
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError((r.stderr or r.stdout)[-3000:])
    return r.stdout + r.stderr


def dur(p):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                      "-of", "csv=p=0", str(p)]).strip())


def font(name, size):
    return ImageFont.truetype(f"C:/Windows/Fonts/{name}", size)


# YouTube legt ueber jeden Short eigene Bedienflaechen: unten Titel, Kanalname und
# Beschreibung (rund 330 px), rechts die Aktionsleiste (ab x 940). Untertitel
# muessen darueber bzw. daneben bleiben, sonst sind sie auf dem Geraet halb verdeckt.
UI_BOTTOM = 340             # Abstand der Untertitel-Unterkante zum unteren Rand
CAP_BOX_MAX = 780           # max. Boxbreite, damit die Aktionsleiste frei bleibt
CAP_SAFE = CAP_BOX_MAX - 60  # nutzbare Textbreite innerhalb der Box


def wrap_to_width(text: str, f: ImageFont.FreeTypeFont, limit: int) -> list[str]:
    """Woerter zu Zeilen packen, die garantiert in die sichere Breite passen."""
    d = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    lines, cur = [], ""
    for word in text.replace("\n", " ").split():
        probe = f"{cur} {word}".strip()
        if cur and d.textlength(probe, font=f) > limit:
            lines.append(cur)
            cur = word
        else:
            cur = probe
    if cur:
        lines.append(cur)
    return lines


def caption_png(text: str, path: Path) -> None:
    """Untertitel als Bild mit weichem Trageschatten -- lesbar auf jedem Grund.

    Die Schriftgroesse wird so lange verkleinert, bis der laengste Umbruch in die
    sichere Breite passt und hoechstens drei Zeilen entstehen.  Ohne das lief der
    Text bei langen deutschen Saetzen aus dem Bild.
    """
    size = 56
    while True:
        f = font("ariblk.ttf", size)
        lines = wrap_to_width(text, f, CAP_SAFE)
        d0 = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
        widest = max(d0.textlength(l, font=f) for l in lines)
        if (widest <= CAP_SAFE and len(lines) <= 4) or size <= 30:
            break
        size -= 2
    pad, lh = 30, int(size * 1.34)
    tw = int(widest)
    box = (min(CAP_BOX_MAX, tw + 2 * pad), len(lines) * lh + 2 * pad)
    img = Image.new("RGBA", (W, box[1] + 60), (0, 0, 0, 0))
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ds = ImageDraw.Draw(shadow)
    x0 = (W - box[0]) // 2
    ds.rounded_rectangle((x0, 30, x0 + box[0], 30 + box[1]), radius=26, fill=(4, 6, 10, 214))
    shadow = shadow.filter(ImageFilter.GaussianBlur(16))
    img.alpha_composite(shadow)
    d = ImageDraw.Draw(img)
    for i, line in enumerate(lines):
        w = d.textlength(line, font=f)
        d.text(((W - w) / 2, 30 + pad + i * lh - 4), line, font=f, fill=(245, 242, 235, 255))
    img.save(path)


def endcard_png(head: str, sub: str, path: Path) -> None:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.text((70, H // 2 - 190), head, font=font("seguisb.ttf", 44), fill=(141, 199, 205))
    d.line((70, H // 2 - 120, 420, H // 2 - 120), fill=(43, 74, 78), width=4)
    # Gleiche Klemme wie bei den Untertiteln: "Die schwarze Schlange" lief bei
    # fester Groesse ueber den rechten Rand hinaus.
    size = 82
    while size > 44:
        f = font("ariblk.ttf", size)
        # Rechte Kante = 70 px linker Rand plus Textbreite. Die Aktionsleiste
        # beginnt bei x 940, also muss die Summe darunter bleiben.
        if 70 + max(d.textlength(l, font=f) for l in sub.split("\n")) <= 930:
            break
        size -= 3
    f = font("ariblk.ttf", size)
    for i, line in enumerate(sub.split("\n")):
        d.text((70, H // 2 - 70 + i * int(size * 1.17)), line, font=f, fill=(243, 239, 230))
    d.text((70, H // 2 + 120), "Ganze Folge im Kanal", font=font("segoeui.ttf", 40),
           fill=(180, 175, 166))
    img.save(path)


def sfx_bed(seconds: float, path: Path) -> None:
    """Ruhiges Bett: tiefe Drone plus sehr leises Rauschen, stark gedaempft."""
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-f", "lavfi", "-i", f"sine=frequency=52:duration={seconds:.3f}",
         "-f", "lavfi", "-i", f"sine=frequency=78:duration={seconds:.3f}",
         "-f", "lavfi", "-i", f"anoisesrc=d={seconds:.3f}:c=brown:a=0.055",
         "-filter_complex",
         "[0:a]volume=0.16[a];[1:a]volume=0.075[b];[2:a]lowpass=f=520,volume=0.5[c];"
         "[a][b][c]amix=inputs=3:normalize=0,"
         f"afade=t=in:st=0:d=1.4,afade=t=out:st={max(0.0, seconds-1.8):.3f}:d=1.8,"
         "volume=0.30[out]",
         "-map", "[out]", "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", str(path)])


def camera(i: int, d: float) -> str:
    frames = int(round(d * FPS)) * SUB
    lin = f"(on/{frames})"
    ease = f"(0.6*{lin}+0.4*({lin}*{lin}*(3-2*{lin})))"
    t = min(1.1, max(0.75, d / 4.0))
    moves = [(1.030, .040), (1.075, -.034), (1.034, .038), (1.070, -.030)]
    z0, dz = moves[i % 4]
    z1 = min(1.115, max(1.014, z0 + dz * t))
    y = "ih/2-(ih/zoom/2)" if i % 2 else f"(ih-ih/zoom)*(0.42+0.16*{ease})"
    return (f"zoompan=z='{z0:.4f}+({z1-z0:.4f})*{ease}':x='iw/2-(iw/zoom/2)':y='{y}'"
            f":d=1:s={W}x{H}:fps={FPS*SUB},tmix=frames={SUB}:weights='1 1 1',fps={FPS},"
            "eq=contrast=1.04:saturation=1.03,unsharp=5:5:.26:5:5:0,format=yuv420p")


def build(key: str, spec: dict, endcard_seconds: float) -> Path:
    seg = S / "segments" / key
    seg.mkdir(parents=True, exist_ok=True)
    vo = S / "voice" / f"{key}_george.mp3"
    total = spec["shots"][-1][1] + endcard_seconds

    files = []
    for i, (a, b, img, text) in enumerate(spec["shots"]):
        if not Path(img).is_file():
            raise SystemExit(f"Bild fehlt: {img}")
        d = b - a
        cap = seg / f"cap_{i:02d}.png"
        caption_png(text, cap)
        out = seg / f"{i:02d}.mp4"
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
             "-loop", "1", "-t", f"{d:.4f}", "-i", str(img),
             "-i", str(cap),
             "-filter_complex",
             f"[0:v]scale={W*2}:{H*2}:force_original_aspect_ratio=increase,"
             f"crop={W*2}:{H*2},loop=loop=-1:size=1:start=0,fps={FPS*SUB},{camera(i, d)}[v];"
             f"[v][1:v]overlay=0:{H}-h-{UI_BOTTOM}[vo]",
             "-map", "[vo]", "-t", f"{d:.4f}", "-an",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "17",
             "-pix_fmt", "yuv420p", "-r", str(FPS), str(out)])
        files.append(out)

    ec_img = seg / "endcard.png"
    endcard_png(spec["endcard"][0], spec["endcard"][1], ec_img)
    ec = seg / "99_endcard.mp4"
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-loop", "1", "-t", f"{endcard_seconds:.3f}", "-i", str(ec_img),
         "-vf", f"fps={FPS},format=yuv420p", "-an",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", str(ec)])
    files.append(ec)

    concat = seg / "concat.txt"
    concat.write_text("\n".join(f"file '{f.as_posix()}'" for f in files) + "\n", encoding="utf-8")
    silent = seg / "video_only.mp4"
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", str(concat), "-c:v", "libx264", "-preset", "medium", "-crf", "18",
         "-pix_fmt", "yuv420p", "-r", str(FPS), "-an", str(silent)])

    bed = S / "sfx" / f"{key}_bed.wav"
    bed.parent.mkdir(parents=True, exist_ok=True)
    sfx_bed(total, bed)

    final = S / "final" / f"EP04A_SHORT_{key}.mp4"
    final.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-i", str(silent), "-i", str(vo), "-i", str(bed),
         "-filter_complex",
         # asplit ist noetig: ein Filter-Label darf nur einmal verbraucht werden,
         # die Stimme geht aber sowohl in den Sidechain als auch in den Mix.
         f"[1:a]apad=whole_dur={total:.3f},pan=stereo|c0=c0|c1=c0,asplit=2[voice][key];"
         "[2:a][key]sidechaincompress=threshold=0.02:ratio=6:attack=15:release=320[duck];"
         "[voice][duck]amix=inputs=2:normalize=0:duration=first,"
         f"atrim=0:{total:.3f},aresample=192000,alimiter=limit=.89,aresample=48000,"
         "loudnorm=I=-14:TP=-1.5:LRA=11[a]",
         "-map", "0:v:0", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k",
         "-ar", "48000", "-ac", "2", "-t", f"{total:.3f}", "-movflags", "+faststart", str(final)])
    return final


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", choices=["S1", "S2", "S3"])
    ap.add_argument("--endcard", type=float, default=2.4)
    args = ap.parse_args()
    report = {}
    for key, spec in SHORTS.items():
        if args.only and key != args.only:
            continue
        print(f"--- {key}: {spec['title']} ---", flush=True)
        f = build(key, spec, args.endcard)
        imgs = [str(s[2]) for s in spec["shots"]]
        report[key] = {"file": str(f), "duration": round(dur(f), 2),
                       "shots": len(spec["shots"]), "unique_images": len(set(imgs))}
        print(f"    {f.name}  {report[key]['duration']}s  "
              f"{report[key]['shots']} Shots  {report[key]['unique_images']} unikat", flush=True)
    (S / "final" / "SHORTS_QA.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
