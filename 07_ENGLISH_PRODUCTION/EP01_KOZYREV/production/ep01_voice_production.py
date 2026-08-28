#!/usr/bin/env python3
"""Prepare, master, align and independently QA the single selected EP01 voice."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
import uuid
from difflib import SequenceMatcher
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from elevenlabs.client import ElevenLabs


ROOT = Path(__file__).resolve().parents[3]
EP = ROOT / "07_ENGLISH_PRODUCTION" / "EP01_KOZYREV"
SCRIPT = EP / "01_SCRIPT" / "VOICE_SCRIPT_EN.txt"
VOICE = EP / "02_VOICE"
SOURCE = VOICE / "source"
RAW = VOICE / "raw_stems"
MASTER_DIR = VOICE / "master"
MASTER = MASTER_DIR / "EP01_EN_KOZYREV_VO_MASTER.wav"
ALIGN = VOICE / "alignment" / "EP01_EN_KOZYREV_alignment.json"
QA = VOICE / "qa" / "EP01_EN_KOZYREV_SCRIBE_QA.json"
CLI_TOOLS = Path(r"C:\Users\iQPrinceps\Documents\Codex\NOESIS Channel\tools")

PRE, GAP, TAIL = 0.35, 0.60, 2.20
ACTS = [
    ("01_HOOK", "Why did a medical device need to rotate?"),
    ("02_KOZYREV", "Nikolai Alexandrovich Kozyrev was a Soviet astronomer and astrophysicist."),
    ("03_MACHINE", "Then they make the apparatus stranger."),
    ("04_ESCALATION", "But Kaznacheev and Trofimov did not keep the idea inside medicine."),
    ("05_THREE_THEORIES", "At this point, the chamber becomes more than a reflector."),
    ("06_BLIND_TARGET", "Imagine four sealed target images."),
    ("07_MISSING_RESULT", "That is why the missing experiment matters more than another story from inside the chamber."),
    ("08_RESIDUE_HANDOFF", "So what remains when the stories are pulled apart?"),
]

VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"
VOICE_NAME = "George - Warm, Captivating Storyteller"
MODEL = "eleven_multilingual_v2"
SETTINGS = {
    "stability": 0.52,
    "similarity_boost": 0.82,
    "style": 0.10,
    "speed": 1.08,
    "use_speaker_boost": True,
}
SEED = 2403


def run(args: list[str], capture: bool = False) -> str:
    result = subprocess.run(args, text=True, capture_output=capture)
    if result.returncode:
        raise RuntimeError((result.stderr or result.stdout or "failed")[-6000:])
    return (result.stdout or "") + (result.stderr or "")


def duration(path: Path) -> float:
    return float(
        run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
            True,
        ).strip()
    )


def load_key() -> str:
    sys.path.insert(0, str(CLI_TOOLS))
    from elevenlabs_cli import _load_key  # type: ignore

    return str(_load_key())


def split_acts(text: str) -> list[tuple[str, str]]:
    positions = []
    for name, marker in ACTS:
        pos = text.find(marker)
        if pos < 0:
            raise RuntimeError(f"Act marker missing: {marker}")
        positions.append((pos, name))
    if positions != sorted(positions):
        raise RuntimeError("Act markers out of order")
    output = []
    for index, (start, name) in enumerate(positions):
        end = positions[index + 1][0] if index + 1 < len(positions) else len(text)
        output.append((name, text[start:end].strip()))
    if "\n\n".join(body for _, body in output) != text.strip():
        raise RuntimeError("Act split does not reconstruct canonical script")
    return output


def prepare() -> None:
    text = SCRIPT.read_text(encoding="utf-8").strip()
    acts = split_acts(text)
    SOURCE.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    stems = []
    report = []
    for name, body in acts:
        stem_id = f"EP01_EN_{name}"
        path = SOURCE / f"{stem_id}.txt"
        path.write_text(body + "\n", encoding="utf-8")
        stems.append({"id": stem_id, "text_file": str(path.resolve())})
        report.append({"id": stem_id, "characters": len(body), "words": len(re.findall(r"\b[\w-]+\b", body))})
    batch = {
        "voice": VOICE_ID,
        "voice_name": VOICE_NAME,
        "model": MODEL,
        "settings": SETTINGS,
        "seed": SEED,
        "output_format": "mp3_44100_128",
        "output_dir": str(RAW.resolve()),
        "stems": stems,
    }
    (VOICE / "voice_batch.json").write_text(json.dumps(batch, indent=2) + "\n", encoding="utf-8")
    (VOICE / "stems.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Prepared {len(stems)} stems / {sum(x['words'] for x in report)} words")


def loudness(path: Path, target: float = -18.0, peak: float = -2.0) -> dict:
    output = run(
        [
            "ffmpeg", "-hide_banner", "-nostats", "-i", str(path),
            "-af", f"loudnorm=I={target}:TP={peak}:LRA=7:print_format=json", "-f", "null", "-",
        ],
        True,
    )
    return json.loads(re.findall(r'\{\s*"input_i".*?\}', output, re.S)[-1])


def normalize(src: Path, dst: Path) -> None:
    stats = loudness(src)
    dst.parent.mkdir(parents=True, exist_ok=True)
    run(
        [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(src),
            "-af",
            (
                f"loudnorm=I=-18:TP=-2:LRA=7:measured_I={stats['input_i']}:"
                f"measured_TP={stats['input_tp']}:measured_LRA={stats['input_lra']}:"
                f"measured_thresh={stats['input_thresh']}:offset={stats['target_offset']}:linear=true,"
                "apad=pad_dur=0.12"
            ),
            "-ac", "2", "-ar", "48000", "-c:a", "pcm_s24le", str(dst),
        ]
    )


def silence(path: Path, seconds: float) -> None:
    run(
        [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "lavfi",
            "-i", f"anullsrc=r=48000:cl=stereo:d={seconds}", "-c:a", "pcm_s24le", str(path),
        ]
    )


def build_master() -> None:
    batch = json.loads((VOICE / "voice_batch.json").read_text(encoding="utf-8"))
    normal = MASTER_DIR / "stems"
    normal.mkdir(parents=True, exist_ok=True)
    parts: list[str] = []
    stem_report = []
    cursor = PRE
    pre = MASTER_DIR / "pre.wav"
    silence(pre, PRE)
    parts.append(f"file '{pre.as_posix()}'")
    for index, stem in enumerate(batch["stems"]):
        src = RAW / f"{stem['id']}.mp3"
        if not src.exists():
            raise FileNotFoundError(src)
        dst = normal / f"{stem['id']}.wav"
        normalize(src, dst)
        d = duration(dst)
        parts.append(f"file '{dst.as_posix()}'")
        stem_report.append({"id": stem["id"], "start": round(cursor, 3), "end": round(cursor + d, 3), "duration": round(d, 3)})
        cursor += d
        if index < len(batch["stems"]) - 1:
            gap = MASTER_DIR / f"gap_{index + 1:02d}.wav"
            silence(gap, GAP)
            parts.append(f"file '{gap.as_posix()}'")
            cursor += GAP
    tail = MASTER_DIR / "tail.wav"
    silence(tail, TAIL)
    parts.append(f"file '{tail.as_posix()}'")
    concat = MASTER_DIR / "concat.txt"
    concat.write_text("\n".join(parts) + "\n", encoding="utf-8")
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(concat), "-c:a", "pcm_s24le", str(MASTER)])
    final_stats = loudness(MASTER)
    report = {
        "voice": VOICE_ID,
        "voice_name": VOICE_NAME,
        "model": MODEL,
        "settings": SETTINGS,
        "seed": SEED,
        "sample_rate_hz": 48000,
        "channels": 2,
        "codec": "pcm_s24le",
        "duration": round(duration(MASTER), 3),
        "measured": final_stats,
        "stems": stem_report,
        "sha256": hashlib.sha256(MASTER.read_bytes()).hexdigest(),
    }
    (MASTER_DIR / "stem_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"master": str(MASTER), "duration": report["duration"], "measured": final_stats}, indent=2))


def normalize_alignment(data: dict) -> dict:
    chars = data.get("characters")
    if isinstance(chars, list) and chars and isinstance(chars[0], dict):
        data = dict(data)
        data["raw_characters"] = chars
        data["characters"] = [item.get("text", "") for item in chars]
        data["character_start_times_seconds"] = [float(item.get("start", 0)) for item in chars]
        data["character_end_times_seconds"] = [float(item.get("end", 0)) for item in chars]
    return data


def align() -> None:
    text = SCRIPT.read_text(encoding="utf-8").strip()
    boundary = "----EP01" + uuid.uuid4().hex
    body = b"".join(
        [
            f"--{boundary}\r\n".encode(),
            b'Content-Disposition: form-data; name="text"\r\n\r\n', text.encode(), b"\r\n",
            f"--{boundary}\r\n".encode(),
            f'Content-Disposition: form-data; name="file"; filename="{MASTER.name}"\r\n'.encode(),
            b"Content-Type: audio/wav\r\n\r\n", MASTER.read_bytes(), b"\r\n",
            f"--{boundary}--\r\n".encode(),
        ]
    )
    request = Request(
        "https://api.elevenlabs.io/v1/forced-alignment",
        data=body,
        headers={"xi-api-key": load_key(), "Content-Type": f"multipart/form-data; boundary={boundary}", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=900) as response:
            data = json.loads(response.read().decode())
    except HTTPError as exc:
        raise RuntimeError(f"Alignment HTTP {exc.code}: {exc.read().decode(errors='replace')[:1000]}")
    data = normalize_alignment(data)
    data.update({"source_text": text, "audio": str(MASTER.resolve()), "audio_sha256": hashlib.sha256(MASTER.read_bytes()).hexdigest()})
    ALIGN.parent.mkdir(parents=True, exist_ok=True)
    ALIGN.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Alignment saved: {ALIGN}")


def tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.casefold())


def as_dict(value) -> dict:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if hasattr(value, "dict"):
        return value.dict()
    return json.loads(value.json())


def content_qa() -> None:
    client = ElevenLabs(api_key=load_key())
    with MASTER.open("rb") as audio:
        response = client.speech_to_text.convert(
            model_id="scribe_v2",
            file=audio,
            language_code="en",
            tag_audio_events=False,
            diarize=False,
            timestamps_granularity="word",
            seed=82601,
            keyterms=["Kozyrev", "Kaznacheev", "Trofimov", "Novosibirsk", "magneto-ionospheric", "Fort Meade"],
        )
    raw = as_dict(response)
    expected = tokens(SCRIPT.read_text(encoding="utf-8"))
    heard = tokens(str(raw.get("text", "")))
    matcher = SequenceMatcher(None, expected, heard, autojunk=False)
    report = {
        "purpose": "independent content and transition QA",
        "model": "scribe_v2",
        "expected_words": len(expected),
        "heard_words": len(heard),
        "sequence_similarity": round(matcher.ratio(), 6),
        "transcription": raw,
    }
    QA.parent.mkdir(parents=True, exist_ok=True)
    QA.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "transcription"}, indent=2))


def main() -> int:
    command = sys.argv[1] if len(sys.argv) > 1 else "prepare"
    if command == "prepare":
        prepare()
    elif command == "master":
        build_master()
    elif command == "align":
        align()
    elif command == "qa":
        content_qa()
    else:
        raise SystemExit("Usage: ep01_voice_production.py [prepare|master|align|qa]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
