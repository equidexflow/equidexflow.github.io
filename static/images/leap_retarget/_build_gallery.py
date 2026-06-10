#!/usr/bin/env python3
"""Trim whitespace from LEAP retarget figures and composite into a single
3x4 collage matching the Allegro gallery style (white bg, uniform cells,
per-figure pixel scale preserved)."""
import os
from PIL import Image, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))

# Reading order = current .retarget-grid order in index.html
FIGURES = [
    "graspit_box__v0.png",
    "sns_cup__v0.png",
    "sugar_box__v0.png",
    "tennis_ball__v90.png",
    "tomato_soup_can__v0.png",
    "apple__v0.png",
    "egad_G6__v90.png",
    "cube__v0.png",
    "softball__v0.png",
    "egad_E4__v90.png",
    "egad_A4__v0.png",
    "egad_F6__v0.png",
]
COLS, ROWS = 6, 2
PAD = 28            # padding inside each cell, px
BG = (255, 255, 255)
THRESH = 8          # how far from white a pixel must be to count as content


def trim(im):
    """Crop to the bounding box of non-white content (with tolerance)."""
    rgb = im.convert("RGB")
    bg = Image.new("RGB", rgb.size, BG)
    diff = ImageChops.difference(rgb, bg)
    # collapse to a mask: any channel diff > THRESH
    mask = diff.convert("L").point(lambda p: 255 if p > THRESH else 0)
    bbox = mask.getbbox()
    return rgb.crop(bbox) if bbox else rgb


def main():
    trimmed = []
    for name in FIGURES:
        path = os.path.join(HERE, name)
        t = trim(Image.open(path))
        trimmed.append(t)
        print(f"{name}: {Image.open(path).size} -> {t.size}")

    cw = max(t.width for t in trimmed) + 2 * PAD
    ch = max(t.height for t in trimmed) + 2 * PAD
    print(f"cell = {cw}x{ch}  canvas = {cw*COLS}x{ch*ROWS}")

    canvas = Image.new("RGB", (cw * COLS, ch * ROWS), BG)
    for i, t in enumerate(trimmed):
        r, c = divmod(i, COLS)
        x = c * cw + (cw - t.width) // 2
        y = r * ch + (ch - t.height) // 2
        canvas.paste(t, (x, y))

    out = os.path.join(HERE, "leap_gallery_2x6.png")
    canvas.save(out)
    print(f"wrote {out}  {canvas.size}")


if __name__ == "__main__":
    main()
