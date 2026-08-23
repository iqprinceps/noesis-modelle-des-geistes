#!/usr/bin/env python3
"""Apply the manually reviewed EP01 visual mapping and report reuse."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CUES = ROOT / "03_EPISODEN" / "TYPE_A" / "EP01_KOZYREV" / "VISUAL_CUE_SHEET.csv"

# Values beginning with IMG use 01_SELECTED. All other values are explicit
# paths relative to 05_GENERATED/EP01_KOZYREV.
MAPPING = {
    "EP01_V_003": "05_ORIGINAL_COMPOSITES/ORIG04_MIRROR_2014_FULL_WIDE.png",
    "EP01_V_004": "05_ORIGINAL_COMPOSITES/ORIG10_PATENT_PAGE1_FULL_WIDE.png",
    "EP01_V_005": "05_ORIGINAL_COMPOSITES/ORIG11_PATENT_HEADER_WIDE.png",
    "EP01_V_005A": "03_EDITOR_CARDS/CARD01_PATENT_EVIDENCE.png",
    "EP01_V_006": "03_EDITOR_CARDS/CARD02_PATENT_TITLE.png",
    "EP01_V_007": "05_ORIGINAL_COMPOSITES/ORIG16_COMMONS_PATENT_APPARATUS_WIDE.png",
    "EP01_V_008": "05_ORIGINAL_COMPOSITES/ORIG01_KOZYREV_FULL_WIDE.png",
    "EP01_V_010": "05_ORIGINAL_COMPOSITES/ORIG08_REFRACTOR_WIDE_SOURCE.png",
    "EP01_V_012": "05_ORIGINAL_COMPOSITES/ORIG07_REFRACTOR_FULL_WIDE.png",
    "EP01_V_013": "05_ORIGINAL_COMPOSITES/ORIG02_KOZYREV_FACE_AND_MOON_WIDE.png",
    "EP01_V_015": "05_ORIGINAL_COMPOSITES/ORIG09_OBSERVATORY_1855_WIDE.png",
    "EP01_V_016": "IMG22",
    "EP01_V_017": "IMG10",
    "EP01_V_018": "IMG09",
    "EP01_V_019": "IMG08",
    "EP01_V_020": "03_EDITOR_CARDS/CARD03_TECHNICAL_DIMENSIONS.png",
    "EP01_V_021": "05_ORIGINAL_COMPOSITES/ORIG13_PATENT_DIMENSIONS_TEXT_WIDE.png",
    "EP01_V_023": "03_EDITOR_CARDS/CARD03_TECHNICAL_DIMENSIONS.png",
    "EP01_V_024": "05_ORIGINAL_COMPOSITES/ORIG06_PATENT_DRAWING_FULL_WIDE.png",
    "EP01_V_025": "03_EDITOR_CARDS/CARD04_CONFIGURATIONS.png",
    "EP01_V_026": "06_IMAGEGEN_ADDITIONS/IMG94_MOTORIZED_BASE_DETAIL.png",
    "EP01_V_027": "05_ORIGINAL_COMPOSITES/ORIG12_PATENT_FIGURE1_WIDE.png",
    "EP01_V_029": "05_ORIGINAL_COMPOSITES/ORIG17_PATENT_PAGE2_FULL_WIDE.png",
    "EP01_V_030": "03_EDITOR_CARDS/CARD05_PATENT_CLAIM.png",
    "EP01_V_031": "07_MOTION_ASSETS/NASA_TRACERS_MAGNETIC_RECONNECTION_CLIP.mp4",
    "EP01_V_032": "05_ORIGINAL_COMPOSITES/ORIG18_PATENT_PAGE4_FULL_WIDE.png",
    "EP01_V_034": "05_ORIGINAL_COMPOSITES/ORIG03_KAZNACHEEV_FULL_WIDE.png",
    "EP01_V_035": "02_RESERVE/IMG84.png",
    "EP01_V_037": "IMG26",
    "EP01_V_038": "IMG23",
    "EP01_V_039": "03_EDITOR_CARDS/CARD06_PUBLICATION_SOURCE.png",
    "EP01_V_040": "02_RESERVE/IMG83.png",
    "EP01_V_042": "05_ORIGINAL_COMPOSITES/ORIG04_MIRROR_2014_FULL_WIDE.png",
    "EP01_V_043": "05_ORIGINAL_COMPOSITES/ORIG05_MIRROR_2014_DETAIL_WIDE.png",
    "EP01_V_044": "IMG13",
    "EP01_V_045": "IMG28",
    "EP01_V_047": "IMG38",
    "EP01_V_048": "02_RESERVE/IMG86.png",
    "EP01_V_049": "02_RESERVE/IMG76.png",
    "EP01_V_050": "IMG42",
    "EP01_V_052": "IMG48",
    "EP01_V_053": "IMG50",
    "EP01_V_055": "IMG38",
    "EP01_V_056": "IMG40",
    "EP01_V_057": "IMG24",
    "EP01_V_058": "IMG41",
    "EP01_V_059": "IMG43",
    "EP01_V_060": "IMG47",
    "EP01_V_061": "IMG54",
    "EP01_V_062": "IMG58",
    "EP01_V_063": "IMG57",
    "EP01_V_064": "06_IMAGEGEN_ADDITIONS/IMG93_INDEPENDENT_JUDGES.png",
    "EP01_V_064A": "06_IMAGEGEN_ADDITIONS/IMG93B_TARGET_POOL_DETAIL.png",
    "EP01_V_064B": "06_IMAGEGEN_ADDITIONS/IMG93_INDEPENDENT_JUDGES.png",
    "EP01_V_064C": "06_IMAGEGEN_ADDITIONS/IMG93B_TARGET_POOL_DETAIL.png",
    "EP01_V_064D": "06_IMAGEGEN_ADDITIONS/IMG91_RED_LIGHTHOUSE_TARGET.png",
    "EP01_V_064E": "06_IMAGEGEN_ADDITIONS/IMG92_CANONICAL_BLINDED_DRAWING.png",
    "EP01_V_064F": "IMG55",
    "EP01_V_064G": "IMG47",
    "EP01_V_065": "IMG56",
    "EP01_V_066": "IMG45",
    "EP01_V_068": "05_ORIGINAL_COMPOSITES/ORIG17_PATENT_PAGE2_FULL_WIDE.png",
    "EP01_V_069": "03_EDITOR_CARDS/CARD06_PUBLICATION_SOURCE.png",
    "EP01_V_070": "IMG55",
    "EP01_V_071": "IMG69",
    "EP01_V_072": "IMG45",
    "EP01_V_073": "03_EDITOR_CARDS/CARD01_PATENT_EVIDENCE.png",
    "EP01_V_074": "05_ORIGINAL_COMPOSITES/ORIG10_PATENT_PAGE1_FULL_WIDE.png",
    "EP01_V_076": "03_EDITOR_CARDS/CARD05_PATENT_CLAIM.png",
    "EP01_V_077": "05_ORIGINAL_COMPOSITES/ORIG06_PATENT_DRAWING_FULL_WIDE.png",
    "EP01_V_078": "05_ORIGINAL_COMPOSITES/ORIG11_PATENT_HEADER_WIDE.png",
    "EP01_V_079": "05_ORIGINAL_COMPOSITES/ORIG12_PATENT_FIGURE1_WIDE.png",
    "EP01_V_080": "05_ORIGINAL_COMPOSITES/ORIG16_COMMONS_PATENT_APPARATUS_WIDE.png",
    "EP01_V_081": "03_EDITOR_CARDS/CARD02_PATENT_TITLE.png",
    "EP01_V_082": "05_ORIGINAL_COMPOSITES/ORIG15_COMMONS_PARTICIPANT_INSIDE_WIDE.png",
    "EP01_V_083": "03_EDITOR_CARDS/CARD04_CONFIGURATIONS.png",
    "EP01_V_084": "IMG66",
    "EP01_V_086": "03_EDITOR_CARDS/CARD07_FINAL_STATUS.png",
    "EP01_V_087": "05_ORIGINAL_COMPOSITES/ORIG15_COMMONS_PARTICIPANT_INSIDE_WIDE.png",
    "EP01_V_089": "IMG69",
    "EP01_V_090": "IMG43",
    "EP01_V_091": "IMG44",
    "EP01_V_092": "IMG52",
    "EP01_V_093": "IMG05",
    "EP01_V_094": "05_ORIGINAL_COMPOSITES/ORIG01_KOZYREV_FULL_WIDE.png",
    "EP01_V_095": "03_EDITOR_CARDS/CARD07_FINAL_STATUS.png",
    "EP01_V_096": "02_RESERVE/IMG83.png",
}


def main() -> None:
    with CUES.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
        fields = list(rows[0])
    seen = set()
    for row in rows:
        cue = row["cue_id"]
        if cue not in MAPPING:
            continue
        seen.add(cue)
        value = MAPPING[cue]
        if value.startswith("IMG") and "/" not in value:
            row["generation_id"] = value
            row["editor_asset"] = ""
        else:
            row["generation_id"] = ""
            row["editor_asset"] = value
    missing = set(MAPPING) - seen
    if missing:
        raise RuntimeError(f"Unknown cue IDs: {sorted(missing)}")
    with CUES.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    assigned = []
    for row in rows:
        assigned.append(row["editor_asset"] or row["generation_id"] or f"ORIGINAL:{row['visual_type']}")
    counts = Counter(assigned)
    print(f"Updated {len(MAPPING)} of {len(rows)} cues")
    print(f"Distinct visual assignments: {len(counts)}")
    for name, count in counts.most_common():
        if count > 2:
            print(f"REUSE {count}x {name}")


if __name__ == "__main__":
    main()
