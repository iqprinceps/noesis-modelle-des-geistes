#!/usr/bin/env python3
"""Bulk Commons research with rate-limit patience and a local cache.

Commons starts returning 429 quickly under a burst of category and metadata
calls, and an episode's worth of research is exactly such a burst. Every response
is cached on disk, so a rerun after a rate limit continues instead of starting
over, and the cache is also the record of what was actually asked.

Only licences without a ShareAlike condition are reported. Ken Burns crops and
moves every still, which makes a film Adapted Material, and ShareAlike would then
oblige the whole film to carry a licence YouTube cannot express.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import sys
import time
import urllib.parse
import urllib.request

API = "https://commons.wikimedia.org/w/api.php"
UA = "NOESIS-production/1.0 (documentary source clearance)"
CACHE = pathlib.Path(__file__).resolve().parents[1] / "tmp" / "commons_cache"
OK = ("public domain", "pd-", "cc0", "cc by 2.0", "cc by 3.0", "cc by 4.0",
      "attribution", "no restrictions")


def api(**params):
    params.update(format="json", formatversion="2")
    key = hashlib.sha256(json.dumps(params, sort_keys=True).encode()).hexdigest()[:32]
    CACHE.mkdir(parents=True, exist_ok=True)
    hit = CACHE / f"{key}.json"
    if hit.is_file():
        return json.loads(hit.read_text(encoding="utf-8"))
    url = API + "?" + urllib.parse.urlencode(params)
    for attempt in range(8):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.load(r)
            hit.write_text(json.dumps(data), encoding="utf-8")
            time.sleep(1.1)
            return data
        except urllib.error.HTTPError as exc:
            if exc.code == 429:
                wait = 15 * (attempt + 1)
                print(f"    rate limited, waiting {wait}s", flush=True)
                time.sleep(wait)
                continue
            raise
        except Exception:
            time.sleep(5 * (attempt + 1))
    raise SystemExit("Commons kept refusing; try again later")


def clean(lic: str) -> bool:
    low = lic.lower()
    if "share" in low or re.search(r"\bsa\b", low) or "-sa" in low:
        return False
    return any(o in low for o in OK)


def meta(titles):
    out = []
    for i in range(0, len(titles), 30):
        d = api(action="query", titles="|".join(titles[i:i + 30]), prop="imageinfo",
                iiprop="url|size|extmetadata", iiurlwidth=900,
                iiextmetadatafilter="LicenseShortName|Artist|DateTimeOriginal")
        for p in d.get("query", {}).get("pages", []):
            ii = (p.get("imageinfo") or [{}])[0]
            md = ii.get("extmetadata", {})
            out.append({
                "title": p["title"],
                "licence": md.get("LicenseShortName", {}).get("value", "?"),
                "artist": re.sub("<[^>]+>", "", md.get("Artist", {}).get("value", "")).strip(),
                "date": re.sub("<[^>]+>", "", md.get("DateTimeOriginal", {}).get("value", "")).strip()[:40],
                "w": ii.get("width", 0), "h": ii.get("height", 0),
                "url": ii.get("url", ""), "thumb": ii.get("thumburl", ""),
            })
    return out


def category(name, limit=200):
    d = api(action="query", list="categorymembers", cmtitle=f"Category:{name}",
            cmtype="file", cmlimit=limit)
    return [m["title"] for m in d.get("query", {}).get("categorymembers", [])]


def search(term, limit=40):
    d = api(action="query", list="search", srsearch=f"filetype:bitmap {term}",
            srnamespace=6, srlimit=limit)
    return [m["title"] for m in d.get("query", {}).get("search", [])]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True, help="JSON file: [{label, category|search, minpx}]")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    plan = json.loads(pathlib.Path(a.plan).read_text(encoding="utf-8"))
    report = {}
    for item in plan:
        label = item["label"]
        print(f"== {label}", flush=True)
        titles = []
        for cat in item.get("category", []):
            got = category(cat)
            print(f"   category {cat}: {len(got)}", flush=True)
            titles += got
        for term in item.get("search", []):
            got = search(term)
            print(f"   search {term!r}: {len(got)}", flush=True)
            titles += got
        titles = list(dict.fromkeys(titles))
        rows = [r for r in meta(titles)
                if clean(r["licence"]) and r["w"] * r["h"] >= item.get("minpx", 300000)]
        rows.sort(key=lambda r: -r["w"] * r["h"])
        report[label] = rows[:item.get("keep", 20)]
        print(f"   -> {len(rows)} clean, keeping {len(report[label])}", flush=True)
    pathlib.Path(a.out).write_text(json.dumps(report, indent=1, ensure_ascii=False),
                                   encoding="utf-8")
    print(f"\nreport -> {a.out}")
    for label, rows in report.items():
        print(f"\n{label}  ({len(rows)})")
        for r in rows[:8]:
            print(f"   {r['w']}x{r['h']:<6} [{r['licence'][:16]:16s}] {r['title'][5:70]}")


if __name__ == "__main__":
    main()
