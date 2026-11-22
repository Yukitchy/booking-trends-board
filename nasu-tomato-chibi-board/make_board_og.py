#!/usr/bin/env python3
"""Board og.jpg for the Nasu-Tomato chibi redesign board (10 variants):
standard comparison-board form. Black bg, white bold title, red underline,
10 variant thumbnails in a row with number badges. 1200x630. Run on m2."""
import os
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.expanduser("~/booking-trends-board/nasu-tomato-chibi-board")
W, H = 1200, 630
F = "/System/Library/Fonts/ヒラギノ角ゴシック W{}.ttc"
RED = (255, 59, 48)

im = Image.new("RGB", (W, H), (10, 10, 10))
d = ImageDraw.Draw(im)

title = "ナスとトマト ちびキャラ新デザイン10案"
ft = ImageFont.truetype(F.format(8), 52)
d.text((60, 52), title, font=ft, fill=(255, 255, 255), anchor="la")
d.rectangle([60, 140, 60 + 150, 150], fill=RED)
sub = "ナス＝男の子・トマト＝女の子、ちびキャラ×緩めデザインで自由に作り替えた10案"
fs = ImageFont.truetype(F.format(6), 26)
d.text((60, 178), sub, font=fs, fill=(200, 200, 200), anchor="la")

files = [f"v{i}.png" for i in range(1, 11)]
labels = [str(i) for i in range(1, 11)]
thumb = 102
gap = 8
total = thumb * 10 + gap * 9
x0 = (W - total) // 2
y0 = 320
fb = ImageFont.truetype(F.format(8), 22)
for i, (fn, lab) in enumerate(zip(files, labels)):
    t = Image.open(os.path.join(BASE, fn))
    if t.mode in ("RGBA", "LA"):
        bg = Image.new("RGB", t.size, (255, 255, 255))
        bg.paste(t, mask=t.split()[-1])
        t = bg
    else:
        t = t.convert("RGB")
    # center-crop to square then resize
    w, h = t.size
    s = min(w, h)
    t = t.crop(((w - s) // 2, (h - s) // 2, (w + s) // 2, (h + s) // 2)).resize((thumb, thumb), Image.LANCZOS)
    x = x0 + i * (thumb + gap)
    im.paste(t, (x, y0))
    d.rectangle([x, y0, x + thumb, y0 + thumb], outline=(90, 90, 90), width=1)
    cx, cy, r = x + 4, y0 + 4, 16
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
    d.text((cx, cy), lab, font=fb, fill=(255, 255, 255), anchor="mm")

out = os.path.join(BASE, "og.jpg")
im.save(out, quality=88, optimize=True)
print("wrote", out, os.path.getsize(out), "bytes")
