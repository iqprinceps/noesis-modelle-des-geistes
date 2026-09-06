#!/usr/bin/env python3
"""Download the EP14 originals chosen from the research reports, and record them.

Two things this enforces, both learned on EP13. Nothing with a ShareAlike
condition is downloaded at all, because Ken Burns makes the film Adapted Material
and ShareAlike would then apply to the whole film. And every file is written with
its licence, creator and source URL into a manifest at the moment it arrives, so
the attribution that CC BY requires cannot drift away from the picture.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import pathlib
import re
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
EP = ROOT / "07_ENGLISH_PRODUCTION" / "EP14_VATICAN_02"
DEST = EP / "03_VISUALS" / "ASSETS" / "SELECTED" / "AUTHENTIC"
MANIFEST = EP / "02_SOURCES" / "COMMONS_RESEARCH_MANIFEST.csv"
UA = "NOESIS-production/1.0 (documentary source clearance)"


def clean(lic: str) -> bool:
    low = lic.lower()
    return not ("share" in low or "-sa" in low or re.search(r"\bsa\b", low))


def fetch(url, dest):
    for attempt in range(6):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=300) as r:
                dest.write_bytes(r.read())
            return True
        except Exception as exc:
            print(f"    retry {attempt + 1}: {str(exc)[:70]}")
            time.sleep(25 * (attempt + 1))
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reports", nargs="+", required=True)
    ap.add_argument("--pick", required=True,
                    help="JSON: {label: [title substrings to take]}")
    a = ap.parse_args()
    reports = {}
    for r in a.reports:
        reports.update(json.loads(pathlib.Path(r).read_text(encoding="utf-8")))
    picks = json.loads(pathlib.Path(a.pick).read_text(encoding="utf-8"))
    DEST.mkdir(parents=True, exist_ok=True)

    rows = []
    if MANIFEST.is_file():
        rows = list(csv.DictReader(MANIFEST.open(encoding="utf-8")))
    have = {r["commons_title"] for r in rows}

    for label, wanted in picks.items():
        pool = reports.get(label, [])
        for frag in wanted:
            hit = next((r for r in pool if frag.casefold() in r["title"].casefold()), None)
            if hit is None:
                print(f"  MISS  {label}: {frag}")
                continue
            if not clean(hit["licence"]):
                print(f"  SKIP  ShareAlike: {hit['title'][5:60]}")
                continue
            if hit["title"] in have:
                continue
            stem = "EP14_" + re.sub(r"[^A-Za-z0-9]+", "_", hit["title"][5:].rsplit(".", 1)[0])[:68]
            ext = hit["url"].rsplit(".", 1)[-1].lower()
            ext = ext if ext in ("jpg", "jpeg", "png", "tif", "tiff") else "jpg"
            out = DEST / f"{stem}.{ext}"
            if not out.is_file() or out.stat().st_size < 20000:
                print(f"  GET   {hit['w']}x{hit['h']}  {hit['title'][5:64]}")
                if not fetch(hit["url"], out):
                    print("        failed")
                    continue
                time.sleep(6)
            b = out.read_bytes()
            rows.append({
                "asset_id": stem.replace("EP14_", "")[:40],
                "file": str(out.relative_to(EP)).replace("\\", "/"),
                "commons_title": hit["title"],
                "source_url": "https://commons.wikimedia.org/wiki/" + hit["title"].replace(" ", "_"),
                "licence": hit["licence"], "creator": hit["artist"] or "unknown",
                "date": hit["date"], "resolution": f"{hit['w']}x{hit['h']}",
                "bytes": len(b), "sha256": hashlib.sha256(b).hexdigest(),
                "research_label": label,
            })
            have.add(hit["title"])

    if rows:
        MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        with MANIFEST.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
    print(f"\n{len(rows)} originals in {MANIFEST.name}")
    import collections
    for lic, n in collections.Counter(r["licence"] for r in rows).most_common():
        print(f"   {n:3d}  {lic}")


if __name__ == "__main__":
    main()
