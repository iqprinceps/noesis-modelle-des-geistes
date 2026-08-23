#!/usr/bin/env python3
"""Generate EP05 project-owned music/SFX stems from finished VO timing.

The generator is deterministic and streams audio in one-second chunks, so it
stays memory-safe even if the final narration is longer than expected.

Run from repository root after `python tools/ep05_voice.py all`:
    python tools/ep05_audio_stems.py

The outputs are working stems. Final loudness, ducking and mix targets are
specified in PRODUCTION_SUMMARY/EP05_JUNG_PAULI_V4/AUDIO_STEMS_PLAN.md.
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
CHUNK = SR
SEED = 5051952
PRE, GAP, TAIL, ENDCARD = 0.35, 0.65, 2.2, 20.0
ACT_GAIN = [0.85, 0.58, 0.70, 0.88, 0.74, 0.92, 1.00, 0.66]

FILES = [
    "EP05_MX_LOW.wav",
    "EP05_MX_HARMONIC.wav",
    "EP05_MX_NOISE.wav",
    "EP05_MX_MASTER.wav",
    "EP05_SFX_WORLD_CLOCK.wav",
    "EP05_SFX_PAPER_LETTERS.wav",
    "EP05_SFX_BEETLE_WINDOW.wav",
    "EP05_SFX_PHONE_NOTIFICATION.wav",
    "EP05_SFX_ROOMTONES.wav",
    "EP05_SFX_SLEEP_HANDOFF.wav",
]


def load_timing():
    if not REPORT.is_file():
        raise SystemExit(
            f"Missing {REPORT}\nGenerate raw voice, then run `python tools/ep05_voice.py all`."
        )
    data = json.loads(REPORT.read_text(encoding="utf-8"))
    durations = [float(s["duration"]) for s in data["stems"]]
    if len(durations) != 8:
        raise SystemExit("EP05 expects exactly eight voice stems.")
    starts, ends = [], []
    cur = PRE
    for i, dur in enumerate(durations):
        starts.append(cur)
        cur += dur
        ends.append(cur)
        if i < 7:
            cur += GAP
    total = cur + TAIL + ENDCARD
    return np.array(starts), np.array(ends), total


def open_wav(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    wf = wave.open(str(path), "wb")
    wf.setnchannels(2)
    wf.setsampwidth(2)
    wf.setframerate(SR)
    return wf


def write_stereo(wf, mono):
    mono = np.asarray(mono, dtype=np.float64)
    pcm = np.int16(np.clip(mono, -0.98, 0.98) * 32767)
    stereo = np.column_stack((pcm, pcm))
    wf.writeframes(stereo.tobytes())


def smooth_act_gain(t, starts, ends):
    """Return an act envelope with gentle 0.65 s transitions."""
    out = np.full_like(t, 0.22, dtype=np.float64)
    ramp = 0.65
    for idx, (a, b) in enumerate(zip(starts, ends)):
        g = ACT_GAIN[idx]
        inside = (t >= a) & (t <= b)
        out[inside] = g
        pre = (t >= a-ramp) & (t < a)
        if np.any(pre):
            p = (t[pre] - (a-ramp)) / ramp
            out[pre] = out[pre]*(1-p) + g*p
        post = (t > b) & (t <= b+ramp)
        if np.any(post):
            p = (t[post] - b) / ramp
            out[post] = g*(1-p) + out[post]*p
    return out


def event_burst(t, center, length, freq, amp, decay=20.0, second=None):
    rel = t-center
    mask = (rel >= 0) & (rel <= length)
    x = np.zeros_like(t)
    if not np.any(mask):
        return x
    r = rel[mask]
    tone = np.sin(2*np.pi*freq*r)
    if second:
        tone += second[1]*np.sin(2*np.pi*second[0]*r)
    x[mask] = amp*np.exp(-r*decay)*tone
    return x


def main():
    starts, ends, total = load_timing()
    n_total = int(math.ceil(total*SR))
    rng = np.random.default_rng(SEED)

    world_ticks = []
    for act in (0, 7):
        pos = starts[act] + 0.9
        k = 0
        while pos < ends[act]-0.25:
            pos += 0.68 + 0.13*math.sin(k*1.7)
            world_ticks.append(pos)
            k += 1

    paper_events = [starts[1]+5.0, starts[2]+4.0, starts[4]+7.0, starts[4]+21.0]
    beetle_event = starts[3] + 18.0
    phone_event = starts[5] + 12.0
    sleep_start = max(starts[7], ends[7]-28.0)
    footsteps = [max(sleep_start, ends[7]-7.0), max(sleep_start, ends[7]-4.3)]

    writers = {name: open_wav(OUT/name) for name in FILES}

    try:
        for offset in range(0, n_total, CHUNK):
            count = min(CHUNK, n_total-offset)
            t = (offset + np.arange(count, dtype=np.float64))/SR
            gain = smooth_act_gain(t, starts, ends)

            # Project-owned music bed. Harmonic energy stays phone-audible.
            low = 0.038*gain*(
                np.sin(2*np.pi*92.0*t + 0.10*np.sin(2*np.pi*0.055*t))
                + 0.42*np.sin(2*np.pi*138.0*t + 0.6)
            )*(0.70 + 0.30*(0.5+0.5*np.sin(2*np.pi*0.19*t)))

            harmonic = np.zeros(count)
            for i, freq in enumerate((742.0, 1113.0, 1484.0, 1855.0)):
                slow = 0.5+0.5*np.sin(2*np.pi*(0.025+0.007*i)*t+i)
                harmonic += (0.30/(i+1))*slow*np.sin(2*np.pi*freq*t+0.4*i)
            harmonic *= 0.020*gain

            white = rng.normal(0, 1, count)
            brown = np.cumsum(white)
            brown -= brown.mean()
            bpeak = np.max(np.abs(brown)) or 1.0
            noise = 0.010*gain*(0.25*white + 0.75*brown/bpeak)
            room = 0.0035*(0.55*white + 0.45*brown/bpeak)

            world = np.zeros(count)
            for sec in world_ticks:
                if t[0]-0.08 <= sec <= t[-1]+0.08:
                    world += event_burst(t, sec, .065, 1250, .075, 55, (620, .45))

            paper = np.zeros(count)
            for sec in paper_events:
                rel = t-sec
                mask = (rel >= 0) & (rel <= .55)
                if np.any(mask):
                    rr = rel[mask]
                    env = np.sin(np.pi*rr/.55)**2
                    paper[mask] += .018*rng.normal(0, 1, np.count_nonzero(mask))*env

            beetle = event_burst(t, beetle_event, .18, 1800, .085, 48, (2900, .45))
            phone = event_burst(t, phone_event, .38, 880, .038, 6.5, (1320, .42))

            sleep = np.zeros(count)
            mask = t >= sleep_start
            if np.any(mask):
                p = np.clip((t[mask]-sleep_start)/max(1.0, total-sleep_start), 0, 1)
                sleep[mask] += .0045*room[mask]*(p**1.6)/0.0035
            for sec in footsteps:
                sleep += event_burst(t, sec, .22, 82, .016, 18)

            write_stereo(writers["EP05_MX_LOW.wav"], low)
            write_stereo(writers["EP05_MX_HARMONIC.wav"], harmonic)
            write_stereo(writers["EP05_MX_NOISE.wav"], noise)
            write_stereo(writers["EP05_MX_MASTER.wav"], low+harmonic+noise)
            write_stereo(writers["EP05_SFX_WORLD_CLOCK.wav"], world)
            write_stereo(writers["EP05_SFX_PAPER_LETTERS.wav"], paper)
            write_stereo(writers["EP05_SFX_BEETLE_WINDOW.wav"], beetle)
            write_stereo(writers["EP05_SFX_PHONE_NOTIFICATION.wav"], phone)
            write_stereo(writers["EP05_SFX_ROOMTONES.wav"], room)
            write_stereo(writers["EP05_SFX_SLEEP_HANDOFF.wav"], sleep)
    finally:
        for wf in writers.values():
            wf.close()

    manifest = {
        "sample_rate": SR,
        "duration_seconds": round(total, 3),
        "source_timing": str(REPORT.relative_to(ROOT)),
        "generator_seed": SEED,
        "note": "Project-owned deterministic synthesis; mix/duck/loudness normalize in final audio stage.",
        "files": FILES,
    }
    (OUT/"audio_stem_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2)+"\n", encoding="utf-8"
    )
    print(f"Generated {len(FILES)} stems in {OUT}")


if __name__ == "__main__":
    main()
