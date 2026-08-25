#!/usr/bin/env python3
"""Create restrained, project-owned EP04A atmospheres and sound effects.

All material is deterministic synthesis: no third-party recordings, no branded
phone sound, no horror stingers, no ritual audio, and no snake hiss.
"""

from __future__ import annotations

import json
import math
import subprocess
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
VOICE_REPORT = (
    ROOT / "06_PRODUCTION" / "JUNG_SERIES_V1" / "VOICE_EP04A" / "master" / "stem_report.json"
)
OUT = ROOT / "06_PRODUCTION" / "JUNG_SERIES_V1" / "RENDER_EP04A" / "audio" / "sfx_stems"
SR = 48000
CHUNK = SR
SEED = 40411

STEMS = [
    "EP04A_SFX_ARCHIVE_ROOM",
    "EP04A_SFX_TRAIN_ABSTRACT",
    "EP04A_SFX_INNER_WATER",
    "EP04A_SFX_CAVE_RESONANCE",
    "EP04A_SFX_BODY_MICRO",
    "EP04A_SFX_PHONE_ROOM",
    "EP04A_SFX_PAPER_CONTACTS",
    "EP04A_SFX_DESCENT",
    "EP04A_SFX_PAULI_HANDOFF",
]


def smooth01(values: np.ndarray) -> np.ndarray:
    values = np.clip(values, 0.0, 1.0)
    return values * values * (3.0 - 2.0 * values)


def segment_envelope(t: np.ndarray, segments: list[tuple[float, float, float]], fade: float = 0.8) -> np.ndarray:
    result = np.zeros_like(t)
    for start, end, gain in segments:
        inside = (t >= start) & (t <= end)
        result[inside] = np.maximum(result[inside], gain)
        if fade > 0:
            pre = (t >= start - fade) & (t < start)
            result[pre] = np.maximum(result[pre], gain * smooth01((t[pre] - start + fade) / fade))
            post = (t > end) & (t <= end + fade)
            result[post] = np.maximum(result[post], gain * smooth01((end + fade - t[post]) / fade))
    return result


def noise_burst(t: np.ndarray, start: float, length: float, amplitude: float, noise: np.ndarray) -> np.ndarray:
    result = np.zeros_like(t)
    mask = (t >= start) & (t <= start + length)
    if np.any(mask):
        phase = (t[mask] - start) / length
        result[mask] = amplitude * noise[mask] * np.sin(np.pi * phase) ** 2
    return result


def chirp(t: np.ndarray, start: float, length: float, high: float, low: float, amplitude: float) -> np.ndarray:
    result = np.zeros_like(t)
    mask = (t >= start) & (t <= start + length)
    if np.any(mask):
        rel = t[mask] - start
        rate = (low - high) / length
        phase = 2.0 * np.pi * (high * rel + 0.5 * rate * rel * rel)
        env = np.sin(np.pi * rel / length) ** 2
        result[mask] = amplitude * env * np.sin(phase)
    return result


