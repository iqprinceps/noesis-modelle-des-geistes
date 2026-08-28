#!/usr/bin/env python3
"""Technical, cadence, near-duplicate and visual-contact QA for the upload master."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from itertools import combinations
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


EP = Path(__file__).resolve().parents[1]
MASTER = EP / "08_MASTER" / "EP06_SLEEP_PARALYSIS_02_EN_MASTER_1080P30.mp4"
EDL = EP / "04_EDIT" / "VISUAL_EDL.json"
SEG = EP / "06_RENDER" / "segments"
QA = EP / "10_QA"
FRAMES = QA / "MIDFRAMES"
FONT = Path(r"C:\Windows\Fonts\arial.ttf")


def run(args: list[str], check: bool = True) -> str:
    p = subprocess.run(args, capture_output=True, text=True)
    if check and p.returncode:
        raise RuntimeError((p.stderr or p.stdout)[-8000:])
    return (p.stdout or "") + (p.stderr or "")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dhash(img: np.ndarray) -> int:
    grey = cv2.cvtColor(cv2.resize(img, (9, 8), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY)
    bits = grey[:, 1:] > grey[:, :-1]
    value = 0
    for bit in bits.flatten(): value = (value << 1) | int(bit)
    return value


def hamming(a: int, b: int) -> int:
    return (a ^ b).bit_count()


def frame_metrics(path: Path) -> tuple[np.ndarray, np.ndarray, int]:
    cap = cv2.VideoCapture(str(path)); frames = []; hashes = []
    while True:
        ok, frame = cap.read()
        if not ok: break
        frames.append(cv2.cvtColor(cv2.resize(frame, (320, 180), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY))
        hashes.append(dhash(frame))
    cap.release()
    diffs = np.asarray([float(cv2.absdiff(frames[i], frames[i-1]).mean()) for i in range(1, len(frames))], dtype=np.float64)
    hashdiffs = np.asarray([hamming(hashes[i], hashes[i-1]) for i in range(1, len(hashes))], dtype=np.int32)
    return diffs, hashdiffs, len(frames)


def extract_midframes(shots: list[dict]) -> list[dict]:
    FRAMES.mkdir(parents=True, exist_ok=True)
    records = []
    for shot in shots:
        seg = SEG / f"{shot['shot_id']}.mp4"
        cap = cv2.VideoCapture(str(seg)); count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, count // 2)); ok, frame = cap.read(); cap.release()
        if not ok: raise RuntimeError(f"cannot read midpoint {seg}")
        out = FRAMES / f"{shot['shot_id']}.jpg"; cv2.imwrite(str(out), frame, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
        records.append({"shot_id": shot["shot_id"], "asset": shot["asset"], "section": shot["section"], "hash": dhash(frame), "path": str(out)})
    return records


def contact_sheets(records: list[dict]) -> list[str]:
    outputs = []; fnt = ImageFont.truetype(str(FONT), 20)
    for page, start in enumerate(range(0, len(records), 20), 1):
        subset = records[start:start+20]; sheet = Image.new("RGB", (1600, 900), (8, 11, 15)); d = ImageDraw.Draw(sheet)
        for i, rec in enumerate(subset):
            img = Image.open(rec["path"]).convert("RGB").resize((400, 225), Image.Resampling.LANCZOS)
            x=(i%4)*400; y=(i//4)*180
            img=ImageOps.fit(img,(400,180),Image.Resampling.LANCZOS)
            sheet.paste(img,(x,y)); d.rectangle((x,y,x+400,y+28),fill=(0,0,0,180)); d.text((x+8,y+4),f"{rec['shot_id']} · {Path(rec['asset']).name[:34]}",font=fnt,fill=(245,245,238))
        out=QA/f"MASTER_VISUAL_CONTACT_{page:02d}.jpg"; sheet.save(out,quality=92); outputs.append(str(out))
    return outputs


# Pillow's ImageOps is imported here to keep the contact-sheet code compact.
from PIL import ImageOps  # noqa: E402


def main() -> None:
    QA.mkdir(parents=True, exist_ok=True)
    data = json.loads(EDL.read_text(encoding="utf-8")); shots = data["shots"]
    probe = json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(MASTER)]))
    video = next(s for s in probe["streams"] if s["codec_type"] == "video")
    audio = next(s for s in probe["streams"] if s["codec_type"] == "audio")
    decode_log = run(["ffmpeg", "-v", "error", "-i", str(MASTER), "-map", "0:v:0", "-map", "0:a:0", "-f", "null", "-"], check=False)
    black_log = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(MASTER), "-vf", "blackdetect=d=0.5:pix_th=0.02", "-an", "-f", "null", "-"], check=False)
    black_events = [line.strip() for line in black_log.splitlines() if "black_start:" in line]
    vfr_log = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(MASTER), "-vf", "vfrdet", "-an", "-f", "null", "-"], check=False)
    vfr_line = next((line.strip() for line in reversed(vfr_log.splitlines()) if "VFR:" in line), "")
    loud_log = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(MASTER), "-af", "loudnorm=I=-14:TP=-0.8:LRA=9:print_format=json", "-vn", "-f", "null", "-"], check=False)
    matches = re.findall(r'\{\s*"input_i".*?\}', loud_log, re.S); loud = json.loads(matches[-1]) if matches else {}

    cadence = []; failures = []
    for shot in shots:
        if shot["treatment"] == "static evidence/viewer frame": continue
        path = SEG / f"{shot['shot_id']}.mp4"; diffs, hashdiffs, frames = frame_metrics(path)
        edge = max(2, int(len(diffs)*.15)); interior = diffs[edge:-edge] if len(diffs)>edge*2+4 else diffs
        median=float(np.median(interior)); jerk=float(np.median(np.abs(np.diff(interior)))/max(median,1e-6)); p95=float(np.percentile(interior,95)/max(median,1e-6)); exact_repeat=float(np.mean(hashdiffs[edge:-edge] == 0)) if len(hashdiffs)>edge*2+4 else float(np.mean(hashdiffs==0)); pixel_repeat=float(np.mean(interior < .05))
        is_clip=shot["asset"].lower().endswith(".mp4")
        status="PASS"
        if is_clip and pixel_repeat>.02: status="FAIL_REPEAT"
        if not is_clip and (jerk>.95 or p95>3.1): status="FAIL_CADENCE"
        if status != "PASS": failures.append(f"{shot['shot_id']} {status}")
        cadence.append({"shot_id":shot["shot_id"],"class":"converted_24fps_clip" if is_clip else "eased_moving_still","frames":frames,"median_difference":round(median,6),"jerk_over_median":round(jerk,4),"p95_over_median":round(p95,4),"pixel_repeat_ratio_below_0_05":round(pixel_repeat,4),"diagnostic_dhash_repeat_ratio":round(exact_repeat,4),"status":status})

    records = extract_midframes(shots); sheets = contact_sheets(records)
    near=[]
    for a,b in combinations(records,2):
        ia=int(a["shot_id"].split("_")[-1]); ib=int(b["shot_id"].split("_")[-1])
        if abs(ia-ib)<=3: continue
        dist=hamming(a["hash"],b["hash"])
        if dist<=5: near.append({"a":a["shot_id"],"b":b["shot_id"],"distance":dist,"asset_a":a["asset"],"asset_b":b["asset"]})

    duration_video=float(video.get("duration", probe["format"]["duration"])); duration_audio=float(audio.get("duration", probe["format"]["duration"])); av_delta=abs(duration_video-duration_audio)
    checks = {
        "decode": "PASS" if not decode_log.strip() else "FAIL",
        "video_spec": "PASS" if (video["width"],video["height"],video["pix_fmt"],video["avg_frame_rate"])==(1920,1080,"yuv420p","30/1") else "FAIL",
        "audio_spec": "PASS" if audio.get("sample_rate")=="48000" and int(audio.get("channels",0))==2 else "FAIL",
        "av_sync_duration": "PASS" if av_delta <= .04 else "FAIL",
        "black": "PASS" if not black_events else "REVIEW",
        "cadence": "PASS" if not failures else "REVIEW",
        "near_duplicates": "PASS" if not near else "REVIEW",
        "loudness": "PASS" if loud and abs(float(loud["input_i"])+14)<=.5 and float(loud["input_tp"])<=-.8+.05 else "FAIL",
    }
    report={"master":str(MASTER.resolve()),"sha256":sha256(MASTER),"checks":checks,"probe":{"video":video,"audio":audio,"format":probe["format"]},"duration_video":duration_video,"duration_audio":duration_audio,"av_delta":av_delta,"loudness":loud,"decode_log":decode_log,"black_events":black_events,"vfrdet":vfr_line,"cadence_failures":failures,"cadence":cadence,"near_duplicate_candidates":near,"contact_sheets":sheets}
    (QA/"TECHNICAL_QA.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"checks":checks,"av_delta":av_delta,"loudness":loud,"black_events":black_events,"cadence_failures":failures,"near_duplicate_candidates":near,"contact_sheets":sheets},indent=2))


if __name__ == "__main__": main()
