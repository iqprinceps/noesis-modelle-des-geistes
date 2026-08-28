#!/usr/bin/env python3
"""Publish EP06-EP08 to the bound German NOESIS YouTube channel.

The script uses only YouTube Data API v3 calls.  It is deliberately
idempotent: after each successful video insert the returned id is persisted,
so an interrupted run resumes without creating a duplicate upload.

Default invocation is a read-only preflight.  ``--execute`` performs the
uploads, sets thumbnails and German captions, creates/fills the series
playlist, adds inter-episode links, and verifies the resulting API state.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOESIS_TOOLS = ROOT.parent / "NOESIS Channel" / "tools"
sys.path.insert(0, str(NOESIS_TOOLS))

from googleapiclient.http import MediaFileUpload  # type: ignore  # noqa: E402
from noesis_cli import channel_cfg, data_api, verify_channel  # type: ignore  # noqa: E402


CHANNEL = "de"
PLAYLIST_TITLE = "Modelle des Geistes · Schlafparalyse"
PLAYLIST_DESCRIPTION = (
    "Drei Perspektiven auf Schlafparalyse: Körper und REM-Atonie, kulturelle "
    "Deutungen von Salem bis zum Nachtmahr und die Internetgeschichte von "
    "Shadow People und Hat Man."
)
CATEGORY_EDUCATION = "27"
STATE_FILE = ROOT / "06_PRODUCTION" / "SCHLAFPARALYSE_YOUTUBE_PUBLISH_STATE.json"

EPISODES = {
    "EP06": {
        "directory": "EP06_SCHLAFPARALYSE_V4",
        "publish_at": "2026-08-30T18:00:00+02:00",
    },
    "EP07": {
        "directory": "EP07_SCHLAFPARALYSE_V4",
        "publish_at": "2026-09-03T18:00:00+02:00",
    },
    "EP08": {
        "directory": "EP08_SCHLAFPARALYSE_V4",
        "publish_at": "2026-09-06T18:00:00+02:00",
    },
}


def die(message: str) -> None:
    raise SystemExit(message)


def load_state() -> dict:
    if STATE_FILE.is_file():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {"channel": CHANNEL, "playlist_id": None, "episodes": {}}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def fenced_block(text: str, heading: str) -> str:
    try:
        section = text.split(heading, 1)[1]
        return section.split("```", 2)[1].strip("\n")
    except IndexError as exc:
        die(f"Metadatenblock fehlt: {heading}")
        raise exc


def files_for(ep: str, cfg: dict) -> dict:
    prod = ROOT / "06_PRODUCTION" / cfg["directory"]
    return {
        "video": prod / "render" / "final" / f"{cfg['directory']}_FINAL.mp4",
        "thumbnail": prod / "upload" / f"{ep}_THUMBNAIL_1280x720.jpg",
        "captions": prod / "render" / "subtitles" / f"{ep}_de.srt",
        "metadata": prod / "upload" / f"{ep}_YOUTUBE_METADATA.md",
    }


def read_metadata(ep: str, cfg: dict) -> dict:
    paths = files_for(ep, cfg)
    text = paths["metadata"].read_text(encoding="utf-8")
    tags = [tag.strip() for tag in fenced_block(text, "## Tags").split(",")]
    return {
        "title": fenced_block(text, "## Titel").splitlines()[0].strip(),
        "description": fenced_block(text, "## Beschreibung"),
        "tags": [tag for tag in tags if tag],
    }


def parse_timestamp(value: str) -> dt.datetime:
    stamp = dt.datetime.fromisoformat(value)
    if stamp.tzinfo is None:
        die(f"Termin braucht Zeitzone: {value}")
    return stamp


def caption_cues(path: Path) -> int:
    return len(re.findall(r"^\d+$", path.read_text(encoding="utf-8"), re.MULTILINE))


def preflight() -> dict[str, dict]:
    prepared: dict[str, dict] = {}
    now = dt.datetime.now(dt.timezone.utc)
    previous = now
    problems: list[str] = []

    for ep, cfg in EPISODES.items():
        paths = files_for(ep, cfg)
        for label, path in paths.items():
            if not path.is_file():
                problems.append(f"{ep}: {label} fehlt: {path}")
        if any(not path.is_file() for path in paths.values()):
            continue

        meta = read_metadata(ep, cfg)
        stamp = parse_timestamp(cfg["publish_at"])
        if stamp.astimezone(dt.timezone.utc) <= now:
            problems.append(f"{ep}: Termin liegt nicht in der Zukunft")
        if stamp <= previous:
            problems.append(f"{ep}: Terminreihenfolge ist nicht aufsteigend")
        previous = stamp
        if len(meta["title"]) > 100:
            problems.append(f"{ep}: Titel hat {len(meta['title'])} Zeichen")
        if len(meta["description"]) > 5000:
            problems.append(f"{ep}: Beschreibung hat {len(meta['description'])} Zeichen")
        tag_chars = sum(len(tag) for tag in meta["tags"]) + max(0, len(meta["tags"]) - 1)
        if tag_chars > 500:
            problems.append(f"{ep}: Tags haben {tag_chars} Zeichen")
        if paths["thumbnail"].stat().st_size > 2 * 1024 * 1024:
            problems.append(f"{ep}: Thumbnail ist groesser als 2 MB")
        cues = caption_cues(paths["captions"])
        if cues < 100:
            problems.append(f"{ep}: nur {cues} Untertitel-Cues")

        prepared[ep] = {"cfg": cfg, "paths": paths, "meta": meta, "cues": cues}

    if problems:
        print("Preflight fehlgeschlagen:")
        for problem in problems:
            print(f"  - {problem}")
        raise SystemExit(1)
    return prepared


def channel_uploads(yt) -> list[dict]:
    channel_id = channel_cfg(CHANNEL)["id"]
    channel = yt.channels().list(part="contentDetails", id=channel_id).execute()
    uploads_id = channel["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    ids: list[str] = []
    page = None
    while True:
        response = yt.playlistItems().list(
            part="contentDetails", playlistId=uploads_id, maxResults=50, pageToken=page
        ).execute()
        ids.extend(item["contentDetails"]["videoId"] for item in response.get("items", []))
        page = response.get("nextPageToken")
        if not page:
            break
    result: list[dict] = []
    for offset in range(0, len(ids), 50):
        response = yt.videos().list(
            part="snippet,status,processingDetails", id=",".join(ids[offset : offset + 50])
        ).execute()
        result.extend(response.get("items", []))
    return result


def check_remote_conflicts(uploads: list[dict], prepared: dict[str, dict], state: dict) -> None:
    known_ids = {
        info.get("video_id") for info in state.get("episodes", {}).values() if info.get("video_id")
    }
    title_to_id = {item["snippet"].get("title"): item["id"] for item in uploads}
    for ep, item in prepared.items():
        duplicate = title_to_id.get(item["meta"]["title"])
        if duplicate and duplicate not in known_ids:
            die(f"Schutzabbruch: Titel existiert bereits auf dem Kanal: {duplicate} ({ep})")

    planned = [
        parse_timestamp(item["status"]["publishAt"])
        for item in uploads
        if item.get("status", {}).get("publishAt") and item["id"] not in known_ids
    ]
    for ep, item in prepared.items():
        target = parse_timestamp(item["cfg"]["publish_at"])
        for existing in planned:
            if abs((target - existing).total_seconds()) < 6 * 3600:
                die(
                    f"Schutzabbruch: {ep} liegt weniger als sechs Stunden von einem "
                    f"bestehenden Termin ({existing.isoformat()}) entfernt"
                )


def list_playlists(yt) -> list[dict]:
    result: list[dict] = []
    page = None
    while True:
        response = yt.playlists().list(
            part="snippet,status", mine=True, maxResults=50, pageToken=page
        ).execute()
        result.extend(response.get("items", []))
        page = response.get("nextPageToken")
        if not page:
            break
    return result


def ensure_playlist(yt, state: dict) -> str:
    if state.get("playlist_id"):
        return state["playlist_id"]
    existing = next(
        (item for item in list_playlists(yt) if item["snippet"]["title"] == PLAYLIST_TITLE),
        None,
    )
    if existing:
        playlist_id = existing["id"]
    else:
        response = yt.playlists().insert(
            part="snippet,status",
            body={
                "snippet": {"title": PLAYLIST_TITLE, "description": PLAYLIST_DESCRIPTION},
                "status": {"privacyStatus": "public"},
            },
        ).execute()
        playlist_id = response["id"]
        print(f"Playlist angelegt: {playlist_id}")
    state["playlist_id"] = playlist_id
    save_state(state)
    return playlist_id


def with_series_navigation(
    description: str,
    playlist_id: str,
    previous_id: str | None = None,
    next_id: str | None = None,
) -> str:
    lines = ["SERIE SCHLAFPARALYSE"]
    lines.append(f"Alle Folgen: https://www.youtube.com/playlist?list={playlist_id}")
    if previous_id:
        lines.append(f"Vorherige Folge: https://youtu.be/{previous_id}")
    if next_id:
        lines.append(f"Nächste Folge: https://youtu.be/{next_id}")
    navigation = "\n".join(lines)
    marker = "\n\nKAPITEL\n"
    if marker in description:
        return description.replace(marker, f"\n\n{navigation}{marker}", 1)
    return f"{description}\n\n{navigation}"


def upload_video(yt, ep: str, item: dict, playlist_id: str) -> str:
    meta = item["meta"]
    cfg = item["cfg"]
    description = with_series_navigation(meta["description"], playlist_id)
    body = {
        "snippet": {
            "title": meta["title"],
            "description": description,
            "tags": meta["tags"],
            "categoryId": CATEGORY_EDUCATION,
            "defaultLanguage": "de",
            "defaultAudioLanguage": "de",
        },
        "status": {
            "privacyStatus": "private",
            "publishAt": cfg["publish_at"],
            "embeddable": True,
            "license": "youtube",
            "publicStatsViewable": True,
            "selfDeclaredMadeForKids": False,
            "containsSyntheticMedia": True,
        },
    }
    media = MediaFileUpload(
        str(item["paths"]["video"]),
        mimetype="video/mp4",
        chunksize=8 * 1024 * 1024,
        resumable=True,
    )
    request = yt.videos().insert(
        part="snippet,status", body=body, media_body=media, notifySubscribers=True
    )
    response = None
    retries = 0
    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                print(f"{ep} Upload {status.progress() * 100:5.1f}%", flush=True)
        except Exception as exc:  # noqa: BLE001
            retries += 1
            if retries > 6:
                raise
            delay = min(2**retries, 32)
            print(f"{ep} temporaerer Fehler, neuer Versuch in {delay}s: {str(exc)[:120]}")
            time.sleep(delay)
    print(f"{ep} Upload 100.0%: {response['id']}")
    return response["id"]


def retry(label: str, operation, attempts: int = 8):
    for number in range(1, attempts + 1):
        try:
            return operation()
        except Exception as exc:  # noqa: BLE001
            if number == attempts:
                raise
            delay = min(5 * number, 30)
            print(f"{label}: Versuch {number} fehlgeschlagen, erneut in {delay}s: {str(exc)[:120]}")
            time.sleep(delay)


def set_thumbnail(yt, video_id: str, path: Path) -> None:
    retry(
        "Thumbnail",
        lambda: yt.thumbnails()
        .set(videoId=video_id, media_body=MediaFileUpload(str(path), mimetype="image/jpeg"))
        .execute(),
    )


def set_captions(yt, video_id: str, path: Path) -> str:
    response = retry(
        "Untertitel",
        lambda: yt.captions()
        .insert(
            part="snippet",
            body={
                "snippet": {
                    "videoId": video_id,
                    "language": "de",
                    "name": "Deutsch",
                    "isDraft": False,
                }
            },
            media_body=MediaFileUpload(str(path), mimetype="application/x-subrip"),
        )
        .execute(),
    )
    return response["id"]


def playlist_video_ids(yt, playlist_id: str) -> list[str]:
    result: list[str] = []
    page = None
    while True:
        response = yt.playlistItems().list(
            part="contentDetails", playlistId=playlist_id, maxResults=50, pageToken=page
        ).execute()
        result.extend(item["contentDetails"]["videoId"] for item in response.get("items", []))
        page = response.get("nextPageToken")
        if not page:
            break
    return result


def add_to_playlist(yt, playlist_id: str, video_id: str) -> None:
    if video_id in playlist_video_ids(yt, playlist_id):
        return
    yt.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {"kind": "youtube#video", "videoId": video_id},
            }
        },
    ).execute()


def update_navigation(yt, video_id: str, playlist_id: str, previous_id, next_id) -> None:
    response = yt.videos().list(part="snippet", id=video_id).execute()
    snippet = response["items"][0]["snippet"]
    description = re.sub(
        r"\n\nSERIE SCHLAFPARALYSE\n.*?(?=\n\nKAPITEL\n)",
        "",
        snippet.get("description", ""),
        flags=re.DOTALL,
    )
    snippet["description"] = with_series_navigation(
        description, playlist_id, previous_id=previous_id, next_id=next_id
    )
    yt.videos().update(
        part="snippet", body={"id": video_id, "snippet": snippet}
    ).execute()


def verify(yt, state: dict, prepared: dict[str, dict]) -> dict:
    result: dict[str, dict] = {}
    for ep, item in prepared.items():
        video_id = state["episodes"][ep]["video_id"]
        response = yt.videos().list(
            part="snippet,status,processingDetails", id=video_id
        ).execute()
        if not response.get("items"):
            die(f"{ep}: Video nach Upload nicht per API auffindbar")
        remote = response["items"][0]
        captions = yt.captions().list(part="snippet", videoId=video_id).execute()
        caption_tracks = [
            {
                "id": caption["id"],
                "language": caption["snippet"].get("language"),
                "name": caption["snippet"].get("name"),
                "track_kind": caption["snippet"].get("trackKind"),
                "status": caption["snippet"].get("status"),
                "is_draft": caption["snippet"].get("isDraft"),
            }
            for caption in captions.get("items", [])
        ]
        result[ep] = {
            "video_id": video_id,
            "url": f"https://youtu.be/{video_id}",
            "title": remote["snippet"].get("title"),
            "privacy": remote["status"].get("privacyStatus"),
            "publish_at": remote["status"].get("publishAt"),
            "synthetic_media": remote["status"].get("containsSyntheticMedia"),
            "processing": remote.get("processingDetails", {}).get("processingStatus"),
            "caption_tracks": caption_tracks,
            "thumbnail_maxres": "maxres" in remote["snippet"].get("thumbnails", {}),
            "local_cues": item["cues"],
        }
    return result


def show_plan(prepared: dict[str, dict]) -> None:
    print(f"Kanal: {channel_cfg(CHANNEL)['label']} ({channel_cfg(CHANNEL)['id']})")
    print(f"Playlist: {PLAYLIST_TITLE}")
    for ep, item in prepared.items():
        print(
            f"{ep}: {item['cfg']['publish_at']} | {item['meta']['title']} | "
            f"{item['paths']['video'].stat().st_size / 1024 / 1024:.1f} MB | "
            f"{item['cues']} SRT-Cues | {len(item['meta']['tags'])} Tags"
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()

    prepared = preflight()
    show_plan(prepared)
    if not args.execute:
        print("\nTrockenlauf: keine API-Schreiboperation ausgeführt.")
        return 0

    yt = data_api(CHANNEL)
    identity = verify_channel(CHANNEL, yt)
    print(f"API-Kanalbindung bestätigt: {identity['title']} ({identity['id']})")
    state = load_state()
    uploads = channel_uploads(yt)
    check_remote_conflicts(uploads, prepared, state)
    playlist_id = ensure_playlist(yt, state)

    for ep, item in prepared.items():
        episode_state = state.setdefault("episodes", {}).setdefault(ep, {})
        video_id = episode_state.get("video_id")
        if not video_id:
            video_id = upload_video(yt, ep, item, playlist_id)
            episode_state.update(
                {
                    "video_id": video_id,
                    "publish_at": item["cfg"]["publish_at"],
                    "title": item["meta"]["title"],
                }
            )
            save_state(state)
        else:
            print(f"{ep}: vorhandenen Upload aus Statusdatei verwenden: {video_id}")

        if not episode_state.get("thumbnail_set"):
            set_thumbnail(yt, video_id, item["paths"]["thumbnail"])
            episode_state["thumbnail_set"] = True
            save_state(state)
            print(f"{ep}: Thumbnail gesetzt")
        if not episode_state.get("caption_id"):
            episode_state["caption_id"] = set_captions(
                yt, video_id, item["paths"]["captions"]
            )
            save_state(state)
            print(f"{ep}: deutsche Untertitel hochgeladen")
        add_to_playlist(yt, playlist_id, video_id)
        episode_state["playlist_added"] = True
        save_state(state)
        print(f"{ep}: Playlist-Zuordnung bestätigt")

    ids = {ep: state["episodes"][ep]["video_id"] for ep in EPISODES}
    order = list(EPISODES)
    for index, ep in enumerate(order):
        previous_id = ids[order[index - 1]] if index > 0 else None
        next_id = ids[order[index + 1]] if index + 1 < len(order) else None
        update_navigation(yt, ids[ep], playlist_id, previous_id, next_id)
        state["episodes"][ep]["navigation_updated"] = True
        save_state(state)
        print(f"{ep}: Serienlinks in Beschreibung gesetzt")

    audit = verify(yt, state, prepared)
    state["verification"] = audit
    state["verified_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    save_state(state)
    print("\nAPI-Verifikation:")
    print(json.dumps(audit, ensure_ascii=False, indent=2))
    print(f"Statusdatei: {STATE_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
