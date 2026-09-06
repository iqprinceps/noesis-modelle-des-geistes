#!/usr/bin/env python3
"""Upload EP13 to the English channel from its own upload package.

Everything published here comes from 09_UPLOAD: the title, description, tags and
flags from UPLOAD_METADATA.json, the picture from 05_DELIVERY and the thumbnail
the SEO profile selected. Nothing is retyped here, so the file on disk and the
video on the channel cannot drift apart.

The upload goes up private with a scheduled publish time. That is what the
package specifies and what was approved: it appears on the channel at the
scheduled moment, not the instant this script finishes.
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

EP = ROOT / "07_ENGLISH_PRODUCTION" / "EP13_VATICAN_01"
META = EP / "09_UPLOAD" / "UPLOAD_METADATA.json"
VIDEO = EP / "05_DELIVERY" / "EP13_EN_FINAL.mp4"
RECORD = EP / "09_UPLOAD" / "YOUTUBE_PUBLICATION_RECORD.md"
CHANNEL = "en"
PLAYLIST_DESCRIPTION = (
    "What happens when an institution takes something uncertain and gives it a "
    "form. Five files from the Vatican archives."
)


def load():
    meta = json.loads(META.read_text(encoding="utf-8"))
    thumb = (META.parent / meta["selectedThumbnail"]).resolve()
    for label, p in (("video", VIDEO), ("thumbnail", thumb), ("metadata", META)):
        if not p.is_file():
            sys.exit(f"missing {label}: {p}")
    return meta, thumb


def preflight(meta, thumb):
    size = VIDEO.stat().st_size / 1048576
    print("preflight")
    print(f"  title      {meta['title']}  ({len(meta['title'])} chars)")
    print(f"  video      {VIDEO.name}  {size:.0f} MiB")
    print(f"  thumbnail  {thumb.name}  {thumb.stat().st_size / 1024:.0f} KiB")
    print(f"  tags       {len(meta['tags'])}, {sum(len(t) for t in meta['tags']) + len(meta['tags']) - 1} chars")
    print(f"  desc       {len(meta['description'])} chars")
    print(f"  privacy    {meta['privacyStatus']}, publish at {meta['publishAt']}")
    if len(meta["title"]) > 100:
        sys.exit("title over 100 characters")
    if len(meta["description"]) > 5000:
        sys.exit("description over 5000 characters")
    if thumb.stat().st_size > 2 * 1024 * 1024:
        sys.exit("thumbnail over 2 MiB")
    when = dt.datetime.fromisoformat(meta["publishAt"])
    if when <= dt.datetime.now(when.tzinfo):
        print("  NOTE     the scheduled time is in the past; YouTube will publish on upload")


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


def ensure_playlist(yt, title):
    page = None
    while True:
        r = yt.playlists().list(part="snippet", mine=True, maxResults=50,
                                pageToken=page).execute()
        for it in r["items"]:
            if it["snippet"]["title"].strip().casefold() == title.strip().casefold():
                return it["id"]
        page = r.get("nextPageToken")
        if not page:
            break
    made = yt.playlists().insert(part="snippet,status", body={
        "snippet": {"title": title, "description": PLAYLIST_DESCRIPTION,
                    "defaultLanguage": "en"},
        "status": {"privacyStatus": "public"}}).execute()
    print(f"  playlist created: {title}")
    return made["id"]


def upload(yt, meta):
    body = {
        "snippet": {
            "title": meta["title"],
            "description": meta["description"],
            "tags": meta["tags"],
            "categoryId": str(meta["categoryId"]),
            "defaultLanguage": meta["defaultLanguage"],
            "defaultAudioLanguage": meta["defaultAudioLanguage"],
        },
        "status": {
            "privacyStatus": meta["privacyStatus"],
            "publishAt": meta["publishAt"],
            "selfDeclaredMadeForKids": bool(meta["madeForKids"]),
            "embeddable": bool(meta["embeddable"]),
            "license": meta["license"],
            "publicStatsViewable": bool(meta["publicStatsViewable"]),
            "containsSyntheticMedia": bool(meta["containsSyntheticMedia"]),
        },
    }
    media = MediaFileUpload(str(VIDEO), chunksize=8 * 1024 * 1024, resumable=True,
                            mimetype="video/mp4")
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media,
                             notifySubscribers=bool(meta["notifySubscribers"]))
    last = -1
    while True:
        status, response = req.next_chunk()
        if status:
            pct = int(status.progress() * 100)
            if pct >= last + 5:
                print(f"  uploading {pct:3d}%", flush=True)
                last = pct
        if response is not None:
            return response["id"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    meta, thumb = load()
    preflight(meta, thumb)
    if a.dry_run:
        print("dry run, nothing sent")
        return
    yt = data_api(CHANNEL)
    who = verify_channel(CHANNEL, yt)
    print(f"channel     {who}")

    existing = already_there(yt, meta["title"])
    if existing:
        print(f"already on the channel as {existing}; refusing to upload a second copy")
        return

    vid = upload(yt, meta)
    print(f"  video id   {vid}")

    for attempt in range(5):
        try:
            yt.thumbnails().set(videoId=vid,
                                media_body=MediaFileUpload(str(thumb))).execute()
            print("  thumbnail  set")
            break
        except Exception as exc:
            print(f"  thumbnail  retry {attempt + 1}: {str(exc)[:120]}")
            time.sleep(5 * (attempt + 1))

    # YouTube returns a transient 409 SERVICE_UNAVAILABLE on playlist writes often
    # enough that a bare call will lose an otherwise finished upload.
    pl = ensure_playlist(yt, meta["playlist"])
    for attempt in range(6):
        try:
            yt.playlistItems().insert(part="snippet", body={"snippet": {
                "playlistId": pl, "position": 0,
                "resourceId": {"kind": "youtube#video", "videoId": vid}}}).execute()
            print(f"  playlist   added to {meta['playlist']}")
            break
        except Exception as exc:
            print(f"  playlist   retry {attempt + 1}: {str(exc)[:100]}")
            time.sleep(6 * (attempt + 1))
    else:
        print(f"  playlist   NOT added; do it by hand for {vid}")

    url = f"https://www.youtube.com/watch?v={vid}"
    RECORD.write_text(
        "# EP13_EN — YouTube Publication Record\n\n"
        f"| | |\n|---|---|\n"
        f"| Video | [{vid}]({url}) |\n"
        f"| Channel | {who} |\n"
        f"| Title | {meta['title']} |\n"
        f"| Uploaded | {dt.datetime.now().astimezone().isoformat(timespec='seconds')} |\n"
        f"| Privacy at upload | {meta['privacyStatus']} |\n"
        f"| Scheduled | {meta['publishAt']} |\n"
        f"| Playlist | {meta['playlist']} |\n"
        f"| Thumbnail | {thumb.name} |\n\n"
        "The pinned comment in `PINNED_COMMENT_EN.txt` has to be posted and pinned "
        "by hand once the video is live; the API cannot pin a comment.\n",
        encoding="utf-8")
    print(f"\n{url}\nrecord -> {RECORD}")


if __name__ == "__main__":
    main()
