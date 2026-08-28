#!/usr/bin/env python3
"""Sync-Plaene in Cue-Sheet plus Render-Manifest uebersetzen (EP06-EP08).

Der Renderer (`tools/noesis_render.py`) arbeitet mit zwei Eingaben:

* einem Cue-Sheet, dessen `anchor_text` per Forced Alignment im Sprechtext
  gefunden wird und so den Startzeitpunkt des Cues setzt, und
* `render_manifest.json`, das jedem `cue_id` einen Pfad **oder eine geordnete
  Liste von Pfaden** zuordnet. Eine Liste wird innerhalb des Cue-Fensters in
  einzelne Shots aufgeteilt.

Genau darauf passen die Sync-Plaene: ein Cue je Sprechertake, darin die
geordneten Shots dieses Takes. Das ergibt ein Timing pro Take statt pro Akt,
ohne dass fuer jeden einzelnen Shot ein eigener Textanker noetig waere.

    python tools/build_schlafparalyse_cue_sheets.py EP08
    python tools/build_schlafparalyse_cue_sheets.py           # alle drei
"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "PRODUCTION_SUMMARY"
PROD = ROOT / "06_PRODUCTION"

MEDIA_EXT = (".png", ".jpg", ".jpeg", ".webp", ".mp4", ".mov")

# Je Episode: Sync-Plan, Sprechtexte, Reinschrift und die Spaltennamen, unter
# denen dieser Plan Take, Akt und Asset fuehrt. Die drei Plaene sind historisch
# unterschiedlich gewachsen; die Zuordnung bleibt darum explizit.
EPISODES = {
    "EP06": {
        "dir": "EP06_SCHLAFPARALYSE_V4",
        "plan": "VOICE_EP06/sync/EP06_VOICE_VISUAL_SYNC.csv",
        "takes": "VOICE_EP06/source",
        "clean": "VOICE_EP06/EP06_VOICE_SCRIPT_CLEAN.txt",
        "take_col": "take_id", "act_col": "act", "asset_col": "asset_path_or_plan",
        "status_col": "asset_status", "ready": {"READY"},
    },
    "EP07": {
        "dir": "EP07_SCHLAFPARALYSE_V4",
        "plan": "EP07_VOICE_VISUAL_SYNC.csv",
        "takes": "VOICE_EP07/source",
        "clean": "VOICE_EP07/EP07_VOICE_SCRIPT_CLEAN.txt",
        "take_col": "take_id", "act_col": "section", "asset_col": "asset_path",
        "status_col": "asset_status", "ready": {"READY", "DERIVE_STATIC_FRAME"},
    },
    "EP08": {
        "dir": "EP08_SCHLAFPARALYSE_V4",
        "plan": "POST_PLAN/EP08_VOICE_VISUAL_SYNC_PLAN.csv",
        "takes": "VOICE_EP08/source",
        "clean": "VOICE_EP08/EP08_SPRECHTEXT_CLEAN.txt",
        "take_col": "take_id", "act_col": "act", "asset_col": "visual_asset",
        "status_col": "asset_status",
        "ready": {"READY", "READY_DERIVED_ORIGINAL", "READY_SEMANTIC_CUT",
                  "EDITORIAL_BUILD", "SOURCE_ACQUISITION", "GENERATION_REQUIRED"},
    },
}

# Kuratierte Zusatzshots.
#
# Der Renderer teilt ein Cue-Fenster gleichmaessig auf seine Assets auf. Wo ein
# Sprechertake im Plan zu wenige Shots hat, entstehen dadurch Standzeiten ueber
# der 9-Sekunden-Grenze des Bilddichte-Locks. Die Ergaenzungen stehen hier
# namentlich statt aus einem Restpool gezogen zu werden - jeder Shot muss zum
# Satz passen, den er bebildert.
#
# `position` ist der Index in der Shotliste des Takes.
FILLS: dict[str, list[tuple[int, str]]] = {
    # Episodenauftakt: der Plan startet mit 3,4 s pro Bild, der Lock verlangt
    # einen ersten Schnitt unter 2,5 s. Der vorhandene Hat-Man-Shot setzt einen
    # kurzen visuellen Promise-of-payoff, danach fuehren zwei schnelle Makros
    # in die Radioszene.
    "EP08_TAKE_001": [
        (0, "IMG017_HAT_MAN_FOOT_OF_BED"),
        (5, "SHOT04_INTERVIEW_TAPE_MACRO"),
    ],
    # Schlussabsatz: 25 s Text auf nur zwei Bildern (12,5 s je Bild). Der Take
    # nennt die Kette Gehirn - Erfahrung - Geschichte - Erwartung explizit;
    # die Ergaenzungen folgen genau dieser Reihenfolge.
    "EP08_TAKE_026": [
        (1, "IMG030_BRAIN_EXPERIENCE_STORY_EXPECTATION_BASE"),
        (2, "IMG029_THREE_EPISODE_MOTIF_TABLE"),
        (3, "EDIT023_GLOBAL_NODE_REVEAL"),
    ],
    # Abspanntake: zwei Saetze - Teaser auf die naechste Folge und die
    # Abschlussfrage - lagen auf einer einzigen Karte, gut zwoelf Sekunden.
    # Der als CTA-Grund gebaute Still traegt jetzt den Teasersatz; die Endcard
    # steht zuletzt und schliesst mit Frage und Handoff.
    "EP07_TAKE_026": [
        (0, "IMG060_WORD_LAYERS_CTA_BG"),
    ],
}

# Bilddichte-Lock: kein Standbild laenger als neun Sekunden.
MAX_STILL_SECONDS = 9.0

# Nicht beschaffbare Belege werden durch die Quellenkarten ersetzt.
#
# Nicht jeder fehlende Beleg bekommt eine eigene Karte. Ein Beleg, der im Text
# nur einmal behauptet wird, braucht auch nur eine Karte - sonst haeuft sich
# Fliesstext im Schnitt. Wo der Cue keine eigene Behauptung traegt, steht
# stattdessen ein Bild (siehe CUE_OVERRIDES).
SUBSTITUTES = {
    "SRC_MISSING_DPH_MEDICAL_SOURCE_FULL": "SRC053_DPH_MEDICAL_STATEMENT",
    "SRC_MISSING_ANON_HAT_FORUM": "SRC055_HAT_REPORTS_EVIDENCE_STATUS",
    # Fuer reine Verbreitungs-/Medienuebergaenge tragen vorhandene Bildfolgen
    # die Aussage besser als eine weitere Textkarte.
    "SRC_MISSING_WEB_ARCHIVE_RESULTS_FULL": "EDIT017_SEARCH_SEQUENCE",
    "SRC_MISSING_PERIOD_FORUM_CAPTURE": "SRC036_SHARP_FAX_MODEM_FULL",
    "SRC_MISSING_NIGHTMARE_LICENSED_KEYART": "SRC058_NIGHTMARE_BIBLIOGRAPHY",
    "SRC_MISSING_MCNALLY_CLANCY_PAPER_PAGE": "IMG015_SUGGESTIVE_INTERVIEW_BASE",
    "EDIT011_HARVARD_RESEARCH_TITLE": "SRC051_HARVARD_RESEARCH_TITLE",
}

# Feste Zuordnung einzelner Cues, die der Tokentabelle widerspricht.
#
# Nach dem ersten Durchlauf standen in EP08 zwischen 330 s und 490 s neun
# Textkarten, zwei davon unmittelbar hintereinander. Ursache war, dass jeder
# fehlende Beleg eine eigene Karte bekam und dieselben Karten zusaetzlich die
# EDIT-Sequenzen speisten. Diese Cues tragen keine eigene Behauptung und
# bekommen deshalb ein Bild.
CUE_OVERRIDES = {
    # Im EP06-Hook ersetzt ein leeres Schlafzimmer die fruehe Quellenkarte.
    # Die Karte bleibt im spaeteren Fogo-Kontext erhalten, wo die Einordnung
    # nicht mehr die Spannung der ersten Sekunden unterbricht.
    ("EP06", "PLANNED/ORIG024_1960S_DORM_CONTEXT.jpg"): "SHOT04_EMPTY_BEDROOM_SHADOWS",
    # Zwei Erklaerkarten direkt hintereinander bremsen den Laborabschnitt. Der
    # Ablauf bleibt auf CARD010 sichtbar; CARD003 faellt auf den unmittelbar
    # davor gezeigten Wecker zurueck und wird dadurch dedupliziert.
    ("EP06", "CARD003_TAKEUCHI_1992"): "IMG018_SLEEP_INTERRUPTION_CLOCK",
    # Vor der Endcard tragen Originalakte und Handoff-Bild die Salem-Bruecke
    # bereits. Eine zweite Textkarte waere nur ein vorgezogener Abspann.
    ("EP06", "CARD014_PRIVATE_NIGHT_PUBLIC_RECORD"): "SHOT08_DAWN_AFTER_PARALYSIS",

    # EP07: Quellenkarten nur dort zeigen, wo sie selbst eine neue Aussage
    # tragen. Wiederholte Werk-, Methoden- und Zitationskarten werden durch die
    # schon vorhandenen, semantisch passenden Bilder im selben Take ersetzt.
    ("EP07", "ORIG_ORIG_HUFFORD_PORTRAIT_LICENSED_portrait"): "IMG013_BODY_TO_STORY_FLOW_BASE",
    ("EP07", "ORIG_ORIG_HUFFORD_TERROR_BOOK_COVER_LICENSED_title_detail"): "IMG060_WORD_LAYERS_CTA_BG",
    ("EP07", "ORIG_ORIG_JALAL_HINTON_EGYPT_DENMARK_PAPER_title_authors"): "CARD004_AEGYPTEN_DAENEMARK",
    ("EP07", "ORIG_ORIG_JALAL_HINTON_EGYPT_DENMARK_PAPER_methods_detail"): "CARD004_AEGYPTEN_DAENEMARK",
    ("EP07", "ORIG_ORIG_EGYPT_SLEEP_PARALYSIS_SOURCE_source_detail"): "ORIG_ORIG_EGYPT_MAP_PD_full_map",
    ("EP07", "ORIG_ORIG_DENMARK_SLEEP_PARALYSIS_SOURCE_source_detail"): "ORIG_ORIG_DENMARK_MAP_PD_full_map",
    ("EP07", "ORIG_ORIG_JALAL_HINTON_EGYPT_DENMARK_PAPER_results_detail"): "SRC_EP07_REM_Polysomnography_30sec_rem_segment_detail",
    ("EP07", "ORIG_ORIG_JALAL_HINTON_EGYPT_DENMARK_PAPER_citation_block"): "IMG046_RAW_MATERIAL_TO_FORM",
    ("EP07", "ORIG_ORIG_HUFFORD_TERROR_BOOK_COVER_LICENSED_cover_return"): "IMG047_CULTURE_FEEDBACK_BRAID",
    # "medizinisch dokumentiert" - die Aussage steht schon auf SRC053 bei V080.
    # Hier genuegt ein klinischer Anker aus dem Originalbestand.
    ("EP08", "SRC_MISSING_DPH_MEDICAL_SOURCE_DETAIL"): "SRC030_EEG_CAP_DETAIL",
    # "Rodney Ascher" - Werk und Regie stehen auf der Karte bei V116.
    # Dieser Cue zeigt die Wirkung des Films, nicht noch einmal seinen Titel.
    ("EP08", "SRC_MISSING_NIGHTMARE_BIBLIOGRAPHY"): "IMG025_DOCUMENTARY_SCREENING_RECON",
    # "dramatische Bilder" - IMG025 steht bereits im Cue davor.
    ("EP08", "IMG025_DOCUMENTARY_SCREENING_RECON.png"): "IMG004_SHADOW_PERIPHERAL_GLIMPSE",

    # Drei der sechs EP06-Zusatzclips liessen sich nicht erzeugen: Veo meldete
    # ueber Stunden hinweg Dienstueberlastung (code 8), kein Inhaltsfilter.
    # EP06 hat mit CLIP001-005, 008 und 009 bereits sieben Clips; die drei
    # offenen Cues bekommen statt eines Clips den Still, der ohnehin als
    # Startframe des jeweiligen Clips vorgesehen war - also genau das Motiv,
    # das der Satz an dieser Stelle braucht.
    ("EP06", "PLANNED/CLIP006_THREE_FAMILIES.mp4"): "SHOT37_ERLEBNISFAMILIEN",
    # Nicht IMG040: das steht im selben Take bereits zwei Shots davor. Der
    # Satz nennt "Sensoren zeichnen Hirnaktivitaet und Muskeltonus auf" - dafuer
    # ist die echte CC0-EEG-Aufzeichnung der praezisere Beleg.
    ("EP06", "PLANNED/CLIP007_INTERRUPTION_CYCLE.mp4"): "ORIG020_EEG_62_CHANNEL_CC0",
    ("EP06", "PLANNED/CLIP010_SHADOW_COMPLETION.mp4"): "SHOT28_SCHATTEN_WIRD_SCHULTER",
    # CLIP009 wurde verworfen: die erzeugte Fassung zeigte eine erfundene
    # EKG-artige Kurve mit lesbaren Achsenzahlen - eine fabrizierte
    # Messaufzeichnung. Eine Neuerzeugung scheiterte an derselben
    # Dienstueberlastung.
    ("EP06", "PLANNED/CLIP009_REALNESS_CAUSE_SPLIT.mp4"): "IMG043_PRESENCE_BEFORE_IMAGE",
}

# Einzelne Wiederholungen nur an ihrem zweiten Einsatz ersetzen. Globale
# CUE_OVERRIDES waeren hier zu grob: dieselbe Quelle ist an ihrer ersten Stelle
# oft genau richtig, wirkt wenige Sekunden spaeter aber wie Recycling.
TAKE_ASSET_OVERRIDES = {
    # Im Schluss von EP08 lag dasselbe Kreislaufmotiv in TAKE 025 und TAKE 026
    # nur rund 24 Sekunden auseinander. TAKE 026 behaelt die explizite
    # Gehirn-Erfahrung-Geschichte-Erwartung-Grafik; TAKE 025 zeigt stattdessen
    # die Weitergabe von Deutungen ueber Bild und Forum. Das ist inhaltlich
    # genauer und verhindert einen sichtbaren Doppel-Einsatz im Finale.
    ("EP08", "EP08_TAKE_025", "IMG030_BRAIN_EXPERIENCE_STORY_EXPECTATION_BASE.png"):
        "IMG026_FORUM_TO_IMAGE_TO_EXPECTATION",
    # Fogo: Dorfansicht und Orts-Rekonstruktion standen in zwei benachbarten
    # Takes erneut. Der zweite Einsatz wird durch Feldarbeit und Archivkarte
    # ersetzt, ohne den Ortsbezug zu verlieren.
    ("EP06", "EP06_TAKE_004_FOGO_ISLAND",
     "EP06_Fogo_Island_Newfoundland_fishing_village_2002.jpg"):
        "IMG061_FOGO_FIELDWORK_INTERVIEW_RECON",
    ("EP06", "EP06_TAKE_004_FOGO_ISLAND",
     "IMG007_FOGO_PLACE_ANCHOR_RECON.png"): "SHOT35_FOGO_ARCHIVANKER",

    # Aegypten/Daenemark: keine Karten zweimal direkt hintereinander. Nach den
    # Interviewraeumen zeigen diese beiden Bilder die inhaltliche Pointe.
    ("EP07", "EP07_TAKE_019",
     "ORIG_ORIG_EGYPT_SLEEP_PARALYSIS_SOURCE_source_detail.png"):
        "IMG044_SAME_BODY_TWO_INTERPRETATIONS",
    ("EP07", "EP07_TAKE_019",
     "ORIG_ORIG_DENMARK_SLEEP_PARALYSIS_SOURCE_source_detail.png"):
        "IMG045_EXPECTATION_ENTERS_BODY",
    # Der historische Jinn-Ausschnitt ist nur 567x264 Pixel gross und wurde im
    # Vollbild sichtbar pixelig. Die Aussage des Takes ist die gemeinsame
    # koerperliche Grundlage; dieses vorhandene Motiv zeigt sie ohne eine
    # schlechte Quelle kuenstlich aufzublasen.
    ("EP07", "EP07_TAKE_008",
     "SRC_EP07_Jinn_from_Ali_manuscript_figure_detail.png"):
        "IMG061_ONE_BODY_THREE_STORIES",

    # EP08-Hook: Vollbild und Ausschnitt desselben Art-Bell-Fotos direkt
    # hintereinander werden durch ein eigenes Radiomotiv aufgeloest.
    ("EP08", "EP08_TAKE_001",
     "SRC002_ART_BELL_PORTRAIT_DETAIL.png"): "SHOT01_RADIO_MICROPHONE_MACRO",
    # Der Detailausschnitt des BBS-Screens folgt ebenfalls direkt auf seine
    # Vollansicht. Das Erinnerungsmotiv transportiert stattdessen, wie eine
    # gelesene Vorlage spaeter Teil des inneren Bildmaterials wird.
    ("EP08", "EP08_TAKE_005",
     "SRC012_BBS_SCREEN_DETAIL.png"): "IMG014_MEMORY_RECONSTRUCTION_LAYERS",
    # Der EEG-Ausschnitt stammt aus einer 289x423-Pixel-Vorlage. Fuer den
    # klinischen Kontext steht eine echte, deutlich hoeher aufgeloeste
    # Polysomnographie-Aufnahme im lizenzierten Bestand bereit.
    ("EP08", "EP08_TAKE_016",
     "SRC_MISSING_DPH_MEDICAL_SOURCE_DETAIL.png"):
        "EP08_Polysomnography_model_side",
}


def normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def build_index(episode_dir: Path) -> dict[str, Path]:
    """Alle nutzbaren Medien der Episode nach Dateistamm."""
    index: dict[str, Path] = {}
    for p in sorted(episode_dir.rglob("*")):
        if p.suffix.lower() not in MEDIA_EXT:
            continue
        s = p.as_posix().upper()
        if "QA_CONTACT" in s or "QA_FRAMES" in s or "VEO_QA" in s:
            continue
        # Reserveclips sind ausdruecklich kein Hauptmaterial.
        if "RESERVE_CLIPS" in s:
            continue
        index.setdefault(p.stem, p)
    return index


def resolve(token: str, index: dict[str, Path], ep: str = "") -> Path | None:
    raw = (token or "").strip()
    override = CUE_OVERRIDES.get((ep, raw))
    # Auch svg/gif/webp abstreifen: die Plaene verweisen teils auf die
    # Rohquelle, im Schnitt liegt aber das gerasterte PNG-Derivat.
    token = re.sub(r"\.(png|jpg|jpeg|mp4|mov|svg|gif|webp)$", "", raw, flags=re.I)
    if not token or token in {"—", "-"}:
        return None
    token = Path(token).name
    if override is None:
        override = CUE_OVERRIDES.get((ep, token))
    if override is not None:
        token = override
    elif token in SUBSTITUTES:
        token = SUBSTITUTES[token]
    if token in index:
        return index[token]
    hits = sorted(k for k in index if k.startswith(token + "_"))
    return index[hits[0]] if hits else None


def take_anchor(take_id: str, takes_dir: Path, clean: str | None) -> str:
    """Kurzer, im Sprechtext eindeutig auffindbarer Anker."""
    candidates = list(takes_dir.glob(f"{take_id}*.txt"))
    if not candidates:
        return ""
    words = normalise(candidates[0].read_text(encoding="utf-8")).split()
    for size in (8, 10, 12, 6):
        anchor = " ".join(words[:size])
        if clean is None or anchor in clean:
            return anchor
    return " ".join(words[:8])


def process(ep: str) -> None:
    cfg = EPISODES[ep]
    episode_dir = PROD / cfg["dir"]
    plan_path = episode_dir / cfg["plan"]
    takes_dir = episode_dir / cfg["takes"]
    clean = None
    if cfg["clean"]:
        clean_path = episode_dir / cfg["clean"]
        if clean_path.is_file():
            clean = normalise(clean_path.read_text(encoding="utf-8"))

    with plan_path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    index = build_index(episode_dir)

    # Reihenfolge der Takes aus dem Plan uebernehmen, nicht alphabetisch.
    order: list[str] = []
    grouped: dict[str, list[dict]] = {}
    for row in rows:
        take = row[cfg["take_col"]].strip()
        if take not in grouped:
            grouped[take] = []
            order.append(take)
        grouped[take].append(row)

    cues: list[dict[str, str]] = []
    assets: dict[str, list[str]] = {}
    unresolved: list[str] = []

    for take in order:
        group = grouped[take]
        paths: list[str] = []
        for row in group:
            raw_asset = row[cfg["asset_col"]]
            raw_key = raw_asset.strip()
            replacement = (TAKE_ASSET_OVERRIDES.get((ep, take, raw_key)) or
                           TAKE_ASSET_OVERRIDES.get((ep, take, Path(raw_key).name)))
            q = resolve(replacement or raw_asset, index, ep)
            if q is None:
                unresolved.append(f"{take}: {row[cfg['asset_col']]}")
                continue
            rel = q.relative_to(ROOT).as_posix()
            # Zwei identische Frames direkt hintereinander verbietet der
            # Bilddichte-Lock; der Renderer wuerde sie sonst hart aneinander
            # schneiden.
            if paths and paths[-1] == rel:
                continue
            paths.append(rel)
        for position, name in FILLS.get(take, []):
            q = resolve(name, index, ep)
            if q is None:
                raise SystemExit(f"{take}: Fuellshot nicht gefunden -> {name}")
            paths.insert(min(position, len(paths)), q.relative_to(ROOT).as_posix())

        if not paths:
            continue

        # Manche Plaene fuehren Pseudo-Takes wie "ENDCARD", zu denen es keinen
        # Sprechertext gibt. Als eigener Cue haetten sie keinen Textanker: der
        # Renderer setzt sie dann ans Ende und gibt ihnen die gesamte Restzeit,
        # waehrend der letzte echte Take auf Bruchteile zusammenschrumpft. In
        # EP06 waren das 30 Sekunden Endcard gegen 0,06 Sekunden je Bild im
        # Schlusstake. Solche Eintraege gehoeren an den vorherigen Cue.
        if not list(takes_dir.glob(f"{take}*.txt")) and cues:
            previous = cues[-1]["cue_id"]
            assets[previous].extend(p for p in paths if p != assets[previous][-1])
            previous_cue = cues[-1]
            previous_cue["planned_shots"] = str(len(assets[previous]))
            print(f"      Hinweis: '{take}' hat keinen Sprechertext und wurde "
                  f"an {previous} angehaengt")
            continue

        assets[take] = paths
        cues.append({
            "cue_id": take,
            "section": group[0][cfg["act_col"]],
            "anchor_text": take_anchor(take, takes_dir, clean),
            "planned_shots": str(len(paths)),
            "edit_rule": "no still >9s; no identical frame twice; "
                         "no two consecutive shots from the same base asset",
        })

    out_dir = SUMMARY / cfg["dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    cue_path = out_dir / "VISUAL_CUE_SHEET_V5.csv"
    with cue_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(cues[0].keys()))
        writer.writeheader()
        writer.writerows(cues)

    manifest_path = episode_dir / "render_manifest.json"
    manifest_path.write_text(json.dumps({
        "episode": ep,
        "note": "Erzeugt aus dem Sync-Plan. Ein Cue je Sprechertake; die Liste "
                "wird innerhalb des Cue-Fensters in Einzelshots aufgeteilt.",
        "assets": {k: (v[0] if len(v) == 1 else v) for k, v in assets.items()},
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    total = sum(len(v) for v in assets.values())
    print(f"{ep}: {len(cues)} Cues, {total} Shots -> {cue_path.relative_to(ROOT)}")
    print(f"      Manifest: {manifest_path.relative_to(ROOT)}")

    # Dichtepruefung. Die Sprechdauer eines Takes wird ueber seinen Anteil an
    # der Reinschrift geschaetzt - das reicht, um zu duenn belegte Takes zu
    # finden, bevor die Stimme ueberhaupt erzeugt ist.
    if clean:
        est_total = len(clean) / 14.6  # Zeichen je Sekunde, George-Tempo
        thin: list[tuple[str, float, int]] = []
        for take, paths in assets.items():
            source = next(takes_dir.glob(f"{take}*.txt"), None)
            if source is None:
                continue
            share = len(normalise(source.read_text(encoding="utf-8"))) / len(clean)
            per_shot = share * est_total / len(paths)
            if per_shot > MAX_STILL_SECONDS:
                thin.append((take, per_shot, len(paths)))
        if thin:
            print(f"      ACHTUNG Bilddichte-Lock verletzt (>{MAX_STILL_SECONDS:.0f}s je Bild):")
            for take, per_shot, n in sorted(thin, key=lambda x: -x[1]):
                print(f"        {take}: {per_shot:.1f}s je Bild bei {n} Shots")
        else:
            print(f"      Bilddichte: alle Takes unter {MAX_STILL_SECONDS:.0f}s je Bild")
    if unresolved:
        print(f"      nicht aufloesbar: {len(unresolved)}")
        for u in unresolved[:15]:
            print(f"        {u}")
        if len(unresolved) > 15:
            print(f"        ... und {len(unresolved) - 15} weitere")


def main() -> int:
    targets = sys.argv[1:] or list(EPISODES)
    for ep in targets:
        if ep not in EPISODES:
            raise SystemExit(f"Unbekannte Episode: {ep}")
        process(ep)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
