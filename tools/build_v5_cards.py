#!/usr/bin/env python3
"""Create additional card visuals for Gateway V5."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "06_PRODUCTION" / "EP02_GATEWAY_V5" / "visuals" / "cards"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1920, 1080
BG = (4, 17, 20)
GOLD = (224, 174, 71)
CYAN = (91, 210, 211)
OFF = (238, 235, 222)
DIM = (105, 160, 160)

ARIAL_B = Path("C:/Windows/Fonts/arialbd.ttf")
SERIF = Path("C:/Windows/Fonts/georgia.ttf")


def f(path, size):
    return ImageFont.truetype(str(path), size)


def make_card(title, subtitle, items, name, color=GOLD):
    canvas = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(canvas)

    # Title
    d.text((W//2, 120), title, font=f(SERIF, 52), fill=color, anchor="mm")

    # Subtitle
    d.text((W//2, 180), subtitle, font=f(ARIAL_B, 24), fill=DIM, anchor="mm")

    # Divider line
    d.line([(200, 220), (W-200, 220)], fill=(*color, 100), width=2)

    # Items
    y = 280
    for item in items:
        if isinstance(item, tuple):
            label, desc = item
            d.text((250, y), label, font=f(ARIAL_B, 32), fill=color)
            d.text((250, y + 40), desc, font=f(SERIF, 26), fill=OFF)
            y += 100
        else:
            d.text((250, y), item, font=f(SERIF, 28), fill=OFF)
            y += 60

    # Bottom line
    d.line([(200, H-120), (W-200, H-120)], fill=(*color, 100), width=2)
    d.text((W//2, H-80), "U.S. ARMY GATEWAY REPORT · 1983", font=f(ARIAL_B, 20), fill=DIM, anchor="mm")

    canvas.save(OUT / name, quality=96)
    print(f"Created: {name}")


def main():
    make_card(
        "FOCUS LEVELS",
        "The Gateway Training Progression",
        [
            ("FOCUS 10", "Mind awake, body deeply relaxed"),
            ("FOCUS 12", "Expanded awareness"),
            ("FOCUS 15", "Travel into the Past"),
            ("FOCUS 21", "The Future — beyond normal space-time"),
        ],
        "V5_CARD_FOCUS_LEVELS.png",
        CYAN
    )

    make_card(
        "BINAURAL BEAT",
        "The Auditory Foundation",
        [
            ("400 Hz", "Left ear"),
            ("410 Hz", "Right ear"),
            ("~10 Hz", "Perceived binaural beat"),
            ("FREQUENCY FOLLOWING RESPONSE", "Brain entrainment hypothesis"),
        ],
        "V5_CARD_BINAURAL_BEAT.png",
        GOLD
    )

    make_card(
        "WORLD MODEL",
        "McDonnell's Theoretical Framework",
        [
            ("BODY", "Resonance and vibration"),
            ("BRAIN", "Electrical patterns"),
            ("COHERENCE", "Synchronization"),
            ("FIELD", "Information access beyond space-time"),
        ],
        "V5_CARD_WORLD_MODEL.png",
        GOLD
    )

    make_card(
        "DISTORTION PROBLEM",
        "Why Three Observers?",
        [
            ("PRESENT", "Current perception"),
            ("PAST", "Focus 15 — memory distortion"),
            ("FUTURE", "Focus 21 — anticipation bias"),
            ("SOLUTION", "Compare all three reports"),
        ],
        "V5_CARD_DISTORTION.png",
        CYAN
    )

    make_card(
        "CONDITIONAL ENDING",
        "What the Report Actually Says",
        [
            ("DOCUMENTED", "Levels, techniques, procedures"),
            ("CLAIMED", "Consciousness beyond body"),
            ("NOT PROVEN", "No verified time information"),
            ("THE GAP", "Small effect ≠ extraordinary claim"),
        ],
        "V5_CARD_CONDITIONAL.png",
        GOLD
    )

    make_card(
        "EVIDENCE SCALE",
        "From Perception to Proof",
        [
            ("AUDITORY EFFECT", "Moderate, measurable"),
            ("ENTRAINMENT", "Contradictory evidence"),
            ("TIME INFORMATION", "No verified data"),
            ("REMOTE VIEWING", "Extraordinary claim, ordinary evidence"),
        ],
        "V5_CARD_EVIDENCE_SCALE.png",
        CYAN
    )

    make_card(
        "TEST PROTOCOL",
        "What Would Proof Require?",
        [
            ("PRE-SELECT TARGET", "Before the session"),
            ("BLIND EVALUATION", "No prior knowledge"),
            ("LOCK SCORING", "Define success in advance"),
            ("REPEAT", "Independent replication"),
        ],
        "V5_CARD_TEST_PROTOCOL.png",
        GOLD
    )


if __name__ == "__main__":
    main()
