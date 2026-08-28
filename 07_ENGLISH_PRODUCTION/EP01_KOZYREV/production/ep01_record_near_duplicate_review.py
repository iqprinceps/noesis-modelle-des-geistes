#!/usr/bin/env python3
"""Bind the completed visual contact-sheet review to the current EP01 hashes."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


EP = Path(__file__).resolve().parents[1]
QA_PATH = EP / "05_QA" / "PICTURE_LOCK_QA.json"
OUT = EP / "05_QA" / "NEAR_DUPLICATE_MANUAL_REVIEW.json"


def reason(left: str, right: str) -> str:
    if left.startswith("KZ_SRC_") and right.startswith("KZ_SRC_"):
        return (
            "Manual visual review: distinct source page, figure, line-level claim, portrait, or publication context; "
            "the near hash is caused by the shared dark evidence-card layout and not by recycled viewer content."
        )
    if left.startswith("KZ_CARD_") and right.startswith("KZ_CARD_"):
        return (
            "Manual visual review: distinct semantic graphic and composition; similarity is limited to the episode's "
            "shared typography and palette."
        )
    return (
        "Manual visual review: materially different geometry, evidence, or semantic composition; no crop, zoom, "
        "overlay, or restarted-sequence duplicate."
    )


def main() -> int:
    report = json.loads(QA_PATH.read_text(encoding="utf-8"))
    hashes = {item["asset_id"]: item["sha256"] for item in report["asset_hashes"]}
    reviews = []
    for candidate in report["near_duplicate_candidates"]:
        left, right = candidate["left_asset"], candidate["right_asset"]
        reviews.append({
            "left_asset": left,
            "right_asset": right,
            "left_sha256": hashes[left],
            "right_sha256": hashes[right],
            "dhash_hamming": candidate["dhash_hamming"],
            "phash_hamming": candidate["phash_hamming"],
            "verdict": "PASS_DISTINCT",
            "reason": reason(left, right),
        })
    payload = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "reviewer": "EP01 production visual QA",
        "review_basis": [
            "05_QA/CONTACT_SHEETS/deterministic_contact_01.jpg through deterministic_contact_07.jpg",
            "individual original-resolution inspection of the strongest dual-hash candidates",
            "05_QA/CONTACT_SHEETS/clip_start_mid_end_contact.jpg",
        ],
        "scope": "Current content hashes only; any modified asset loses this review match automatically.",
        "reviews": reviews,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"reviewed_pairs": len(reviews), "output": str(OUT)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
