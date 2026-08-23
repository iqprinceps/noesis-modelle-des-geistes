#!/usr/bin/env python3
"""Generate EP05 project-owned music/SFX stems from the finished VO timing.

No third-party music is used. The script reads the voice stem report produced by
`tools/ep05_voice.py`, derives act boundaries from the eight voice stems, and
writes deterministic 48 kHz WAV stems for the production mix.

Usage from repository root:
    python tools/ep05_audio_stems.py
"""

from __future__ import annotations

import json
import math
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PROD = ROOT / "PRODUCTION_SUMMARY" / "EP05_JUNG_PAULI_V4"
REPORT = PROD / "voice" / "master" / "stem_report.json"
OUT = PROD / "audio" / "stems"
SR = 48000
SEED = 5051952

ACT_GAIN = np.array([0.85, 0.58, 0.70, 0.88, 0.74, 0.92, 1.00, 0.66], dtype=float)
GAP = 0.65
PRE = 0.35
TAIL = 2.2


def write_wav(path: Path, x: np.ndarray, stereo: bool = True):
    path.parent.mkdir(parents=True, exist_ok=True)
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 1 and stereo:
        x = np.column_stack([x, x])
    peak = float(np.max(np.abs(x))) if x.size else 1.0
    if peak > 0.98:
        x = x * (0.98 / peak)
    pcm = np.int16(np.clip(x, -1, 1) * 32767)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(2 if x.ndim == 2 else 1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())


