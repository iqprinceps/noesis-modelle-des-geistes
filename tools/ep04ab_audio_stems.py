#!/usr/bin/env python3
"""Generate individualized project-owned EP04A / EP04B music and SFX stems.

The generator follows the actual rendered VO stem timings from stem_report.json.
It does not target a predeclared runtime. All dramaturgic placements are tied to
voice segments and can still be moved in the edit.

Usage:
    python tools/ep04ab_audio_stems.py EP04A
    python tools/ep04ab_audio_stems.py EP04B
"""

from __future__ import annotations

import json
import math
import sys
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SR = 48000
CHUNK = SR

PROFILES = {
    "EP04A": {
        "prod": ROOT / "PRODUCTION_SUMMARY" / "EP04A_JUNG_KUNDALINI_V5",
        "seed": 40411,
        "files": [
            "EP04A_MX_GROUND.wav",
            "EP04A_MX_AIR_METAL.wav",
            "EP04A_MX_PULSE.wav",
            "EP04A_MX_MASTER.wav",
            "EP04A_SFX_INNER_WATER.wav",
            "EP04A_SFX_CAVE_RESONANCE.wav",
            "EP04A_SFX_ARCHIVE_ROOM.wav",
            "EP04A_SFX_PAPER_PROJECTOR.wav",
            "EP04A_SFX_BODY_MICRO.wav",
            "EP04A_SFX_PHONE_PAUSE.wav",
            "EP04A_SFX_PAULI_HANDOFF.wav",
        ],
        "ground": {
            "EP04A_V5_01_WARNUNG": .48, "EP04A_V5_02_FLUT_BILD": .90,
            "EP04A_V5_03_FLUT_DEUTUNG": .78, "EP04A_V5_04_HOEHLE_SCHLANGE": 1.0,
            "EP04A_V5_05_PHILEMON_BODEN": .72, "EP04A_V5_06_SEMINAR_GEFAHR": .35,
            "EP04A_V5_07_MANIPURA": .42, "EP04A_V5_08_ANAHATA_WAHL": .25,
            "EP04A_V5_09_ZWEI_SEKUNDEN": .18, "EP04A_V5_10_KARTE_BEWEGT_SICH": .38,
            "EP04A_V5_11_WAS_BLEIBT": .46, "EP04A_V5_12_PAULI_HOOK": .24,
        },
        "air": {
            "EP04A_V5_01_WARNUNG": .72, "EP04A_V5_02_FLUT_BILD": .45,
            "EP04A_V5_03_FLUT_DEUTUNG": .52, "EP04A_V5_04_HOEHLE_SCHLANGE": .82,
            "EP04A_V5_05_PHILEMON_BODEN": .75, "EP04A_V5_06_SEMINAR_GEFAHR": .26,
            "EP04A_V5_07_MANIPURA": .20, "EP04A_V5_08_ANAHATA_WAHL": .44,
            "EP04A_V5_09_ZWEI_SEKUNDEN": .12, "EP04A_V5_10_KARTE_BEWEGT_SICH": .32,
            "EP04A_V5_11_WAS_BLEIBT": .68, "EP04A_V5_12_PAULI_HOOK": .22,
        },
        "pulse": {
            "EP04A_V5_01_WARNUNG": .20, "EP04A_V5_02_FLUT_BILD": .0,
            "EP04A_V5_03_FLUT_DEUTUNG": .0, "EP04A_V5_04_HOEHLE_SCHLANGE": .0,
            "EP04A_V5_05_PHILEMON_BODEN": .0, "EP04A_V5_06_SEMINAR_GEFAHR": .50,
            "EP04A_V5_07_MANIPURA": .56, "EP04A_V5_08_ANAHATA_WAHL": .34,
            "EP04A_V5_09_ZWEI_SEKUNDEN": .08, "EP04A_V5_10_KARTE_BEWEGT_SICH": .62,
            "EP04A_V5_11_WAS_BLEIBT": .12, "EP04A_V5_12_PAULI_HOOK": .18,
        },
    },
    "EP04B": {
        "prod": ROOT / "PRODUCTION_SUMMARY" / "EP04B_CHAKRA_GENEALOGIE_V5",
        "seed": 40422,
        "files": [
            "EP04B_MX_DRY_PULSE.wav",
            "EP04B_MX_PAPER_TONE.wav",
            "EP04B_MX_HARMONIC_THREAD.wav",
            "EP04B_MX_MASTER.wav",
            "EP04B_SFX_PAGE_PRINT.wav",
            "EP04B_SFX_LAYER_PEEL.wav",
            "EP04B_SFX_ARCHIVE_ROOM.wav",
            "EP04B_SFX_TYPE_MOTION.wav",
            "EP04B_SFX_ROUTE_PAPER.wav",
            "EP04B_SFX_FINAL_SEAMS.wav",
        ],
        "pulse": {
            "EP04B_V5_01_KARTE_ZERFAELLT": .58, "EP04B_V5_02_VIELE_KARTEN": .36,
            "EP04B_V5_03_DIE_SECHS": .28, "EP04B_V5_04_AVALON_WOODROFFE": .52,
            "EP04B_V5_05_GHOSE_NETZWERK": .64, "EP04B_V5_06_LEADBEATER": .42,
            "EP04B_V5_07_MUTATION_A": .72, "EP04B_V5_08_MUTATION_B": .80,
            "EP04B_V5_09_WARUM_BLEIBT_SIE": .32, "EP04B_V5_10_DIE_NAEHTE": .16,
        },
        "paper": {
            "EP04B_V5_01_KARTE_ZERFAELLT": .30, "EP04B_V5_02_VIELE_KARTEN": .44,
            "EP04B_V5_03_DIE_SECHS": .62, "EP04B_V5_04_AVALON_WOODROFFE": .74,
            "EP04B_V5_05_GHOSE_NETZWERK": .68, "EP04B_V5_06_LEADBEATER": .50,
            "EP04B_V5_07_MUTATION_A": .44, "EP04B_V5_08_MUTATION_B": .42,
            "EP04B_V5_09_WARUM_BLEIBT_SIE": .32, "EP04B_V5_10_DIE_NAEHTE": .58,
        },
        "harmonic": {
            "EP04B_V5_01_KARTE_ZERFAELLT": .34, "EP04B_V5_02_VIELE_KARTEN": .18,
            "EP04B_V5_03_DIE_SECHS": .24, "EP04B_V5_04_AVALON_WOODROFFE": .28,
            "EP04B_V5_05_GHOSE_NETZWERK": .34, "EP04B_V5_06_LEADBEATER": .40,
            "EP04B_V5_07_MUTATION_A": .46, "EP04B_V5_08_MUTATION_B": .50,
            "EP04B_V5_09_WARUM_BLEIBT_SIE": .62, "EP04B_V5_10_DIE_NAEHTE": .46,
        },
    },
}


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
    wf.writeframes(np.column_stack((pcm, pcm)).tobytes())


