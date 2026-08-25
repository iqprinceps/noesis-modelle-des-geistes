#!/usr/bin/env python3
"""Build the editor-facing visual master index for sleep-paralysis EP06-EP08."""

from __future__ import annotations

import csv
import re
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
PRODUCTION = ROOT / "06_PRODUCTION"
OUTPUT_CSV = PRODUCTION / "SCHLAFPARALYSE_EP06-EP08_VISUAL_MASTER.csv"

EPISODES = {
    "EP06": {
        "kit": PRODUCTION / "EP06_SCHLAFPARALYSE_V4" / "IMAGE_GENERATION_KIT",
        "output": "03_GENERATED_OUTPUT/NanoBanana_2K_Series",
    },
    "EP07": {
        "kit": PRODUCTION / "EP07_SCHLAFPARALYSE_V4" / "IMAGE_GENERATION_KIT",
        "output": "03_GENERATED_OUTPUT/NanoBanana_Pro_2K_Series",
    },
    "EP08": {
        "kit": PRODUCTION / "EP08_SCHLAFPARALYSE_V4" / "IMAGE_GENERATION_KIT",
        "output": "03_GENERATED_OUTPUT",
    },
}


def friendly_name(episode: str, value: str) -> str:
    if value.startswith(f"{episode}_IMG"):
        return value.removeprefix(f"{episode}_")
    match = re.fullmatch(rf"{episode}_RSV(\d{{2}})_(.+\.png)", value)
    if match:
        return f"SHOT{match.group(1)}_{match.group(2)}"
    return value


def timeline_block(prompt_source: str) -> str:
    match = re.search(r"_S(\d+)_S(\d+)\.md$", prompt_source)
    return f"S{match.group(1)}-S{match.group(2)}" if match else "SERIES"


def image_dimensions(path: Path) -> str:
    with Image.open(path) as image:
        return f"{image.width}x{image.height}"


def main() -> int:
    rows: list[dict[str, str | int]] = []
    missing: list[Path] = []

    for episode, config in EPISODES.items():
        kit = config["kit"]
        output_dir = kit / config["output"]
        with (kit / "GENERATION_QUEUE.csv").open(encoding="utf-8-sig", newline="") as handle:
            queue = list(csv.DictReader(handle))

        visual_order = 0
        for item in queue:
            if item["kind"] == "STYLE_MASTER":
                continue
            visual_order += 1
            filename = friendly_name(episode, item["output_filename"])
            path = output_dir / filename
            if not path.is_file():
                missing.append(path)
                continue
            rows.append(
                {
                    "episode": episode,
                    "visual_order": visual_order,
                    "timeline_block": timeline_block(item["prompt_source"]),
                    "kind": item["kind"],
                    "filename": filename,
                    "resolution": image_dimensions(path),
                    "prompt_source": item["prompt_source"],
                    "references": item["references"],
                    "qa_status": "FINAL",
                    "relative_path": path.relative_to(ROOT).as_posix(),
                }
            )

        for clip_order, path in enumerate(sorted(output_dir.glob("CLIP*.mp4")), 1):
            rows.append(
                {
                    "episode": episode,
                    "visual_order": f"V{clip_order:02d}",
                    "timeline_block": "SEE_VEO_PLAN",
                    "kind": "VEO_CLIP",
                    "filename": path.name,
                    "resolution": "1920x1080",
                    "prompt_source": "VEO_CLIP_PLAN.md",
                    "references": "start frame documented in episode Veo plan",
                    "qa_status": "FINAL",
                    "relative_path": path.relative_to(ROOT).as_posix(),
                }
            )

        cards_dir = kit / "03_GENERATED_OUTPUT" / "CARDS"
        for card_order, path in enumerate(sorted(cards_dir.glob("CARD*.png")), 1):
            rows.append(
                {
                    "episode": episode,
                    "visual_order": f"C{card_order:02d}",
                    "timeline_block": "SEE_CARD_MANIFEST",
                    "kind": "GRAPHICS_CARD",
                    "filename": path.name,
                    "resolution": image_dimensions(path),
                    "prompt_source": "CARDS/CARDS_MANIFEST.csv",
                    "references": "factual content locked in production summary",
                    "qa_status": "FINAL",
                    "relative_path": path.relative_to(ROOT).as_posix(),
                }
            )

    if missing:
        formatted = "\n".join(str(path) for path in missing)
        raise SystemExit(f"Missing expected final visuals:\n{formatted}")

    fieldnames = [
        "episode",
        "visual_order",
        "timeline_block",
        "kind",
        "filename",
        "resolution",
        "prompt_source",
        "references",
        "qa_status",
        "relative_path",
    ]
    with OUTPUT_CSV.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {OUTPUT_CSV} with {len(rows)} entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
