#!/usr/bin/env python3
"""Waisupi OGP round 2: polish round-1 variant 1.
Fix per Yuuki: logo ink height matched to the 2-line copy ink height
(round 1 was logo 76px vs copy 117px). Copy text, band text and colors
are unchanged from round-1 variant 1. 1200x630, white base.
Run on m2: /opt/homebrew/bin/python3 make_ogp5_v2.py
"""
import os
from PIL import Image, ImageChops, ImageDraw, ImageFont

BASE = os.path.expanduser("~/booking-trends-board/wifi-map")
OUT = os.path.join(BASE, "ogp-board2")
os.makedirs(OUT, exist_ok=True)

W, H = 1200, 630
INK = (26, 26, 26)
GREEN = (35, 227, 110)          # #23E36E, sampled from the logo artwork
F = "/System/Library/Fonts/ヒラギノ角ゴシック W{}.ttc"
COPY = ["近くて速いWi-Fiが、", "すぐわかる。"]
BAND_TEXT = "実測した速度だけを載せるマップ"

def font(w, s):
    return ImageFont.truetype(F.format(w), s)

def ink_bbox(im):
    d = ImageChops.difference(im.convert("RGB"), Image.new("RGB", im.size, "white")).convert("L")
    return d.point(lambda v: 255 if v > 24 else 0).getbbox()

LOGO = Image.open(os.path.join(BASE, "logo.png")).convert("RGB")
LOGO = LOGO.crop(ink_bbox(LOGO))
ASPECT = LOGO.width / LOGO.height

def copy_image(size):
    """Render the 2-line copy and crop to its ink bbox."""
    fc = font(8, size)
    lead = round(size * 1.36)
    w = int(max(fc.getlength(l) for l in COPY)) + 60
    h = lead + size * 2 + 60
    layer = Image.new("RGB", (w, h), "white")
    d = ImageDraw.Draw(layer)
    for i, l in enumerate(COPY):
        d.text((30, 30 + i * lead), l, font=fc, fill=INK, anchor="la")
    return layer.crop(ink_bbox(layer))

VARIANTS = [
    # 1: logo height == copy height, exactly
    dict(name="01", x0=80, xr=1120, gap=44, ratio=1.00, band_h=70, band_fs=24),
    # 2: logo a touch larger than the copy (+6%)
    dict(name="02", x0=80, xr=1120, gap=44, ratio=1.06, band_h=70, band_fs=24),
    # 3: wider gap between logo and copy
    dict(name="03", x0=80, xr=1120, gap=84, ratio=1.00, band_h=70, band_fs=24),
    # 4: whole lockup a bit larger (narrower side margins)
    dict(name="04", x0=56, xr=1144, gap=44, ratio=1.00, band_h=70, band_fs=24),
    # 5: thicker band, larger band text
    dict(name="05", x0=80, xr=1120, gap=44, ratio=1.00, band_h=88, band_fs=28),
]

def region_ink_h(im, box):
    reg = im.crop(box)
    bb = ink_bbox(reg)
    return (bb[3] - bb[1]) if bb else 0

def build(v):
    x0, xr, gap, ratio = v["x0"], v["xr"], v["gap"], v["ratio"]
    band_h, band_fs = v["band_h"], v["band_fs"]
    avail = xr - x0 - gap
    chosen = None
    for size in range(100, 29, -1):
        cimg = copy_image(size)
        hc, cw = cimg.height, cimg.width
        lh = round(ratio * hc)
        lw = round(lh * ASPECT)
        if lw + cw <= avail:
            chosen = (size, cimg, hc, cw, lh, lw)
            break
    size, cimg, hc, cw, lh, lw = chosen

    im = Image.new("RGB", (W, H), "white")
    cy = (H - band_h) // 2
    im.paste(LOGO.resize((lw, lh), Image.LANCZOS), (x0, cy - lh // 2))
    copy_x = x0 + lw + gap
    im.paste(cimg, (copy_x, cy - hc // 2))

    d = ImageDraw.Draw(im)
    d.rectangle([0, H - band_h, W, H], fill=GREEN)
    fb = font(7, band_fs)
    d.text((x0, H - band_h / 2), BAND_TEXT, font=fb, fill=INK, anchor="lm")

    out = os.path.join(OUT, f"ogp-{v['name']}.png")
    im.save(out, optimize=True)

    mid = copy_x - gap // 2
    logo_h_meas = region_ink_h(im, (0, 0, mid, H - band_h))
    copy_h_meas = region_ink_h(im, (mid, 0, W, H - band_h))
    print(f"ogp-{v['name']}: font={size} logo={lw}x{lh} (meas {logo_h_meas}) "
          f"copy_h={hc} (meas {copy_h_meas}) copy_w={cw} gap={gap} "
          f"band_h={band_h} band_fs={band_fs} bytes={os.path.getsize(out)}")
    return out

if __name__ == "__main__":
    for v in VARIANTS:
        build(v)
