#!/usr/bin/env python3
"""Setzt den vorbereiteten Kommentar unter jede Folge, sobald sie oeffentlich ist.

Der angepinnte Kommentar ist am ersten Abend der staerkste Kommentartreiber.
Er laesst sich aber erst setzen, wenn das Video oeffentlich ist — vorher nimmt
YouTube keinen Kommentar an. Genau diese Luecke schliesst dieses Werkzeug:
es laeuft regelmaessig, sieht nach, welche Folge inzwischen oeffentlich ist,
und setzt den Text.

Der Text steht nicht hier, sondern in der METADATA.md der jeweiligen Folge,
unter der Ueberschrift "Angepinnter Kommentar". Eine Textquelle, wie ueberall
sonst in diesem Projekt.

Was das Werkzeug NICHT tut:

* Es pinnt nicht an. Die YouTube Data API hat dafuer keinen Endpunkt; das
  bleibt ein Klick im Studio.
* Es kommentiert nie zweimal. Vor jedem Schreiben wird geprueft, ob der Kanal
  unter diesem Video schon einen Kommentar stehen hat.
* Es schreibt nichts unter fremde Videos. Die Kanal-ID wird gegengeprueft.

    python tools/spg_kommentar.py pruefen      # nur zeigen, nichts schreiben
    python tools/spg_kommentar.py setzen       # tatsaechlich setzen
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROD = ROOT / "06_PRODUCTION"
NOESIS = pathlib.Path(r"C:\Users\iQPrinceps\Documents\Codex\NOESIS Channel")
KANAL = "UCtKNr3gg66uT5GFcmbkItKA"
LOG = ROOT / "01_GLOBAL" / "kommentar_log.jsonl"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def api():
    sys.path.insert(0, str(NOESIS / "tools"))
    from noesis_cli import data_api  # type: ignore
    return data_api("de")


def kommentartext(ordner: pathlib.Path) -> str | None:
    """Den Abschnitt 'Angepinnter Kommentar' aus der METADATA.md holen."""
    md = ordner / "METADATA.md"
    if not md.is_file():
        return None
    t = md.read_text(encoding="utf-8")
    m = re.search(r"##\s*Angepinnter Kommentar\s*\n+```(?:text)?\n(.*?)\n```",
                  t, re.S)
    if not m:
        return None
    return " ".join(m.group(1).split())


def aufgaben() -> list[dict]:
    """Alle Folgen mit Uploadvermerk und vorbereitetem Kommentar."""
    out = []
    for zustand in sorted(PROD.glob("*/upload/upload_state.json")):
        ordner = zustand.parent.parent
        text = kommentartext(ordner)
        if not text:
            continue
        d = json.loads(zustand.read_text(encoding="utf-8"))
        if d.get("channelId") != KANAL:
            continue
        for v in d.get("videos", []):
            if v.get("role") == "longform" and v.get("id"):
                out.append({"folge": ordner.name, "id": v["id"], "text": text})
    return out


def schon_kommentiert(client, video_id: str) -> bool:
    r = client.commentThreads().list(part="snippet", videoId=video_id,
                                     maxResults=100, textFormat="plainText").execute()
    for th in r.get("items", []):
        if th["snippet"]["topLevelComment"]["snippet"].get(
                "authorChannelId", {}).get("value") == KANAL:
            return True
    return False


def notiz(eintrag: dict) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    eintrag["zeit"] = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(eintrag, ensure_ascii=False) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("befehl", choices=("pruefen", "setzen"))
    args = ap.parse_args()

    liste = aufgaben()
    if not liste:
        print("Keine Folge mit vorbereitetem Kommentar gefunden.")
        return

    client = api()
    ids = ",".join(a["id"] for a in liste)
    zustand = {v["id"]: v for v in client.videos().list(
        part="snippet,status", id=ids).execute()["items"]}

    for a in liste:
        v = zustand.get(a["id"])
        if not v:
            print(f"  {a['folge']:20s} {a['id']}  nicht gefunden")
            continue
        if v["snippet"]["channelId"] != KANAL:
            print(f"  {a['folge']:20s} {a['id']}  FREMDER KANAL — uebersprungen")
            continue
        if v["status"]["privacyStatus"] != "public":
            print(f"  {a['folge']:20s} {a['id']}  noch nicht oeffentlich "
                  f"({v['status']['privacyStatus']})")
            continue
        if schon_kommentiert(client, a["id"]):
            print(f"  {a['folge']:20s} {a['id']}  Kommentar steht bereits")
            continue

        if args.befehl == "pruefen":
            print(f"  {a['folge']:20s} {a['id']}  WUERDE SETZEN: {a['text'][:60]}…")
            continue

        r = client.commentThreads().insert(part="snippet", body={"snippet": {
            "videoId": a["id"],
            "topLevelComment": {"snippet": {"textOriginal": a["text"]}}}}).execute()
        print(f"  {a['folge']:20s} {a['id']}  gesetzt ({r['id']})")
        notiz({"folge": a["folge"], "video": a["id"], "thread": r["id"],
               "text": a["text"]})
        print("     Anpinnen geht nur im Studio — die API kann das nicht.")


if __name__ == "__main__":
    main()
