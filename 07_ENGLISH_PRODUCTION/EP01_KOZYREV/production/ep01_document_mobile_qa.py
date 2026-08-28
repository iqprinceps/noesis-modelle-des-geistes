#!/usr/bin/env python3
"""Create true 480x270 playback proofs for accepted EP01 document frames."""

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


EP = Path(__file__).resolve().parents[1]
CROPS = EP / "04_ASSETS" / "GENERATED" / "DOCUMENT_EVIDENCE"
META = EP / "04_ASSETS" / "METADATA" / "DOCUMENT_EVIDENCE"
OUT = EP / "05_QA" / "DOCUMENT_EVIDENCE" / "MOBILE"


def font(size: int):
    for path in (Path("C:/Windows/Fonts/segoeui.ttf"), Path("C:/Windows/Fonts/arial.ttf")):
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for stale in OUT.glob("MOBILE_DOCUMENT_PROOF_*.png"):
        stale.unlink()
    records = []
    for asset in sorted(CROPS.glob("KZ_DOC_*.png")):
        metadata = json.loads((META / f"{asset.stem}.json").read_text(encoding="utf-8"))
        if not str(metadata.get("status", "")).startswith("PASS"):
            continue
        image = Image.open(asset).convert("RGB").resize((480, 270), Image.Resampling.LANCZOS)
        records.append((asset, image, metadata))

    sheets = []
    for number, offset in enumerate(range(0, len(records), 4), 1):
        sheet = Image.new("RGB", (960, 600), (10, 15, 18))
        draw = ImageDraw.Draw(sheet)
        for slot, (asset, image, metadata) in enumerate(records[offset:offset + 4]):
            x, y = (slot % 2) * 480, (slot // 2) * 300
            sheet.paste(image, (x, y))
            draw.rectangle((x, y + 270, x + 479, y + 299), fill=(10, 15, 18))
            draw.text((x + 8, y + 274), asset.stem, font=font(17), fill=(239, 236, 224))
        out = OUT / f"MOBILE_DOCUMENT_PROOF_{number:02d}.png"
        sheet.save(out)
        sheets.append(str(out))

    report = {
        "status": "PENDING_MANUAL_VISUAL_REVIEW",
        "playback_size": "480x270",
        "asset_count": len(records),
        "sheets": sheets,
        "policy": "Document shots remain static; no pan or zoom permitted.",
    }
    (OUT / "MOBILE_DOCUMENT_PROOF.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
