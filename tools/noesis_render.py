#!/usr/bin/env python3
"""NOESIS render orchestrator for episode-specific local production.

Shared engine, individual episode profiles. Runtime and shot timing come from
forced alignment; creative counts are never forced to a global quota.

Usage:
    python tools/noesis_render.py EP04A doctor
    python tools/noesis_render.py EP04A manifest
    python tools/noesis_render.py EP04A plan
    python tools/noesis_render.py EP04A all

Supported: EP04A, EP04B, EP05, EP06, EP07, EP08.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
FPS = 30
SUB = 4
VIDEO_EXT = {".mp4", ".mov", ".mkv", ".webm", ".m4v", ".avi"}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"}
MEDIA_EXT = VIDEO_EXT | IMAGE_EXT

PROFILES = {
    "EP04A": {
        "summary": "EP04A_JUNG_KUNDALINI_V5",
        "cue": "VISUAL_CUE_SHEET_V5_FINAL.csv",
        "voice": "EP04A_JUNG_KUNDALINI_V5_VO_MASTER.wav",
        "alignment": "EP04A_JUNG_KUNDALINI_V5_alignment.json",
        "out": "EP04A_JUNG_KUNDALINI_V5",
        "camera": "vision", "zoom": 0.052, "hold_zoom": 0.022,
        "fade": 0.18, "bg": "#0B0A0D",
    },
    "EP04B": {
        "summary": "EP04B_CHAKRA_GENEALOGIE_V5",
        "cue": "VISUAL_CUE_SHEET_V5.csv",
        "voice": "EP04B_CHAKRA_GENEALOGIE_V5_VO_MASTER.wav",
        "alignment": "EP04B_CHAKRA_GENEALOGIE_V5_alignment.json",
        "out": "EP04B_CHAKRA_GENEALOGIE_V5",
        "camera": "archive", "zoom": 0.042, "hold_zoom": 0.015,
        "fade": 0.12, "bg": "#11100E",
    },
    "EP05": {
        "summary": "EP05_JUNG_PAULI_V4",
        "cue": "VISUAL_CUE_SHEET.csv",
        "cue_fallback": "03_EPISODEN/TYPE_B/EP05_JUNG_PAULI/VISUAL_CUE_SHEET.csv",
        "voice": "EP05_JUNG_PAULI_V4_VO_MASTER.wav",
        "alignment": "EP05_JUNG_PAULI_V4_alignment.json",
        "out": "EP05_JUNG_PAULI_V4",
        "camera": "precision", "zoom": 0.044, "hold_zoom": 0.018,
        "fade": 0.14, "bg": "#0D1014",
    },
    "EP06": {
        "summary": "EP06_SCHLAFPARALYSE_V4",
        "cue": "VISUAL_CUE_SHEET.csv",
        "voice": "EP06_SCHLAFPARALYSE_V4_VO_MASTER.wav",
        "alignment": "EP06_SCHLAFPARALYSE_V4_alignment.json",
        "out": "EP06_SCHLAFPARALYSE_V4",
        "camera": "intimate", "zoom": 0.048, "hold_zoom": 0.020,
        "fade": 0.16, "bg": "#090A0D",
    },
    "EP07": {
        "summary": "EP07_SCHLAFPARALYSE_V4",
        "cue": "VISUAL_CUE_SHEET.csv",
        "voice": "EP07_SCHLAFPARALYSE_V4_VO_MASTER.wav",
        "alignment": "EP07_SCHLAFPARALYSE_V4_alignment.json",
        "out": "EP07_SCHLAFPARALYSE_V4",
        "camera": "archive", "zoom": 0.038, "hold_zoom": 0.014,
        "fade": 0.12, "bg": "#100D0B",
    },
    "EP08": {
        "summary": "EP08_SCHLAFPARALYSE_V4",
        "cue": "VISUAL_CUE_SHEET.csv",
        "voice": "EP08_SCHLAFPARALYSE_V4_VO_MASTER.wav",
        "alignment": "EP08_SCHLAFPARALYSE_V4_alignment.json",
        "out": "EP08_SCHLAFPARALYSE_V4",
        "camera": "network", "zoom": 0.050, "hold_zoom": 0.018,
        "fade": 0.14, "bg": "#080B10",
    },
}


def run(args: list[str], capture: bool = False) -> str:
    p = subprocess.run(args, text=True, capture_output=capture)
    if p.returncode:
        raise RuntimeError((p.stderr or p.stdout or "command failed")[-8000:])
    return (p.stdout or "") + (p.stderr or "")


def duration(path: Path) -> float:
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                      "-of", "csv=p=0", str(path)], True).strip())


def paths(ep: str) -> dict[str, Path]:
    c = PROFILES[ep]
    summary = ROOT / "PRODUCTION_SUMMARY" / c["summary"]
    prod = ROOT / "06_PRODUCTION" / c["out"]
    cue_candidates = [summary / c["cue"]]
    if c.get("cue_fallback"):
        cue_candidates.append(ROOT / c["cue_fallback"])
    cue = next((q for q in cue_candidates if q.is_file()), cue_candidates[0])
    voice_candidates = [summary / "voice" / "master" / c["voice"],
                        prod / "voice" / "master" / c["voice"],
                        prod / "audio" / c["voice"]]
    align_candidates = [summary / "voice" / "alignment" / c["alignment"],
                        prod / "voice" / "alignment" / c["alignment"]]
    voice = next((q for q in voice_candidates if q.is_file()), voice_candidates[0])
    alignment = next((q for q in align_candidates if q.is_file()), align_candidates[0])
    return {
        "summary": summary, "prod": prod, "cue": cue, "voice": voice,
        "alignment": alignment,
        "timeline": prod / "timeline" / f"{c['out']}_timeline.json",
        "segments": prod / "render" / "segments",
        "picture": prod / "render" / "picture.mp4",
        "final": prod / "render" / "final" / f"{c['out']}_FINAL.mp4",
        "manifest": prod / "render_manifest.json",
    }


def read_cues(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise SystemExit(f"Empty cue sheet: {path}")
    return rows


def alignment_chars(data: dict) -> tuple[str, list[float], list[float]]:
    candidates = [data] + [data[k] for k in ("alignment", "normalized_alignment")
                           if isinstance(data.get(k), dict)]
    for d in candidates:
        chars = d.get("characters") or d.get("chars")
        starts = d.get("character_start_times_seconds") or d.get("starts")
        ends = d.get("character_end_times_seconds") or d.get("ends")
        if isinstance(chars, list) and isinstance(starts, list) and isinstance(ends, list):
            return "".join(chars), [float(x) for x in starts], [float(x) for x in ends]
    words = data.get("words")
    if isinstance(words, list) and words:
        text, starts, ends = "", [], []
        for w in words:
            token = str(w.get("text") or w.get("word") or "")
            if text and token and token[0] not in ".,;:!?": token = " " + token
            s, e = float(w.get("start", 0)), float(w.get("end", w.get("start", 0)))
            text += token; starts.extend([s] * len(token)); ends.extend([e] * len(token))
        return text, starts, ends
    raise SystemExit("Unsupported forced-alignment JSON schema")


def anchor_time(anchor: str, text: str, starts: list[float], default: float) -> float:
    probes = [p.strip() for p in re.split(r"\s*/\s*|\s*\.\.\.\s*", anchor) if len(p.strip()) >= 3]
    for probe in probes or [anchor]:
        m = re.search(re.escape(probe), text, flags=re.I)
        if m: return starts[min(m.start(), len(starts) - 1)]
    return default


def media_index(p: dict[str, Path]) -> list[Path]:
    roots = [p["prod"] / "visuals", p["prod"] / "motion", p["prod"] / "motion_clips",
             ROOT / "05_GENERATED", ROOT / "04_ASSETS"]
    out: list[Path] = []
    for root in roots:
        if root.exists():
            out.extend(x for x in root.rglob("*") if x.is_file() and x.suffix.lower() in MEDIA_EXT)
    return out


def token_parts(raw: str) -> list[str]:
    bad = {"archive", "edit", "motion", "generated", "archive+motion"}
    return [x.strip() for x in re.split(r"\s*\+\s*|\s+or\s+|\s*->\s*|\s*,\s*", raw or "", flags=re.I)
            if x.strip() and x.strip().casefold() not in bad]


def score(token: str, path: Path) -> int:
    t = re.sub(r"[^a-z0-9]+", "", token.casefold())
    n = re.sub(r"[^a-z0-9]+", "", path.stem.casefold())
    if len(t) < 3: return -1
    if t == n: return 100
    if t in n: return 70
    chunks = [re.sub(r"[^a-z0-9]+", "", c.casefold()) for c in re.split(r"[^A-Za-z0-9]+", token)]
    return sum(10 for c in chunks if len(c) >= 3 and c in n)


def load_manifest(p: dict[str, Path]) -> dict[str, str]:
    if not p["manifest"].is_file(): return {}
    raw = json.loads(p["manifest"].read_text(encoding="utf-8"))
    return {str(k): str(v) for k, v in raw.get("assets", raw).items() if v}


def resolve_visual(row: dict, idx: list[Path], manifest: dict[str, str]) -> Path | None:
    cue = row.get("cue_id") or row.get("id") or ""
    if cue in manifest:
        q = Path(manifest[cue]); q = q if q.is_absolute() else ROOT / q
        if q.is_file(): return q
    spec = row.get("source_or_generated") or row.get("asset") or row.get("visual") or ""
    for tok in token_parts(spec):
        ranked = sorted(((score(tok, q), q) for q in idx), reverse=True, key=lambda z: z[0])
        if ranked and ranked[0][0] >= 20: return ranked[0][1]
    words = [w for w in re.findall(r"[A-Za-z0-9]{4,}", row.get("primary_visual") or "")
             if w.casefold() not in {"real", "archive", "historical", "generic", "motion", "source"}]
    ranked = [(sum(w.casefold() in q.stem.casefold() for w in words), q) for q in idx]
    ranked = [x for x in ranked if x[0] > 0]
    return max(ranked, default=(0, None), key=lambda z: z[0])[1]


def write_manifest(ep: str, p: dict[str, Path], cues: list[dict], idx: list[Path]) -> None:
    old = load_manifest(p); assets = dict(old); unresolved = []
    for i, row in enumerate(cues):
        cue = row.get("cue_id") or row.get("id") or f"CUE{i+1:03d}"
        if cue in assets: continue
        q = resolve_visual(row, idx, old)
        if q:
            try: assets[cue] = str(q.relative_to(ROOT))
            except ValueError: assets[cue] = str(q)
        else:
            assets[cue] = ""; unresolved.append(cue)
    p["manifest"].parent.mkdir(parents=True, exist_ok=True)
    p["manifest"].write_text(json.dumps({
        "episode": ep,
        "note": "Auto-resolved where possible. Empty entries must be filled with local media paths.",
        "assets": assets,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Manifest: {p['manifest']}")
    if unresolved: print(f"Unresolved: {len(unresolved)} -> {', '.join(unresolved[:20])}")


def build_timeline(ep: str, p: dict[str, Path], cues: list[dict], idx: list[Path]) -> list[dict]:
    text, starts, _ = alignment_chars(json.loads(p["alignment"].read_text(encoding="utf-8")))
    total = duration(p["voice"]); manifest = load_manifest(p); rows = []; cursor = 0.0
    for i, cue in enumerate(cues):
        anchor = cue.get("voice_anchor") or cue.get("anchor") or ""
        t = max(cursor, min(anchor_time(anchor, text, starts, cursor), total - 0.05))
        rows.append({"cue": cue, "start": t}); cursor = t
    for i, item in enumerate(rows):
        start = item["start"]; end = rows[i+1]["start"] if i + 1 < len(rows) else total
        if end <= start: end = min(total, start + 0.35)
        cue = item.pop("cue"); visual = resolve_visual(cue, idx, manifest)
        item.update({
            "shot_id": cue.get("cue_id") or f"SHOT{i+1:03d}",
            "scene": cue.get("section") or cue.get("scene") or "",
            "anchor": cue.get("voice_anchor") or cue.get("anchor") or "",
            "pace": (cue.get("pace") or "normal").casefold(),
            "function": cue.get("edit_function") or "",
            "notes": cue.get("notes") or "",
            "visual": str(visual) if visual else "",
            "kind": "VIDEO" if visual and visual.suffix.lower() in VIDEO_EXT else "STILL",
            "start": round(start, 3), "end": round(end, 3), "duration": round(end-start, 3),
        })
    for i, row in enumerate(rows):
        row["scene_first"] = i == 0 or rows[i-1]["scene"] != row["scene"]
        row["scene_last"] = i == len(rows)-1 or rows[i+1]["scene"] != row["scene"]
    p["timeline"].parent.mkdir(parents=True, exist_ok=True)
    p["timeline"].write_text(json.dumps({"episode": ep, "duration": total, "voice": str(p["voice"]), "shots": rows}, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    missing = [r for r in rows if not r["visual"]]
    print(f"Timeline: {len(rows)} cues / {total:.2f}s / unresolved visuals {len(missing)}")
    if missing: print("Missing: " + ", ".join(r["shot_id"] for r in missing[:30]))
    return rows


def contain_needed(path: Path) -> bool:
    if path.suffix.lower() in VIDEO_EXT: return False
    try:
        from PIL import Image
        with Image.open(path) as im: ar = im.width / max(1, im.height)
        return not (1.62 <= ar <= 1.95)
    except Exception: return False


def camera_filter(ep: str, index: int, row: dict) -> str:
    c = PROFILES[ep]; frames = max(2, round(row["duration"] * FPS * SUB))
    amount = c["hold_zoom"] if row.get("pace") in {"hold", "reset"} else c["zoom"]
    families = {
        "vision": ["in", "diag", "out", "up", "in", "left", "out", "right"],
        "archive": ["left", "right", "in", "down", "right", "out", "up", "left"],
        "precision": ["in", "right", "out", "left", "down", "in", "up", "right"],
        "intimate": ["in", "in", "left", "out", "right", "in", "up", "out"],
        "network": ["diag", "right", "in", "left", "out", "down", "diag", "up"],
    }
    mode = families[c["camera"]][index % 8]; z0, z1 = (1.0, 1.0 + amount)
    if mode == "out": z0, z1 = z1, z0
    pfrac = f"on/{frames}"; q = f"(({pfrac})*({pfrac})*(3-2*({pfrac})))"
    z = f"({z0:.5f}+({z1-z0:.5f})*{q})"
    if mode == "left": x = f"(iw-iw/zoom)*(0.70*(1-{q}))"
    elif mode == "right": x = f"(iw-iw/zoom)*(0.70*{q})"
    elif mode == "diag": x = f"(iw-iw/zoom)*(0.15+0.55*{q})"
    else: x = "(iw-iw/zoom)/2"
    if mode == "up": y = f"(ih-ih/zoom)*(0.70*(1-{q}))"
    elif mode == "down": y = f"(ih-ih/zoom)*(0.70*{q})"
    elif mode == "diag": y = f"(ih-ih/zoom)*(0.70-0.50*{q})"
    else: y = "(ih-ih/zoom)/2"
    if contain_needed(Path(row["visual"])):
        base = ("split=2[fg][bg];[bg]scale=1920:1080:force_original_aspect_ratio=increase,"
                "crop=1920:1080,gblur=sigma=28,eq=brightness=-0.24[back];"
                "[fg]scale=1920:1080:force_original_aspect_ratio=decrease[front];"
                "[back][front]overlay=(W-w)/2:(H-h)/2,scale=3840:2160")
    else:
        base = "scale=3840:2160:force_original_aspect_ratio=increase,crop=3840:2160"
    fade = float(c["fade"]); bg = c["bg"]
    fi = f",fade=t=in:st=0:d={fade:.3f}:color={bg}" if row.get("scene_first") else ""
    fo = f",fade=t=out:st={max(0.0,row['duration']-fade):.3f}:d={fade:.3f}:color={bg}" if row.get("scene_last") else ""
    return base + f",zoompan=z='{z}':x='{x}':y='{y}':d=1:s=1920x1080:fps={FPS*SUB},tblend=all_mode=average,framestep={SUB},fps={FPS},format=yuv420p" + fi + fo


def render_segments(ep: str, p: dict[str, Path], rows: list[dict]) -> None:
    missing = [r for r in rows if not r["visual"] or not Path(r["visual"]).is_file()]
    if missing: raise SystemExit("Unresolved/missing visuals: " + ", ".join(r["shot_id"] for r in missing[:30]))
    p["segments"].mkdir(parents=True, exist_ok=True)
    for i, row in enumerate(rows):
        target = p["segments"] / f"{i+1:03d}_{row['shot_id']}.mp4"
        if target.is_file() and duration(target) >= max(0.1, row["duration"] - 0.08): continue
        inp = ["-stream_loop", "-1", "-i", row["visual"]] if row["kind"] == "VIDEO" else ["-loop", "1", "-i", row["visual"]]
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *inp,
             "-t", f"{row['duration']:.3f}", "-vf", camera_filter(ep, i, row), "-an",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p",
             "-r", str(FPS), str(target)])
        print(f"render {i+1:03d}/{len(rows)} {row['shot_id']}")


def concat_picture(p: dict[str, Path], rows: list[dict]) -> Path:
    lst = p["segments"].parent / "concat.txt"
    lines = ["file '" + (p["segments"] / f"{i+1:03d}_{r['shot_id']}.mp4").as_posix() + "'" for i, r in enumerate(rows)]
    lst.write_text("\n".join(lines) + "\n", encoding="utf-8")
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", str(lst), "-c", "copy", str(p["picture"])])
    return p["picture"]


def audio_choice(p: dict[str, Path]) -> Path:
    candidates: list[Path] = []
    for d in (p["prod"] / "audio", p["summary"] / "audio", p["summary"] / "audio_stems"):
        if d.exists():
            candidates.extend(q for q in d.glob("*.wav") if "MASTER" in q.name.upper() or "MIX" in q.name.upper())
    return candidates[0] if candidates else p["voice"]


def final_mux(p: dict[str, Path], rows: list[dict]) -> None:
    picture = concat_picture(p, rows); audio = audio_choice(p); p["final"].parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(picture), "-i", str(audio),
         "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k",
         "-shortest", "-movflags", "+faststart", str(p["final"])])
    print(f"Final: {p['final']} ({duration(p['final']):.2f}s)")


def doctor(p: dict[str, Path]) -> int:
    checks = [("summary", p["summary"].is_dir(), p["summary"]), ("cue", p["cue"].is_file(), p["cue"]),
              ("voice", p["voice"].is_file(), p["voice"]), ("alignment", p["alignment"].is_file(), p["alignment"])]
    for name, ok, path in checks: print(f"{'OK' if ok else 'MISS':4} {name:10} {path}")
    for b in ("ffmpeg", "ffprobe"): print(f"{'OK' if shutil.which(b) else 'MISS':4} binary     {b}")
    return 0 if all(ok for _, ok, _ in checks) and all(shutil.which(b) for b in ("ffmpeg", "ffprobe")) else 1


def qa(p: dict[str, Path], rows: list[dict]) -> int:
    bad = []
    for i, row in enumerate(rows):
        seg = p["segments"] / f"{i+1:03d}_{row['shot_id']}.mp4"
        if not seg.is_file(): bad.append((row["shot_id"], "missing")); continue
        d = duration(seg)
        if abs(d-row["duration"]) > 0.15: bad.append((row["shot_id"], f"duration {d:.2f}/{row['duration']:.2f}"))
    print(f"QA segments: {len(rows)-len(bad)}/{len(rows)} OK")
    if bad:
        for x in bad[:20]: print("  ", *x)
        return 1
    jitter = ROOT / "tools" / "spg_zappelpruefung.py"
    if jitter.is_file():
        try: run([sys.executable, str(jitter), str(p["timeline"]), "--segmente", str(p["segments"])])
        except Exception as exc: print(f"Camera QA warning: {exc}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("episode", choices=PROFILES)
    ap.add_argument("command", nargs="?", default="all",
                    choices=["doctor", "manifest", "plan", "render", "final", "qa", "all"])
    args = ap.parse_args(); ep = args.episode; p = paths(ep)
    if args.command == "doctor": return doctor(p)
    if doctor(p): raise SystemExit("Production inputs incomplete. Build voice master/alignment first.")
    cues = read_cues(p["cue"]); idx = media_index(p)
    if args.command in {"manifest", "all"}: write_manifest(ep, p, cues, idx)
    rows = build_timeline(ep, p, cues, idx)
    if args.command == "plan": return 0
    if args.command in {"render", "all"}: render_segments(ep, p, rows)
    if args.command in {"final", "all"}: final_mux(p, rows)
    if args.command in {"qa", "all"}: return qa(p, rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
