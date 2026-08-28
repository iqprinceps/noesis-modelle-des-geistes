#!/usr/bin/env python3
"""Decode all of EP02_EN and create auditable video, transition, and mix QA."""

from __future__ import annotations

import csv
import json
import math
import pathlib
import re
import subprocess
import wave

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
EP = ROOT / "07_ENGLISH_PRODUCTION" / "EP02_GATEWAY"
MASTER = EP / "06_RENDER" / "EP02_GATEWAY_EN_REVIEW_MASTER_1080P.mp4"
EDL = EP / "05_DELIVERY" / "GW_EN_EDIT_SHOT_LIST.csv"
QA = EP / "03_VISUALS" / "QA"
REPORT = QA / "GW_EN_FULL_RENDER_AV_QA.json"
VOICE_STEM = EP / "04_AUDIO" / "GW_EN_PROCESSED_VOICE_STEM.wav"
BED_STEM = EP / "04_AUDIO" / "GW_EN_DUCKED_BED_STEM.wav"
COVERAGE_CSV = QA / "GW_EN_FULL_RENDER_4S_COVERAGE.csv"
TRANSITIONS_CSV = QA / "GW_EN_RENDER_TRANSITION_QA.csv"


def font(size: int):
    return ImageFont.truetype("C:/Windows/Fonts/arial.ttf", size)


