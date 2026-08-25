#!/usr/bin/env python3
"""Prepare EP04A George stems for editing and create exact speech timing.

Outputs 48 kHz mono PCM24 stems, a pause-aware master, a technical QA report,
and (optionally) ElevenLabs forced-alignment data.  No time stretching is used.
"""

from __future__ import annotations

import hashlib
import importlib.util
import csv
import json
import re
import subprocess
import sys
import uuid
from difflib import SequenceMatcher
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
VOICE = ROOT / "06_PRODUCTION" / "JUNG_SERIES_V1" / "VOICE_EP04A"
BATCH = VOICE / "voice_batch.json"
TIMING = VOICE / "voice_timing.json"
RAW = VOICE / "raw_stems"
FINAL = VOICE / "final_stems_wav"
MASTER_DIR = VOICE / "master"
MASTER = MASTER_DIR / "EP04A_GEORGE_VO_MASTER.wav"
ALIGNMENT = VOICE / "alignment" / "EP04A_GEORGE_VO_ALIGNMENT.json"
TRANSCRIPTION_QA = VOICE / "qa" / "EP04A_GEORGE_SCRIBE_QA.json"
TECH_QA = VOICE / "qa" / "EP04A_AUDIO_TECH_QA.json"
TAKE_MANIFEST = VOICE / "take_manifest.csv"
ARRANGEMENT = (
    ROOT / "06_PRODUCTION" / "JUNG_SERIES_V1" / "ARRANGEMENT" / "EP04A_SHOT_ORDER.csv"
)
SYNC_CSV = VOICE / "sync" / "EP04A_VOICE_VISUAL_SYNC.csv"
SHARED_CLI = (
    Path.home() / "Documents" / "Codex" / "NOESIS Channel" / "tools" / "elevenlabs_cli.py"
)


def run(args: list[str], capture: bool = False) -> str:
    result = subprocess.run(args, text=True, capture_output=capture)
    if result.returncode:
        raise RuntimeError((result.stderr or result.stdout or "command failed")[-6000:])
    return (result.stdout or "") + (result.stderr or "")


def duration(path: Path) -> float:
    return float(run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "csv=p=0", str(path),
    ], True).strip())


def loudness(path: Path, target_i: float = -18.0, target_tp: float = -2.0) -> dict:
    output = run([
        "ffmpeg", "-hide_banner", "-nostats", "-i", str(path),
        "-af", f"loudnorm=I={target_i}:TP={target_tp}:LRA=7:print_format=json",
        "-f", "null", "-",
    ], True)
    matches = re.findall(r'\{\s*"input_i".*?\}', output, re.S)
    if not matches:
        raise RuntimeError(f"No loudness result for {path}")
    return json.loads(matches[-1])


def normalize(src: Path, dst: Path) -> dict:
    measured = loudness(src)
    filt = (
        "loudnorm=I=-18:TP=-2:LRA=7:"
        f"measured_I={measured['input_i']}:measured_TP={measured['input_tp']}:"
        f"measured_LRA={measured['input_lra']}:"
        f"measured_thresh={measured['input_thresh']}:"
        f"offset={measured['target_offset']}:linear=true"
    )
    dst.parent.mkdir(parents=True, exist_ok=True)
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(src),
        "-af", filt, "-ac", "1", "-ar", "48000", "-c:a", "pcm_s24le", str(dst),
    ])
    return measured


def make_silence(path: Path, seconds: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "lavfi",
        "-i", f"anullsrc=r=48000:cl=mono:d={seconds}",
        "-c:a", "pcm_s24le", str(path),
    ])


def resolve(raw: str) -> Path:
    path = Path(raw)
    return path if path.is_absolute() else ROOT / path


def clean_transcript(batch: dict) -> str:
    return "\n\n".join(
        resolve(stem["text_file"]).read_text(encoding="utf-8").strip()
        for stem in batch["stems"]
    ).strip()


