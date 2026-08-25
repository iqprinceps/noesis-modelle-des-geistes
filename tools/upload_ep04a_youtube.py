#!/usr/bin/env python3
"""EP04A auf YouTube hochladen, terminieren, Thumbnail und Untertitel setzen.

Voraussetzungen (einmalig):

    pip install google-api-python-client google-auth-oauthlib

    Google Cloud Console -> Projekt -> "YouTube Data API v3" aktivieren
    -> OAuth-Client (Anwendungstyp "Desktop") anlegen
    -> client_secret.json herunterladen und den Pfad unten setzen bzw.
       per --client-secret uebergeben.

Beim ersten Lauf oeffnet sich der Google-Anmeldedialog im Browser.  Die
Freigabe erteilt der Kanalinhaber selbst; danach liegt das Token lokal in
token_youtube.json und der Lauf braucht keine Anmeldung mehr.

    python tools/upload_ep04a_youtube.py --dry-run     # nur pruefen
    python tools/upload_ep04a_youtube.py               # wirklich hochladen

Hinweis zur Terminierung: YouTube laesst "publishAt" nur zu, wenn der Status
beim Upload "private" ist.  Genau so macht es dieses Skript.  Frisch angelegte
API-Projekte stehen ausserdem im Pruefstatus "unverified" -- solche Uploads
bleiben dauerhaft privat und lassen sich nicht terminieren, bis die App
verifiziert ist.  Das Skript prueft das nach dem Upload und sagt es deutlich.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RENDER = ROOT / "06_PRODUCTION" / "JUNG_SERIES_V1" / "RENDER_EP04A"

VIDEO = RENDER / "final" / "EP04A_JUNG_KUNDALINI_FINAL_V3.mp4"
THUMB = RENDER / "thumbnail" / "EP04A_THUMB_B_unten.jpg"
CAPTIONS = RENDER / "subtitles" / "EP04A_de.srt"
METADATA = RENDER / "publish" / "EP04A_YOUTUBE_METADATA.md"

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]

TITLE = "Wovor C. G. Jung warnte: Kundalini und die schwarze Schlange"

TAGS = [
    "C. G. Jung", "Carl Gustav Jung", "Kundalini", "Chakren", "Tiefenpsychologie",
    "Analytische Psychologie", "Das Rote Buch", "Aktive Imagination", "Philemon",
    "The Serpent Power", "John Woodroffe", "Arthur Avalon", "Wolfgang Pauli",
    "Ideengeschichte", "Psychologiegeschichte", "Zürich 1932", "Modelle des Geistes",
]

CATEGORY_EDUCATION = "27"

# Erster Kommentar.  Nimmt die Einordnung vorweg, die sonst als erste Rueckfrage
# kommt, und stellt die binaere Frage aus der Videomitte noch einmal -- das ist
# der Teil, der Antworten erzeugt.
FIRST_COMMENT = """Kurz zur Einordnung, weil das erfahrungsgemäß die erste Rückfrage ist:
Jungs schwarze Schlange von 1913 ist nirgends als Kundalini belegt. Ich erzähle sie als \
Parallele, nicht als Beweis — Jung selbst hat sich da nie festgelegt. Genauso ist die \
Flutvision keine Vorhersage des Krieges, sondern Jungs eigene spätere Umdeutung.

Und die Frage aus der Mitte bleibt hier offen: Ist so eine Karte für dich eher eine \
Karte oder ein Spiegel? Ein Wort reicht.

