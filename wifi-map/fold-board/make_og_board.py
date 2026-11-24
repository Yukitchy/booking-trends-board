#!/usr/bin/env python3
"""Compose og.jpg for the fold-board: black bg, white bold title, red underline,
5 option screenshots in a row. 1200x630."""
import os
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.expanduser("~/booking-trends-board/wifi-map/fold-board")
W, H = 1200, 630
img = Image.new("RGB", (W, H), (8, 8, 8))
d = ImageDraw.Draw(img)

FONT_CANDIDATES = [
    "/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc",
    "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
]


def font(size):
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            for idx in range(0, 12):
                try:
                    return ImageFont.truetype(path, size, index=idx)
                except Exception:
                    break
    return ImageFont.load_default()


TITLE = "ワイスピ 任意項目トグル 5案"
size = 72
while size > 30:
    f = font(size)
    if d.textlength(TITLE, font=f) <= W - 120:
        break
    size -= 2
tw = d.textlength(TITLE, font=f)
x = (W - tw) / 2
d.text((x, 42), TITLE, font=f, fill=(255, 255, 255))
d.rectangle([x, 42 + size + 18, x + tw, 42 + size + 26], fill=(217, 35, 35))

# Screenshots row
shots = []
for i in range(1, 6):
    p = os.path.join(BASE, f"shot-v{i}.png")
    s = Image.open(p).convert("RGB")
    # stage is 390 CSS px centered in a 500 CSS px window at 2x scale:
    # stage left = (500-390)/2 = 55 CSS -> 110 device; panel margin 8 -> +16
    s = s.crop((126, 16, 874, 1476))
    shots.append(s)

target_h = 400
resized = []
for s in shots:
    w = int(s.width * target_h / s.height)
    resized.append(s.resize((w, target_h), Image.LANCZOS))

gap = 14
total_w = sum(s.width for s in resized) + gap * (len(resized) - 1)
sx = (W - total_w) // 2
sy = 185
for i, s in enumerate(resized):
    img.paste(s, (sx, sy))
    # number badge
    bx, by = sx + 8, sy + 8
    d.ellipse([bx, by, bx + 44, by + 44], fill=(16, 20, 16))
    nf = font(26)
    label = str(i + 1)
    lw = d.textlength(label, font=nf)
    d.text((bx + (44 - lw) / 2, by + 5), label, font=nf, fill=(255, 255, 255))
    sx += s.width + gap

img.save(os.path.join(BASE, "og.jpg"), quality=88)
print("wrote og.jpg", img.size)
