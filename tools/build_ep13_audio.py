#!/usr/bin/env python3
"""EP13_EN music, SFX and final mix.

All material is project-owned deterministic synthesis, following the channel's
existing audio approach: no third-party recordings, no library stingers, no
whoosh on every cut.

Two rules from 00_GLOBAL/ENGLISH_PRODUCTION_STANDARD.md drive the design:

  * music changes texture, density or motif when the episode changes world, so a
    single permanent drone is not a score;
  * SFX are semantic accents tied to something visible or spoken, they sit below
    speech, and they are checked against consonant intelligibility.

Section boundaries and SFX placement both come from the cue sheet, so every
sound lands on the beat it belongs to rather than on a grid.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import pathlib
import subprocess
import wave

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
EP = ROOT / "07_ENGLISH_PRODUCTION" / "EP13_VATICAN_01"
CUE = EP / "05_DELIVERY" / "EP13_EN_VISUAL_CUE_SHEET.csv"
VOICE = EP / "02_VOICE" / "MASTER" / "EP13_EN_VO_MASTER.wav"
PICTURE = ROOT / "tmp" / "render" / "ep13" / "EP13_EN_PICTURE.mp4"
AUDIO = EP / "04_AUDIO"
STEMS = AUDIO / "stems"
MIXWAV = AUDIO / "EP13_EN_FINAL_MIX.wav"
FINAL = EP / "05_DELIVERY" / "EP13_EN_FINAL.mp4"

SR = 48000
SEED = 130513
rng = np.random.default_rng(SEED)

# The episode's worlds, in seconds, taken from the act turns in the script.
# name, start, character
SECTIONS = [
    ("cold_open", 0.0, "object"),
    ("becomes_object", 56.0, "paper"),
    ("the_waiting", 105.0, "held"),
    ("the_attack", 157.0, "pressure"),
    ("the_room", 190.0, "held"),
    ("the_reveal", 227.0, "vision"),
    ("the_absence", 281.0, "vision"),
    ("recognition", 310.0, "paper"),
    ("the_crown", 372.0, "object"),
    ("the_form", 430.0, "held"),
    ("handoff", 460.0, "pressure"),
]

# state id fragment -> sfx kind, placed at that shot's in-point
SFX_MAP = {
    "CLIP03_WRITING": "pencil",
    "CLIP04_SEALING": "wax",
    "CLIP09_PUTTING_IT_AWAY": "lid",
    "H06_FOLDING_SHEET": "paper",
    "H01_ENVELOPE_SEALED": "paper",
    "H36_KEY_RING": "keys",
    "H35_SAFE_DOOR": "metaldoor",
    "H18_LOCKED_DOOR": "metaldoor",
    "H20_CROWD_TURNING": "crowdturn",
    "P04_CROWD_ALARM_FACES": "crowdturn",
    "H12_SQUARE_CROWD_1981": "crowd",
    "P03_CROWD_FACES_1981": "crowd",
    "P15_OPEN_CAR_IN_CROWD": "crowd",
    "H22_SURGICAL_LIGHT": "roomclinic",
    "H13_CORRIDOR_1981": "roomclinic",
    "P13_DOCTORS_CORRIDOR": "roomclinic",
    "H27_ARCHIVE_LEDGER": "paper",
    "H32_SEALS_ON_CORD": "metalclink",
    "H53_WIDE_PARCHMENT_EDGE": "metalclink",
    "H54_SEAL_SINGLE_MACRO": "metalclink",
    "H34_WASTE_PAPER_WEIGHED": "weights",
    "H57_SCALE_PAN_EMPTY": "weights",
    "H29_CANDLE_WALL": "flame",
    "P07_PILGRIMS_CANDLES": "flame",
    "CLIP08_SETTING_THE_METAL": "setmetal",
    "H16_NEWSPAPER_STACK": "paper",
    "H39_CALENDAR_PAGES": "paper",
    "H33_CRATES_MOUNTAIN_ROAD": "cart",
    "H55_CART_WHEEL_MUD": "cart",
}


def read_wav(path):
    with wave.open(str(path), "rb") as w:
        n, sw, ch = w.getnframes(), w.getsampwidth(), w.getnchannels()
        raw = w.readframes(n)
    dtype = {2: np.int16, 3: None, 4: np.int32}[sw]
    if sw == 3:
        a = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3).astype(np.int32)
        data = (a[:, 0] | (a[:, 1] << 8) | (a[:, 2].astype(np.int8).astype(np.int32) << 16)).astype(np.float64)
        data /= 2 ** 23
    else:
        data = np.frombuffer(raw, dtype=dtype).astype(np.float64) / np.iinfo(dtype).max
    if ch > 1:
        data = data.reshape(-1, ch).mean(axis=1)
    return data


def write_wav(path, mono, peak_norm=None):
    x = np.asarray(mono, dtype=np.float64)
    if peak_norm:
        m = np.max(np.abs(x)) or 1.0
        x = x / m * peak_norm
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


def env(n, attack, release):
    e = np.ones(n)
    a, r = int(attack * SR), int(release * SR)
    if a:
        e[:a] = np.linspace(0, 1, a) ** 1.6
    if r:
        e[-r:] = np.linspace(1, 0, r) ** 1.6
    return e


def lp(x, cutoff):
    """One-pole low pass, stable and cheap."""
    a = math.exp(-2 * math.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(0, len(x), 8192):
        blk = x[i:i + 8192]
        out = np.empty_like(blk)
        for j, v in enumerate(blk):
            acc = a * acc + (1 - a) * v
            out[j] = acc
        y[i:i + 8192] = out
    return y


def noise(n, cutoff=2000.0):
    return lp(rng.standard_normal(n), cutoff)


# ---------------------------------------------------------------- music -----

def bed(character, n, t0):
    """One section of score. Each character is a different texture, not a drone."""
    t = (np.arange(n) + int(t0 * SR)) / SR
    out = np.zeros(n)
    if character == "object":
        for f, g in ((55.0, 0.42), (82.5, 0.16), (110.0, 0.10)):
            out += g * np.sin(2 * math.pi * f * t + 0.3 * np.sin(2 * math.pi * 0.031 * t))
        out += 0.05 * noise(n, 320)
    elif character == "paper":
        for f, g in ((73.4, 0.34), (110.0, 0.14), (146.8, 0.07)):
            out += g * np.sin(2 * math.pi * f * t)
        out += 0.09 * noise(n, 900) * (0.5 + 0.5 * np.sin(2 * math.pi * 0.07 * t))
    elif character == "held":
        out += 0.40 * np.sin(2 * math.pi * 49.0 * t)
        out += 0.11 * np.sin(2 * math.pi * 98.0 * t + 0.6)
        out *= 0.75 + 0.25 * np.sin(2 * math.pi * 0.021 * t)
        out += 0.035 * noise(n, 240)
    elif character == "pressure":
        out += 0.44 * np.sin(2 * math.pi * 41.2 * t)
        out += 0.18 * np.sin(2 * math.pi * 61.8 * t)
        out += 0.13 * noise(n, 520) * (0.6 + 0.4 * np.sin(2 * math.pi * 0.11 * t))
    elif character == "vision":
        for f, g in ((146.8, 0.20), (220.0, 0.13), (293.7, 0.08), (440.0, 0.05)):
            out += g * np.sin(2 * math.pi * f * t + 0.4 * np.sin(2 * math.pi * 0.013 * t))
        out += 0.05 * noise(n, 3500)
        out *= 0.6 + 0.4 * np.sin(2 * math.pi * 0.017 * t + 1.1)
    return out


def build_music(total):
    n = int(total * SR)
    music = np.zeros(n)
    bounds = [(s[1], (SECTIONS[i + 1][1] if i + 1 < len(SECTIONS) else total), s[2])
              for i, s in enumerate(SECTIONS)]
    xf = int(2.5 * SR)
    for start, end, char in bounds:
        a, b = int(start * SR), min(n, int(end * SR) + xf)
        seg = bed(char, b - a, start) * env(b - a, 2.5, 2.5)
        music[a:b] += seg
    m = np.max(np.abs(music)) or 1.0
    return music / m * 0.5


# ------------------------------------------------------------------ sfx -----

def sfx(kind):
    def n_of(sec):
        return int(sec * SR)

    if kind == "pencil":
        n = n_of(1.6)
        x = noise(n, 5200) * env(n, 0.02, 0.5)
        x *= 0.5 + 0.5 * np.abs(np.sin(2 * math.pi * 5.5 * np.arange(n) / SR))
        return x * 0.5
    if kind == "paper":
        n = n_of(1.1)
        return noise(n, 4200) * env(n, 0.01, 0.7) * 0.55
    if kind == "wax":
        n = n_of(1.4)
        t = np.arange(n) / SR
        press = np.sin(2 * math.pi * 70 * t) * np.exp(-6 * t) * 0.5
        return (press + noise(n, 1800) * env(n, 0.005, 0.9) * 0.35) * 0.7
    if kind == "lid":
        n = n_of(1.3)
        t = np.arange(n) / SR
        knock = (np.sin(2 * math.pi * 128 * t) + 0.5 * np.sin(2 * math.pi * 196 * t)) * np.exp(-11 * t)
        return (knock * 0.6 + noise(n, 900) * env(n, 0.002, 0.6) * 0.25)
    if kind == "keys":
        n = n_of(1.5)
        out = np.zeros(n)
        for k in range(7):
            s = int(rng.uniform(0.0, 0.55) * SR)
            m = n_of(0.5)
            t = np.arange(m) / SR
            f = rng.uniform(1900, 3600)
            out[s:s + m] += (np.sin(2 * math.pi * f * t) * np.exp(-24 * t)) * rng.uniform(0.2, 0.5)
        return out * 0.5
    if kind in ("metaldoor", "metalclink"):
        n = n_of(1.8 if kind == "metaldoor" else 1.0)
        t = np.arange(n) / SR
        base = 92.0 if kind == "metaldoor" else 720.0
        x = sum(g * np.sin(2 * math.pi * base * k * t) for k, g in ((1, .6), (2.7, .25), (4.1, .12)))
        return x * np.exp(-(5.0 if kind == "metaldoor" else 12.0) * t) * 0.6
    if kind == "crowd":
        n = n_of(6.0)
        x = noise(n, 1400) * (0.55 + 0.45 * np.sin(2 * math.pi * 0.23 * np.arange(n) / SR))
        return x * env(n, 1.2, 1.6) * 0.4
    if kind == "crowdturn":
        n = n_of(3.0)
        t = np.arange(n) / SR
        gasp = noise(n, 2600) * np.exp(-1.6 * t)
        return (gasp * 0.7 + noise(n, 900) * env(n, 0.05, 1.4) * 0.3) * 0.55
    if kind == "roomclinic":
        n = n_of(5.0)
        t = np.arange(n) / SR
        hum = 0.25 * np.sin(2 * math.pi * 100 * t) + 0.10 * np.sin(2 * math.pi * 150 * t)
        return (hum + noise(n, 3000) * 0.18) * env(n, 1.0, 1.5) * 0.35
    if kind == "weights":
        n = n_of(1.4)
        out = np.zeros(n)
        for k in range(3):
            s = int((0.05 + 0.28 * k) * SR)
            m = n_of(0.4)
            t = np.arange(m) / SR
            out[s:s + m] += np.sin(2 * math.pi * rng.uniform(320, 520) * t) * np.exp(-17 * t) * 0.45
        return out * 0.6
    if kind == "flame":
        n = n_of(5.0)
        x = noise(n, 900) * (0.6 + 0.4 * rng.standard_normal(n).cumsum() / max(1, n) ** 0.5)
        return np.clip(x, -1, 1) * env(n, 1.4, 1.8) * 0.3
    if kind == "setmetal":
        n = n_of(1.6)
        t = np.arange(n) / SR
        tick = np.sin(2 * math.pi * 2400 * t) * np.exp(-40 * t) * 0.5
        seat = np.sin(2 * math.pi * 180 * t) * np.exp(-9 * t) * 0.35
        return tick + seat
    if kind == "cart":
        n = n_of(6.0)
        t = np.arange(n) / SR
        roll = noise(n, 260) * (0.6 + 0.4 * np.sin(2 * math.pi * 1.9 * t))
        return roll * env(n, 1.2, 1.8) * 0.42
    return np.zeros(n_of(0.5))


def build_sfx(total):
    n = int(total * SR)
    track = np.zeros(n)
    placed = []
    rows = list(csv.DictReader(CUE.open(encoding="utf-8-sig")))
    seen = set()
    for r in rows:
        state = r["state"]
        for frag, kind in SFX_MAP.items():
            if frag in state:
                key = (state, kind)
                if key in seen:
                    break
                seen.add(key)
                s = int(float(r["in"]) * SR)
                x = sfx(kind)
                e = min(n, s + len(x))
                track[s:e] += x[:e - s]
                placed.append({"at": round(float(r["in"]), 2), "state": state, "sfx": kind})
                break
    m = np.max(np.abs(track)) or 1.0
    return track / m * 0.55, placed


# ------------------------------------------------------------------ mix -----

def duck(bedtrack, voice, depth=0.62, atk=0.12, rel=0.55):
    """Sidechain the bed under the narration."""
    envv = np.abs(voice)
    win = int(0.02 * SR)
    envv = np.convolve(envv, np.ones(win) / win, mode="same")
    envv = envv / (np.max(envv) or 1.0)
    a = math.exp(-1.0 / (atk * SR))
    r = math.exp(-1.0 / (rel * SR))
    g = np.empty_like(envv)
    cur = 1.0
    for i in range(0, len(envv), 8192):
        blk = envv[i:i + 8192]
        o = np.empty_like(blk)
        for j, v in enumerate(blk):
            target = 1.0 - depth * min(1.0, v * 3.2)
            coef = a if target < cur else r
            cur = coef * cur + (1 - coef) * target
            o[j] = cur
        g[i:i + 8192] = o
    return bedtrack * g


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["stems", "mix", "all"])
    a = ap.parse_args()
    voice = read_wav(VOICE)
    total = len(voice) / SR
    print(f"voice {total:.2f}s")

    if a.command in ("stems", "all"):
        music = build_music(total)
        sfxt, placed = build_sfx(total)
        write_wav(STEMS / "EP13_MX_SCORE.wav", music)
        write_wav(STEMS / "EP13_SFX_BED.wav", sfxt)
        (AUDIO / "SFX_PLACEMENT.json").write_text(json.dumps(placed, indent=1), encoding="utf-8")
        print(f"score + sfx stems written, {len(placed)} sfx events")

    if a.command in ("mix", "all"):
        music = read_wav(STEMS / "EP13_MX_SCORE.wav")
        sfxt = read_wav(STEMS / "EP13_SFX_BED.wav")
        n = len(voice)
        music = np.pad(music, (0, max(0, n - len(music))))[:n]
        sfxt = np.pad(sfxt, (0, max(0, n - len(sfxt))))[:n]
        mix = voice + duck(music * 0.26, voice) + duck(sfxt * 0.34, voice, depth=0.45)
        write_wav(MIXWAV, mix, peak_norm=0.89)
        print(f"mix {len(mix)/SR:.2f}s -> {MIXWAV}")
        # normalise to the channel's delivery target and mux
        tmp = AUDIO / "_mix_norm.wav"
        # loudnorm in linear mode leaves the target about a decibel short here, so
        # the gain is measured and applied explicitly with a limiter catching peaks.
        import re as _re

        def measure(path):
            out = subprocess.run(
                ["ffmpeg", "-hide_banner", "-nostats", "-i", str(path),
                 "-af", "loudnorm=I=-14:TP=-1:LRA=9:print_format=json", "-f", "null", "-"],
                capture_output=True, text=True).stderr
            blk = _re.findall(r"\{[^{}]*\"input_i\".*?\}", out, _re.S)
            return json.loads(blk[-1])

        # Limiting costs loudness, so the gain is corrected over a couple of passes
        # and the true peak is checked each time rather than assumed.
        gain = -14.0 - float(measure(MIXWAV)["input_i"])
        for _ in range(4):
            chain = (f"volume={gain:.2f}dB,"
                     f"alimiter=limit=0.79:attack=4:release=70:level=disabled")
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(MIXWAV),
                            "-af", chain, "-ar", "48000", "-ac", "1",
                            "-c:a", "pcm_s24le", str(tmp)], check=True)
            a = measure(tmp)
            li, tp = float(a["input_i"]), float(a["input_tp"])
            if abs(li + 14.0) <= 0.25 and tp <= -1.0:
                break
            if tp > -1.0:
                gain -= 0.4
            else:
                gain += min(1.0, -14.0 - li)
        print(f"loudness {li:.1f} LUFS, TP {tp:.1f} dBTP, applied gain {gain:.2f} dB")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(PICTURE), "-i", str(tmp),
                        "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac",
                        "-b:a", "256k", "-shortest", "-movflags", "+faststart", str(FINAL)],
                       check=True)
        tmp.unlink(missing_ok=True)
        print(f"final -> {FINAL}")


if __name__ == "__main__":
    main()
