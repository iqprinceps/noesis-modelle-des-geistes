#!/usr/bin/env python3
"""EP01A Die Spiegel — zwei eigenstaendige Shorts: Reinschrift und Sprechtext.

Die beiden Shorts sind keine Ausschnitte aus der Folge. Sie erzaehlen je eine
abgeschlossene Sache und funktionieren fuer jemanden, der die Folge nicht
kennt. Wer sie sehen will, findet sie danach — aber der Short haelt auch ohne.

Aufbau, beide gleich:

    Sekunde 0 bis 2   Ein Satz, der eine Frage aufmacht. Kein Kanalname, kein
                      "in diesem Video". Wer in Sekunde zwei nicht bleibt,
                      bleibt gar nicht.
    Mitte             Die Sache selbst, in kurzen Saetzen, ein Bild je Satz.
    Schluss           Die offene Stelle. Kein Aufruf zu abonnieren — die
                      unbeantwortete Frage traegt weiter als eine Bitte.

Alle Angaben decken sich mit `07_VOICE_SCRIPT_CLEAN.txt`. Ein Short, der der
Folge widerspricht, beschaedigt beide.

    python tools/spg_shorts_texte.py
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROD = ROOT / "06_PRODUCTION" / "EP01A_SPIEGEL" / "shorts"
QUELLE = PROD / "voice" / "source"
BATCH = PROD / "voice" / "voice_batch.json"
RAW = PROD / "voice" / "raw_stems"

# Stimme und Einstellungen wie in der Folge — ein Short klingt sonst wie ein
# fremder Kanal.
VOICE = "JBFqnCBsd6RMkjVDRZzb"
VOICE_NAME = "George - Warm, Captivating Storyteller"
MODEL = "eleven_multilingual_v2"
SETTINGS = {"stability": 0.58, "similarity_boost": 0.80, "style": 0.08,
            "speed": 1.06, "use_speaker_boost": True}
SEED = 2402

ZAHLEN = [
    (r"\b1990\b", "neunzehnhundertneunzig"),
    (r"\b1991\b", "neunzehnhunderteinundneunzig"),
]

SHORTS = {
    "SHORT_A_DER_STUHL": {
        "titel": "Der Stuhl",
        "hook": "NACH VIER MINUTEN",
        "text": """Du sitzt auf einem Stuhl aus Metall.

Um dich herum steht eine Spirale aus poliertem Aluminium, fast drei Meter hoch. Sie schließt sich hinter dir bis auf einen Spalt.

Das Licht geht aus.

Nach etwa vier Minuten beginnt es. Zuerst nur ein Schimmern am Rand des Blickfelds.

Dann Farbe. Flächen, die wandern. Ringe, die sich ineinanderschieben.

Der Raum ist vollständig dunkel. Deine Augen sind offen.

Nach zehn Minuten werden daraus Bilder. Ein Zimmer mit einem Fenster. Ein Gesicht, das dich ansieht.

Und irgendwann verlierst du das Gefühl dafür, wie lange du schon hier sitzt.

Als die Tür aufgeht, sagt man dir, es seien zwanzig Minuten gewesen. Du hättest auf einen halben Tag getippt.

Diese Anlage steht in Nowosibirsk. Es gibt ein Patent darauf.

Und keiner von denen, die sie gebaut haben, nennt sie Zeitmaschine.""",
    },
    "SHORT_B_DER_VERSUCH": {
        "titel": "Der Versuch",
        "hook": "DREITAUSEND KILOMETER",
        "text": """Dreitausend Kilometer nördlich von Nowosibirsk liegt Dikson.

Eine Siedlung am Rand des Nordpolarmeers. Im Winter monatelang dunkel, minus vierzig Grad, Eis bis zum Horizont.

1990 bringen sowjetische Forscher Aluminiumplatten von fast drei Metern Höhe hierher, in einen Ort, in dem ein paar hundert Menschen leben.

Ihre Überlegung: Wenn dieser Raum Information über Entfernung trägt, dann muss er dorthin, wo das Magnetfeld der Erde am dünnsten ist.

Zu einer festgelegten Minute setzt sich dort jemand hinein und konzentriert sich auf ein einziges Symbol. Einen Kreis. Ein Kreuz. Ein Dreieck.

Zur selben Minute sitzen irgendwo auf der Welt Menschen mit einem Blatt Papier und zeichnen auf, was bei ihnen ankommt.

Koordiniert über Kurzwelle und Aufrufe in Zeitungen. Nach Angaben der Beteiligten machen Tausende mit.

Der Versuch heißt Aurora Borealis.

Die Auswertung meldet auffällige Übereinstimmungen. Am deutlichsten bei den einfachen Formen.

Alle Auswertungen stammen bis heute aus dem Kreis der Beteiligten.""",
    },
}


def gesprochen(text: str) -> tuple[str, list[str]]:
    log = []
    for muster, ersatz in ZAHLEN:
        text, n = re.subn(muster, ersatz, text)
        if n:
            log.append(f"{muster.strip(chr(92) + 'b')} ({n}x)")
    return text, log


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    QUELLE.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)

    stems = []
    for name, kurz in SHORTS.items():
        rein = PROD / f"{name}_CLEAN.txt"
        rein.write_text(kurz["text"].strip() + "\n", encoding="utf-8")

        sprech, log = gesprochen(kurz["text"].strip())
        ziel = QUELLE / f"{name}.txt"
        ziel.write_text(sprech + "\n", encoding="utf-8")
        stems.append({"id": name, "text_file": str(ziel.resolve())})

        woerter = len(kurz["text"].split())
        print(f"{name:22s} {woerter:3d} Woerter  ~{woerter / 2.45:4.1f} s"
              f"   Ersetzt: {', '.join(log) or 'nichts'}")

    BATCH.write_text(json.dumps({
        "voice": VOICE, "voice_name": VOICE_NAME, "model": MODEL,
        "settings": SETTINGS, "seed": SEED,
        "output_format": "mp3_44100_128",
        "output_dir": str(RAW.resolve()),
        "stems": stems,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nBatchdatei: {BATCH}")


if __name__ == "__main__":
    main()