def tc(seconds: float) -> str:
    minutes = int(seconds // 60)
    return f"{minutes:02d}:{seconds - minutes * 60:06.3f}"


def edl_rows() -> list[dict[str, str]]:
    with EDL.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def make_page(cells, output: pathlib.Path, cols=5, cell_w=384, image_h=216, label_h=42):
    rows = math.ceil(len(cells) / cols)
    sheet = Image.new("RGB", (cols * cell_w, rows * (image_h + label_h)), "#07111a")
    draw = ImageDraw.Draw(sheet)
    for index, (image, label) in enumerate(cells):
        x = (index % cols) * cell_w
        y = (index // cols) * (image_h + label_h)
        sheet.paste(image.resize((cell_w, image_h), Image.Resampling.LANCZOS), (x, y))
        draw.text((x + 7, y + image_h + 4), label, fill="#eef3f5", font=font(15))
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def video_qa():
    rows = edl_rows()
    boundaries = []
    for index, row in enumerate(rows[:-1]):
        at = float(row["end"])
        boundaries.append({"transition": index + 1, "at": at, "from_asset": row["primary_asset"], "to_asset": rows[index + 1]["primary_asset"]})

    cap = cv2.VideoCapture(str(MASTER))
    fps = float(cap.get(cv2.CAP_PROP_FPS))
    expected = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = expected / fps
    sample_targets = {min(expected - 1, round(t * fps)): float(t) for t in range(0, int(duration) + 1, 4)}
    if max(sample_targets.values()) < 480.0:
        sample_targets[expected - 1] = duration - 1 / fps
    transition_targets = {}
    for boundary in boundaries:
        pre = max(0, round((boundary["at"] - 0.12) * fps))
        post = min(expected - 1, round((boundary["at"] + 0.12) * fps))
        boundary["pre_frame"], boundary["post_frame"] = pre, post
        transition_targets.setdefault(pre, []).append((boundary, "pre"))
        transition_targets.setdefault(post, []).append((boundary, "post"))

    decoded, black_frames, longest_frozen, frozen = 0, 0, 0, 0
    previous, differences, samples, transition_frames = None, [], {}, {}
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        gray = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), (320, 180), interpolation=cv2.INTER_AREA)
        black_frames += int(float(gray.mean()) < 2.0)
        if previous is not None:
            difference = float(np.mean(cv2.absdiff(previous, gray)))
            differences.append(difference)
            frozen = frozen + 1 if difference < 0.006 else 0
            longest_frozen = max(longest_frozen, frozen)
        previous = gray
        if decoded in sample_targets:
            rgb = cv2.cvtColor(cv2.resize(frame, (384, 216), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2RGB)
            samples[decoded] = Image.fromarray(rgb)
        if decoded in transition_targets:
            rgb = cv2.cvtColor(cv2.resize(frame, (192, 108), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2RGB)
            for boundary, side in transition_targets[decoded]:
                transition_frames[(boundary["transition"], side)] = Image.fromarray(rgb)
        decoded += 1
    cap.release()

    coverage_rows, ordered = [], []
    for frame_no, requested in sample_targets.items():
        if frame_no not in samples:
            continue
        ordered.append((samples[frame_no], f"{tc(frame_no / fps)} | frame {frame_no}"))
        index = len(ordered) - 1
        coverage_rows.append({"requested_seconds": f"{requested:.3f}", "decoded_seconds": f"{frame_no / fps:.3f}", "frame": frame_no, "page": index // 25 + 1, "cell": index % 25 + 1})
    page_files = []
    for start in range(0, len(ordered), 25):
        chunk, page = ordered[start:start + 25], start // 25 + 1
        first, last = coverage_rows[start]["decoded_seconds"], coverage_rows[start + len(chunk) - 1]["decoded_seconds"]
        path = QA / f"GW_EN_FULL_RENDER_4S_PAGE_{page:02d}_{float(first):03.0f}-{float(last):03.0f}s.png"
        make_page(chunk, path)
        page_files.append({"page": page, "file": path.name, "coverage_start": first, "coverage_end": last, "frames": len(chunk)})
    with COVERAGE_CSV.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(coverage_rows[0]))
        writer.writeheader(); writer.writerows(coverage_rows)

    transition_rows, transition_cells = [], []
    for boundary in boundaries:
        pre = transition_frames[(boundary["transition"], "pre")]
        post = transition_frames[(boundary["transition"], "post")]
        diff = float(np.mean(np.abs(np.asarray(pre, dtype=np.int16) - np.asarray(post, dtype=np.int16))))
        exact = bool(np.array_equal(np.asarray(pre), np.asarray(post)))
        split = Image.new("RGB", (384, 108)); split.paste(pre, (0, 0)); split.paste(post, (192, 0))
        transition_cells.append((split, f"T{boundary['transition']:03d} {tc(boundary['at'])} | d={diff:.1f}"))
        transition_rows.append({"transition": boundary["transition"], "boundary_seconds": f"{boundary['at']:.3f}", "pre_seconds": f"{boundary['pre_frame'] / fps:.3f}", "post_seconds": f"{boundary['post_frame'] / fps:.3f}", "from_asset": boundary["from_asset"], "to_asset": boundary["to_asset"], "mean_abs_pixel_difference": f"{diff:.4f}", "exact_same_frame": exact, "status": "FAIL" if exact else "PASS"})
    transition_page_files = []
    for start in range(0, len(transition_cells), 25):
        chunk, page = transition_cells[start:start + 25], start // 25 + 1
        first_t, last_t = float(transition_rows[start]["boundary_seconds"]), float(transition_rows[start + len(chunk) - 1]["boundary_seconds"])
        path = QA / f"GW_EN_TRANSITIONS_PAGE_{page:02d}_{first_t:03.0f}-{last_t:03.0f}s.png"
        make_page(chunk, path, image_h=108)
        transition_page_files.append({"page": page, "file": path.name, "coverage_start": f"{first_t:.3f}", "coverage_end": f"{last_t:.3f}", "transitions": len(chunk)})
    with TRANSITIONS_CSV.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(transition_rows[0]))
        writer.writeheader(); writer.writerows(transition_rows)

    return {"fps": fps, "expected_frames": expected, "decoded_frames": decoded, "full_decode_pass": decoded == expected, "black_frame_count_mean_luma_lt_2": black_frames, "mean_adjacent_frame_difference": round(float(np.mean(differences)), 5), "p01_adjacent_frame_difference": round(float(np.percentile(differences, 1)), 5), "longest_near_frozen_run_seconds": round(longest_frozen / fps, 3), "four_second_coverage": {"range_seconds": [round(float(coverage_rows[0]["decoded_seconds"]), 3), round(float(coverage_rows[-1]["decoded_seconds"]), 3)], "sample_count": len(coverage_rows), "pages": page_files, "coverage_csv": COVERAGE_CSV.name}, "transition_coverage": {"expected_transitions": len(boundaries), "checked_transitions": len(transition_rows), "exact_same_frame_failures": sum(row["exact_same_frame"] for row in transition_rows), "pages": transition_page_files, "coverage_csv": TRANSITIONS_CSV.name}}


def read_wav_float(path: pathlib.Path) -> tuple[int, np.ndarray]:
    with wave.open(str(path), "rb") as handle:
        rate, channels, width = handle.getframerate(), handle.getnchannels(), handle.getsampwidth()
        raw = handle.readframes(handle.getnframes())
    if width == 3:
        data = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
        values = data[:, 0].astype(np.int32) | (data[:, 1].astype(np.int32) << 8) | (data[:, 2].astype(np.int32) << 16)
        values = (values ^ 0x800000) - 0x800000
        audio = values.astype(np.float64) / 8388608.0
    elif width == 2:
        audio = np.frombuffer(raw, dtype="<i2").astype(np.float64) / 32768.0
    else:
        raise ValueError(f"unsupported WAV width {width}")
    return rate, audio.reshape(-1, channels)


def loudness_json(path: pathlib.Path) -> dict:
    process = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "loudnorm=I=-16:TP=-1.2:LRA=7:print_format=json", "-f", "null", "-"], capture_output=True, text=True, check=True)
    matches = re.findall(r'\{\s*"input_i".*?\}', process.stderr, re.S)
    if not matches:
        raise RuntimeError(f"loudnorm analysis missing for {path.name}")
    return json.loads(matches[-1])


