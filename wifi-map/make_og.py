#!/usr/bin/env python3
"""Build og.jpg for the measured Wi-Fi map.
Simple design: dark navy bg + Wi-Fi arcs + big white title. 1200x630."""
import os
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.expanduser("~/booking-trends-board/wifi-map")
W, H = 1200, 630
img = Image.new("RGB", (W, H), (10, 15, 30))
d = ImageDraw.Draw(img)

FONT_CANDIDATES = [
    "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/AppleSDGothicNeo.ttc",
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

# Wi-Fi symbol: three arcs + dot, cyan, left side
cx, cy = 250, 330          # dot center (bottom of the fan)
ACCENT = (56, 189, 248)
for r, w in ((90, 26), (165, 26), (240, 26)):
    d.arc([cx - r, cy - r, cx + r, cy + r], start=205, end=335, fill=ACCENT, width=w)
d.ellipse([cx - 26, cy - 26, cx + 26, cy + 26], fill=ACCENT)

# Accent underline
d.rectangle([cx - 150, cy + 62, cx + 150, cy + 72], fill=(226, 57, 46))

# Title / subtitle, right side (auto-fit so the title never clips)
TITLE = "実測Wi-Fiマップ"
size = 96
while size > 40:
    f_title = font(size)
    if d.textlength(TITLE, font=f_title) <= W - 550 - 36:
        break
    size -= 4
d.text((550, 190), TITLE, font=f_title, fill=(255, 255, 255))
f_sub = font(37)
d.text((554, 322), "近くて速いWi-Fiを、実測だけで選ぶ", font=f_sub, fill=(169, 182, 218))
f_foot = font(28)
d.text((554, 392), "秋葉原 ・ 錦糸町 — measured spots only", font=f_foot, fill=(120, 134, 170))

img.save(os.path.join(BASE, "og.jpg"), quality=88)
print("wrote", os.path.join(BASE, "og.jpg"), img.size)
