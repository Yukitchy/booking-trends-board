#!/usr/bin/env python3
"""Board og.jpg for the Nasu head-item board (current + 4 patterns):
standard comparison-board form. Black bg, white bold title, red underline,
5 thumbnails in a row with badges (gray 'current' + red numbers). 1200x630.
Run on m2."""
import os
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.expanduser("~/booking-trends-board/nasu-tomato-head-board")
W, H = 1200, 630
F = "/System/Library/Fonts/ヒラギノ角ゴシック W{}.ttc"
RED = (255, 59, 48)
GRAY = (140, 140, 140)

im = Image.new("RGB", (W, H), (10, 10, 10))
d = ImageDraw.Draw(im)

title = "ナスとトマト ナスの頭アイテム4パターン"
ft = ImageFont.truetype(F.format(8), 52)
d.text((60, 52), title, font=ft, fill=(255, 255, 255), anchor="la")
d.rectangle([60, 140, 60 + 150, 150], fill=RED)
sub = "現行＝縞ハチマキ／1＝ヘアバンド黒／2＝キャップ赤／3＝キャップ紺／4＝キャップ黒"
fs = ImageFont.truetype(F.format(6), 26)
d.text((60, 178), sub, font=fs, fill=(200, 200, 200), anchor="la")

files = [f"v{i}.png" for i in range(5)]
labels = ["現", "1", "2", "3", "4"]
colors = [GRAY, RED, RED, RED, RED]
thumb = 190
gap = 14
total = thumb * 5 + gap * 4
x0 = (W - total) // 2
y0 = 300
fb = ImageFont.truetype(F.format(8), 30)
for i, (fn, lab, col) in enumerate(zip(files, labels, colors)):
    t = Image.open(os.path.join(BASE, fn))
    if t.mode in ("RGBA", "LA"):
        bg = Image.new("RGB", t.size, (255, 255, 255))
        bg.paste(t, mask=t.split()[-1])
        t = bg
    else:
        t = t.convert("RGB")
    w, h = t.size
    s = min(w, h)
    t = t.crop(((w - s) // 2, (h - s) // 2, (w + s) // 2, (h + s) // 2)).resize((thumb, thumb), Image.LANCZOS)
    x = x0 + i * (thumb + gap)
    im.paste(t, (x, y0))
    d.rectangle([x, y0, x + thumb, y0 + thumb], outline=(90, 90, 90), width=1)
    cx, cy, r = x + 6, y0 + 6, 24
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    d.text((cx, cy), lab, font=fb, fill=(255, 255, 255), anchor="mm")

out = os.path.join(BASE, "og.jpg")
im.save(out, quality=88, optimize=True)
print("wrote", out, os.path.getsize(out), "bytes")
