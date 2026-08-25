#!/usr/bin/env python3
"""Build restrained project-owned music and SFX stems for EP06-EP08.

The final George stem report is the timing authority.  Audio is generated from
deterministic synthesis only: no licensed recordings, horror stingers, occult
drones or sounds that assert a supernatural event as fact.

Usage after the final voice master exists:
    python tools/build_schlafparalyse_audio_stems.py EP06
    python tools/build_schlafparalyse_audio_stems.py all
"""

from __future__ import annotations

import json
import math
import struct
import sys
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SR = 48_000
CHUNK = SR
PRE, GAP, TAIL, ENDCARD = 0.35, 0.65, 2.2, 20.0

CONFIG = {
    "EP06": {
        "folder": "EP06_SCHLAFPARALYSE_V4",
        "seed": 6062402,
        "act_gain": [.82, .64, .72, .78, .68, .86, .76, .58],
        "tones": (82.0, 123.0, 330.0),
        "sfx": [
            "BEDROOM_ROOMTONE", "FOOTSTEPS_DISTANT", "MATTRESS_WEIGHT",
            "SLEEP_LAB", "EEG_MOTION", "BREATH_BODY",
        ],
    },
    "EP07": {
        "folder": "EP07_SCHLAFPARALYSE_V4",
        "seed": 7072402,
        "act_gain": [.72, .82, .68, .76, .88, .70, .84, .60],
        "tones": (98.0, 147.0, 392.0),
        "sfx": [
            "SALEM_ROOMTONE", "PAPER_INK", "WOOD_BED",
            "COURT_MURMUR", "MAP_MOTION", "MEDIA_HANDOFF",
        ],
    },
    "EP08": {
        "folder": "EP08_SCHLAFPARALYSE_V4",
        "seed": 8082402,
        "act_gain": [.76, .66, .82, .70, .88, .74, .90, .62],
        "tones": (110.0, 165.0, 440.0),
        "sfx": [
            "RADIO_ROOM", "SHORTWAVE_STATIC", "FAX_PAPER",
            "CRT_ROOM", "FORUM_UI", "SHADOW_ROOMTONE",
        ],
    },
}


class Wave24:
    """Minimal streaming stereo PCM24 writer; keeps the production script dependency-free."""

    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.handle = path.open("wb")
        self.frames = 0
        self.handle.write(b"\0" * 44)

    def write(self, stereo: np.ndarray):
        values = np.asarray(np.clip(stereo, -.999999, .999999) * 8_388_607, dtype="<i4")
        packed = values.reshape(-1).view(np.uint8).reshape(-1, 4)[:, :3]
        self.handle.write(packed.tobytes())
        self.frames += len(values)

    def close(self):
        data_size = self.frames * 2 * 3
        byte_rate = SR * 2 * 3
        block_align = 2 * 3
        self.handle.seek(0)
        self.handle.write(b"RIFF")
        self.handle.write(struct.pack("<I", 36 + data_size))
        self.handle.write(b"WAVEfmt ")
        self.handle.write(struct.pack("<IHHIIHH", 16, 1, 2, SR, byte_rate, block_align, 24))
        self.handle.write(b"data")
        self.handle.write(struct.pack("<I", data_size))
        self.handle.close()


def timing(ep: str):
    cfg = CONFIG[ep]
    prod = ROOT / "PRODUCTION_SUMMARY" / cfg["folder"]
    final_voice = ROOT / "06_PRODUCTION" / cfg["folder"] / f"VOICE_{ep}"
    final_report = final_voice / "master" / "stem_report.json"
    report_path = final_report if final_report.is_file() else prod / "voice" / "master" / "stem_report.json"
    if report_path == final_report:
        prod = final_voice.parent
    if not report_path.is_file():
        raise SystemExit(
            f"Missing {report_path}\nGenerate/finalize George first with "
            f"`python tools/schlafparalyse_voice.py {ep} all`."
        )
    report = json.loads(report_path.read_text(encoding="utf-8"))
    stems = report["stems"]
    if stems and all("start" in item and "end" in item and item.get("section") for item in stems):
        starts, ends = [], []
        for number in range(1, 9):
            section = f"S{number}"
            members = [item for item in stems if item.get("section") == section]
            if not members:
                raise SystemExit(f"{ep} final stem report has no takes for {section}")
            starts.append(min(float(item["start"]) for item in members))
            ends.append(max(float(item["end"]) for item in members))
        cursor = max(ends)
    else:
        durations = [float(item["duration"]) for item in stems]
        if len(durations) != 8:
            raise SystemExit(f"{ep} legacy report expects eight act stems, got {len(durations)}")
        starts, ends = [], []
        cursor = PRE
        for index, duration in enumerate(durations):
            starts.append(cursor)
            cursor += duration
            ends.append(cursor)
            if index < 7:
                cursor += GAP
    master_duration = float(report.get("duration", report.get("master_duration", cursor + TAIL)))
    total = max(master_duration, cursor + TAIL) + ENDCARD
    return prod, report_path, np.asarray(starts), np.asarray(ends), total


