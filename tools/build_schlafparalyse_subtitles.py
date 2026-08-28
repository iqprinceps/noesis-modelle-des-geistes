#!/usr/bin/env python3
"""Untertitel fuer EP06-EP08 aus dem Forced Alignment der Sprecherspur.

Baut SRT und WebVTT aus den Wortzeiten. Die Segmentierung folgt zuerst
Satzgrenzen, dann Nebensatzgrenzen und erst zuletzt der Wortgrenze - so bleiben
die Zeilen lesbar statt mechanisch gefuellt.

Uebernimmt Aufbau und Grenzwerte von `tools/build_ep04a_subtitles.py`, damit
die Serie einheitlich untertitelt ist. Neu ist die episodenweise Tabelle der
ausgeschriebenen Zahlwoerter: die Sprecherfassung schreibt Jahreszahlen aus,
damit die Stimme sie richtig liest - im Untertitel gehoeren Ziffern hin.

Nicht ersetzt wird, was im Deutschen als Wort gemeint ist: "Tausende
Menschen", "tausend aehnliche Geschichten", "die achtziger Jahre". Diese
Woerter bezeichnen keine Zahl, sondern eine Menge.

    python tools/build_schlafparalyse_subtitles.py EP06
    python tools/build_schlafparalyse_subtitles.py            # alle mit Alignment
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MAX_LINE = 42          # Zeichen pro Zeile
MAX_LINES = 2
# Dichte deutschsprachige Dokumentar-Erzaehlung: 20 CPS ist der harte
# Auslieferungs-Lock. 17 CPS bleibt ein gutes Komfortziel, ist bei der
# gesprochenen Textmenge der drei fertigen Master aber nicht durchgehend
# erreichbar, ohne Untertitel deutlich vor oder nach der Stimme zu zeigen.
MAX_CPS = 20.0         # Zeichen pro Sekunde, harter Lesegeschwindigkeits-Lock
MIN_DUR = 1.20
MAX_DUR = 6.00
GAP_BREAK = 0.65       # Sprechpause, die immer einen neuen Cue erzwingt

EPISODES = {
    "EP06": dict(dir="EP06_SCHLAFPARALYSE_V4",
                 alignment="voice/alignment/EP06_SCHLAFPARALYSE_V4_alignment.json"),
    "EP07": dict(dir="EP07_SCHLAFPARALYSE_V4",
                 alignment="voice/alignment/EP07_SCHLAFPARALYSE_V4_alignment.json"),
    "EP08": dict(dir="EP08_SCHLAFPARALYSE_V4",
                 alignment="voice/alignment/EP08_SCHLAFPARALYSE_V4_alignment.json"),
}

# Ausgeschriebene Zahlwoerter zurueck in Ziffern. Schluessel kleingeschrieben,
# Vergleich ohne Satzzeichen.
SPOKEN_NUMBERS = {
    "sechzehnhundertzweiundneunzig": "1692",
    "neunzehnhundertdreiundsechzig": "1963",
    "neunzehnhundertzweiundachtzig": "1982",
    "neunzehnhundertzweiundneunzig": "1992",
    "zweitausendeins": "2001",
    "zweitausendfuenfzehn": "2015",
    "zweitausendfünfzehn": "2015",
    "viertausendfuenfhundert": "4.500",
    "viertausendfünfhundert": "4.500",
}

# Mehrwortfolgen, die als Ganzes ersetzt werden. Wird nach dem Zusammensetzen
# des Cue-Textes angewandt, damit "am zwoelften April 2001" zu "am 12. April
# 2001" wird statt zu drei Einzelersetzungen.
SPOKEN_PHRASES = [
    (re.compile(r"\bzwölften April\b", re.I), "12. April"),
    (re.compile(r"\bzwoelften April\b", re.I), "12. April"),
]

CLAUSE_END = re.compile(r"[,;–—]$")
ABBREV = {"c", "g", "z", "b", "u", "d", "h", "bzw", "ca", "vgl", "dr", "prof",
          "st", "nr", "ca", "usw"}


def is_sentence_end(token: str) -> bool:
    if not re.search(r"[.!?:]$", token):
        return False
    bare = token.strip(".,;:!?").casefold()
    return bare not in ABBREV and len(bare) > 1


def load_words(alignment: Path) -> list[dict]:
    data = json.loads(alignment.read_text(encoding="utf-8"))
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
    bare = token.strip(".,;:!?„“\"'»«")
    tail = token[len(token.rstrip(".,;:!?„“\"'»«")):]
    head = token[:len(token) - len(token.lstrip(".,;:!?„“\"'»«"))]
    key = bare.casefold()
    if key in SPOKEN_NUMBERS:
        return head + SPOKEN_NUMBERS[key] + tail
    return token


def apply_phrases(text: str) -> str:
    for pattern, replacement in SPOKEN_PHRASES:
        text = pattern.sub(replacement, text)
    return text


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
        text = apply_phrases(detokenize([normalise(w["text"]) for w in buf]))
        lines = wrap(text)
        if lines is None:
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
        text = apply_phrases(detokenize([normalise(w["text"]) for w in buf]))
        span = buf[-1]["end"] - buf[0]["start"]
        nxt = words[index + 1] if index + 1 < len(words) else None
        gap = (nxt["start"] - word["end"]) if nxt else 99.0

        # Kein gieriges Fuellen bis zur Zeichengrenze: das schnitt den Satz
        # genau dann ab, wenn nur noch ein Wort uebrig war ("... vor seinem" /
        # "Mikrofon."). Gesammelt wird bis Satzende, Sprechpause oder
        # Hoechstdauer; zu langer Text wird in flush() an einer Satzgrenze
        # ausgewogen halbiert.
        if is_sentence_end(word["text"]):
            flush()
        elif gap >= GAP_BREAK:
            flush()
        elif span >= MAX_DUR:
            flush()
    flush()

    cues = merge_short(cues)
    cues = merge_for_reading_speed(cues)
    retime(cues)
    return cues


def try_join(a: dict, b: dict) -> dict | None:
    lines = wrap(" ".join(a["lines"]) + " " + " ".join(b["lines"]))
    if lines is None:
        return None
    if b["start"] - a["end"] >= GAP_BREAK:
        return None
    if b["end"] - a["start"] > MAX_DUR:
        return None
    return {"start": a["start"], "end": b["end"], "lines": lines}


def merge_short(cues: list[dict]) -> list[dict]:
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


def cue_cps(cue: dict) -> float:
    chars = sum(len(line) for line in cue["lines"])
    return chars / max(0.01, cue["end"] - cue["start"])


def merge_for_reading_speed(cues: list[dict]) -> list[dict]:
    """Kurze schnelle Saetze mit dem passenden Nachbarsatz ausgleichen.

    Die Sprecherfassung ist bewusst dicht. Satzweise Untertitel erzeugen darin
    viele sehr kurze Einblendungen, obwohl zwei benachbarte Saetze gemeinsam
    bequem in den Zwei-Zeilen-Lock passen. Wir verbinden jeweils das Paar mit
    der groessten CPS-Verbesserung und wiederholen das, solange der Textblock,
    die Sprechpause und die Sechs-Sekunden-Grenze gewahrt bleiben.
    """
    cues = list(cues)
    while True:
        best: tuple[float, int, dict] | None = None
        for i in range(len(cues) - 1):
            joined = try_join(cues[i], cues[i + 1])
            if joined is None:
                continue
            before = max(cue_cps(cues[i]), cue_cps(cues[i + 1]))
            after = cue_cps(joined)
            if before <= MAX_CPS or after >= before:
                continue
            gain = before - after
            if best is None or gain > best[0]:
                best = (gain, i, joined)
        if best is None:
            return cues
        _, i, joined = best
        cues[i:i + 2] = [joined]


def retime(cues: list[dict]) -> None:
    """Lesetempo einhalten, danach Ueberlappung hart ausschliessen.

    Bei durchlaufender Rede laesst sich das Lesetempo nicht beliebig senken -
    ein Untertitel, der laenger steht als der Satz gesprochen wird, laeuft der
    Stimme hinterher. Zusaetzliche Lesezeit kommt deshalb aus den Sprechpausen:
    liegt vor einem Cue eine Luecke, wird er bis zu LEAD_IN frueher
    eingeblendet. Das ist uebliche Untertitelpraxis und faellt nicht auf.
    """
    for cue in cues:
        cue["speech_start"] = cue["start"]
        cue["speech_end"] = cue["end"]

    lead_in = 0.30
    for i, cue in enumerate(cues):
        floor = cues[i - 1]["end"] + 0.08 if i else 0.0
        room = cue["start"] - floor
        if room > 0:
            cue["start"] = max(floor, cue["start"] - min(lead_in, room))

    for cue in cues:
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

    # Einzelne schnelle Phrasen erhalten bis zu 0,45 s Vorlauf aus einem
    # langsameren Vorgänger. Dabei bleibt die 40-ms-Trennung bestehen und der
    # Vorgänger fällt selbst nie über den CPS-Lock. So beseitigen wir kurze
    # Lesespitzen, ohne einen Untertitel verspätet zur Sprache einzublenden.
    for i in range(1, len(cues)):
        cue = cues[i]
        need = sum(len(line) for line in cue["lines"]) / MAX_CPS
        deficit = need - (cue["end"] - cue["start"])
        if deficit <= 0:
            continue
        prev = cues[i - 1]
        prev_need = max(MIN_DUR, sum(len(line) for line in prev["lines"]) / MAX_CPS)
        prev_slack = max(0.0, (prev["end"] - prev["start"]) - prev_need)
        early_room = max(0.0, cue["start"] - (cue["speech_start"] - 0.45))
        shift = min(deficit, prev_slack, early_room)
        if shift > 0:
            prev["end"] -= shift
            cue["start"] -= shift


def stamp(seconds: float, comma: bool) -> str:
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d}{',' if comma else '.'}{ms:03d}"


def build(ep: str) -> bool:
    cfg = EPISODES[ep]
    prod = ROOT / "06_PRODUCTION" / cfg["dir"]
    alignment = prod / cfg["alignment"]
    if not alignment.is_file():
        print(f"{ep}: kein Alignment ({alignment.name}) - uebersprungen")
        return False

    out_dir = prod / "render" / "subtitles"
    out_dir.mkdir(parents=True, exist_ok=True)
    cues = build_cues(load_words(alignment))

    srt = []
    for i, cue in enumerate(cues, 1):
        srt.append(f"{i}\n{stamp(cue['start'], True)} --> {stamp(cue['end'], True)}\n"
                   + "\n".join(cue["lines"]) + "\n")
    (out_dir / f"{ep}_de.srt").write_text("\n".join(srt), encoding="utf-8")

    vtt = ["WEBVTT", ""]
    for cue in cues:
        vtt.append(f"{stamp(cue['start'], False)} --> {stamp(cue['end'], False)}")
        vtt.extend(cue["lines"])
        vtt.append("")
    (out_dir / f"{ep}_de.vtt").write_text("\n".join(vtt), encoding="utf-8")

    durations = [c["end"] - c["start"] for c in cues]
    cps = [sum(len(l) for l in c["lines"]) / (c["end"] - c["start"]) for c in cues]
    longest = max(len(l) for c in cues for l in c["lines"])
    # Millisekunden-Rundung kann intern Werte wie 20.0000000003 erzeugen.
    over = sum(1 for c in cps if c > MAX_CPS + 0.01)
    print(f"{ep}: {len(cues)} Cues | laengste Zeile {longest}/{MAX_LINE} Zeichen | "
          f"Dauer {min(durations):.2f}-{max(durations):.2f}s | "
          f"Lesetempo max {max(cps):.1f}/{MAX_CPS} ({over} darueber) | "
          f"Ende {cues[-1]['end']:.1f}s")
    print(f"      -> {out_dir.relative_to(ROOT)}")
    return True


def main() -> int:
    targets = sys.argv[1:] or list(EPISODES)
    for ep in targets:
        if ep not in EPISODES:
            raise SystemExit(f"Unbekannte Episode: {ep}")
        build(ep)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
