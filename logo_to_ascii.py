#!/usr/bin/env python3
"""
Turns a high-contrast logo (e.g. black mark on cyan / transparent) into
portrait.txt for the profile card. PNG/JPEG/WebP are all fine — no SVG needed.

    pip install pillow numpy
    python logo_to_ascii.py logos_www_marlonii-ColorLogo.png
    python generate_profile.py

Unlike photo_to_ascii.py this does not use rembg; it thresholds dark ink
against a bright/transparent background.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

SRC = sys.argv[1] if len(sys.argv) > 1 else "logos_www_marlonii-ColorLogo.png"
COLS = 88
ASPECT = 1.72          # must match generate_profile.py ART_LH / ART_CW
INK_LUMA = 80          # pixels darker than this become ink
MASK = 0.35            # after resize, keep cells above this ink density
PAD = 40
RAMP = "@%#*+=-:. "    # darkest -> lightest


def main():
    im = Image.open(SRC).convert("RGBA")
    arr = np.asarray(im)
    rgb = arr[:, :, :3].astype(float)
    alpha = arr[:, :, 3].astype(float) / 255.0
    luma = 0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]
    ink = (luma < INK_LUMA) & (alpha > 0.5)

    ys, xs = np.nonzero(ink)
    if len(xs) == 0:
        raise SystemExit(f"no dark ink found in {SRC}")

    x0 = max(0, int(xs.min()) - PAD)
    x1 = min(arr.shape[1], int(xs.max()) + PAD + 1)
    y0 = max(0, int(ys.min()) - PAD)
    y1 = min(arr.shape[0], int(ys.max()) + PAD + 1)
    ink = ink[y0:y1, x0:x1].astype(np.float32)
    h, w = ink.shape

    rows = max(1, int(COLS * (h / w) / ASPECT))
    small = np.asarray(
        Image.fromarray((ink * 255).astype(np.uint8)).resize((COLS, rows), Image.LANCZOS),
        dtype=float,
    ) / 255.0

    n = len(RAMP) - 1
    lines = []
    for y in range(rows):
        line = "".join(
            RAMP[round((1.0 - small[y, x]) * n)] if small[y, x] > MASK else " "
            for x in range(COLS)
        )
        lines.append(line.rstrip())

    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()

    text = "\n".join(lines)
    Path(__file__).parent.joinpath("portrait.txt").write_text(text, encoding="utf-8")
    print(text)
    print(f"\nwrote portrait.txt  ({COLS} cols x {len(lines)} rows)")


if __name__ == "__main__":
    main()