def act_envelope(t: np.ndarray, starts: np.ndarray, ends: np.ndarray, gains: list[float]):
    result = np.full_like(t, .18, dtype=np.float64)
    ramp = .8
    for index, (start, end) in enumerate(zip(starts, ends)):
        gain = gains[index]
        inside = (t >= start) & (t <= end)
        result[inside] = gain
        before = (t >= start-ramp) & (t < start)
        after = (t > end) & (t <= end+ramp)
        if np.any(before):
            p = (t[before] - start + ramp) / ramp
            result[before] = result[before] * (1-p) + gain * p
        if np.any(after):
            p = (t[after] - end) / ramp
            result[after] = gain * (1-p) + result[after] * p
    return result


def burst(t, start, length, frequency, amplitude, decay=10.0, noise=None):
    result = np.zeros_like(t)
    mask = (t >= start) & (t <= start + length)
    if not np.any(mask):
        return result
    rel = t[mask] - start
    env = np.sin(np.pi * rel / length) ** 2 * np.exp(-decay * rel)
    tone = np.sin(2*np.pi*frequency*rel)
    if noise is not None:
        tone = .35*tone + .65*noise[mask]
    result[mask] = amplitude * env * tone
    return result


def texture(t, white, slow, base, gain=.004):
    return gain * (.48*white + .32*slow + .20*np.sin(2*np.pi*base*t))


def sfx_signals(ep, t, starts, ends, white, slow):
    """Six restrained full-length layers with sparse semantic events."""
    signals = {}
    if ep == "EP06":
        room_gate = ((t >= starts[0]) & (t <= ends[1])) | ((t >= starts[5]) & (t <= ends[7]))
        signals["BEDROOM_ROOMTONE"] = room_gate * texture(t, white, slow, 57, .0028)
        foot = sum((burst(t, starts[0]+x, .22, 74, .018, 14, white) for x in (8.2, 9.0, 9.9)), np.zeros_like(t))
        signals["FOOTSTEPS_DISTANT"] = foot
        signals["MATTRESS_WEIGHT"] = burst(t, starts[1]+6.0, .85, 48, .020, 3.5, white)
        lab_gate = (t >= starts[4]) & (t <= ends[4])
        signals["SLEEP_LAB"] = lab_gate * texture(t, white, slow, 119, .0025)
        eeg = np.zeros_like(t)
        pos = starts[4] + 7.0
        while pos < ends[4] - .5:
            eeg += burst(t, pos, .055, 980, .018, 45)
            pos += 1.35
        signals["EEG_MOTION"] = eeg
        body_gate = (t >= starts[5]) & (t <= ends[6])
        breath = .0022*np.sin(2*np.pi*.21*t) * (.5+.5*np.sin(2*np.pi*.21*t))
        signals["BREATH_BODY"] = body_gate * (breath + .0012*slow)
    elif ep == "EP07":
        signals["SALEM_ROOMTONE"] = texture(t, white, slow, 66, .0025)
        paper = np.zeros_like(t)
        for act, offset in ((0, 5.0), (1, 8.0), (3, 4.5), (4, 7.5), (6, 3.5)):
            paper += burst(t, starts[act]+offset, .55, 430, .025, 3.0, white)
        signals["PAPER_INK"] = paper
        signals["WOOD_BED"] = burst(t, starts[2]+5.0, .7, 71, .017, 4.0, white)
        court_gate = (t >= starts[3]) & (t <= ends[4])
        signals["COURT_MURMUR"] = court_gate * (.0015*slow + .0008*white)
        map_motion = np.zeros_like(t)
        for offset in (4.0, 9.0, 14.0):
            map_motion += burst(t, starts[5]+offset, .35, 260, .013, 5.0, white)
        signals["MAP_MOTION"] = map_motion
        signals["MEDIA_HANDOFF"] = burst(t, starts[6]+3.0, .6, 520, .020, 5.0, white)
    else:
        signals["RADIO_ROOM"] = texture(t, white, slow, 60, .0024)
        shortwave_gate = (t >= starts[0]) & (t <= ends[1])
        signals["SHORTWAVE_STATIC"] = shortwave_gate * (.0024*white + .0010*np.sin(2*np.pi*1330*t))
        fax = np.zeros_like(t)
        for offset in np.arange(4.0, min(16.0, ends[2]-starts[2]-1), .62):
            fax += burst(t, starts[2]+float(offset), .12, 720, .011, 7.0, white)
        signals["FAX_PAPER"] = fax
        crt_gate = (t >= starts[3]) & (t <= ends[4])
        signals["CRT_ROOM"] = crt_gate * (.0016*white + .0012*np.sin(2*np.pi*100*t))
        ui = np.zeros_like(t)
        for act, offset in ((4, 5.0), (5, 8.0), (6, 4.0)):
            ui += burst(t, starts[act]+offset, .10, 840, .015, 18)
        signals["FORUM_UI"] = ui
        shadow_gate = (t >= starts[6]) & (t <= ends[7])
        signals["SHADOW_ROOMTONE"] = shadow_gate * texture(t, white, slow, 52, .0022)
    return signals


