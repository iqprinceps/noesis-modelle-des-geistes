#!/usr/bin/env python3
"""Measure how evenly a Ken Burns move actually advances, per frame.

The complaint is that the moves judder. Measured on the delivered master, the
per-frame displacement of a 6.6 s shot was 0.126 px on average with a standard
deviation of 0.111 px: several frames completely still, then a hop. That is what
judder is.

The cause is arithmetic. A 3 percent zoom across 1920 px is 58 px of travel; over
197 frames that is 0.29 px per frame. zoompan positions its crop on whole pixels
of the working image, so at a 3840 px working width one step is 0.5 output px.
The move is smaller than the grid it has to land on.

This probe renders the same still several ways and reports which one advances
most evenly, so the fix is chosen on a number rather than on a hunch.
"""

from __future__ import annotations

import argparse
import pathlib
import subprocess

import numpy as np

FPS = 30


def render(src, out, dur, mode, zoom=0.030, work=3840, sub=4):
    frames = max(2, round(dur * FPS * sub))
    q = f"((on/{frames})*(on/{frames})*(3-2*(on/{frames})))"
    if mode == "zoompan":
        z = f"(1+{zoom:.5f}*{q})"
        vf = (f"scale={work}:{work*9//16}:force_original_aspect_ratio=increase,crop={work}:{work*9//16},"
              f"zoompan=z='{z}':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2':d=1:s=1920x1080:"
              f"fps={FPS*sub},tmix=frames={sub}:weights='{' '.join(['1']*sub)}',"
              f"framestep={sub},fps={FPS},format=yuv420p")
    elif mode == "perspective":
        # float corner coordinates, bilinear resampling: no integer crop anywhere
        n = max(2, round(dur * FPS))
        p = f"(on/{n})"
        qq = f"(({p})*({p})*(3-2*({p})))"
        m = f"({zoom:.5f}*{qq}/(1+{zoom:.5f}))"          # inset fraction per side
        x0 = f"W*{m}/2"; y0 = f"H*{m}/2"
        x1 = f"W-W*{m}/2"; y1 = f"H*{m}/2"
        x2 = f"W*{m}/2"; y2 = f"H-H*{m}/2"
        x3 = f"W-W*{m}/2"; y3 = f"H-H*{m}/2"
        vf = (f"scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
              f"perspective={x0}:{y0}:{x1}:{y1}:{x2}:{y2}:{x3}:{y3}:"
              f"interpolation=linear:sense=source:eval=frame,fps={FPS},format=yuv420p")
    else:
        raise SystemExit("unknown mode " + mode)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", str(src),
                    "-t", f"{dur:.3f}", "-vf", vf, "-c:v", "libx264", "-preset", "veryfast",
                    "-crf", "14", "-pix_fmt", "yuv420p", str(out)], check=True)
    return out


def steps(path, W=480, H=270):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-vf",
                          f"scale={W}:{H},format=gray", "-f", "rawvideo",
                          "-pix_fmt", "gray", "-"], capture_output=True).stdout
    n = len(raw) // (W * H)
    fr = np.frombuffer(raw, dtype=np.uint8)[:n * W * H].reshape(n, H, W).astype(np.float64)
    win = np.outer(np.hanning(H), np.hanning(W))

    def sh(a, b):
        A, B = np.fft.rfft2(a * win), np.fft.rfft2(b * win)
        R = A * np.conj(B)
        R /= (np.abs(R) + 1e-9)
        c = np.fft.irfft2(R, s=a.shape)
        p = np.unravel_index(np.argmax(c), c.shape)
        out = []
        for ax, size in ((0, H), (1, W)):
            i = p[ax]
            lo, hi = list(p), list(p)
            lo[ax], hi[ax] = (i - 1) % size, (i + 1) % size
            y0, y1, y2 = c[tuple(lo)], c[p], c[tuple(hi)]
            den = y0 - 2 * y1 + y2
            v = i + (0.5 * (y0 - y2) / den if abs(den) > 1e-12 else 0.0)
            out.append(v - size if v > size / 2 else v)
        return out[0] * (1080 / H), out[1] * (1920 / W)

    d = np.array([sh(fr[i], fr[i + 1]) for i in range(n - 1)])
    return np.hypot(d[:, 1], d[:, 0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--dur", type=float, default=6.0)
    ap.add_argument("--zoom", type=float, default=0.030)
    a = ap.parse_args()
    work = pathlib.Path("tmp/judder")
    work.mkdir(parents=True, exist_ok=True)
    trials = [(f"zoom {z:.0%} w{w} sub{sb}", dict(mode="zoompan", work=w, sub=sb, zoom=z))
              for z, w, sb in ((0.030, 3840, 4), (0.060, 3840, 4), (0.100, 3840, 4),
                               (0.150, 3840, 4), (0.100, 3840, 8), (0.100, 7680, 4))]
    print(f"{'variant':22s} {'mean':>7} {'sd':>7} {'sd/mean':>8} {'still frames':>13}")
    for label, kw in trials:
        out = work / (label.replace(" ", "_") + ".mp4")
        try:
            render(a.src, out, a.dur, **({"zoom": a.zoom} | kw))
            s = steps(out)
        except Exception as exc:
            print(f"{label:22s} FAIL {str(exc)[:60]}")
            continue
        still = int((s < 0.02).sum())
        print(f"{label:22s} {s.mean():7.3f} {s.std():7.3f} {s.std()/max(s.mean(),1e-6):8.2f} "
              f"{still:6d}/{len(s):<6d}")


if __name__ == "__main__":
    main()
