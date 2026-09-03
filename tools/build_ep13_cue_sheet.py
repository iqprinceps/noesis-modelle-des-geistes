#!/usr/bin/env python3
"""EP13 cue sheet.

Every visual state is bound to a word range from the forced alignment, so the
timings are measured rather than estimated. The assignment table below is
editorial: one line per spoken beat, naming the state that carries it.

Rules enforced by this script, from 00_GLOBAL/VISUAL_RETENTION_STANDARD.md and
the card lock:

  * a state may not return non-contiguously anywhere in the timeline;
  * holds are reported and anything at or beyond 8 s is flagged for review;
  * a clip and the still it was generated from count as the same state.
"""

from __future__ import annotations

import argparse
import csv
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
EP = ROOT / "07_ENGLISH_PRODUCTION" / "EP13_VATICAN_01"
ALIGN = EP / "02_VOICE" / "ALIGNMENT" / "EP13_EN_VO_ALIGNMENT.json"
SCRIPT = EP / "01_SCRIPT" / "VOICE_SCRIPT_EN.txt"
OUT = EP / "05_DELIVERY" / "EP13_EN_VISUAL_CUE_SHEET.csv"

# A clip replaces its source still: using both would be a near-identical repeat.
CLIP_OF = {
    "CLIP01_FLAMES_FAIL": "V01_ANGEL_SWORD",
    "CLIP03_WRITING": "H05_WRITING_HAND_1944",
    "CLIP04_SEALING": "H07_SEALING_WAX",
    "CLIP06_THE_CLIMB": "V09_THE_CLIMB",
    "CLIP08_SETTING_THE_METAL": "H15_SETTING_THE_METAL",
    "CLIP09_PUTTING_IT_AWAY": "H10_BOX_RETURNED",
    "CLIP10_THE_WAY": "V04_THE_WAY",
}


def beats() -> list[dict]:
    align = json.loads(ALIGN.read_text(encoding="utf-8"))
    words = [w for w in align["words"] if w["text"].strip()]
    blocks = [b.strip() for b in re.split(r"\n\s*\n", SCRIPT.read_text(encoding="utf-8")) if b.strip()]
    out, cursor = [], 0
    for i, b in enumerate(blocks, 1):
        n = len(re.findall(r"[0-9a-z']+", b.casefold()))
        if not n:
            continue
        seg = words[cursor:cursor + n]
        if not seg:
            break
        out.append({"beat": i, "start": round(seg[0]["start"], 2), "end": round(seg[-1]["end"], 2),
                    "text": b.replace("\n", " ")})
        cursor += n
    return out


def load_assignment(path: pathlib.Path) -> dict[int, list[str]]:
    """beat number -> ordered list of state ids covering it."""
    table: dict[int, list[str]] = {}
    for row in csv.DictReader(path.open(encoding="utf-8-sig")):
        b = int(row["beat"])
        states = [s.strip() for s in row["states"].split("|") if s.strip()]
        table[b] = states
    return table


def build(assignment: pathlib.Path) -> None:
    bs = beats()
    table = load_assignment(assignment)
    rows, seen, problems = [], {}, []
    prev_state = None
    for b in bs:
        states = table.get(b["beat"])
        if not states:
            problems.append(f"beat {b['beat']} has no state assigned")
            states = ["__GAP__"]
        span = b["end"] - b["start"]
        share = span / len(states)
        for k, st in enumerate(states):
            canon = CLIP_OF.get(st.replace("EP13_", ""), st.replace("EP13_", ""))
            start = round(b["start"] + k * share, 2)
            end = round(b["start"] + (k + 1) * share, 2)
            if canon in seen and prev_state != canon:
                problems.append(f"beat {b['beat']}: {st} returns non-contiguously "
                                f"(first used at {seen[canon]}s)")
            seen.setdefault(canon, start)
            rows.append({"beat": b["beat"], "state": st, "canonical": canon,
                         "in": start, "out": end, "hold": round(end - start, 2),
                         "text": b["text"][:110]})
            prev_state = canon
    for r in rows:
        if r["hold"] >= 8:
            problems.append(f"hold {r['hold']}s at {r['in']}s on {r['state']} exceeds 8 s")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    holds = [r["hold"] for r in rows]
    print(f"States: {len(rows)} over {len(bs)} beats")
    print(f"Hold: min {min(holds):.1f}s  median {sorted(holds)[len(holds)//2]:.1f}s  max {max(holds):.1f}s")
    print(f"Distinct canonical states used: {len(seen)}")
    print(f"Wrote {OUT}")
    if problems:
        print(f"\n{len(problems)} problem(s):")
        for p in problems[:40]:
            print("  " + p)
    else:
        print("\nNo rule violations.")


def skeleton(path: pathlib.Path) -> None:
    """Emit an empty assignment table for editing."""
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["beat", "start", "dur", "states", "text"])
        for b in beats():
            w.writerow([b["beat"], b["start"], round(b["end"] - b["start"], 2), "", b["text"]])
    print(f"Wrote skeleton {path}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["skeleton", "build"])
    ap.add_argument("--table", default=str(EP / "05_DELIVERY" / "EP13_EN_CUE_ASSIGNMENT.csv"))
    a = ap.parse_args()
    p = pathlib.Path(a.table)
    p.parent.mkdir(parents=True, exist_ok=True)
    if a.action == "skeleton":
        skeleton(p)
    else:
        if not p.is_file():
            sys.exit(f"assignment table missing: {p}")
        build(p)


if __name__ == "__main__":
    main()
