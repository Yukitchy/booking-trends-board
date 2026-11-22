#!/usr/bin/env python3
"""Waisupi OGP 5 variants in Tadayomi composition:
left = confirmed logo (logo.png, artwork as-is), right = 2-line copy,
bottom = green band with a supplementary line. 1200x630, white base.
Run on m2: /opt/homebrew/bin/python3 make_ogp5.py
"""
import os
from PIL import Image, ImageChops, ImageDraw, ImageFont

BASE = os.path.expanduser("~/booking-trends-board/wifi-map")
OUT = os.path.join(BASE, "ogp-board")
os.makedirs(OUT, exist_ok=True)

W, H = 1200, 630
X0, XR = 80, 1120
INK = (26, 26, 26)
GREEN = (35, 227, 110)          # sampled from the logo artwork (#23E36E)
GREEN_DEEP = (22, 141, 68)      # same hue, darkened for white text
F = "/System/Library/Fonts/ヒラギノ角ゴシック W{}.ttc"

def font(w, s):
    return ImageFont.truetype(F.format(w), s)

def ink_bbox(im):
    d = ImageChops.difference(im, Image.new("RGB", im.size, "white")).convert("L")
    return d.point(lambda v: 255 if v > 24 else 0).getbbox()

LOGO = Image.open(os.path.join(BASE, "logo.png")).convert("RGB")
LOGO = LOGO.crop(ink_bbox(LOGO))

VARIANTS = [
    dict(name="01", logo_w=500, copy=["近くて速いWi-Fiが、", "すぐわかる。"],
         band_h=70, band_fill=GREEN, band_color=INK,
         band_text="実測した速度だけを載せるマップ"),
    dict(name="02", logo_w=620, copy=["載っている速度は、", "すべて実測。"],
         band_h=88, band_fill=GREEN_DEEP, band_color=(255, 255, 255),
         band_text="未計測の店は「未計測」と表示"),
    dict(name="03", logo_w=430, copy=["歩きながら探せる、", "実測Wi-Fiマップ。"],
         band_h=64, band_fill=GREEN, band_color=INK,
         band_text="近い順・速い順／電源ありで絞り込み"),
    dict(name="04", logo_w=540, copy=["SSIDもパスワードも、", "その場でわかる。"],
         band_h=76, band_fill=GREEN_DEEP, band_color=(255, 255, 255),
         band_text="自分で測って、スポット追加もできる"),
    dict(name="05", logo_w=470, copy=["カフェのWi-Fiを、", "速い順に探せる。"],
         band_h=80, band_fill=GREEN, band_color=INK,
         band_text="実測スポットを少しずつ追加中"),
]

def build(v):
    band_h = v["band_h"]
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)

    # logo: left, vertically centered in the area above the band
    lw = v["logo_w"]
    lh = round(LOGO.height * lw / LOGO.width)
    logo = LOGO.resize((lw, lh), Image.LANCZOS)
    logo_y = (H - band_h - lh) // 2
    im.paste(logo, (X0, logo_y))

    # copy: right column, W8, largest size that fits the column, lines left-aligned,
    # block centered in (right column x above-band area)
    x = X0 + lw + 44
    col_w = XR - x
    lines = v["copy"]
    size = 88
    while size > 30 and max(font(8, size).getlength(l) for l in lines) > col_w:
        size -= 1
    fc = font(8, size)
    lead = round(size * 1.36)
    block_w = max(fc.getlength(l) for l in lines)
    t = fc.getbbox(lines[0])[1]
    b = lead * (len(lines) - 1) + fc.getbbox(lines[-1])[3]
    cx, cy = (x + XR) / 2, (H - band_h) / 2
    lx = cx - block_w / 2
    y = cy - (t + b) / 2
    for i, l in enumerate(lines):
        d.text((lx, y + i * lead), l, font=fc, fill=INK, anchor="la")

    # band: full-width green strip, supplementary line at X0, vertically centered
    d.rectangle([0, H - band_h, W, H], fill=v["band_fill"])
    fb = font(7, 26 if band_h >= 76 else 24)
    d.text((X0, H - band_h / 2), v["band_text"], font=fb, fill=v["band_color"], anchor="lm")

    out = os.path.join(OUT, f"ogp-{v['name']}.png")
    im.save(out, optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes; logo", lw, "x", lh,
          "copy size", size, "col", col_w)
    return out

if __name__ == "__main__":
    for v in VARIANTS:
        build(v)
