#!/usr/bin/env python3
"""Board og.jpg for the Nasu-Tomato face redesign board: standard comparison-board form.
Black bg, white bold title, red underline, current + 5 variant thumbnails in a row
with badges. 1200x630. Run on m2."""
import os
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.expanduser("~/booking-trends-board/nasu-tomato-face-board")
W, H = 1200, 630
F = "/System/Library/Fonts/ヒラギノ角ゴシック W{}.ttc"
RED = (255, 59, 48)
GRAY = (130, 130, 130)

im = Image.new("RGB", (W, H), (10, 10, 10))
d = ImageDraw.Draw(im)

title = "ナスとトマト 顔・手足リニューアル5案"
ft = ImageFont.truetype(F.format(8), 52)
d.text((60, 52), title, font=ft, fill=(255, 255, 255), anchor="la")
d.rectangle([60, 140, 60 + 150, 150], fill=RED)
sub = "体は現行のまま、顔パーツと手足だけを段家テイストに作り直した5案"
fs = ImageFont.truetype(F.format(6), 26)
d.text((60, 178), sub, font=fs, fill=(200, 200, 200), anchor="la")

files = ["current.png", "v1.png", "v2.png", "v3.png", "v4.png", "v5.png"]
labels = ["現", "1", "2", "3", "4", "5"]
thumb = 180
gap = 14
total = thumb * 6 + gap * 5
x0 = (W - total) // 2
y0 = 300
fb = ImageFont.truetype(F.format(8), 24)
for i, (fn, lab) in enumerate(zip(files, labels)):
    t = Image.open(os.path.join(BASE, fn))
    if t.mode in ("RGBA", "LA"):
        bg = Image.new("RGB", t.size, (255, 255, 255))
        bg.paste(t, mask=t.split()[-1])
        t = bg
    else:
        t = t.convert("RGB")
    t = t.resize((thumb, thumb), Image.LANCZOS)
    x = x0 + i * (thumb + gap)
    im.paste(t, (x, y0))
    d.rectangle([x, y0, x + thumb, y0 + thumb], outline=(90, 90, 90), width=1)
    cx, cy, r = x + 4, y0 + 4, 18
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED if lab != "現" else GRAY)
    d.text((cx, cy), lab, font=fb, fill=(255, 255, 255), anchor="mm")

out = os.path.join(BASE, "og.jpg")
im.save(out, quality=88, optimize=True)
print("wrote", out, os.path.getsize(out), "bytes")