def audio_qa():
    voice_rate, voice = read_wav_float(VOICE_STEM)
    bed_rate, bed = read_wav_float(BED_STEM)
    if voice_rate != 48_000 or bed_rate != voice_rate:
        raise RuntimeError("stem sample-rate mismatch")
    count = min(len(voice), len(bed)); voice, bed = voice[:count], bed[:count]
    block_rows = []
    for start in range(0, count - voice_rate + 1, voice_rate):
        vrms = math.sqrt(float(np.mean(voice[start:start + voice_rate] ** 2)))
        brms = math.sqrt(float(np.mean(bed[start:start + voice_rate] ** 2)))
        vdb, bdb = 20 * math.log10(max(vrms, 1e-12)), 20 * math.log10(max(brms, 1e-12))
        if vdb > -25:
            block_rows.append((start / voice_rate, vdb - bdb, vdb, bdb))
    margins = np.asarray([row[1] for row in block_rows])
    voice_loud, bed_loud, mix_loud = loudness_json(VOICE_STEM), loudness_json(BED_STEM), loudness_json(MASTER)
    integrated_margin = float(voice_loud["input_i"]) - float(bed_loud["input_i"])
    probes = {"hook": (0, 32), "dense_music_sfx": (299, 324), "closing": (455, 481.0)}
    probe_rows = []
    for name, (start, end) in probes.items():
        selected = [row for row in block_rows if start <= row[0] < end]
        minimum, median = min(row[1] for row in selected), float(np.median([row[1] for row in selected]))
        probe_rows.append({"name": name, "range_seconds": [start, end], "minimum_voice_over_bed_rms_db": round(minimum, 3), "median_voice_over_bed_rms_db": round(median, 3), "status": "PASS" if minimum >= 3.0 else "FAIL"})
    return {"definition": "Voice and ducked-bed stems are measured before their common final loudness stage. Positive dB means narration energy exceeds music/SFX; one-second blocks with fully active narration (voice RMS > -25 dBFS) are assessed so pauses and clipped boundary words are not mislabeled as masking.", "sample_rate": voice_rate, "channels": 2, "decoded_duration_seconds": round(count / voice_rate, 3), "active_voice_blocks": len(block_rows), "voice_integrated_lufs": float(voice_loud["input_i"]), "ducked_bed_integrated_lufs": float(bed_loud["input_i"]), "integrated_voice_over_bed_lu": round(integrated_margin, 3), "minimum_active_block_voice_over_bed_rms_db": round(float(np.min(margins)), 3), "p05_active_block_voice_over_bed_rms_db": round(float(np.percentile(margins, 5)), 3), "median_active_block_voice_over_bed_rms_db": round(float(np.median(margins)), 3), "final_mix_integrated_lufs": float(mix_loud["input_i"]), "final_mix_true_peak_dbtp": float(mix_loud["input_tp"]), "targeted_listening_proxies": probe_rows, "status": "PASS" if integrated_margin >= 6.0 and float(np.percentile(margins, 5)) >= 3.0 and all(x["status"] == "PASS" for x in probe_rows) else "FAIL", "superseded_metric": "The earlier sample-regression SNR was invalid because it compared an unfiltered mono source to a filtered, limited, loudness-normalized stereo sum; its negative coefficient was not a narration/background ratio."}


def timeline_qa():
    rows = edl_rows(); total = sum(float(row["duration"]) for row in rows)
    docs = sum(float(row["duration"]) for row in rows if "DOCUMENT" in row["internal_mode"])
    maps = sum(float(row["duration"]) for row in rows if row["internal_mode"] == "MAP")
    cards = sum(float(row["duration"]) for row in rows if row["primary_asset"].startswith("GW_EN_CARD"))
    clips = sum(float(row["duration"]) for row in rows if row["primary_asset"].lower().endswith(".mp4"))
    formal = docs + maps + cards
    return {"edit_shots": len(rows), "duration_seconds": round(total, 3), "documents_percent": round(100 * docs / total, 2), "maps_percent": round(100 * maps / total, 2), "cards_percent": round(100 * cards / total, 2), "documents_maps_cards_percent": round(100 * formal / total, 2), "moving_clip_percent": round(100 * clips / total, 2), "filmic_still_percent": round(100 * (total - formal - clips) / total, 2)}


def main():
    QA.mkdir(parents=True, exist_ok=True)
    report = {"status": "PENDING_MANUAL_PAGE_REVIEW", "master": str(MASTER.relative_to(EP)).replace("\\", "/"), "video": video_qa(), "audio": audio_qa(), "timeline": timeline_qa(), "manual_page_review": "PENDING: every coverage and transition page must be inspected before release status is promoted."}
    objective_pass = report["video"]["full_decode_pass"] and not report["video"]["black_frame_count_mean_luma_lt_2"] and not report["video"]["transition_coverage"]["exact_same_frame_failures"] and report["audio"]["status"] == "PASS"
    if not objective_pass:
        report["status"] = "FAIL"
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["status"] == "FAIL":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
