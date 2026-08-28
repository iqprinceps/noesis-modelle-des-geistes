#!/usr/bin/env python3
"""Animate the three controllable inputs as one linear, non-repeating insert."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib
import subprocess

import cv2
import numpy as np


ROOT = pathlib.Path(__file__).resolve().parent.parent
EP = ROOT / "07_ENGLISH_PRODUCTION" / "EP02_GATEWAY"
SOURCE = EP / "03_VISUALS/GENERATED/STILLS/GW_EN_FILMIC24_THREE_INPUTS_NATIVE.png"
OUTPUT = EP / "03_VISUALS/CLIPS/GW_EN_CLIP12_THREE_INPUTS_PROGRESS.mp4"


def fit_1080(source: np.ndarray) -> np.ndarray:
    h0, w0 = source.shape[:2]
    scale = max(1920 / w0, 1080 / h0)
    source = cv2.resize(source, (round(w0 * scale), round(h0 * scale)), interpolation=cv2.INTER_LANCZOS4)
    y0 = (source.shape[0] - 1080) // 2
    x0 = (source.shape[1] - 1920) // 2
    return source[y0:y0 + 1080, x0:x0 + 1920].copy()


def smoothstep(value: float, start: float, end: float) -> float:
    x = min(1.0, max(0.0, (value - start) / (end - start)))
    return x * x * (3.0 - 2.0 * x)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if OUTPUT.is_file() and OUTPUT.stat().st_size > 100_000 and not args.force:
        print(f"SKIP {OUTPUT.name}")
        return
    base = fit_1080(cv2.imread(str(SOURCE), cv2.IMREAD_COLOR))
    yy, xx = np.indices((1080, 1920), dtype=np.float32)
    zones = [
        (390.0, 490.0, 430.0, 370.0),   # tape and headphones
        (960.0, 560.0, 330.0, 330.0),   # target and ten responses
        (1510.0, 500.0, 400.0, 390.0),  # physiological recorder
    ]
    masks = []
    for cx, cy, rx, ry in zones:
        radius = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2
        masks.append((np.clip(1.0 - radius, 0.0, 1.0) ** 2)[..., None])
    proc = subprocess.Popen([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", "1920x1080", "-r", "30",
        "-i", "-", "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(OUTPUT),
    ], stdin=subprocess.PIPE)
    frames = 240
    for frame_no in range(frames):
        p = frame_no / (frames - 1)
        frame = base.astype(np.float32) * (0.82 + 0.03 * math.sin(p * math.pi))
        for idx, mask in enumerate(masks):
            activation = smoothstep(p, 0.05 + idx * 0.26, 0.23 + idx * 0.26)
            color = np.zeros_like(frame)
            color[..., 0], color[..., 1], color[..., 2] = 18, 32, 48
            frame += color * mask * activation * 0.72
        # The two tape reels rotate continuously once the audio input wakes.
        if p > 0.08:
            angle = p * 720.0
            for center in [(252, 390), (486, 390)]:
                for offset in (0, 120, 240):
                    a = math.radians(angle + offset)
                    end = (int(center[0] + math.cos(a) * 62), int(center[1] + math.sin(a) * 62))
                    cv2.line(frame, center, end, (135, 153, 163), 3, cv2.LINE_AA)
        # A warm scan line advances down the blank recorder paper only after
        # the third input illuminates; no data or invented readable marks.
        if p > 0.62:
            y = int(330 + smoothstep(p, 0.62, 0.96) * 265)
            cv2.line(frame, (1450, y), (1735, y), (80, 145, 202), 3, cv2.LINE_AA)
        proc.stdin.write(np.clip(frame, 0, 255).astype(np.uint8).tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError("ffmpeg encoding failed")
    metadata = {
        "provider": "code-native controlled motion",
        "source": str(SOURCE.relative_to(EP)).replace("\\", "/"),
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "duration_seconds": 8,
        "fps": 30,
        "resolution": "1920x1080",
        "motion_arc": "audio deck illuminates and reels turn; target/response field illuminates; physiological recorder illuminates and blank scan line advances",
        "visible_mode_badge": False,
        "series_usage": "EP02_ONLY",
    }
    OUTPUT.with_suffix(".json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK {OUTPUT.name}")


if __name__ == "__main__":
    main()
