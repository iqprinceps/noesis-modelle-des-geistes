from __future__ import annotations

import json
import math
import re
import shutil
import subprocess
from pathlib import Path


ROOT = Path(r"C:\Users\iQPrinceps\Documents\Codex\Youtube Modelle des Geistes")
ASSETS = ROOT / "05_GENERATED" / "EP01_KOZYREV" / "SHORTS"
APPROVED = ROOT / "04_ASSETS" / "02_CURATED" / "EP01_KOZYREV" / "APPROVED"
COMMONS = ROOT / "04_ASSETS" / "01_DOWNLOADS" / "EP01_KOZYREV" / "WIKIMEDIA_COMMONS"
PATENT = ROOT / "05_GENERATED" / "EP01_KOZYREV" / "05_ORIGINAL_COMPOSITES" / "sources"
PROD = ROOT / "06_PRODUCTION" / "EP01_KOZYREV" / "shorts"
VOICE = PROD / "voice" / "raw"
FFMPEG = shutil.which("ffmpeg") or "ffmpeg"
FFPROBE = shutil.which("ffprobe") or "ffprobe"


SHORTS = {
    "SHORT01_PATENTCHECK": {
        "voice": "EP01_SHORT01.mp3",
        "assets": "SHORT01",
        "images": [
            "IMG01_PHONE.png", str(PATENT / "PATENT_PAGE_02.png"),
            str(PATENT / "PATENT_PAGE_01.png"), str(APPROVED / "KZ_002_Kozyrev_mirror_apparatus_drawing_1996.jpg"),
            str(APPROVED / "KZ_003_Kozyrev_mirrors_modern_photo_2014.jpg"), "IMG03_METAL_MACRO.png",
            str(PATENT / "PATENT_PAGE_02.png"), str(COMMONS / "KZ_WC_02_BIG_S1_2015.jpg"),
            "IMG05_CLAIM_SPLIT.png", str(PATENT / "PATENT_PAGE_02.png"),
        ],
        "modes": ["cover", "contain", "contain", "contain", "contain", "cover", "contain", "cover", "cover", "contain"],
        "tags": ["VISUELLE REKONSTRUKTION", "ORIGINALDOKUMENT", "ORIGINALDOKUMENT", "ORIGINALZEICHNUNG 1996", "ORIGINALFOTO 2014", "VISUELLE REKONSTRUKTION", "ORIGINALDOKUMENT", "ORIGINALFOTO 2015", "VISUELLE REKONSTRUKTION", "ORIGINALDOKUMENT"],
        "hook": "ZEITMASCHINE?",
        "beats": [(10.0, 14.0, "LIES DEN TITEL."), (30.0, 38.0, "PATENT ≠ BEWEIS")],
        "subs": [
            "Dieses Patent wird im Netz als Bauplan", "einer Zeitmaschine verkauft.",
            "Doch schon der Titel sagt etwas anderes:", "Gerät zur Korrektur psychosomatischer Erkrankungen.",
            "Kein Zeitportal. Kein Sprung ins Jahr zweitausendfünfzig.",
            "Der interessante Teil steckt tiefer.", "Das Dokument beschreibt gekrümmte Metallflächen",
            "und verbindet sie mit einer behaupteten Wirkung.", "Was wurde gebaut? Was wurde nur behauptet?",
            "Ein Patent beweist, dass eine Idee eingereicht wurde.",
            "Nicht, dass jede Behauptung darin stimmt.",
            "Die echte Geschichte beginnt, wo der Clickbait aufhört.",
        ],
        "music": (43, 87),
    },
    "SHORT02_WAHRNEHMUNG": {
        "voice": "EP01_SHORT02.mp3",
        "assets": "SHORT02",
        "images": [
            str(COMMONS / "KZ_WC_02_BIG_S1_2015.jpg"), "IMG01_ENTER.png",
            str(APPROVED / "KZ_003_Kozyrev_mirrors_modern_photo_2014.jpg"), "IMG04_ACOUSTIC.png",
            str(COMMONS / "KZ_WC_02_BIG_S1_2015.jpg"), str(COMMONS / "KZ_WC_01_HORIZONTAL_BIG_G2PF_2015.jpg"),
            "IMG03_CLOSEUP.png", "IMG05_TARGET.png",
            str(APPROVED / "KZ_002_Kozyrev_mirror_apparatus_drawing_1996.jpg"), str(COMMONS / "KZ_WC_02_BIG_S1_2015.jpg"),
        ],
        "modes": ["cover", "cover", "contain", "cover", "cover", "contain", "cover", "cover", "contain", "cover"],
        "tags": ["ORIGINALFOTO 2015", "VISUELLE REKONSTRUKTION", "ORIGINALFOTO 2014", "VISUELLE REKONSTRUKTION", "ORIGINALFOTO 2015", "ORIGINALFOTO 2015", "VISUELLE REKONSTRUKTION", "TESTMODELL", "ORIGINALZEICHNUNG 1996", "ORIGINALFOTO 2015"],
        "hook": "DEIN GEHIRN FÜLLT DIE LÜCKEN.",
        "beats": [(17.0, 23.0, "ERLEBNIS ≠ INFORMATION"), (32.0, 41.0, "WAS KONNTE SIE NICHT WISSEN?")],
        "subs": [
            "Du brauchst keine Zeitmaschine,", "damit dein Gehirn Alarm schlägt.",
            "Setz dich allein in einen engen Metallraum.",
            "Geräusche kehren verändert zurück.", "Bewegungen tauchen als Reflexion wieder auf.",
            "Vertraute Orientierungspunkte verschwinden.", "Dein Gehirn beginnt, Lücken zu füllen.",
            "Das Erlebnis kann intensiv und vollkommen echt sein –",
            "ohne Information aus der Zukunft.",
            "Ungewöhnliche Gefühle sind der Anfang einer Untersuchung,",
            "nicht ihr Ende.", "Kann die Person etwas beschreiben,",
            "das sie unmöglich wissen konnte?",
        ],
        "music": (47, 71),
    },
    "SHORT03_BLINDTEST": {
        "voice": "EP01_SHORT03.mp3",
        "assets": "SHORT03",
        "images": [
            "IMG01_ENVELOPES.png", str(COMMONS / "KZ_WC_02_BIG_S1_2015.jpg"),
            "IMG04_DRAWING.png", "IMG05_REVIEWERS.png",
            str(APPROVED / "KZ_002_Kozyrev_mirror_apparatus_drawing_1996.jpg"), "IMG04_DRAWING.png",
            str(COMMONS / "KZ_WC_02_BIG_S1_2015.jpg"), "IMG03_LIGHTHOUSE.png",
            str(COMMONS / "KZ_WC_01_HORIZONTAL_BIG_G2PF_2015.jpg"), "IMG03_LIGHTHOUSE.png",
        ],
        "modes": ["cover", "cover", "cover", "cover", "contain", "cover", "cover", "cover", "contain", "cover"],
        "tags": ["TESTMODELL", "ORIGINALFOTO 2015", "TESTMODELL", "TESTMODELL", "ORIGINALZEICHNUNG 1996", "TESTMODELL", "ORIGINALFOTO 2015", "ZIELBILD", "ORIGINALFOTO 2015", "ZIELBILD"],
        "hook": "MACH DEN BLINDTEST.",
        "beats": [(19.0, 27.0, "VORHER FESTLEGEN."), (32.0, 41.0, "TREFFER ODER ZUFALL?")],
        "subs": [
            "Mach den Test mit.", "Hinter dieser Auswahl liegt genau ein Zielbild.",
            "Die Person im Spiegel sieht es nicht.", "Der Versuchsleiter kennt es ebenfalls nicht.",
            "Sie beschreibt nur Formen, Farben und Bewegung.",
            "Erst danach vergleichen unabhängige Prüfer die Notizen.",
            "Treffer zählen nur, wenn vorher feststand,", "was als Treffer gilt –",
            "und wenn ein zweites Labor dasselbe Ergebnis bekommt.",
            "Unser Ziel heute: ein roter Turm im Eis.",
            "Klingt eine Zeichnung passend? Vielleicht.", "Beweis? Noch nicht.",
            "So wird eine wilde Geschichte zur prüfbaren Frage.",
        ],
        "music": (39, 79),
    },
}