def fade(x: np.ndarray, sec: float = 0.08):
    n = min(len(x)//2, int(sec*SR))
    if n <= 0:
        return x
    ramp = np.linspace(0, 1, n)
    x[:n] *= ramp
    x[-n:] *= ramp[::-1]
    return x


def load_timing():
    if not REPORT.is_file():
        raise SystemExit(
            f"Missing {REPORT}\nRun voice first: generate raw ElevenLabs stems, then `python tools/ep05_voice.py all`."
        )
    data = json.loads(REPORT.read_text(encoding="utf-8"))
    ds = [float(s["duration"]) for s in data["stems"]]
    if len(ds) != 8:
        raise SystemExit("EP05 expects exactly 8 voice stems.")
    starts, ends = [], []
    cur = PRE
    for i, d in enumerate(ds):
        starts.append(cur)
        cur += d
        ends.append(cur)
        if i < 7:
            cur += GAP
    total = cur + TAIL + 20.0  # include endcard bed
    return ds, np.array(starts), np.array(ends), total


def act_envelope(n: int, starts: np.ndarray, ends: np.ndarray):
    env = np.full(n, 0.25, dtype=np.float64)
    for i, (a, b) in enumerate(zip(starts, ends)):
        ia, ib = int(a*SR), min(n, int(b*SR))
        env[ia:ib] = ACT_GAIN[i]
    # Smooth envelope on ~0.8 s scale without scipy.
    win = max(3, int(0.8*SR))
    kernel = np.ones(win, dtype=np.float64) / win
    return np.convolve(env, kernel, mode="same")


def pinkish_noise(rng, n: int):
    white = rng.normal(0, 1, n)
    # Lightweight multi-timescale smoothing gives a pink-ish texture.
    out = np.zeros(n)
    for width, gain in [(7, .35), (31, .25), (127, .20), (511, .12)]:
        kernel = np.ones(width)/width
        out += gain*np.convolve(white, kernel, mode="same")
    out += .08*white
    return out / max(1e-9, np.max(np.abs(out)))


def music_low(t, env):
    # Dark ordered foundation: two slow sines below phone-hostile sub-bass range.
    phase = 2*np.pi*(92.0*t + 0.10*np.sin(2*np.pi*0.055*t))
    x = np.sin(phase) + 0.42*np.sin(2*np.pi*138.0*t + 0.6)
    pulse = 0.70 + 0.30*(0.5+0.5*np.sin(2*np.pi*0.19*t))
    return 0.038*x*pulse*env


def music_harmonic(t, env):
    # Audible on phones: sparse partials in 700–2600 Hz, no meditation-pad wash.
    freqs = [742.0, 1113.0, 1484.0, 1855.0]
    x = np.zeros_like(t)
    for i, f in enumerate(freqs):
        slow = 0.5 + 0.5*np.sin(2*np.pi*(0.025+0.007*i)*t + i)
        x += (0.30/(i+1))*slow*np.sin(2*np.pi*f*t + 0.4*i)
    return 0.020*x*env


def music_noise(rng, n, env):
    return 0.010*pinkish_noise(rng, n)*env


def sfx_world_clock(total, starts, ends):
    n = int(total*SR)
    x = np.zeros(n)
    rng = np.random.default_rng(SEED+1)
    regions = [(starts[0], ends[0]), (starts[7], min(total, ends[7]))]
    for a, b in regions:
        pos = a + 0.8
        k = 0
        while pos < b-0.3:
            pos += 0.68 + 0.13*math.sin(k*1.7) + rng.uniform(-0.035, 0.035)
            i = int(pos*SR)
            m = min(int(.065*SR), n-i)
            if m <= 0:
                break
            tt = np.arange(m)/SR
            hit = np.exp(-tt*55)*(np.sin(2*np.pi*1250*tt)+.45*np.sin(2*np.pi*620*tt))
            x[i:i+m] += .09*hit
            k += 1
    return x


def sfx_paper(total, starts, ends):
    n = int(total*SR)
    x = np.zeros(n)
    rng = np.random.default_rng(SEED+2)
    for sec in [starts[1]+5, starts[2]+4, starts[4]+7, starts[4]+21]:
        i = int(sec*SR)
        m = min(int(.55*SR), n-i)
        if m <= 0:
            continue
        tt = np.arange(m)/SR
        noise = rng.normal(0, 1, m)
        env = np.sin(np.pi*np.clip(tt/.55, 0, 1))**2
        x[i:i+m] += .028*noise*env
    return x


def sfx_beetle(total, starts):
    n = int(total*SR)
    x = np.zeros(n)
    sec = starts[3] + 18.0
    i = int(sec*SR)
    m = min(int(.18*SR), n-i)
    if m > 0:
        tt = np.arange(m)/SR
        tap = np.exp(-tt*48)*(np.sin(2*np.pi*1800*tt)+.45*np.sin(2*np.pi*2900*tt))
        x[i:i+m] += .10*tap
    return x


def sfx_phone(total, starts):
    n = int(total*SR)
    x = np.zeros(n)
    sec = starts[5] + 12.0
    i = int(sec*SR)
    m = min(int(.38*SR), n-i)
    if m > 0:
        tt = np.arange(m)/SR
        env = np.exp(-tt*6.5)
        tone = np.sin(2*np.pi*880*tt)+.42*np.sin(2*np.pi*1320*tt)
        x[i:i+m] += .045*env*tone
    return x


def sfx_roomtones(rng, total):
    n = int(total*SR)
    base = pinkish_noise(rng, n)
    return 0.0045*base


def sfx_sleep_handoff(total, starts, ends):
    n = int(total*SR)
    x = np.zeros(n)
    rng = np.random.default_rng(SEED+4)
    a = max(starts[7], ends[7]-28.0)
    ia = int(a*SR)
    m = n-ia
    if m <= 0:
        return x
    noise = pinkish_noise(rng, m)
    env = np.linspace(0, 1, m)**1.8
    x[ia:] += .006*noise*env
    # Two tiny, ambiguous low floor/door transients near final handoff.
    for sec in [ends[7]-7.0, ends[7]-4.3]:
        i = int(sec*SR)
        mm = min(int(.22*SR), n-i)
        if mm > 0:
            tt = np.arange(mm)/SR
            x[i:i+mm] += .018*np.exp(-tt*18)*np.sin(2*np.pi*82*tt)
    return x


def main():
    _, starts, ends, total = load_timing()
    n = int(math.ceil(total*SR))
    t = np.arange(n)/SR
    env = act_envelope(n, starts, ends)
    rng = np.random.default_rng(SEED)

    low = music_low(t, env)
    harmonic = music_harmonic(t, env)
    noise = music_noise(rng, n, env)

    write_wav(OUT / "EP05_MX_LOW.wav", low)
    write_wav(OUT / "EP05_MX_HARMONIC.wav", harmonic)
    write_wav(OUT / "EP05_MX_NOISE.wav", noise)
    write_wav(OUT / "EP05_MX_MASTER.wav", low + harmonic + noise)

    write_wav(OUT / "EP05_SFX_WORLD_CLOCK.wav", sfx_world_clock(total, starts, ends))
    write_wav(OUT / "EP05_SFX_PAPER_LETTERS.wav", sfx_paper(total, starts, ends))
    write_wav(OUT / "EP05_SFX_BEETLE_WINDOW.wav", sfx_beetle(total, starts))
    write_wav(OUT / "EP05_SFX_PHONE_NOTIFICATION.wav", sfx_phone(total, starts))
    write_wav(OUT / "EP05_SFX_ROOMTONES.wav", sfx_roomtones(np.random.default_rng(SEED+3), total))
    write_wav(OUT / "EP05_SFX_SLEEP_HANDOFF.wav", sfx_sleep_handoff(total, starts, ends))

    manifest = {
        "sample_rate": SR,
        "duration_seconds": round(total, 3),
        "source_timing": str(REPORT.relative_to(ROOT)),
        "note": "Project-owned deterministic synthesis. Mix/duck and loudness-normalize in final audio stage.",
        "files": sorted(p.name for p in OUT.glob("*.wav")),
    }
    (OUT / "audio_stem_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2)+"\n", encoding="utf-8"
    )
    print(f"Generated {len(manifest['files'])} stems in {OUT}")


if __name__ == "__main__":
    main()
