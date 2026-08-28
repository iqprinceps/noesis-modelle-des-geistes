#!/usr/bin/env python3
"""Render a controlled nonphysical-presence insert without literal entity formation."""

from __future__ import annotations

import json
import argparse
import hashlib
import math
import pathlib
import subprocess

import cv2
import numpy as np


ROOT = pathlib.Path(__file__).resolve().parent.parent
EP = ROOT / "07_ENGLISH_PRODUCTION" / "EP02_GATEWAY"
SOURCE = EP / "03_VISUALS/GENERATED/INNER/GW_EN_INNER04_NONPHYSICAL_PRESENCE_NATIVE.png"
OUTPUT = EP / "03_VISUALS/CLIPS/GW_EN_CLIP09_NONPHYSICAL_PRESENCE_SAFE.mp4"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if OUTPUT.is_file() and OUTPUT.stat().st_size > 100_000 and not args.force:
        print(f"SKIP {OUTPUT.name}")
        return
    source = cv2.imread(str(SOURCE), cv2.IMREAD_COLOR)
    h0, w0 = source.shape[:2]
    scale = max(1920 / w0, 1080 / h0)
    source = cv2.resize(source, (round(w0 * scale), round(h0 * scale)), interpolation=cv2.INTER_LANCZOS4)
    y0 = (source.shape[0] - 1080) // 2
    x0 = (source.shape[1] - 1920) // 2
    base = source[y0:y0 + 1080, x0:x0 + 1920].copy()
    yy, xx = np.indices((1080, 1920), dtype=np.float32)
    fixed_cx, cy = 1260.0, 505.0
    proc = subprocess.Popen([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", "1920x1080", "-r", "30",
        "-i", "-", "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(OUTPUT),
    ], stdin=subprocess.PIPE)
    for frame_no in range(180):
        t = frame_no / 30.0
        progress = frame_no / 179.0
        envelope = math.sin(math.pi * progress) ** 1.25
        phase = t * 2.5
        # The disturbance travels across the secured perimeter, grows, then
        # releases.  This produces an unmistakable temporal arc without ever
        # resolving into a body or face.
        cx = 1020.0 + 360.0 * progress
        radius = np.sqrt(((xx - cx) / 345.0) ** 2 + ((yy - cy) / 290.0) ** 2)
        mask = np.clip(1.0 - radius, 0.0, 1.0) ** 2
        dx = mask * envelope * (42.0 * np.sin((yy - cy) * 0.040 - phase))
        dy = mask * envelope * (21.0 * np.cos((xx - cx) * 0.034 + phase * 0.9))
        frame = cv2.remap(base, xx + dx.astype(np.float32), yy + dy.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        # A soft pool of light follows the refraction and visibly peaks at the
        # midpoint; it changes the scene, not merely the camera crop.
        glow = np.clip(1.0 - radius, 0.0, 1.0)[..., None]
        tint = np.zeros_like(frame, dtype=np.float32)
        tint[..., 0], tint[..., 1], tint[..., 2] = 28, 38, 48
        frame = np.clip(frame.astype(np.float32) + tint * glow * envelope * 1.65, 0, 255).astype(np.uint8)
        overlay = frame.copy()
        # Two pressure fronts pass through the fence at different radii.  They
        # are environmental reactions, never a silhouette.
        for ring_index in range(2):
            ring_phase = (progress * 1.45 + ring_index * 0.48) % 1.0
            axes = (int(110 + ring_phase * 330), int(80 + ring_phase * 245))
            ring_alpha = envelope * (1.0 - ring_phase) * 0.32
            ring_layer = frame.copy()
            cv2.ellipse(ring_layer, (int(cx), int(cy)), axes, 0, 0, 360, (112, 148, 162), 4, cv2.LINE_AA)
            frame = cv2.addWeighted(ring_layer, ring_alpha, frame, 1.0 - ring_alpha, 0)
        overlay = frame.copy()
        for n in range(68):
            angle = n * 2.399 + t * (0.40 + (n % 3) * 0.045)
            r = 40 + (n * 13) % 310
            px = int(cx + math.cos(angle) * r * 1.05)
            py = int(cy + math.sin(angle) * r * 0.72)
            alpha = envelope * (0.16 + 0.16 * (n % 4) / 3)
            color = (145, 168, 175)
            cv2.circle(overlay, (px, py), 2 + n % 3, color, -1, lineType=cv2.LINE_AA)
            if alpha > 0:
                frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
                overlay[:] = frame
        proc.stdin.write(frame.tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError("ffmpeg encoding failed")
    meta = {
        "provider": "code-native controlled motion",
        "source": str(SOURCE.relative_to(EP)).replace("\\", "/"),
        "duration_seconds": 6,
        "fps": 30,
        "resolution": "1920x1080",
        "purpose": "nonphysical-presence cue without literal entity formation",
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "visible_mode_badge": False,
        "motion_arc": "disturbance travels left-to-right, intensifies at midpoint, then releases; localized glow and moving particles follow it",
        "qa_rule": "local geometric distortion, light response, and particles only; no body, face, text, or smoke figure",
    }
    OUTPUT.with_suffix(".json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK {OUTPUT.name}")


if __name__ == "__main__":
    main()