def run(args: list[str], cwd: Path | None = None, capture: bool = False) -> str:
    print(" ".join(str(a) for a in args[:8]), "...")
    result = subprocess.run(args, cwd=cwd, check=True, text=True,
                            stdout=subprocess.PIPE if capture else None,
                            stderr=subprocess.STDOUT if capture else None,
                            encoding="utf-8", errors="replace")
    return result.stdout or ""


def duration(path: Path) -> float:
    return float(run([FFPROBE, "-v", "error", "-show_entries", "format=duration",
                      "-of", "default=nk=1:nw=1", str(path)], capture=True).strip())


def ass_time(value: float) -> str:
    cs = int(round(value * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def ass_escape(text: str) -> str:
    return text.replace("{", "\\{").replace("}", "\\}")


def write_ass(path: Path, cfg: dict, voice_duration: float, total: float) -> None:
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Arial,62,&H00FFFFFF,&H0000FFFF,&HDC061015,&H7A061015,-1,0,0,0,100,100,0,0,1,5,1,2,90,150,260,1
Style: Hook,Arial,82,&H0038E7FF,&H0038E7FF,&HE8061015,&H86061015,-1,0,0,0,100,100,1,0,3,4,1,8,75,175,220,1
Style: Beat,Arial,70,&H00FFFFFF,&H00FFFFFF,&HE8061015,&H86061015,-1,0,0,0,100,100,1,0,3,4,1,8,75,175,220,1
Style: Brand,Arial,28,&H00A8B7BC,&H00A8B7BC,&H80061015,&H00000000,-1,0,0,0,100,100,2,0,1,2,0,7,52,150,70,1
Style: Source,Arial,24,&H00FFFFFF,&H00FFFFFF,&HCC061015,&H94061015,-1,0,0,0,100,100,1,0,3,2,0,9,80,150,74,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = [
        f"Dialogue: 2,0:00:00.00,{ass_time(total)},Brand,,0,0,0,,NOESIS  /  KOZYREV FILES",
        f"Dialogue: 3,0:00:00.00,{ass_time(min(3.1,total))},Hook,,0,0,0,,{ass_escape(cfg['hook'])}",
    ]
    for start, end, text in cfg["beats"]:
        if start < total:
            events.append(f"Dialogue: 3,{ass_time(start)},{ass_time(min(end,total))},Beat,,0,0,0,,{ass_escape(text)}")

    shot_duration = total / len(cfg["images"])
    for index, tag in enumerate(cfg.get("tags", [])):
        start = index * shot_duration + 0.08
        end = min(total, (index + 1) * shot_duration - 0.08)
        events.append(f"Dialogue: 2,{ass_time(start)},{ass_time(end)},Source,,0,0,0,,{ass_escape(tag)}")

    chunks = cfg["subs"]
    weights = [max(2.5, len(re.findall(r"\w+", chunk)) + (1.2 if chunk.endswith((".", "?", "!")) else 0)) for chunk in chunks]
    usable_start, usable_end = 0.18, min(total - 0.30, voice_duration + 0.15)
    cursor = usable_start
    for chunk, weight in zip(chunks, weights):
        span = (usable_end - usable_start) * weight / sum(weights)
        end = cursor + span
        display = ass_escape(chunk)
        events.append(f"Dialogue: 4,{ass_time(cursor)},{ass_time(end)},Sub,,0,0,0,,{display}")
        cursor = end
    path.write_text(header + "\n".join(events) + "\n", encoding="utf-8-sig")


def render_short(name: str, cfg: dict) -> dict:
    outdir = PROD / name
    outdir.mkdir(parents=True, exist_ok=True)
    voice = VOICE / cfg["voice"]
    vd = duration(voice)
    total = vd + 0.85
    ass = outdir / "subtitles.ass"
    write_ass(ass, cfg, vd, total)

    shot_count = len(cfg["images"])
    shot_duration = total / shot_count
    inputs: list[str] = []
    filters: list[str] = []
    video_labels: list[str] = []
    for i, image_name in enumerate(cfg["images"]):
        candidate = Path(image_name)
        image = candidate if candidate.is_absolute() else ASSETS / cfg["assets"] / image_name
        inputs += ["-loop", "1", "-framerate", "30", "-t", f"{shot_duration:.5f}", "-i", str(image)]
        # Alternating slow push/pull and horizontal drift. The full 9:16 composition remains intact.
        if i % 3 == 0:
            z = "min(zoom+0.00045,1.055)"
            x = "iw/2-(iw/zoom/2)"
        elif i % 3 == 1:
            z = "min(zoom+0.00030,1.045)"
            x = "iw/2-(iw/zoom/2)+18*sin(on/45)"
        else:
            z = "if(lte(on,1),1.05,max(1.0,zoom-0.00035))"
            x = "iw/2-(iw/zoom/2)-14*sin(on/50)"
        if cfg.get("modes", ["cover"] * shot_count)[i] == "contain":
            filters.append(
                f"[{i}:v]split=2[bg{i}][fg{i}];"
                f"[bg{i}]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
                f"gblur=sigma=36,eq=brightness=-0.30:saturation=0.55[bgx{i}];"
                f"[fg{i}]scale=1000:1700:force_original_aspect_ratio=decrease[fgx{i}];"
                f"[bgx{i}][fgx{i}]overlay=(W-w)/2:(H-h)/2,"
                f"zoompan=z='min(zoom+0.00018,1.022)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
                f"d=1:s=1080x1920:fps=30,setsar=1,format=yuv420p[v{i}]"
            )
        else:
            filters.append(
                f"[{i}:v]scale=1200:2134:force_original_aspect_ratio=increase,"
                f"crop=1200:2134,zoompan=z='{z}':x='{x}':y='ih/2-(ih/zoom/2)':"
                f"d=1:s=1080x1920:fps=30,setsar=1,format=yuv420p[v{i}]"
            )
        video_labels.append(f"[v{i}]")

    voice_index = shot_count
    tone1_index = shot_count + 1
    tone2_index = shot_count + 2
    inputs += ["-i", str(voice)]
    f1, f2 = cfg["music"]
    inputs += ["-f", "lavfi", "-t", f"{total:.3f}", "-i", f"sine=frequency={f1}:sample_rate=48000"]
    inputs += ["-f", "lavfi", "-t", f"{total:.3f}", "-i", f"sine=frequency={f2}:sample_rate=48000"]

    filters.append("".join(video_labels) + f"concat=n={shot_count}:v=1:a=0[base]")
    filters.append("[base]ass=subtitles.ass,scale=in_range=auto:out_range=limited,format=yuv420p,setparams=range=limited[vout]")
    filters.append(f"[{voice_index}:a]aformat=sample_rates=48000:channel_layouts=stereo,adelay=150|150,loudnorm=I=-16:TP=-1.5:LRA=7[vo]")
    filters.append(f"[{tone1_index}:a]volume=0.020,afade=t=in:st=0:d=1.2,afade=t=out:st={max(0,total-1.5):.3f}:d=1.5[t1]")
    filters.append(f"[{tone2_index}:a]volume=0.010,tremolo=f=0.18:d=0.45,afade=t=in:st=0:d=1.2,afade=t=out:st={max(0,total-1.5):.3f}:d=1.5[t2]")
    filters.append("[vo][t1][t2]amix=inputs=3:duration=longest:normalize=0,alimiter=limit=0.90,loudnorm=I=-14.5:TP=-1.2:LRA=8[aout]")

    output = outdir / f"EP01_{name}_HYBRID_9x16.mp4"
    cmd = [FFMPEG, "-y", *inputs, "-filter_complex", ";".join(filters),
           "-map", "[vout]", "-map", "[aout]", "-t", f"{total:.3f}",
           "-c:v", "libx264", "-preset", "medium", "-crf", "17",
           "-profile:v", "high", "-level", "4.1", "-pix_fmt", "yuv420p",
           "-r", "30", "-g", "60", "-movflags", "+faststart",
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", str(output)]
    run(cmd, cwd=outdir)

    contact = outdir / f"EP01_{name}_HYBRID_CONTACT.jpg"
    run([FFMPEG, "-y", "-i", str(output), "-vf",
         f"fps=6/{total:.3f},scale=270:480,tile=3x2:padding=8:margin=8:color=0x061015",
         "-frames:v", "1", "-q:v", "2", str(contact)])

    probe = json.loads(run([FFPROBE, "-v", "error", "-show_streams", "-show_format", "-of", "json", str(output)], capture=True))
    loud = run([FFMPEG, "-hide_banner", "-i", str(output), "-af", "loudnorm=I=-14:TP=-1:LRA=11:print_format=json", "-f", "null", "-"], capture=True)
    match = re.search(r"\{\s*\"input_i\".*?\}", loud, re.S)
    loudness = json.loads(match.group(0)) if match else {"raw": loud[-2000:]}
    vstream = next(s for s in probe["streams"] if s.get("codec_type") == "video")
    astream = next(s for s in probe["streams"] if s.get("codec_type") == "audio")
    qa = {
        "file": str(output), "duration": float(probe["format"]["duration"]),
        "video": {k: vstream.get(k) for k in ("codec_name", "width", "height", "pix_fmt", "r_frame_rate")},
        "audio": {k: astream.get(k) for k in ("codec_name", "sample_rate", "channels", "channel_layout")},
        "loudness": loudness,
        "checks": {
            "vertical_9_16": vstream.get("width") == 1080 and vstream.get("height") == 1920,
            "under_60_seconds": float(probe["format"]["duration"]) < 60.0,
            "h264_yuv420p": vstream.get("codec_name") == "h264" and vstream.get("pix_fmt") == "yuv420p",
            "aac_48k_stereo": astream.get("codec_name") == "aac" and astream.get("sample_rate") == "48000" and astream.get("channels") == 2,
        },
        "assets": [str(Path(x) if Path(x).is_absolute() else ASSETS / cfg["assets"] / x) for x in dict.fromkeys(cfg["images"])],
        "voice": str(voice), "subtitles": str(ass), "contact_sheet": str(contact),
    }
    (outdir / "QA_HYBRID.json").write_text(json.dumps(qa, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return qa


def main() -> None:
    reports = {name: render_short(name, cfg) for name, cfg in SHORTS.items()}
    summary = PROD / "EP01_SHORTS_HYBRID_QA_SUMMARY.json"
    summary.write_text(json.dumps(reports, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(summary)


if __name__ == "__main__":
    main()
