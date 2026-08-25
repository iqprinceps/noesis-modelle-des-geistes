#!/usr/bin/env python3
"""Untertitel fuer EP04A aus dem Forced Alignment der Sprecherspur.

Baut SRT und WebVTT aus den Wortzeiten in EP04A_GEORGE_VO_ALIGNMENT.json.
Die Segmentierung folgt zuerst Satzgrenzen, dann Nebensatzgrenzen und erst
zuletzt der Wortgrenze -- so bleiben die Zeilen lesbar statt mechanisch
gefuellt.  Zahlwoerter, die fuer die Sprachausgabe ausgeschrieben wurden,
werden fuer die Lesefassung zurueckgesetzt (die Stimme sagt
"neunzehnhundertdreizehn", im Untertitel steht 1913).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VOICE = ROOT / "06_PRODUCTION" / "JUNG_SERIES_V1" / "VOICE_EP04A"
ALIGNMENT = VOICE / "alignment" / "EP04A_GEORGE_VO_ALIGNMENT.json"
OUT_DIR = ROOT / "06_PRODUCTION" / "JUNG_SERIES_V1" / "RENDER_EP04A" / "subtitles"

MAX_LINE = 42          # Zeichen pro Zeile
MAX_LINES = 2
MAX_CPS = 17.0         # Zeichen pro Sekunde, Lesegeschwindigkeit
MIN_DUR = 1.20
MAX_DUR = 6.00
GAP_BREAK = 0.65       # Sprechpause, die immer einen neuen Cue erzwingt

# Die Sprecherfassung schreibt Jahreszahlen aus.  Fuer die Lesefassung zurueck.
SPOKEN_NUMBERS = {
    "neunzehnhundertzweiunddreissig": "1932",
    "neunzehnhundertzweiunddreißig": "1932",
    "neunzehnhundertdreizehn": "1913",
    "neunzehnhundertvierzehn": "1914",
    "neunzehnhundertneunzehn": "1919",
    "neunzehn": "19",
}

CLAUSE_END = re.compile(r"[,;–—]$")
# "C." und "G." in "C. G. Jung" sind keine Satzenden, ebensowenig gaengige
# Abkuerzungen.  Ohne diese Ausnahme zerfaellt der Name in drei Cues.
ABBREV = {"c", "g", "z", "b", "u", "d", "h", "bzw", "ca", "vgl", "dr", "prof", "st", "nr"}


def is_sentence_end(token: str) -> bool:
    if not re.search(r"[.!?:]$", token):
        return False
    bare = token.strip(".,;:!?").casefold()
    return bare not in ABBREV and len(bare) > 1


def load_words() -> list[dict]:
    data = json.loads(ALIGNMENT.read_text(encoding="utf-8"))
    words = []
    for w in data["words"]:
        text = (w.get("text") or "").strip()
        if not text:
            continue
        words.append({"text": text, "start": float(w["start"]), "end": float(w["end"])})
    return words


def detokenize(tokens: list[str]) -> str:
    out = ""
    for token in tokens:
        if out and not re.match(r"^[,.;:!?)\]]", token):
            out += " "
        out += token
    return out.strip()


def normalise(token: str) -> str:
    bare = token.strip(".,;:!?")
    tail = token[len(bare):]
    key = bare.casefold()
    if key in SPOKEN_NUMBERS:
        return SPOKEN_NUMBERS[key] + tail
    return token


def wrap(text: str) -> list[str] | None:
    """Auf hoechstens MAX_LINES Zeilen umbrechen, moeglichst ausgewogen."""
    if len(text) <= MAX_LINE:
        return [text]
    words = text.split()
    best = None
    for split in range(1, len(words)):
        a = " ".join(words[:split])
        b = " ".join(words[split:])
        if len(a) > MAX_LINE or len(b) > MAX_LINE:
            continue
        score = abs(len(a) - len(b))
        # Ein Umbruch nach einem Satzzeichen liest sich besser.
        if CLAUSE_END.search(a):
            score -= 12
        if best is None or score < best[0]:
            best = (score, [a, b])
    return best[1] if best else None


def build_cues(words: list[dict]) -> list[dict]:
    cues: list[dict] = []
    buf: list[dict] = []

    def flush():
        if not buf:
            return
        tokens = [normalise(w["text"]) for w in buf]
        text = detokenize(tokens)
        lines = wrap(text)
        if lines is None:
            # Zu lang fuer zwei Zeilen: an der besten Grenze halbieren und beide
            # Haelften einzeln abschliessen.
            half = len(buf) // 2
            for i in range(len(buf) - 1, 0, -1):
                if CLAUSE_END.search(buf[i - 1]["text"]):
                    half = i
                    break
            left, right = buf[:half], buf[half:]
            buf.clear()
            buf.extend(left)
            flush()
            buf.clear()
            buf.extend(right)
            flush()
            buf.clear()
            return
        cues.append({"start": buf[0]["start"], "end": buf[-1]["end"], "lines": lines})
        buf.clear()

    for index, word in enumerate(words):
        buf.append(word)
        tokens = [normalise(w["text"]) for w in buf]
        text = detokenize(tokens)
        span = buf[-1]["end"] - buf[0]["start"]
        nxt = words[index + 1] if index + 1 < len(words) else None
        gap = (nxt["start"] - word["end"]) if nxt else 99.0

        if is_sentence_end(word["text"]):
            flush()
        elif gap >= GAP_BREAK:
            flush()
        elif len(text) >= MAX_LINE * MAX_LINES - 6 or span >= MAX_DUR:
            flush()
    flush()

    cues = merge_short(cues)
    retime(cues)
    return cues


def try_join(a: dict, b: dict) -> dict | None:
    """Zwei Cues zusammenlegen, wenn Text und Dauer das hergeben."""
    lines = wrap(" ".join(a["lines"]) + " " + " ".join(b["lines"]))
    if lines is None:
        return None
    if b["start"] - a["end"] >= GAP_BREAK:
        return None
    if b["end"] - a["start"] > MAX_DUR:
        return None
    return {"start": a["start"], "end": b["end"], "lines": lines}


def merge_short(cues: list[dict]) -> list[dict]:
    """Zu kurze Cues anlagern -- erst an den vorherigen, sonst an den naechsten."""
    out: list[dict] = []
    i = 0
    while i < len(cues):
        cue = cues[i]
        words = " ".join(cue["lines"]).split()
        short = (cue["end"] - cue["start"]) < MIN_DUR or len(words) <= 2
        if short:
            if out:
                joined = try_join(out[-1], cue)
                if joined:
                    out[-1] = joined
                    i += 1
                    continue
            if i + 1 < len(cues):
                joined = try_join(cue, cues[i + 1])
                if joined:
                    out.append(joined)
                    i += 2
                    continue
        out.append(cue)
        i += 1
    return out


def retime(cues: list[dict]) -> None:
    """Standzeiten setzen: Lesetempo einhalten, danach Ueberlappung hart ausschliessen.

    Das Alignment liefert an einzelnen Stellen Wortzeiten, die sich minimal
    ueberlappen; ohne die harte Klemme wandert das in die SRT-Datei.
    """
    for i, cue in enumerate(cues):
        chars = sum(len(l) for l in cue["lines"])
        need = max(MIN_DUR, chars / MAX_CPS)
        cue["end"] = max(cue["end"], cue["start"] + need)

    for i in range(len(cues) - 1):
        limit = cues[i + 1]["start"] - 0.04
        if cues[i]["end"] > limit:
            cues[i]["end"] = limit
    for cue in cues:
        if cue["end"] <= cue["start"]:
            cue["end"] = cue["start"] + 0.30


def stamp(seconds: float, comma: bool) -> str:
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    sep = "," if comma else "."
    return f"{h:02d}:{m:02d}:{s:02d}{sep}{ms:03d}"


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cues = build_cues(load_words())

    srt = []
    for i, cue in enumerate(cues, 1):
        srt.append(f"{i}\n{stamp(cue['start'], True)} --> {stamp(cue['end'], True)}\n"
                   + "\n".join(cue["lines"]) + "\n")
    (OUT_DIR / "EP04A_de.srt").write_text("\n".join(srt), encoding="utf-8")

    vtt = ["WEBVTT", ""]
    for cue in cues:
        vtt.append(f"{stamp(cue['start'], False)} --> {stamp(cue['end'], False)}")
        vtt.extend(cue["lines"])
        vtt.append("")
    (OUT_DIR / "EP04A_de.vtt").write_text("\n".join(vtt), encoding="utf-8")

    durations = [c["end"] - c["start"] for c in cues]
    cps = [sum(len(l) for l in c["lines"]) / (c["end"] - c["start"]) for c in cues]
    longest = max(len(l) for c in cues for l in c["lines"])
    print(f"Cues:            {len(cues)}")
    print(f"Laengste Zeile:  {longest} Zeichen (Grenze {MAX_LINE})")
    print(f"Dauer:           min {min(durations):.2f}s  max {max(durations):.2f}s")
    print(f"Lesetempo:       max {max(cps):.1f} Zeichen/s (Grenze {MAX_CPS})")
    print(f"Ueber Grenze:    {sum(1 for c in cps if c > MAX_CPS)} Cues")
    print(f"Letztes Ende:    {cues[-1]['end']:.2f}s")
    print(f"Geschrieben:     {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
