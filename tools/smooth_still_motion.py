#!/usr/bin/env python3
"""Shared FFmpeg filter builder for smooth motion on still images.

`zoompan` rounds crop coordinates to source pixels. Rendering directly from
the delivery-sized frame therefore creates visible stepwise motion. This
module makes the project-wide production rule executable: spatial 4x
supersampling, four temporal subframes per delivery frame, an eased path and
temporal averaging before returning to the episode frame rate.
"""

from __future__ import annotations


ENGINE_VERSION = 1
SUPERSAMPLE_WIDTH = 7680
SUPERSAMPLE_HEIGHT = 4320
TEMPORAL_SUBFRAMES = 4


def eased_zoompan_filter(
    *,
    duration: float,
    fps: int,
    width: int,
    height: int,
    x_bias: float = 0.5,
    y_bias: float = 0.5,
    zoom_amount: float = 0.025,
    background: str = "black",
) -> str:
    """Return a smooth, duration-exact FFmpeg filter for one still image."""

    if duration <= 0:
        raise ValueError("duration must be positive")
    if fps <= 0 or width <= 0 or height <= 0:
        raise ValueError("fps and output dimensions must be positive")

    x_bias = min(0.9, max(0.1, float(x_bias)))
    y_bias = min(0.9, max(0.1, float(y_bias)))
    zoom_amount = min(0.08, max(0.002, float(zoom_amount)))

    output_frames = max(2, round(duration * fps))
    sub_fps = fps * TEMPORAL_SUBFRAMES
    sub_frames = max(2, output_frames * TEMPORAL_SUBFRAMES)
    progress = f"(0.5-0.5*cos(PI*on/{sub_frames - 1}))"
    weights = " ".join("1" for _ in range(TEMPORAL_SUBFRAMES))

    return (
        f"scale={SUPERSAMPLE_WIDTH}:{SUPERSAMPLE_HEIGHT}:"
        "force_original_aspect_ratio=decrease:flags=lanczos,"
        f"pad={SUPERSAMPLE_WIDTH}:{SUPERSAMPLE_HEIGHT}:"
        f"(ow-iw)/2:(oh-ih)/2:color={background},"
        "loop=loop=-1:size=1:start=0,"
        f"fps={sub_fps},"
        f"zoompan=z='1+{zoom_amount:.6f}*{progress}':"
        f"x='(iw-iw/zoom)*{x_bias:.6f}':"
        f"y='(ih-ih/zoom)*{y_bias:.6f}':"
        f"d=1:s={width}x{height}:fps={sub_fps},"
        f"tmix=frames={TEMPORAL_SUBFRAMES}:weights='{weights}',"
        f"fps={fps},trim=duration={duration:.6f},"
        "setpts=PTS-STARTPTS,format=yuv420p"
    )

