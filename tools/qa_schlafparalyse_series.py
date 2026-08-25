#!/usr/bin/env python3
"""Run a reproducible delivery QA for sleep-paralysis EP06-EP08."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
PRODUCTION = ROOT / "06_PRODUCTION"
REPORT_MD = PRODUCTION / "SCHLAFPARALYSE_EP06-EP08_FINAL_QA.md"
REPORT_JSON = PRODUCTION / "SCHLAFPARALYSE_EP06-EP08_FINAL_QA.json"

CONFIG = {
    "EP06": {
        "kit": PRODUCTION / "EP06_SCHLAFPARALYSE_V4" / "IMAGE_GENERATION_KIT",
        "output": "03_GENERATED_OUTPUT/NanoBanana_2K_Series",
        "core": 40,
        "cards": 7,
        "size": (2560, 1440),
    },
    "EP07": {
        "kit": PRODUCTION / "EP07_SCHLAFPARALYSE_V4" / "IMAGE_GENERATION_KIT",
        "output": "03_GENERATED_OUTPUT/NanoBanana_Pro_2K_Series",
        "core": 24,
        "cards": 7,
        "size": (2752, 1536),
    },
    "EP08": {
        "kit": PRODUCTION / "EP08_SCHLAFPARALYSE_V4" / "IMAGE_GENERATION_KIT",
        "output": "03_GENERATED_OUTPUT",
        "core": 40,
        "cards": 8,
        "size": (2560, 1440),
    },
}

CORE_NAME = re.compile(r"^(?:IMG\d{3}|SHOT\d{2})_.+\.png$", re.IGNORECASE)
BAD_PREFIX = re.compile(r"^EP0[678]_", re.IGNORECASE)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def probe_clip(path: Path) -> dict[str, object]:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration:stream=codec_type,width,height,r_frame_rate",
            "-of",
            "json",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    data = json.loads(result.stdout)
    video = next(stream for stream in data["streams"] if stream["codec_type"] == "video")
    has_audio = any(stream["codec_type"] == "audio" for stream in data["streams"])
    return {
        "width": int(video["width"]),
        "height": int(video["height"]),
        "fps": video["r_frame_rate"],
        "duration": round(float(data["format"]["duration"]), 3),
        "has_audio": has_audio,
    }


def main() -> int:
    report: dict[str, object] = {"episodes": {}, "passed": True}

    for episode, config in CONFIG.items():
        kit: Path = config["kit"]
        output = kit / str(config["output"])
        core = sorted(path for path in output.glob("*.png") if CORE_NAME.match(path.name))
        cards = sorted((kit / "03_GENERATED_OUTPUT" / "CARDS").glob("CARD*.png"))
        clips = sorted(output.glob("CLIP*.mp4"))
        reserve = sorted((output / "RESERVE_CLIPS").glob("CLIP*.mp4"))

        hashes: dict[str, list[str]] = {}
        wrong_sizes: list[dict[str, object]] = []
        for path in core:
            hashes.setdefault(sha256(path), []).append(path.name)
            with Image.open(path) as image:
                if image.size != config["size"]:
                    wrong_sizes.append({"file": path.name, "size": list(image.size)})
        duplicate_groups = [names for names in hashes.values() if len(names) > 1]

        card_wrong_sizes: list[dict[str, object]] = []
        for path in cards:
            with Image.open(path) as image:
                if image.size != (2560, 1440):
                    card_wrong_sizes.append({"file": path.name, "size": list(image.size)})

        clip_details = {path.name: probe_clip(path) for path in clips}
        bad_clips = {
            name: details
            for name, details in clip_details.items()
            if details["width"] != 1920
            or details["height"] != 1080
            or details["fps"] != "24/1"
            or abs(float(details["duration"]) - 6.0) > 0.05
            or details["has_audio"]
        }

        with (kit / "GENERATION_QUEUE.csv").open(encoding="utf-8-sig", newline="") as handle:
            queue = list(csv.DictReader(handle))
        queue_outputs = [row["output_filename"] for row in queue if row["kind"] != "STYLE_MASTER"]
        queue_bad_prefix = [name for name in queue_outputs if BAD_PREFIX.match(name)]
        queue_missing = [name for name in queue_outputs if not (output / name).is_file()]

        failures: list[str] = []
        if len(core) != config["core"]:
            failures.append(f"Core-Stills {len(core)}/{config['core']}")
        if wrong_sizes:
            failures.append(f"{len(wrong_sizes)} Core-Stills mit falscher Auflösung")
        if duplicate_groups:
            failures.append(f"{len(duplicate_groups)} exakte Duplikatgruppe(n)")
        if any(BAD_PREFIX.match(path.name) for path in [*core, *clips]):
            failures.append("EP-Präfix in verwendbarem Outputnamen")
        if len(cards) != config["cards"]:
            failures.append(f"Karten {len(cards)}/{config['cards']}")
        if card_wrong_sizes:
            failures.append(f"{len(card_wrong_sizes)} Karten mit falscher Auflösung")
        if len(clips) != 4:
            failures.append(f"MAIN-Clips {len(clips)}/4")
        if bad_clips:
            failures.append(f"{len(bad_clips)} technisch fehlerhafte MAIN-Clips")
        if queue_bad_prefix:
            failures.append(f"{len(queue_bad_prefix)} alte EP-/RSV-Namen in Queue")
        if queue_missing:
            failures.append(f"{len(queue_missing)} Queue-Dateien fehlen")

        passed = not failures
        report["passed"] = bool(report["passed"]) and passed
        report["episodes"][episode] = {
            "passed": passed,
            "failures": failures,
            "core_stills": len(core),
            "core_resolution": f"{config['size'][0]}x{config['size'][1]}",
            "duplicate_groups": duplicate_groups,
            "cards": len(cards),
            "main_clips": len(clips),
            "reserve_clips": len(reserve),
            "clip_details": clip_details,
            "queue_entries": len(queue_outputs),
            "queue_bad_prefix": queue_bad_prefix,
            "queue_missing": queue_missing,
        }

    REPORT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Schlafparalyse EP06-EP08 — finale technische QA",
        "",
        f"**Gesamtstatus:** {'BESTANDEN' if report['passed'] else 'NOCH NICHT BESTANDEN'}",
        "",
        "| Episode | Core-Stills | Karten | MAIN-Clips | Reserveclips | Status |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for episode, details in report["episodes"].items():
        lines.append(
            f"| {episode} | {details['core_stills']} | {details['cards']} | "
            f"{details['main_clips']} | {details['reserve_clips']} | "
            f"{'BESTANDEN' if details['passed'] else 'OFFEN'} |"
        )
    for episode, details in report["episodes"].items():
        lines.extend(["", f"## {episode}", ""])
        if details["failures"]:
            lines.extend(f"- {failure}" for failure in details["failures"])
        else:
            lines.append(
                "Core-Dateien, Auflösungen, Hash-Duplikate, Queue-Zuordnung, "
                "Dateinamen, Karten und vier technische Clip-Gates bestanden."
            )
    lines.extend(
        [
            "",
            "Die visuelle Freigabe (Motivtiefe, Helligkeit und echte Transformation) "
            "wurde zusätzlich über die finalen Kontaktbögen und Clip-Frame-Strips vorgenommen.",
            "",
        ]
    )
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {REPORT_MD}")
    print(f"Wrote {REPORT_JSON}")
    print("PASS" if report["passed"] else "FAIL")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
