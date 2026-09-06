#!/usr/bin/env python3
"""Upload the EP13 teaser shorts from their own metadata files.

Same contract as the episode publisher: everything published comes from
05_OUTPUT/YOUTUBE_METADATA.json and the master beside it, nothing is retyped
here, and each upload goes up private with a scheduled publish time.

Shorts flank the episode rather than compete with it. The first goes up before
the film so it can find an audience for it; the second goes up after, for people
who arrive late.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent / "NOESIS Channel" / "tools"))
from googleapiclient.http import MediaFileUpload  # noqa: E402
from noesis_cli import data_api, verify_channel  # noqa: E402

SHORTS = {
    "en1": {"dir": ROOT / "07_ENGLISH_PRODUCTION" / "EP13_VATICAN_01_SHORTS" / "S01_BULLET_IN_CROWN" / "05_OUTPUT",
            "channel": "en", "publish_at": "2026-09-10T18:30:00+02:00"},
    "en2": {"dir": ROOT / "07_ENGLISH_PRODUCTION" / "EP13_VATICAN_01_SHORTS" / "S02_THE_SILENCE" / "05_OUTPUT",
            "channel": "en", "publish_at": "2026-09-14T18:30:00+02:00"},
    "de1": {"dir": ROOT / "08_GERMAN_PRODUCTION" / "EP13_VATIKAN_01_SHORTS" / "S01_KUGEL_IN_KRONE" / "05_OUTPUT",
            "channel": "de", "publish_at": "2026-09-17T18:30:00+02:00"},
    "de2": {"dir": ROOT / "08_GERMAN_PRODUCTION" / "EP13_VATIKAN_01_SHORTS" / "S02_DAS_SCHWEIGEN" / "05_OUTPUT",
            "channel": "de", "publish_at": "2026-09-21T18:30:00+02:00"},
}


def load(key):
    cfg = SHORTS[key]
    meta = json.loads((cfg["dir"] / "YOUTUBE_METADATA.json").read_text(encoding="utf-8"))
    video = cfg["dir"] / meta["video"]
    if not video.is_file():
        sys.exit(f"{key}: missing master {video}")
    return cfg, meta, video


def preflight(key):
    cfg, meta, video = load(key)
    print(f"{key}  {meta['title']}")
    print(f"     {video.stat().st_size / 1048576:.0f} MiB, channel {cfg['channel']}, "
          f"publish {cfg['publish_at']}")
    if "[LINK" in meta["description"]:
        print("     BLOCKED: the description still carries a placeholder link")
        return False
    if len(meta["title"]) > 100:
        print("     BLOCKED: title over 100 characters")
        return False
    return True


def already_there(yt, title):
    ch = yt.channels().list(part="contentDetails", mine=True).execute()
    uploads = ch["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    page = None
    while True:
        r = yt.playlistItems().list(part="snippet", playlistId=uploads,
                                    maxResults=50, pageToken=page).execute()
        for it in r["items"]:
            if it["snippet"]["title"].strip() == title.strip():
                return it["snippet"]["resourceId"]["videoId"]
        page = r.get("nextPageToken")
        if not page:
            return None


def upload(key):
    cfg, meta, video = load(key)
    yt = data_api(cfg["channel"])
    who = verify_channel(cfg["channel"], yt)
    existing = already_there(yt, meta["title"])
    if existing:
        print(f"{key}: already on the channel as {existing}, skipping")
        return existing
    body = {
        "snippet": {"title": meta["title"], "description": meta["description"],
                    "tags": meta["tags"], "categoryId": str(meta["categoryId"]),
                    "defaultLanguage": meta["defaultLanguage"],
                    "defaultAudioLanguage": meta["defaultAudioLanguage"]},
        "status": {"privacyStatus": "private", "publishAt": cfg["publish_at"],
                   "selfDeclaredMadeForKids": bool(meta["madeForKids"]),
                   "containsSyntheticMedia": bool(meta["containsSyntheticMedia"])},
    }
    media = MediaFileUpload(str(video), chunksize=4 * 1024 * 1024, resumable=True,
                            mimetype="video/mp4")
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media,
                             notifySubscribers=bool(meta.get("notifySubscribers", False)))
    last = -1
    while True:
        status, response = req.next_chunk()
        if status:
            pct = int(status.progress() * 100)
            if pct >= last + 25:
                print(f"  {key} uploading {pct:3d}%", flush=True)
                last = pct
        if response is not None:
            break
    vid = response["id"]
    print(f"  {key} video id {vid}  on {who}")

    if meta.get("playlist"):
        pid = None
        page = None
        while True:
            r = yt.playlists().list(part="snippet", mine=True, maxResults=50,
                                    pageToken=page).execute()
            for it in r["items"]:
                if it["snippet"]["title"].strip().casefold() == meta["playlist"].strip().casefold():
                    pid = it["id"]
            page = r.get("nextPageToken")
            if not page or pid:
                break
        if pid:
            for attempt in range(6):
                try:
                    yt.playlistItems().insert(part="snippet", body={"snippet": {
                        "playlistId": pid,
                        "resourceId": {"kind": "youtube#video", "videoId": vid}}}).execute()
                    print(f"  {key} added to {meta['playlist']}")
                    break
                except Exception as exc:
                    print(f"  {key} playlist retry {attempt + 1}: {str(exc)[:80]}")
                    time.sleep(6 * (attempt + 1))
    (cfg["dir"] / "YOUTUBE_UPLOAD.json").write_text(json.dumps({
        "video_id": vid, "url": f"https://www.youtube.com/watch?v={vid}",
        "channel": who, "title": meta["title"], "privacy_at_upload": "private",
        "scheduled": cfg["publish_at"],
        "uploaded": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return vid


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--which", default="en1,en2")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    keys = [k.strip() for k in a.which.split(",") if k.strip()]
    ok = all(preflight(k) for k in keys)
    if a.dry_run or not ok:
        print("nothing sent" if a.dry_run else "preflight failed, nothing sent")
        return
    for k in keys:
        upload(k)


if __name__ == "__main__":
    main()