def load_timing(profile: str):
    prod = PROFILES[profile]["prod"]
    report_path = prod / "voice" / "master" / "stem_report.json"
    if not report_path.is_file():
        raise SystemExit(
            f"Missing {report_path}\nRun `python tools/ep04ab_voice.py {profile} all` after generating raw VO."
        )
    report = json.loads(report_path.read_text(encoding="utf-8"))
    stems = {row["id"]: row for row in report["stems"]}
    total = float(report["duration"]) + 20.0
    return prod, report_path, stems, total


def envelope(t, stems, levels, ramp=.7):
    out = np.zeros_like(t, dtype=np.float64)
    for stem_id, gain in levels.items():
        if gain <= 0 or stem_id not in stems:
            continue
        a, b = float(stems[stem_id]["start"]), float(stems[stem_id]["end"])
        inside = (t >= a) & (t <= b)
        out[inside] = np.maximum(out[inside], gain)
        pre = (t >= a-ramp) & (t < a)
        if np.any(pre):
            p = (t[pre] - (a-ramp)) / ramp
            out[pre] = np.maximum(out[pre], gain*p)
        post = (t > b) & (t <= b+ramp)
        if np.any(post):
            p = 1 - (t[post]-b)/ramp
            out[post] = np.maximum(out[post], gain*p)
    return out


def burst(t, center, length, freq, amp, decay=12.0, second=None):
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


def stem_start(stems, stem_id, frac=0.0):
    row = stems[stem_id]
    return float(row["start"]) + frac*(float(row["end"])-float(row["start"]))