def generate_signals(t: np.ndarray, rng: np.random.Generator) -> dict[str, np.ndarray]:
    white = rng.normal(0.0, 1.0, len(t))
    walk = np.cumsum(rng.normal(0.0, 0.018, len(t)))
    walk -= np.linspace(walk[0], walk[-1], len(t))
    walk /= max(1.0, float(np.max(np.abs(walk))))

    archive_env = segment_envelope(t, [
        (0.0, 22.27, .85), (38.1, 78.3, .45), (93.34, 139.96, .75),
        (217.66, 315.72, .82), (344.1, 397.26, .55), (449.448, 613.436, .70),
    ], 1.0)
    archive = archive_env * (.0020 * white + .0032 * walk + .0010 * np.sin(2*np.pi*73*t))

    train_env = segment_envelope(t, [(58.58, 78.3, 1.0)], .35)
    click_gate = np.maximum(0.0, np.sin(2*np.pi*1.9*t)) ** 18
    train = train_env * (
        .0045 * walk + .0030 * np.sin(2*np.pi*(58 + 2*np.sin(2*np.pi*.08*t))*t)
        + .0030 * click_gate * white
    )

    water_env = segment_envelope(t, [
        (27.04, 34.38, 1.0), (38.1, 58.58, .48), (78.3, 93.34, .95),
        (166.36, 181.56, .55), (330.22, 335.68, .72),
        (539.96, 547.86, .55), (547.86, 588.74, .22),
    ], .8)
    water = water_env * (
        .0040 * walk + .0028 * white + .0030 * np.sin(2*np.pi*(38+.8*np.sin(2*np.pi*.011*t))*t)
    )

    cave_env = segment_envelope(t, [
        (27.04, 29.54, .55), (162.15, 217.66, 1.0), (539.96, 547.86, .45),
    ], 1.2)
    cave_gate = .35 + .65 * smooth01(.5 + .5*np.sin(2*np.pi*.073*t))
    cave = cave_env * cave_gate * (
        .0032*np.sin(2*np.pi*310*t) + .0018*np.sin(2*np.pi*465*t+1.2) + .0013*walk
    )

    body_env = segment_envelope(t, [
        (315.72, 330.22, .55), (335.68, 397.26, .92), (402.68, 449.448, .82),
    ], .55)
    body = body_env * (.0027*white + .0020*walk + .0016*np.sin(2*np.pi*54*t))

    phone_env = segment_envelope(t, [(397.26, 427.86, .55), (423.76, 427.86, .22)], .25)
    phone = phone_env * (.0015*white + .0014*walk)
    phone += noise_burst(t, 397.26, .06, .030, white)
    phone += noise_burst(t, 412.20, .07, .025, white)
    phone += noise_burst(t, 412.54, .07, .023, white)

    paper = np.zeros_like(t)
    events = [
        (4.84,.45,.038), (34.38,.42,.028), (93.34,.45,.040), (109.90,.55,.045),
        (239.12,.45,.038), (252.70,.45,.042), (260.10,.35,.030),
        (268.38,.38,.030), (278.10,.38,.032), (284.20,.36,.040), (290.30,.38,.032),
        (302.78,.30,.026), (472.64,.55,.052), (478.26,.48,.040),
        (488.70,.46,.042), (491.76,.20,.030), (510.30,.38,.032),
        (513.50,.38,.030), (517.72,.55,.037), (609.08,.42,.030),
    ]
    for start, length, amplitude in events:
        paper += noise_burst(t, start, length, amplitude, white)

    descent = chirp(t, 135.58, 1.8, 420, 70, .045)
    descent += chirp(t, 158.72, 3.0, 460, 62, .060)
    descent += segment_envelope(t, [(135.58,137.58,.50),(158.72,161.72,.90)], .1) * .012 * walk

    pauli = np.zeros_like(t)
    rel = t - 596.50
    mask = (rel >= 0) & (rel <= .55)
    if np.any(mask):
        r = rel[mask]
        pauli[mask] = .060 * np.exp(-5.5*r) * (
            np.sin(2*np.pi*610*r) + .35*np.sin(2*np.pi*915*r)
        )

    return {
        "EP04A_SFX_ARCHIVE_ROOM": archive,
        "EP04A_SFX_TRAIN_ABSTRACT": train,
        "EP04A_SFX_INNER_WATER": water,
        "EP04A_SFX_CAVE_RESONANCE": cave,
        "EP04A_SFX_BODY_MICRO": body,
        "EP04A_SFX_PHONE_ROOM": phone,
        "EP04A_SFX_PAPER_CONTACTS": paper,
        "EP04A_SFX_DESCENT": descent,
        "EP04A_SFX_PAULI_HANDOFF": pauli,
    }


def main() -> int:
    report = json.loads(VOICE_REPORT.read_text(encoding="utf-8"))
    duration = float(report["master_duration"])
    total_samples = int(round(duration * SR))
    OUT.mkdir(parents=True, exist_ok=True)
    raw_paths = {stem: OUT / f".{stem}.f32" for stem in STEMS}
    files = {stem: raw_paths[stem].open("wb") for stem in STEMS}
    rng = np.random.default_rng(SEED)
    try:
        for offset in range(0, total_samples, CHUNK):
            count = min(CHUNK, total_samples - offset)
            t = (offset + np.arange(count, dtype=np.float64)) / SR
            signals = generate_signals(t, rng)
            for stem, signal in signals.items():
                files[stem].write(np.asarray(signal, dtype="<f4").tobytes())
    finally:
        for handle in files.values():
            handle.close()

    outputs = []
    for stem in STEMS:
        raw = raw_paths[stem]
        wav = OUT / f"{stem}.wav"
        subprocess.run([
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", str(raw),
            "-ac", "2", "-c:a", "pcm_s24le", str(wav),
        ], check=True)
        raw.unlink()
        outputs.append(str(wav.resolve()))
        print(wav)

    manifest = {
        "episode": "EP04A",
        "duration_seconds": round(duration, 3),
        "sample_rate": SR,
        "channels": 2,
        "codec": "pcm_s24le",
        "generator_seed": SEED,
        "source": "project-owned deterministic synthesis",
        "restrictions": [
            "no third-party recordings", "no branded phone sound", "no snake hiss",
            "no horror stingers", "no battle audio", "no ritual audio", "no heartbeat",
        ],
        "files": outputs,
    }
    (OUT / "sfx_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