def build(ep: str):
    cfg = CONFIG[ep]
    prod, report_path, starts, ends, total = timing(ep)
    out = prod / "audio" / "stems"
    out.mkdir(parents=True, exist_ok=True)
    names = [f"{ep}_MX_LOW", f"{ep}_MX_HARMONIC", f"{ep}_MX_NOISE", f"{ep}_MX_MASTER"]
    names += [f"{ep}_SFX_{name}" for name in cfg["sfx"]]
    paths = {name: out / f"{name}.wav" for name in names}
    writers = {name: Wave24(path) for name, path in paths.items()}
    rng = np.random.default_rng(cfg["seed"])
    total_samples = int(math.ceil(total*SR))
    f0, f1, fh = cfg["tones"]
    try:
        for offset in range(0, total_samples, CHUNK):
            count = min(CHUNK, total_samples-offset)
            t = (offset + np.arange(count, dtype=np.float64))/SR
            gain = act_envelope(t, starts, ends, cfg["act_gain"])
            white = rng.normal(0, 1, count)
            slow = np.cumsum(rng.normal(0, .025, count))
            slow -= np.linspace(slow[0], slow[-1], count)
            slow /= max(1.0, float(np.max(np.abs(slow))))

            # Warm, restrained and phone-audible; deliberately not depressive.
            low = .017*gain*(np.sin(2*np.pi*f0*t) + .35*np.sin(2*np.pi*f1*t+.7))
            shimmer = .0065*gain*(.65+.35*np.sin(2*np.pi*.031*t))*np.sin(2*np.pi*fh*t+.4)
            noise = .0028*gain*(.35*white + .65*slow)
            music = {f"{ep}_MX_LOW": low, f"{ep}_MX_HARMONIC": shimmer,
                     f"{ep}_MX_NOISE": noise, f"{ep}_MX_MASTER": low+shimmer+noise}
            sfx = sfx_signals(ep, t, starts, ends, white, slow)
            signals = {**music, **{f"{ep}_SFX_{key}": value for key, value in sfx.items()}}
            for name, signal in signals.items():
                stereo = np.column_stack((signal, signal))
                writers[name].write(np.clip(stereo, -.98, .98))
    finally:
        for writer in writers.values():
            writer.close()

    manifest = {
        "episode": ep,
        "duration_seconds": round(total, 3),
        "sample_rate": SR,
        "channels": 2,
        "subtype": "PCM_24",
        "source_timing": str(report_path.relative_to(ROOT)),
        "generator_seed": cfg["seed"],
        "source": "project-owned deterministic synthesis",
        "mix_note": "VO remains foreground; final bed about -30 LUFS, deliver at -14 LUFS +/-0.5 and <=-0.8 dBTP.",
        "restrictions": [
            "no third-party recordings", "no jump scares", "no trailer booms",
            "no occult drones", "no branded interface sounds",
            "no sound that asserts a supernatural entity as fact",
        ],
        "files": [str(path.resolve()) for path in paths.values()],
    }
    (out / "audio_stem_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2)+"\n", encoding="utf-8"
    )
    print(f"{ep}: generated {len(paths)} stems in {out}")


def main():
    if len(sys.argv) != 2 or sys.argv[1].upper() not in {*CONFIG, "ALL"}:
        raise SystemExit("Usage: python tools/build_schlafparalyse_audio_stems.py EP06|EP07|EP08|all")
    requested = sys.argv[1].upper()
    for episode in CONFIG if requested == "ALL" else (requested,):
        build(episode)


if __name__ == "__main__":
    main()