def generate_ep04a(cfg, stems, t, rng):
    g = envelope(t, stems, cfg["ground"])
    a = envelope(t, stems, cfg["air"])
    p = envelope(t, stems, cfg["pulse"])

    ground = 0.032*g*(np.sin(2*np.pi*82*t + .18*np.sin(2*np.pi*.041*t)) + .36*np.sin(2*np.pi*123*t+.8))
    air = 0.014*a*(
        .55*np.sin(2*np.pi*780*t + .3*np.sin(2*np.pi*.021*t)) +
        .30*np.sin(2*np.pi*1170*t + 1.1) +
        .18*np.sin(2*np.pi*1850*t + 2.0)
    )
    pulse_gate = (0.5+0.5*np.sign(np.sin(2*np.pi*.42*t + .35*np.sin(2*np.pi*.037*t))))
    pulse = 0.010*p*pulse_gate*np.sin(2*np.pi*190*t)

    white = rng.normal(0, 1, len(t))
    brown = np.cumsum(white); brown -= brown.mean(); brown /= max(np.max(np.abs(brown)), 1e-9)
    archive = .0028*(.40*white + .60*brown)

    water_env = envelope(t, stems, {
        "EP04A_V5_02_FLUT_BILD": .9, "EP04A_V5_04_HOEHLE_SCHLANGE": .55,
        "EP04A_V5_11_WAS_BLEIBT": .22,
    }, ramp=1.2)
    water = .006*water_env*(.35*white + .65*np.sin(2*np.pi*(38+.8*np.sin(2*np.pi*.011*t))*t))

    cave_env = envelope(t, stems, {
        "EP04A_V5_04_HOEHLE_SCHLANGE": 1.0, "EP04A_V5_05_PHILEMON_BODEN": .65,
    }, ramp=1.4)
    cave = .006*cave_env*(np.sin(2*np.pi*310*t)+.5*np.sin(2*np.pi*465*t+1.2))*(.5+.5*np.sin(2*np.pi*.073*t))

    paper = np.zeros_like(t)
    for sid, frac in [("EP04A_V5_06_SEMINAR_GEFAHR", .10), ("EP04A_V5_10_KARTE_BEWEGT_SICH", .05), ("EP04A_V5_10_KARTE_BEWEGT_SICH", .55)]:
        c = stem_start(stems, sid, frac)
        rel=t-c; m=(rel>=0)&(rel<=.55)
        if np.any(m):
            r=rel[m]; paper[m] += .010*rng.normal(0,1,np.count_nonzero(m))*np.sin(np.pi*r/.55)**2

    body_env = envelope(t, stems, {
        "EP04A_V5_07_MANIPURA": .75, "EP04A_V5_08_ANAHATA_WAHL": .45,
        "EP04A_V5_09_ZWEI_SEKUNDEN": .52,
    }, ramp=.4)
    body = .0032*body_env*(.55*white + .45*np.sin(2*np.pi*54*t))

    phone_env = envelope(t, stems, {"EP04A_V5_09_ZWEI_SEKUNDEN": 1.0}, ramp=.2)
    phone = .0018*phone_env*(.65*white + .35*brown)

    pauli = burst(t, stem_start(stems, "EP04A_V5_12_PAULI_HOOK", .18), .55, 610, .026, 5.5, (915,.35))

    return {
        "EP04A_MX_GROUND.wav": ground,
        "EP04A_MX_AIR_METAL.wav": air,
        "EP04A_MX_PULSE.wav": pulse,
        "EP04A_MX_MASTER.wav": ground+air+pulse,
        "EP04A_SFX_INNER_WATER.wav": water,
        "EP04A_SFX_CAVE_RESONANCE.wav": cave,
        "EP04A_SFX_ARCHIVE_ROOM.wav": archive,
        "EP04A_SFX_PAPER_PROJECTOR.wav": paper,
        "EP04A_SFX_BODY_MICRO.wav": body,
        "EP04A_SFX_PHONE_PAUSE.wav": phone,
        "EP04A_SFX_PAULI_HANDOFF.wav": pauli,
    }


