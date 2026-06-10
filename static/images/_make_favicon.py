#!/usr/bin/env python3
"""Generate EquiDexFlow favicons.

Concept: green->teal gradient rounded tile (site --gradient-start/-end) with a
white rotation arc + arrowhead (SE(3) equivariance / flow) encircling a
three-point grasp triad (dexterous contacts).
"""
import os, math
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
S = 16          # supersample factor
B = 64          # base (reference) size
W = B * S
C0 = (54, 161, 116)   # hsl(155,50%,42%) brand green  -> top-left
C1 = (52, 130, 179)   # hsl(200,55%,45%) teal          -> bottom-right


def gradient_tile():
    yy, xx = np.mgrid[0:W, 0:W].astype(np.float32)
    t = (xx + yy) / (2 * (W - 1))
    rgb = np.empty((W, W, 3), np.float32)
    for k in range(3):
        rgb[..., k] = C0[k] + (C1[k] - C0[k]) * t
    img = Image.fromarray(rgb.astype(np.uint8), "RGB").convert("RGBA")
    # rounded-rect alpha mask
    mask = Image.new("L", (W, W), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([0, 0, W - 1, W - 1], radius=int(0.235 * W), fill=255)
    img.putalpha(mask)
    return img


def draw_glyph(img):
    d = ImageDraw.Draw(img)
    cx = cy = W / 2
    white = (255, 255, 255, 255)

    # --- rotation arc (flow / equivariance) ---
    ra = 0.30 * W                 # arc radius
    lw = int(0.072 * W)           # stroke width
    start, end = 160, 70          # leaves a gap, sweeps clockwise through 360
    d.arc([cx - ra, cy - ra, cx + ra, cy + ra], start=start, end=end,
          fill=white, width=lw)
    # arrowhead at the arc end (angle `end`), pointing tangentially
    a = math.radians(end)
    ex, ey = cx + ra * math.cos(a), cy + ra * math.sin(a)
    tang = a + math.pi / 2        # clockwise tangent
    ah = 0.12 * W                 # arrowhead size
    tip = (ex + ah * math.cos(tang), ey + ah * math.sin(tang))
    b1 = (ex + 0.55 * ah * math.cos(a), ey + 0.55 * ah * math.sin(a))
    b2 = (ex - 0.55 * ah * math.cos(a), ey - 0.55 * ah * math.sin(a))
    d.polygon([tip, b1, b2], fill=white)

    # --- grasp triad: three contacts on a central object ---
    obj_r = 0.052 * W
    d.ellipse([cx - obj_r, cy - obj_r, cx + obj_r, cy + obj_r], fill=white)
    rr = 0.155 * W                # contact ring radius
    tip_r = 0.058 * W             # fingertip dot radius
    for ang in (-90, 30, 150):
        a = math.radians(ang)
        px, py = cx + rr * math.cos(a), cy + rr * math.sin(a)
        d.line([cx, cy, px, py], fill=white, width=int(0.040 * W))
        d.ellipse([px - tip_r, py - tip_r, px + tip_r, py + tip_r], fill=white)
    return img


def main():
    img = draw_glyph(gradient_tile())
    base = img.resize((B * 4, B * 4), Image.LANCZOS)  # high-res master

    png32 = base.resize((32, 32), Image.LANCZOS)
    png16 = base.resize((16, 16), Image.LANCZOS)
    apple = base.resize((180, 180), Image.LANCZOS)
    master = base.resize((256, 256), Image.LANCZOS)

    png32.save(os.path.join(HERE, "favicon-32x32.png"))
    png16.save(os.path.join(HERE, "favicon-16x16.png"))
    apple.save(os.path.join(HERE, "apple-touch-icon.png"))
    master.save(os.path.join(HERE, "favicon-256.png"))
    # multi-size .ico for legacy
    master.save(os.path.join(HERE, "favicon.ico"),
                sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
    print("wrote favicon-16/32, apple-touch-icon (180), favicon-256, favicon.ico")


if __name__ == "__main__":
    main()
