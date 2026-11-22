#!/usr/bin/env python3
"""OGP v2 for Waisupi: white bg + big confirmed logo (speedline, board3 #3). 1200x630."""
import os
from PIL import Image

BASE = os.path.expanduser("~/booking-trends-board/wifi-map")
W, H = 1200, 630
img = Image.new("RGB", (W, H), (255, 255, 255))

logo = Image.open(os.path.join(BASE, "logo.png")).convert("RGB")
target_w = 940
scale = target_w / logo.width
target_h = round(logo.height * scale)
logo_big = logo.resize((target_w, target_h), Image.LANCZOS)
x = (W - target_w) // 2
y = (H - target_h) // 2
img.paste(logo_big, (x, y))

out = os.path.join(BASE, "ogp-waisupi-20261122.png")
img.save(out)
print("wrote", out, img.size, os.path.getsize(out), "bytes; logo at", x, y, target_w, target_h)
