#!/usr/bin/env python3
"""YouTube-Uploadpaket fuer EP06-EP08 zusammenstellen.

Aufbau folgt `06_PRODUCTION/JUNG_SERIES_V1/RENDER_EP04A/publish/EP04A_YOUTUBE_METADATA.md`.

Drei Teile werden **aus den Produktionsdaten abgeleitet**, nicht von Hand
getippt - genau dort entstehen sonst Fehler:

* **Kapitelmarken** aus dem Stem-Report: jeder Akt beginnt beim ersten Take,
  der ihm im Sync-Plan zugeordnet ist.
* **Bildquellen** aus den Lizenzdateien der Assets, die im Render-Manifest
  tatsaechlich vorkommen. Nicht verwendete Quellen werden nicht genannt, und
  attributionspflichtige Lizenzen (CC BY, CC BY-SA) stehen namentlich da.
* **Laufzeit, Dateigroesse, Untertitelzahl** aus den fertigen Dateien.

Titel, Beschreibungstext und Einordnung sind redaktionell und stehen in
EDITORIAL.

    python tools/build_schlafparalyse_upload_package.py EP06 EP08
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EPISODES = {
    "EP06": dict(
        dir="EP06_SCHLAFPARALYSE_V4",
        plan="VOICE_EP06/sync/EP06_VOICE_VISUAL_SYNC.csv",
        take_col="take_id", act_col="act",
        acts={"S1": "Jemand kommt ins Zimmer",
              "S2": "Die Old Hag kennt ihn schon",
              "S3": "Der Körper schläft weiter",
              "S4": "Drei Arten, wie die Nacht zurückschlägt",
              "S5": "Das Labor verschiebt den Schlaf",
              "S6": "Körper oder Besucher?",
              "S7": "Warum aus Lähmung eine Begegnung wird",
              "S8": "Was bleibt — und wer als Nächstes kommt"},
    ),
    "EP07": dict(
        dir="EP07_SCHLAFPARALYSE_V4",
        plan="EP07_VOICE_VISUAL_SYNC.csv",
        take_col="take_id", act_col="section",
        acts={"S1": "Salem, Mai 1692", "S2": "Füsslis Nachtmahr",
              "S3": "Viele Namen für dieselbe Nacht", "S4": "Wenn Kultur wahr wird",
              "S5": "Hufford hört zu", "S6": "Erfahrung und Erzählung",
              "S7": "Ägypten und Dänemark", "S8": "Wie ein Nachtgeist reist"},
    ),
    "EP08": dict(
        dir="EP08_SCHLAFPARALYSE_V4",
        plan="POST_PLAN/EP08_VOICE_VISUAL_SYNC_PLAN.csv",
        take_col="take_id", act_col="act",
        acts={"S1": "4.500 Nachrichten", "S2": "Der Schatten bekommt eine Form",
              "S3": "Aliens im Schlafzimmer", "S4": "Harvard streitet über Erinnerung",
              "S5": "Der Mann mit dem Hut", "S6": "Muster oder Meme?",
              "S7": "Das Netz zeigt mit", "S8": "Der Kreis"},
    ),
}

EDITORIAL = {
    "EP06": dict(
        title="Schlafparalyse: Warum du jemanden im Zimmer spürst",
        alternatives=[
            "Du bist wach. Dein Körper nicht. — Was bei Schlafparalyse passiert",
            "Wach und gelähmt: Was im Gehirn bei Schlafparalyse wirklich passiert",
        ],
        intro=(
            "Schlafparalyse kann sich anfühlen, als stünde wirklich jemand im Zimmer. "
            "Dezember 1963 wacht ein Student auf und kann sich nicht bewegen. Er hört "
            "Schritte, spürt Druck auf der Brust und ist überzeugt, dass jemand im Zimmer "
            "steht. Jahre später wird er als Forscher genau danach fragen — und feststellen, "
            "dass Menschen auf der ganzen Welt dasselbe schildern, auch dort, wo sie die "
            "Geschichte vorher nie gehört haben.\n\n"
            "Diese Folge zeigt, was währenddessen im Körper messbar ist: warum Bewegung "
            "blockiert bleibt, während das Bewusstsein schon zurück ist. Und sie bleibt bei "
            "der Frage stehen, die damit noch nicht beantwortet ist — warum aus einer "
            "Lähmung so oft eine Begegnung wird."
        ),
        einordnung=(
            "Die REM-Atonie erklärt die Bewegungsblockade. Warum daraus so häufig eine "
            "erlebte Anwesenheit wird, ist damit nicht erklärt — das Präsenzmodell in der "
            "Folge ist eine Hypothese, kein Beweis. Die Old Hag, Mara und Incubus sind "
            "kulturelle Deutungen der Erfahrung, keine belegten Wesen. Historische Szenen "
            "ohne Bildquelle sind als Rekonstruktion gestaltet; wissenschaftliche Bilder "
            "sind anschauliche Metaphern und keine Aufnahmen der genannten Studien."
        ),
        naechste="Salem 1692: Wie Schlafparalyse als Hexerei gedeutet wurde.",
        hashtags="#Schlafparalyse #Schlafforschung #OldHag #Bewusstsein #ModelleDesGeistes",
        tags=("Schlafparalyse, Sleep Paralysis, REM-Atonie, REM-Schlaf, Schlafforschung, "
              "Old Hag, David Hufford, Neufundland, Cheyne, Takeuchi, Intruder, Incubus, "
              "Vestibulär, Außerkörpererfahrung, Bewusstsein, Neurowissenschaft, "
              "Modelle des Geistes"),
    ),
    "EP07": dict(
        title="Salem 1692: Wie Schlafparalyse als Hexerei gedeutet wurde",
        alternatives=[
            "Wer sitzt auf deiner Brust? — Als Schlafparalyse zur Hexe wurde",
            "Salem 1692: Eine Nacht wird zur Anklage — Schlafparalyse II",
        ],
        intro=(
            "Schlafparalyse wurde 1692 in Salem nicht medizinisch, sondern als Hexerei "
            "gedeutet. Ein Mann berichtet, eine Frau sei durch das verschlossene "
            "Zimmer zu ihm gekommen und habe sich auf seine Brust gelegt. Er habe weder "
            "sprechen noch sich bewegen können. Seine Schilderung wird Teil einer Anklage "
            "wegen Hexerei.\n\n"
            "Diese Folge verfolgt, wie aus derselben körperlichen Erfahrung in "
            "verschiedenen Kulturen verschiedene Wesen wurden — und was passiert, wenn eine "
            "private Nacht vor Gericht zur öffentlichen Wahrheit wird."
        ),
        einordnung=(
            "Ähnliche Motive in verschiedenen Kulturen belegen keine gemeinsame Abstammung "
            "und kein reales Wesen. Historische Dokumente und Kunstwerke werden als "
            "Originalquellen gezeigt und niemals nachgebaut; Spielszenen sind als "
            "Rekonstruktion gestaltet. Wo für einen Beleg keine frei nutzbare Abbildung "
            "vorlag, nennt die Folge die Quelle in Textform statt ein Bild zu erfinden."
        ),
        naechste="Shadow People bei Schlafparalyse: Warum viele den Hat Man sehen.",
        hashtags="#Schlafparalyse #Salem #Hexenprozesse #Kulturgeschichte #ModelleDesGeistes",
        tags=("Schlafparalyse, Salem, Hexenprozesse, Bridget Bishop, Füssli, Nachtmahr, "
              "Mahr, Incubus, Kanashibari, Jinn, Old Hag, David Hufford, Kulturgeschichte, "
              "Volksglaube, Modelle des Geistes"),
    ),
    "EP08": dict(
        title="Shadow People bei Schlafparalyse: Warum viele den Hat Man sehen",
        alternatives=[
            "Der Mann mit dem Hut — wie das Internet einer Halluzination ein Gesicht gab",
            "Shadow People: Warum Tausende dieselbe Gestalt sehen — Schlafparalyse III",
        ],
        intro=(
            "Shadow People und der Hat Man gehören zu den bekanntesten Gestalten, von denen "
            "Menschen bei Schlafparalyse berichten. Am 12. April 2001 macht ein "
            "amerikanischer Nachtradiomoderator dunkle Gestalten zum Sendethema. Im Archiv "
            "der Sendung ist von mehr als 4.500 Reaktionen die "
            "Rede. Viele beschreiben dasselbe: eine große, schwarze Silhouette, kein Gesicht "
            "— und einen deutlichen Hutrand.\n\n"
            "Diese Folge fragt, wie ein Motiv entsteht, das so viele Menschen gleichzeitig "
            "erkennen: Was steuert der Körper bei, was die Erwartung, und was tut ein Netz, "
            "das Schilderungen innerhalb von Stunden zusammenführt."
        ),
        einordnung=(
            "Dass hohe Dosen Diphenhydramin ein anticholinerges Delirium mit Halluzinationen "
            "auslösen können, ist medizinisch dokumentiert. Eine klinisch belegte Verbindung "
            "zu einer bestimmten Gestalt gibt es nicht — die stammt aus Erfahrungsberichten "
            "im Netz und wird hier als kulturelles Motiv behandelt, nicht als Diagnose. "
            "Heidi Hollis wird als wichtige Popularisiererin genannt, nicht als Erfinderin "
            "des Begriffs. Die Forschung von Susan Clancy und Richard McNally widerlegt "
            "niemanden persönlich; sie fragt, wie Überzeugung entsteht. Für nicht frei "
            "nutzbare Belege zeigt die Folge Quellenkarten statt nachgebauter Screenshots."
        ),
        naechste="NOESIS — Modelle des Geistes.",
        hashtags="#Schlafparalyse #ShadowPeople #HatMan #Erinnerung #ModelleDesGeistes",
        tags=("Shadow People, Hat Man, Der Mann mit dem Hut, Schlafparalyse, Art Bell, "
              "Coast to Coast AM, John Mack, Susan Clancy, Richard McNally, False Memory, "
              "Erinnerung, Diphenhydramin, Internetkultur, Meme, Modelle des Geistes"),
    ),
}


def run(args: list[str]) -> str:
    return subprocess.run(args, capture_output=True, text=True).stdout.strip()


def hms(seconds: float) -> str:
    total = int(seconds)
    return f"{total // 60}:{total % 60:02d}"


def act_starts(ep: str) -> list[tuple[str, float]]:
    """Startzeit je Akt aus dem Stem-Report."""
    cfg = EPISODES[ep]
    prod = ROOT / "06_PRODUCTION" / cfg["dir"]
    report = json.loads((prod / "voice" / "master" / "stem_report.json")
                        .read_text(encoding="utf-8"))
    seen: dict[str, float] = {}
    for stem in report["stems"]:
        section = stem.get("section") or ""
        if section and section not in seen:
            seen[section] = float(stem["start"])
    return sorted(seen.items(), key=lambda kv: kv[1])


def source_of_derivatives(prod: Path) -> dict[str, str]:
    """Ableitung -> Quelldatei, aus den Manifesten der Derivatordner.

    Die Exportnamen der Ableitungen (SRC001_..., ORIG017_...) haben mit dem
    Dateinamen der Quelle nichts gemeinsam. Ohne diese Bruecke findet die
    Lizenzsuche nichts.
    """
    mapping: dict[str, str] = {}
    for manifest in prod.rglob("*MANIFEST.csv"):
        try:
            rows = list(csv.DictReader(manifest.open(encoding="utf-8-sig")))
        except Exception:
            continue
        for row in rows:
            name = row.get("filename")
            src = row.get("base_asset") or row.get("source_file")
            if name and src and src != "-":
                mapping[Path(name).stem.upper()] = Path(src).stem.upper()
    return mapping


def canonical(stem: str) -> str:
    """Dateistamm auf den Kern reduzieren.

    Die Lizenzdateien heissen `EP08_S01_1996_radio_studio_context_CC-BY-SA-4.0`,
    im Schnitt liegt dieselbe Quelle als `EP08_1996_radio_studio_context`. Ohne
    Normalisierung findet kein Vergleich etwas: das Aktpraefix `S01_` und das
    angehaengte Lizenzkuerzel stehen dazwischen.
    """
    s = stem.upper()
    s = re.sub(r"^(EP\d\d)_S\d\d[A-Z]?_", r"\1_", s)
    s = re.sub(r"_(CC0|PD|GFDL|CC-BY(-SA)?(-\d(\.\d)?)?(-[A-Z]{2}(-\d+(\.\d+)?)?)?)$",
               "", s)
    return s.strip("_")


def used_licences(ep: str) -> list[dict]:
    """Lizenzangaben der Quellen, die im Render-Manifest wirklich vorkommen."""
    cfg = EPISODES[ep]
    prod = ROOT / "06_PRODUCTION" / cfg["dir"]
    manifest = json.loads((prod / "render_manifest.json").read_text(encoding="utf-8"))
    derived = source_of_derivatives(prod)

    used_stems: set[str] = set()
    for value in manifest["assets"].values():
        for path in (value if isinstance(value, list) else [value]):
            stem = Path(path).stem.upper()
            used_stems.add(canonical(stem))
            # Ableitung auf ihre Quelle zurueckfuehren.
            if stem in derived:
                used_stems.add(canonical(derived[stem]))

    entries: list[dict] = []
    for lic in (ROOT / "SCHLAFPARALYSE_ASSETS_PHASE2").rglob("*.license.txt"):
        fields = {}
        for line in lic.read_text(encoding="utf-8").splitlines():
            if ":" in line:
                key, _, val = line.partition(":")
                fields[key.strip().lower()] = val.strip()
        source_stem = canonical(Path(lic.name.replace(".license.txt", "")).stem)
        hit = any(source_stem == u or source_stem in u or u in source_stem
                  for u in used_stems)
        if not hit:
            m = re.search(r"(ORIG\d+|SRC\d+)", source_stem)
            hit = bool(m and any(m.group(1) in u for u in used_stems))
        if hit and fields.get("license/status"):
            entries.append({
                "title": fields.get("title", source_stem),
                "licence": fields.get("license/status", ""),
                "credit": fields.get("credit", ""),
                "source": fields.get("source page", ""),
            })
    unique: dict[str, dict] = {}
    for e in entries:
        unique.setdefault(e["title"], e)
    return sorted(unique.values(), key=lambda e: e["title"])


def needs_attribution(licence: str) -> bool:
    low = licence.lower()
    return "cc by" in low or "attribution" in low


def build(ep: str) -> bool:
    cfg = EPISODES[ep]
    ed = EDITORIAL[ep]
    prod = ROOT / "06_PRODUCTION" / cfg["dir"]
    final = prod / "render" / "final" / f"{cfg['dir']}_FINAL.mp4"
    srt = prod / "render" / "subtitles" / f"{ep}_de.srt"
    thumb = prod / "upload" / f"{ep}_THUMBNAIL_1280x720.jpg"

    if not final.is_file():
        print(f"{ep}: kein fertiges Video - uebersprungen")
        return False

    duration = float(run(["ffprobe", "-v", "error", "-show_entries",
                          "format=duration", "-of", "csv=p=0", str(final)]) or 0)
    size_mb = final.stat().st_size / 1024 / 1024
    cues = len(re.findall(r"^\d+$", srt.read_text(encoding="utf-8"), re.M)) if srt.is_file() else 0

    lines: list[str] = []
    add = lines.append
    add(f"# {ep} — YouTube-Metadaten\n")
    add(f"**Datei:** `{final.relative_to(ROOT).as_posix()}` "
        f"({size_mb:.0f} MB, {hms(duration)}, 1920×1080p30)")
    add(f"**Thumbnail:** `{thumb.relative_to(ROOT).as_posix()}` (1280×720)"
        if thumb.is_file() else "**Thumbnail:** fehlt")
    add(f"**Untertitel:** `{srt.relative_to(ROOT).as_posix()}` ({cues} Cues, Deutsch)"
        if srt.is_file() else "**Untertitel:** fehlen")
    add("\n---\n")

    add("## Titel\n")
    add(f"**Primär** ({len(ed['title'])} Zeichen):\n")
    add("```")
    add(ed["title"])
    add("```\n")
    add("Alternativen:\n")
    add("```")
    for alt in ed["alternatives"]:
        add(alt)
    add("```\n")
    add("---\n")

    add("## Beschreibung\n")
    add("```")
    add(ed["intro"])
    add("")
    add("KAPITEL")
    # YouTube verlangt eine Marke bei 0:00. Der erste Akt beginnt praktisch
    # immer dort - dann braucht es keine zusaetzliche Zeile "Einstieg".
    chapters = act_starts(ep)
    if not chapters or chapters[0][1] > 1.0:
        add("0:00 Einstieg")
    for index, (section, start) in enumerate(chapters):
        label = cfg["acts"].get(section, section)
        add(f"{hms(0 if index == 0 else start)} {label}")
    add("")
    add("ZUR EINORDNUNG")
    add(ed["einordnung"])
    add("")

    licences = used_licences(ep)
    attribution = [e for e in licences if needs_attribution(e["licence"])]
    free = [e for e in licences if not needs_attribution(e["licence"])]
    if attribution:
        add("BILDQUELLEN UND LIZENZEN")
        for e in attribution:
            add(f"• {e['title']} — {e['credit'] or e['licence']}")
            if e["source"]:
                add(f"  {e['source'].replace('https://', '')}")
        add("")
    if free:
        add("Weitere Aufnahmen sind gemeinfrei oder CC0: "
            + ", ".join(e["title"] for e in free[:12])
            + ("." if len(free) <= 12 else " und weitere."))
        add("")
    add("NÄCHSTE FOLGE")
    add(ed["naechste"])
    add("")
    add(ed["hashtags"])
    add("```\n")
    add("---\n")

    add("## Tags\n")
    add("```")
    add(ed["tags"])
    add("```\n")
    add("---\n")

    add("## Einstellungen\n")
    add("| Feld | Wert |")
    add("|---|---|")
    add("| Sichtbarkeit | noch festzulegen |")
    add("| Kategorie | Bildung |")
    add("| Sprache Video | Deutsch |")
    add(f"| Sprache Untertitel | Deutsch (`{ep}_de.srt` hochladen) |")
    add("| Für Kinder | Nein |")
    add("| Altersbeschränkung | Keine |")
    add("| **Veränderte/synthetische Inhalte** | **Ja** — realistisch wirkende Szenen "
        "sind KI-generiert, ebenso die Sprecherstimme |")
    add("| Kommentare | An |")
    add("| Playlist | Modelle des Geistes · Schlafparalyse |")
    add("")
    add("> Die Angabe „veränderte oder synthetische Inhalte\" ist im Upload-Formular zu")
    add("> setzen. Die Folge nutzt eine synthetische Sprecherstimme und KI-generierte")
    add("> Rekonstruktionen; beides fällt unter die Kennzeichnungspflicht.")
    add("")
    add("---\n")
    add("## Hinweis zur Erzeugung\n")
    add("Kapitelmarken, Laufzeit, Untertitelzahl und die Liste der Bildquellen sind aus")
    add("den Produktionsdaten abgeleitet (`voice/master/stem_report.json`,")
    add("`render_manifest.json`, Lizenzdateien in `SCHLAFPARALYSE_ASSETS_PHASE2`).")
    add("Titel, Beschreibungstext und Einordnung sind redaktionell und stehen in")
    add("`tools/build_schlafparalyse_upload_package.py`.")

    out_dir = prod / "upload"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{ep}_YOUTUBE_METADATA.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{ep}: {hms(duration)}, {cues} Untertitel-Cues, "
          f"{len(attribution)} attributionspflichtige Quellen, {len(free)} freie")
    print(f"     -> {path.relative_to(ROOT)}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("episodes", nargs="*")
    args = parser.parse_args()
    for ep in args.episodes or list(EPISODES):
        if ep not in EPISODES:
            raise SystemExit(f"Unbekannte Episode: {ep}")
        build(ep)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
