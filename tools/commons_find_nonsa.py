#!/usr/bin/env python3
"""Find Commons replacements whose licence carries no ShareAlike condition.

Ken Burns crops and moves every still, which makes the film Adapted Material
under CC BY-SA. ShareAlike would then require the whole film to be BY-SA, and
YouTube cannot express that. Public domain, CC0 and plain CC BY carry no such
condition, so they are the only pool this episode can draw from.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
import urllib.request

API = "https://commons.wikimedia.org/w/api.php"
UA = "NOESIS-production/1.0 (documentary source clearance)"
OK = ("public domain", "pd-", "cc0", "cc by 2.0", "cc by 3.0", "cc by 4.0",
      "attribution", "no restrictions")


def api(**params):
    params.update(format="json", formatversion="2")
    req = urllib.request.Request(API + "?" + urllib.parse.urlencode(params),
                                 headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.load(r)


def clean(lic: str) -> bool:
    low = lic.lower()
    if "sa" in low.replace("share", "").split("-") or "share" in low:
        return False
    return any(low.startswith(o) or o in low for o in OK)


def look(titles):
    out = []
    for i in range(0, len(titles), 40):
        d = api(action="query", titles="|".join(titles[i:i + 40]), prop="imageinfo",
                iiprop="url|size|extmetadata",
                iiextmetadatafilter="LicenseShortName|Artist|LicenseUrl")
        for p in d.get("query", {}).get("pages", []):
            ii = (p.get("imageinfo") or [{}])[0]
            md = ii.get("extmetadata", {})
            lic = md.get("LicenseShortName", {}).get("value", "?")
            art = md.get("Artist", {}).get("value", "?")
            import re
            art = re.sub("<[^>]+>", "", art).strip()
            out.append({"title": p["title"], "licence": lic, "artist": art,
                        "w": ii.get("width", 0), "h": ii.get("height", 0),
                        "url": ii.get("url", "")})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--category", action="append", default=[])
    ap.add_argument("--search", action="append", default=[])
    ap.add_argument("--minpx", type=int, default=1_500_000)
    ap.add_argument("--limit", type=int, default=200)
    a = ap.parse_args()

    titles = []
    for c in a.category:
        cm = api(action="query", list="categorymembers", cmtitle=f"Category:{c}",
                 cmtype="file", cmlimit=a.limit)
        titles += [m["title"] for m in cm.get("query", {}).get("categorymembers", [])]
    for s in a.search:
        sr = api(action="query", list="search", srsearch=f"filetype:bitmap {s}",
                 srnamespace=6, srlimit=a.limit)
        titles += [m["title"] for m in sr.get("query", {}).get("search", [])]
    titles = list(dict.fromkeys(titles))
    if not titles:
        sys.exit("no candidates")

    rows = [r for r in look(titles) if clean(r["licence"]) and r["w"] * r["h"] >= a.minpx]
    rows.sort(key=lambda r: -r["w"] * r["h"])
    print(f"{len(rows)} clean of {len(titles)} candidates\n")
    for r in rows[:30]:
        print(f'  {r["w"]}x{r["h"]:<6} [{r["licence"]}] {r["artist"][:34]}')
        print(f'      {r["title"]}')


if __name__ == "__main__":
    main()