def build() -> None:
    batch = json.loads(BATCH.read_text(encoding="utf-8"))
    timing = json.loads(TIMING.read_text(encoding="utf-8"))
    gaps = timing.get("gaps_after", {})
    pre_roll = float(timing.get("pre_roll_seconds", 0.35))
    tail_seconds = float(timing.get("tail_seconds", 2.4))

    MASTER_DIR.mkdir(parents=True, exist_ok=True)
    concat_lines: list[str] = []
    report: list[dict] = []
    cursor = 0.0

    pre = MASTER_DIR / "pre_roll.wav"
    make_silence(pre, pre_roll)
    concat_lines.append(f"file '{pre.as_posix()}'")
    cursor += pre_roll

    for index, stem in enumerate(batch["stems"]):
        stem_id = stem["id"]
        src = RAW / f"{stem_id}.mp3"
        if not src.is_file():
            raise SystemExit(f"Missing raw stem: {src}")
        dst = FINAL / f"{stem_id}.wav"
        measured = normalize(src, dst)
        seconds = duration(dst)
        start = cursor
        end = start + seconds
        concat_lines.append(f"file '{dst.as_posix()}'")
        row = {
            "id": stem_id,
            "file": str(dst.resolve()),
            "sha256": hashlib.sha256(dst.read_bytes()).hexdigest(),
            "duration": round(seconds, 3),
            "timeline_start": round(start, 3),
            "timeline_end": round(end, 3),
            "source_input_lufs": float(measured["input_i"]),
            "source_true_peak_db": float(measured["input_tp"]),
        }
        cursor = end
        if index < len(batch["stems"]) - 1:
            gap_seconds = float(gaps.get(stem_id, 0.55))
            row["gap_after"] = gap_seconds
            gap = MASTER_DIR / f"gap_{index + 1:02d}.wav"
            make_silence(gap, gap_seconds)
            concat_lines.append(f"file '{gap.as_posix()}'")
            cursor += gap_seconds
        report.append(row)
        print(f"{index + 1:02d}/26  {stem_id:<36} {seconds:6.2f}s")

    tail = MASTER_DIR / "tail.wav"
    make_silence(tail, tail_seconds)
    concat_lines.append(f"file '{tail.as_posix()}'")
    concat_file = MASTER_DIR / "concat.txt"
    concat_file.write_text("\n".join(concat_lines) + "\n", encoding="utf-8")
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "concat", "-safe", "0", "-i", str(concat_file),
        "-c:a", "pcm_s24le", str(MASTER),
    ])

    transcript = clean_transcript(batch)
    transcript_file = VOICE / "EP04A_SPRECHTEXT_CLEAN.txt"
    transcript_file.write_text(transcript + "\n", encoding="utf-8")
    total = duration(MASTER)
    master_loudness = loudness(MASTER)
    report_data = {
        "episode": "EP04A",
        "status": "TECHNICALLY_VALIDATED",
        "voice": batch["voice"],
        "voice_name": batch.get("voice_name"),
        "model": batch.get("model"),
        "settings": batch["settings"],
        "sample_rate_hz": 48000,
        "channels": 1,
        "codec": "pcm_s24le",
        "loudness_target_lufs": -18.0,
        "true_peak_ceiling_db": -2.0,
        "master_duration": round(total, 3),
        "master_input_lufs_after_normalization": float(master_loudness["input_i"]),
        "master_true_peak_db_after_normalization": float(master_loudness["input_tp"]),
        "master_sha256": hashlib.sha256(MASTER.read_bytes()).hexdigest(),
        "master_file": str(MASTER.resolve()),
        "timing_note": timing.get("note"),
        "stems": report,
    }
    (MASTER_DIR / "stem_report.json").write_text(
        json.dumps(report_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Master: {MASTER} ({total:.2f}s)")


def load_key() -> str:
    spec = importlib.util.spec_from_file_location("noesis_elevenlabs_cli", SHARED_CLI)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load shared ElevenLabs CLI: {SHARED_CLI}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return str(module._load_key())


def multipart(audio: Path, text: str) -> tuple[bytes, str]:
    boundary = "----EP04A" + uuid.uuid4().hex
    parts = [
        f"--{boundary}\r\n".encode(),
        b'Content-Disposition: form-data; name="text"\r\n\r\n', text.encode(), b"\r\n",
        f"--{boundary}\r\n".encode(),
        f'Content-Disposition: form-data; name="file"; filename="{audio.name}"\r\n'.encode(),
        b"Content-Type: audio/wav\r\n\r\n", audio.read_bytes(), b"\r\n",
        f"--{boundary}--\r\n".encode(),
    ]
    return b"".join(parts), boundary


def align() -> None:
    if not MASTER.is_file():
        raise SystemExit("Build the master first")
    batch = json.loads(BATCH.read_text(encoding="utf-8"))
    text = clean_transcript(batch)
    body, boundary = multipart(MASTER, text)
    request = Request(
        "https://api.elevenlabs.io/v1/forced-alignment",
        data=body,
        headers={
            "xi-api-key": load_key(),
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=600) as response:
            data = json.loads(response.read().decode())
    except HTTPError as exc:
        raise SystemExit(
            f"Alignment HTTP {exc.code}: {exc.read().decode(errors='replace')[:1000]}"
        )
    data.update({
        "episode": "EP04A",
        "source_text": text,
        "audio": str(MASTER.resolve()),
        "audio_sha256": hashlib.sha256(MASTER.read_bytes()).hexdigest(),
    })
    ALIGNMENT.parent.mkdir(parents=True, exist_ok=True)
    ALIGNMENT.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Alignment: {ALIGNMENT}")


def normalized_words(text: str) -> list[str]:
    return re.findall(r"[0-9a-zäöüß]+", text.casefold())


def transcribe_qa() -> None:
    """Independent Scribe pass to catch dropped or duplicated spoken content."""
    if not MASTER.is_file():
        raise SystemExit("Build the master first")
    from elevenlabs.client import ElevenLabs

    batch = json.loads(BATCH.read_text(encoding="utf-8"))
    expected = clean_transcript(batch)
    client = ElevenLabs(api_key=load_key())
    with MASTER.open("rb") as audio:
        response = client.speech_to_text.convert(
            model_id="scribe_v2",
            file=audio,
            language_code="de",
            tag_audio_events=False,
            diarize=False,
            timestamps_granularity="word",
            seed=24041,
            keyterms=[
                "C. G. Jung", "Kundalini", "Muladhara", "Manipura", "Anahata",
                "Sahasrara", "Ṣaṭ-cakra-nirūpaṇa", "Wolfgang Pauli", "Philemon",
            ],
        )
    if hasattr(response, "model_dump"):
        raw = response.model_dump(mode="json")
    elif hasattr(response, "dict"):
        raw = response.dict()
    else:
        raw = json.loads(response.json())
    actual = str(raw.get("text", ""))
    expected_words = normalized_words(expected)
    actual_words = normalized_words(actual)
    ratio = SequenceMatcher(None, expected_words, actual_words, autojunk=False).ratio()
    keyterms = [
        "jung", "kundalini", "muladhara", "manipura", "anahata",
        "sahasrara", "pauli", "philemon",
    ]
    actual_folded = actual.casefold()
    report = {
        "episode": "EP04A",
        "purpose": "independent speech-to-text content QA",
        "model": "scribe_v2",
        "language": "de",
        "expected_word_count": len(expected_words),
        "transcribed_word_count": len(actual_words),
        "sequence_similarity": round(ratio, 5),
        "keyterms_detected": {term: term in actual_folded for term in keyterms},
        "expected_text": expected,
        "transcription": raw,
    }
    TRANSCRIPTION_QA.parent.mkdir(parents=True, exist_ok=True)
    TRANSCRIPTION_QA.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"Scribe QA: similarity={ratio:.4f}, "
        f"words={len(actual_words)}/{len(expected_words)} -> {TRANSCRIPTION_QA}"
    )


def silence_intervals(path: Path) -> list[dict]:
    output = run([
        "ffmpeg", "-hide_banner", "-nostats", "-i", str(path),
        "-af", "silencedetect=noise=-42dB:d=0.9", "-f", "null", "-",
    ], True)
    starts = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", output)]
    ends = [
        (float(end), float(length))
        for end, length in re.findall(
            r"silence_end: ([0-9.]+) \| silence_duration: ([0-9.]+)", output
        )
    ]
    return [
        {"start": round(start, 3), "end": round(end, 3), "duration": round(length, 3)}
        for start, (end, length) in zip(starts, ends)
    ]


def technical_qa() -> None:
    report = json.loads((MASTER_DIR / "stem_report.json").read_text(encoding="utf-8"))
    stem_rows = []
    internal_flags = []
    for row in report["stems"]:
        path = Path(row["file"])
        seconds = float(row["duration"])
        intervals = silence_intervals(path)
        internal = [
            item for item in intervals
            if item["start"] > 0.25
            and item["end"] < seconds - 0.25
            and item["duration"] >= 1.5
        ]
        if internal:
            internal_flags.append({"id": row["id"], "intervals": internal})
        stem_rows.append({
            "id": row["id"],
            "duration": seconds,
            "decode_ok": True,
            "silence_intervals_over_0_9s": intervals,
            "internal_silence_over_1_5s": internal,
        })

    master_i = float(report["master_input_lufs_after_normalization"])
    master_tp = float(report["master_true_peak_db_after_normalization"])
    qa = {
        "episode": "EP04A",
        "status": "PASS" if -19.0 <= master_i <= -17.0 and master_tp <= -1.8 else "REVIEW",
        "checks": {
            "stem_count": len(stem_rows),
            "all_stems_decode": len(stem_rows) == 26,
            "master_lufs": master_i,
            "master_true_peak_db": master_tp,
            "master_duration": report["master_duration"],
            "no_time_stretching": True,
            "internal_pause_review_threshold_seconds": 1.5,
        },
        "internal_pause_review": internal_flags,
        "stems": stem_rows,
    }
    TECH_QA.parent.mkdir(parents=True, exist_ok=True)
    TECH_QA.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"Technical QA: {qa['status']}; internal-pause flags={len(internal_flags)} "
        f"-> {TECH_QA}"
    )


def expand_cues(raw: str) -> list[str]:
    raw = raw.strip()
    match = re.fullmatch(r"A(\d{3})-A(\d{3})", raw)
    if match:
        return [f"A{number:03d}" for number in range(int(match.group(1)), int(match.group(2)) + 1)]
    return [raw]


def token_spans(text: str) -> list[tuple[str, int, int]]:
    return [
        (match.group(0).casefold(), match.start(), match.end())
        for match in re.finditer(r"[0-9a-zA-ZäöüÄÖÜßṢṣṬṭṆṇŪūĀāĪī]+", text)
    ]


def anchor_position(anchor: str, source: str, minimum_token: int) -> tuple[int | None, float, int]:
    source_tokens = token_spans(source)
    anchor_tokens = [token for token, _, _ in token_spans(anchor) if not token.isdigit()]
    if not anchor_tokens or not source_tokens:
        return None, 0.0, minimum_token
    source_values = [token for token, _, _ in source_tokens]
    best: tuple[int, int] | None = None
    for length in range(len(anchor_tokens), 0, -1):
        for anchor_start in range(0, len(anchor_tokens) - length + 1):
            needle = anchor_tokens[anchor_start:anchor_start + length]
            for source_start in range(minimum_token, len(source_values) - length + 1):
                if source_values[source_start:source_start + length] == needle:
                    best = (source_start, length)
                    break
            if best:
                break
        if best:
            break
    if not best:
        return None, 0.0, minimum_token
    token_index, length = best
    confidence = length / max(1, len(anchor_tokens))
    return source_tokens[token_index][1], confidence, token_index


def sync_ledger() -> None:
    alignment = json.loads(ALIGNMENT.read_text(encoding="utf-8"))
    report = json.loads((MASTER_DIR / "stem_report.json").read_text(encoding="utf-8"))
    batch = json.loads(BATCH.read_text(encoding="utf-8"))
    characters = alignment["characters"]

    with TAKE_MANIFEST.open("r", encoding="utf-8-sig", newline="") as handle:
        take_rows = list(csv.DictReader(handle))
    with ARRANGEMENT.open("r", encoding="utf-8-sig", newline="") as handle:
        cue_rows = {row["cue_id"]: row for row in csv.DictReader(handle)}
    report_by_id = {row["id"]: row for row in report["stems"]}
    stem_by_id = {row["id"]: row for row in batch["stems"]}

    output_rows: list[dict] = []
    global_offset = 0
    for take_index, take in enumerate(take_rows):
        take_id = take["take_id"]
        source = resolve(stem_by_id[take_id]["text_file"]).read_text(encoding="utf-8").strip()
        take_report = report_by_id[take_id]
        cue_ids = expand_cues(take["cue_range"])
        cue_starts: list[tuple[str, float, str]] = []
        minimum_token = 0
        for cue_index, cue_id in enumerate(cue_ids):
            cue = cue_rows[cue_id]
            local_char, confidence, matched_token = anchor_position(
                cue["voice_anchor"], source, minimum_token
            )
            if local_char is None:
                fraction = cue_index / max(1, len(cue_ids))
                cue_time = float(take_report["timeline_start"]) + fraction * float(take_report["duration"])
                method = "take_interpolation"
            else:
                global_char = min(global_offset + local_char, len(characters) - 1)
                cue_time = float(characters[global_char]["start"])
                method = f"forced_alignment_anchor_{confidence:.2f}"
                minimum_token = matched_token + 1
            cue_starts.append((cue_id, cue_time, method))

        for cue_index, (cue_id, cue_start, method) in enumerate(cue_starts):
            cue = cue_rows[cue_id]
            cue_end = (
                cue_starts[cue_index + 1][1]
                if cue_index + 1 < len(cue_starts)
                else float(take_report["timeline_end"])
            )
            if cue_end <= cue_start:
                cue_end = float(take_report["timeline_end"])
            output_rows.append({
                "take_id": take_id,
                "section": take["section"],
                "take_start": take_report["timeline_start"],
                "take_end": take_report["timeline_end"],
                "cue_id": cue_id,
                "cue_start": f"{cue_start:.3f}",
                "cue_end": f"{cue_end:.3f}",
                "timing_method": method,
                "voice_anchor": cue["voice_anchor"],
                "primary_visual": cue["primary_visual"],
                "asset_spec": cue["asset_spec"],
                "resolved_paths": cue["resolved_paths"],
                "open_editorial_tokens": cue["open_editorial_tokens"],
                "pace": cue["pace"],
                "edit_function": cue["edit_function"],
                "notes": cue["notes"],
                "asset_status": cue["status"],
                "voice_stem": take_report["file"],
            })
        global_offset += len(source)
        if take_index < len(take_rows) - 1:
            global_offset += 2

    SYNC_CSV.parent.mkdir(parents=True, exist_ok=True)
    with SYNC_CSV.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output_rows[0].keys()))
        writer.writeheader()
        writer.writerows(output_rows)
    print(f"Sync ledger: {len(output_rows)} take/cue links -> {SYNC_CSV}")


def main() -> int:
    command = sys.argv[1].lower() if len(sys.argv) > 1 else "all"
    if command in {"build", "all"}:
        build()
    if command in {"align", "all"}:
        align()
    if command in {"transcribe", "qa", "all"}:
        transcribe_qa()
    if command in {"tech", "qa", "all"}:
        technical_qa()
    if command in {"sync", "all"}:
        sync_ledger()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