Alle Bildquellen und Lizenzen stehen in der Beschreibung. Nächste Folge: Jung und Pauli.\
"""


def description() -> str:
    """Beschreibungstext aus dem Metadatendokument ziehen (eine Quelle der Wahrheit)."""
    text = METADATA.read_text(encoding="utf-8")
    marker = "## Beschreibung"
    body = text.split(marker, 1)[1]
    block = body.split("```", 2)[1]
    return block.strip("\n")


def publish_at(when: str | None) -> str:
    """RFC-3339-Zeitpunkt in UTC.  Ohne Angabe: morgen 17:00 Europe/Berlin."""
    if when:
        stamp = dt.datetime.fromisoformat(when)
    else:
        try:
            from zoneinfo import ZoneInfo
            berlin = ZoneInfo("Europe/Berlin")
        except Exception:
            sys.exit("zoneinfo fehlt -- Zeitpunkt bitte per --publish-at explizit angeben.")
        tomorrow = dt.datetime.now(berlin).date() + dt.timedelta(days=1)
        stamp = dt.datetime.combine(tomorrow, dt.time(17, 0), tzinfo=berlin)
    if stamp.tzinfo is None:
        sys.exit("Zeitpunkt braucht eine Zeitzone, z. B. 2026-08-26T17:00:00+02:00")
    if stamp <= dt.datetime.now(dt.timezone.utc):
        sys.exit(f"Zeitpunkt liegt in der Vergangenheit: {stamp.isoformat()}")
    return stamp.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def preflight(when: str) -> None:
    problems = []
    for path, limit, label in (
        (VIDEO, None, "Video"),
        (THUMB, 2 * 1024 * 1024, "Thumbnail"),
        (CAPTIONS, None, "Untertitel"),
        (METADATA, None, "Metadaten"),
    ):
        if not path.is_file():
            problems.append(f"fehlt: {label} -> {path}")
        elif limit and path.stat().st_size > limit:
            problems.append(f"{label} zu gross: {path.stat().st_size/1024/1024:.1f} MB > 2 MB")
    if len(TITLE) > 100:
        problems.append(f"Titel {len(TITLE)} Zeichen (max 100)")
    body = description()
    if len(body) > 5000:
        problems.append(f"Beschreibung {len(body)} Zeichen (max 5000)")
    if sum(len(t) for t in TAGS) + len(TAGS) > 500:
        problems.append("Tags ueberschreiten 500 Zeichen")

    print(f"Video        {VIDEO.name}  {VIDEO.stat().st_size/1024/1024:.0f} MB"
          if VIDEO.is_file() else "Video        FEHLT")
    print(f"Thumbnail    {THUMB.name}  {THUMB.stat().st_size/1024:.0f} KB"
          if THUMB.is_file() else "Thumbnail    FEHLT")
    print(f"Untertitel   {CAPTIONS.name}" if CAPTIONS.is_file() else "Untertitel   FEHLT")
    print(f"Titel        {len(TITLE)} Zeichen")
    print(f"Beschreibung {len(body)} Zeichen")
    print(f"Tags         {len(TAGS)}")
    print(f"Veroeffentlichung {when} UTC")
    if problems:
        print("\nPruefung fehlgeschlagen:")
        for p in problems:
            print("  -", p)
        sys.exit(1)
    print("Pruefung: in Ordnung")


def service(client_secret: Path):
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError:
        sys.exit("Fehlende Pakete. Bitte:\n"
                 "  pip install google-api-python-client google-auth-oauthlib")
    token = ROOT / "token_youtube.json"
    creds = None
    if token.is_file():
        creds = Credentials.from_authorized_user_file(str(token), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not client_secret.is_file():
                sys.exit(f"client_secret.json nicht gefunden: {client_secret}\n"
                         "In der Google Cloud Console anlegen (OAuth-Client, Typ Desktop).")
            creds = InstalledAppFlow.from_client_secrets_file(
                str(client_secret), SCOPES).run_local_server(port=0)
        token.write_text(creds.to_json(), encoding="utf-8")
        print(f"Token gespeichert: {token}")
    from googleapiclient.discovery import build as _build
    return _build("youtube", "v3", credentials=creds)


def upload(yt, when: str) -> str:
    from googleapiclient.http import MediaFileUpload
    body = {
        "snippet": {
            "title": TITLE,
            "description": description(),
            "tags": TAGS,
            "categoryId": CATEGORY_EDUCATION,
            "defaultLanguage": "de",
            "defaultAudioLanguage": "de",
        },
        "status": {
            "privacyStatus": "private",      # Pflicht, damit publishAt greift
            "publishAt": when,
            "selfDeclaredMadeForKids": False,
            "containsSyntheticMedia": True,  # KI-generierte realistische Szenen
        },
    }
    media = MediaFileUpload(str(VIDEO), chunksize=8 * 1024 * 1024, resumable=True,
                            mimetype="video/mp4")
    request = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  Upload {int(status.progress() * 100):3d} %", end="\r", flush=True)
    print("  Upload 100 %")
    return response["id"]


def post_first_comment(yt, video_id: str) -> None:
    """Erstkommentar setzen.

    Erst nach der Veroeffentlichung sinnvoll: auf einem privaten oder
    terminierten Video weist die API den Kommentar ab bzw. er bleibt unsichtbar.
    Anpinnen kann die YouTube Data API nicht -- das geht nur in YouTube Studio.
    """
    yt.commentThreads().insert(
        part="snippet",
        body={"snippet": {
            "videoId": video_id,
            "topLevelComment": {"snippet": {"textOriginal": FIRST_COMMENT}},
        }},
    ).execute()
    print("Erstkommentar gesetzt.")
    print("Anpinnen bitte in Studio -- dafuer gibt es keinen API-Aufruf:")
    print(f"  https://studio.youtube.com/video/{video_id}/comments")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="nur pruefen, nichts senden")
    ap.add_argument("--publish-at", help="z. B. 2026-08-26T17:00:00+02:00")
    ap.add_argument("--client-secret", default=str(ROOT / "client_secret.json"))
    ap.add_argument("--comment-only", metavar="VIDEO_ID",
                    help="nur den Erstkommentar setzen, nach der Veroeffentlichung")
    args = ap.parse_args()

    if args.comment_only:
        yt = service(Path(args.client_secret))
        post_first_comment(yt, args.comment_only)
        return 0

    when = publish_at(args.publish_at)
    preflight(when)
    if args.dry_run:
        print(f"\nErstkommentar ({len(FIRST_COMMENT)} Zeichen), nach Veroeffentlichung:")
        print("  " + FIRST_COMMENT.replace("\n", "\n  "))
        print("\nTrockenlauf -- es wurde nichts hochgeladen.")
        return 0

    yt = service(Path(args.client_secret))
    print("\nLade Video hoch ...")
    video_id = upload(yt, when)
    url = f"https://youtu.be/{video_id}"
    print(f"Video-ID: {video_id}  ({url})")

    from googleapiclient.http import MediaFileUpload
    print("Setze Thumbnail ...")
    yt.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(str(THUMB))).execute()

    print("Lade Untertitel hoch ...")
    yt.captions().insert(
        part="snippet",
        body={"snippet": {"videoId": video_id, "language": "de",
                          "name": "Deutsch", "isDraft": False}},
        media_body=MediaFileUpload(str(CAPTIONS)),
    ).execute()

    info = yt.videos().list(part="status", id=video_id).execute()
    status = info["items"][0]["status"]
    print("\nStatus laut API:", json.dumps(status, ensure_ascii=False, indent=2))
    if not status.get("publishAt"):
        print("\nACHTUNG: Es ist kein Veroeffentlichungszeitpunkt gesetzt.")
        print("Das passiert bei API-Projekten im Pruefstatus 'unverified' -- solche")
        print("Uploads bleiben privat.  Termin dann in YouTube Studio setzen:")
        print(f"  https://studio.youtube.com/video/{video_id}/edit")
    else:
        print(f"\nTerminiert auf {status['publishAt']}.")

    print("\nNoch offen, beides erst nach der Veroeffentlichung moeglich:")
    print(f"  python tools/upload_ep04a_youtube.py --comment-only {video_id}")
    print(f"  Kommentar anpinnen: https://studio.youtube.com/video/{video_id}/comments")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