def generate_ep04b(cfg, stems, t, rng):
    p = envelope(t, stems, cfg["pulse"])
    paper_env = envelope(t, stems, cfg["paper"])
    h = envelope(t, stems, cfg["harmonic"])

    dry_gate = (0.5+0.5*np.sign(np.sin(2*np.pi*.55*t + .18*np.sin(2*np.pi*.031*t))))
    pulse = .0095*p*dry_gate*(np.sin(2*np.pi*164*t)+.30*np.sin(2*np.pi*246*t+.5))

    white = rng.normal(0,1,len(t))
    brown = np.cumsum(white); brown -= brown.mean(); brown /= max(np.max(np.abs(brown)),1e-9)
    paper_tone = .0058*paper_env*(.30*white + .70*brown)
    harmonic = .010*h*(.62*np.sin(2*np.pi*840*t)+.28*np.sin(2*np.pi*1260*t+1.0)+.16*np.sin(2*np.pi*1680*t+2.0))
    archive = .0024*(.42*white+.58*brown)

    page = np.zeros_like(t)
    for sid, frac in [("EP04B_V5_03_DIE_SECHS",.18),("EP04B_V5_04_AVALON_WOODROFFE",.05),("EP04B_V5_06_LEADBEATER",.06)]:
        c=stem_start(stems,sid,frac); rel=t-c; m=(rel>=0)&(rel<=.45)
        if np.any(m):
            r=rel[m]; page[m] += .011*rng.normal(0,1,np.count_nonzero(m))*np.sin(np.pi*r/.45)**2

    peel = np.zeros_like(t)
    for sid, frac in [("EP04B_V5_01_KARTE_ZERFAELLT",.28),("EP04B_V5_08_MUTATION_B",.75),("EP04B_V5_10_DIE_NAEHTE",.48)]:
        c=stem_start(stems,sid,frac); rel=t-c; m=(rel>=0)&(rel<=.75)
        if np.any(m):
            r=rel[m]; peel[m] += .006*rng.normal(0,1,np.count_nonzero(m))*np.sin(np.pi*r/.75)**2

    type_fx = np.zeros_like(t)
    for sid, frac in [
        ("EP04B_V5_01_KARTE_ZERFAELLT",.48), ("EP04B_V5_03_DIE_SECHS",.08),
        ("EP04B_V5_04_AVALON_WOODROFFE",.20), ("EP04B_V5_06_LEADBEATER",.06),
    ]:
        type_fx += burst(t, stem_start(stems,sid,frac), .08, 1500, .020, 45, (900,.35))

    route_env = envelope(t, stems, {"EP04B_V5_05_GHOSE_NETZWERK":1.0}, ramp=.5)
    route = .0035*route_env*(.5*white+.5*np.sin(2*np.pi*72*t))

    final_env = envelope(t, stems, {"EP04B_V5_10_DIE_NAEHTE":1.0}, ramp=.7)
    seams = .0035*final_env*(.75*brown+.25*white)

    return {
        "EP04B_MX_DRY_PULSE.wav": pulse,
        "EP04B_MX_PAPER_TONE.wav": paper_tone,
        "EP04B_MX_HARMONIC_THREAD.wav": harmonic,
        "EP04B_MX_MASTER.wav": pulse+paper_tone+harmonic,
        "EP04B_SFX_PAGE_PRINT.wav": page,
        "EP04B_SFX_LAYER_PEEL.wav": peel,
        "EP04B_SFX_ARCHIVE_ROOM.wav": archive,
        "EP04B_SFX_TYPE_MOTION.wav": type_fx,
        "EP04B_SFX_ROUTE_PAPER.wav": route,
        "EP04B_SFX_FINAL_SEAMS.wav": seams,
    }


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1].upper() not in PROFILES:
        raise SystemExit("Usage: python tools/ep04ab_audio_stems.py EP04A|EP04B")
    profile = sys.argv[1].upper()
    cfg = PROFILES[profile]
    prod, report_path, stems, total = load_timing(profile)
    out = prod / "audio" / "stems"
    rng = np.random.default_rng(cfg["seed"])
    writers = {name: open_wav(out/name) for name in cfg["files"]}
    n_total = int(math.ceil(total*SR))

    try:
        for offset in range(0, n_total, CHUNK):
            count = min(CHUNK, n_total-offset)
            t = (offset + np.arange(count, dtype=np.float64))/SR
            signals = generate_ep04a(cfg, stems, t, rng) if profile == "EP04A" else generate_ep04b(cfg, stems, t, rng)
            for name, signal in signals.items():
                write_stereo(writers[name], signal)
    finally:
        for wf in writers.values():
            wf.close()

    manifest = {
        "episode": profile,
        "sample_rate": SR,
        "duration_seconds": round(total,3),
        "source_timing": str(report_path.relative_to(ROOT)),
        "generator_seed": cfg["seed"],
        "note": "Project-owned deterministic synthesis tied to actual VO timings. Edit placement and final mix remain flexible.",
        "files": cfg["files"],
    }
    (out/"audio_stem_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Generated {len(cfg['files'])} {profile} stems in {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
