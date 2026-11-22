#!/usr/bin/env python3
"""Board og.jpg for the Waisupi OGP board round 3: standard comparison-board form.
Black bg, white bold title, red underline, 5 variant thumbnails in a row
with number badges. 1200x630. Run on m2."""
import os
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.expanduser("~/booking-trends-board/wifi-map/ogp-board3")
W, H = 1200, 630
F = "/System/Library/Fonts/ヒラギノ角ゴシック W{}.ttc"
RED = (255, 59, 48)

im = Image.new("RGB", (W, H), (10, 10, 10))
d = ImageDraw.Draw(im)

title = "ワイスピ OGP案 スクショ入り5案"
ft = ImageFont.truetype(F.format(8), 56)
d.text((60, 52), title, font=ft, fill=(255, 255, 255), anchor="la")
d.rectangle([60, 140, 60 + 150, 150], fill=RED)
sub = "実画面のスクショ入り・ロゴとコピーの縦幅は全案一致"
fs = ImageFont.truetype(F.format(6), 26)
d.text((60, 178), sub, font=fs, fill=(200, 200, 200), anchor="la")

thumb_w = 204
thumb_h = round(thumb_w * 630 / 1200)
gap = 16
total = thumb_w * 5 + gap * 4
x0 = (W - total) // 2
y0 = 300
fb = ImageFont.truetype(F.format(8), 24)
for i in range(1, 6):
    t = Image.open(os.path.join(BASE, f"ogp-0{i}.png")).convert("RGB")
    t = t.resize((thumb_w, thumb_h), Image.LANCZOS)
    x = x0 + (i - 1) * (thumb_w + gap)
    im.paste(t, (x, y0))
    d.rectangle([x, y0, x + thumb_w, y0 + thumb_h], outline=(90, 90, 90), width=1)
    cx, cy, r = x + 4, y0 + 4, 18
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
    d.text((cx, cy), str(i), font=fb, fill=(255, 255, 255), anchor="mm")

out = os.path.join(BASE, "og.jpg")
im.save(out, quality=88, optimize=True)
print("wrote", out, os.path.getsize(out), "bytes")
