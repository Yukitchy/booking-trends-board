#!/usr/bin/env python3
"""Build og.jpg for the ANIMAX minutes comparison board.
Standard format: black bg + big white bold title + short red underline
+ a row of the 5 actual design screenshots."""
import os
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.expanduser("~/booking-trends-board/animax-minutes")
W, H = 1200, 630
img = Image.new("RGB", (W, H), (10, 10, 10))
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

title = "ANIMAX打ち上げ議事録 デザイン5案"
f_title = font(58)
d.text((56, 42), title, font=f_title, fill=(255, 255, 255))
d.rectangle([58, 128, 58 + 110, 137], fill=(226, 57, 46))
f_sub = font(25)
d.text((58, 152), "2026-11-21 ライブ帰りの議事録A「秋田民泊とAI活用談義」", font=f_sub, fill=(170, 170, 170))

shots = [os.path.join(BASE, f"shot-v{i}.png") for i in range(1, 6)]
margin, gap = 56, 16
tw_each = (W - 2 * margin - (len(shots) - 1) * gap) // len(shots)
top = 224
th_each = 340
for i, path in enumerate(shots):
    s = Image.open(path).convert("RGB")
    crop_h = int(s.width * th_each / tw_each)
    if crop_h > s.height:
        crop_h = s.height
    s = s.crop((0, 0, s.width, crop_h)).resize((tw_each, th_each))
    x = margin + i * (tw_each + gap)
    img.paste(s, (x, top))
    d.rectangle([x, top, x + tw_each - 1, top + th_each - 1], outline=(70, 70, 70), width=2)
    r = 17
    cx, cy = x + 24, top + 24
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(226, 57, 46))
    f_num = font(24)
    label = str(i + 1)
    try:
        nw = d.textlength(label, font=f_num)
    except Exception:
        nw = 14
    d.text((cx - nw / 2, cy - 15), label, font=f_num, fill=(255, 255, 255))

out = os.path.join(BASE, "og.jpg")
img.save(out, quality=88)
print("saved", out, os.path.getsize(out))
