#!/usr/bin/env python3
"""Waisupi OGP round 4: polish of round-3 variant 5 (phone + enlarged
close-up panel). Both screenshots are REAL captures of the live page,
taken via CDP with sort=speed and the map zoomed in, so the measured
Sarutahiko card (down 199 / up 152.2 Mbps, green badge + speed bar)
is what shows. 1200x630, white base, green band.
Run on m2: /opt/homebrew/bin/python3 make_ogp5_v4.py
"""
import os
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

BASE = os.path.expanduser("~/booking-trends-board/wifi-map")
OUT = os.path.join(BASE, "ogp-board4")
os.makedirs(OUT, exist_ok=True)

W, H = 1200, 630
INK = (26, 26, 26)
GREEN = (35, 227, 110)          # #23E36E, sampled from the logo artwork
BAND_H = 70
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

FULL = Image.open(os.path.join(OUT, "src-speed-full.png")).convert("RGB")    # 780x1688 DSF2
POPSHOT = Image.open(os.path.join(OUT, "src-speed-popup.png")).convert("RGB")  # 780x1688 DSF2
CARD = FULL.crop((13, 1472, 492, 1664))        # 479x192: Sarutahiko strip card
POP = POPSHOT.crop((30, 250, 750, 624))        # 720x374: popup photo+name+speed+password

def copy_image(size):
    fc = font(8, size)
    lead = round(size * 1.36)
    w = int(max(fc.getlength(l) for l in COPY)) + 60
    h = lead + size * 2 + 60
    layer = Image.new("RGB", (w, h), "white")
    d = ImageDraw.Draw(layer)
    for i, l in enumerate(COPY):
        d.text((30, 30 + i * lead), l, font=fc, fill=INK, anchor="la")
    return layer.crop(ink_bbox(layer))

def fit_lockup(zone_w, cap_h):
    """(logo_img, copy_img, h) with logo ink height == copy ink height."""
    for size in range(110, 29, -1):
        c = copy_image(size)
        if c.height > cap_h:
            continue
        lh = c.height
        lw = round(lh * ASPECT)
        if lw <= zone_w and c.width <= zone_w:
            return LOGO.resize((lw, lh), Image.LANCZOS), c, lh
    raise AssertionError("no fit")

def cover_crop_bias(im, tw, th, bias=0.35):
    """Cover-crop to tw x th; bias = fraction of vertical overflow cut from top."""
    s = max(tw / im.width, th / im.height)
    nw, nh = round(im.width * s), round(im.height * s)
    r = im.resize((nw, nh), Image.LANCZOS)
    x = (nw - tw) // 2
    y = int((nh - th) * bias)
    return r.crop((x, y, x + tw, y + th))

def rounded_mask(size, radius):
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius=radius, fill=255)
    return m

def phone_frame(img, fw, fh, bias=0.35):
    pad = 26
    cw, ch = fw + pad * 2, fh + pad * 2
    layer = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ds = ImageDraw.Draw(sh)
    ds.rounded_rectangle([pad, pad + 10, pad + fw, pad + fh + 10], radius=36, fill=(0, 0, 0, 90))
    sh = sh.filter(ImageFilter.GaussianBlur(12))
    layer = Image.alpha_composite(layer, sh)
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([pad, pad, pad + fw, pad + fh], radius=36, fill=(18, 18, 18, 255))
    inset = 9
    iw, ih = fw - inset * 2, fh - inset * 2
    shot = cover_crop_bias(img, iw, ih, bias)
    layer.paste(shot, (pad + inset, pad + inset), rounded_mask((iw, ih), 27))
    return layer, pad

def panel(crop, target_w):
    """Enlarged close-up panel: white border + soft shadow (v5 style)."""
    tw = target_w
    th = round(crop.height * tw / crop.width)
    img = crop.resize((tw, th), Image.LANCZOS)
    layer = Image.new("RGBA", (tw + 12, th + 12), (0, 0, 0, 0))
    sh = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([6, 12, tw + 6, th + 12], radius=12, fill=(0, 0, 0, 85))
    sh = sh.filter(ImageFilter.GaussianBlur(8))
    layer = Image.alpha_composite(layer, sh)
    layer.paste(img, (6, 6), rounded_mask((tw, th), 10))
    ImageDraw.Draw(layer).rounded_rectangle([6, 6, tw + 5, th + 5], radius=10, outline=(255, 255, 255, 255), width=3)
    return layer, tw, th

def base_canvas():
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    d.rectangle([0, H - BAND_H, W, H], fill=GREEN)
    d.text((56, H - BAND_H / 2), BAND_TEXT, font=font(7, 24), fill=INK, anchor="lm")
    return im

def paste_rgba(im, layer, pad, x, y):
    im.paste(layer, (x - pad, y - pad), layer)

def draw_lockup(im, zone_w, cap_h, gap=32):
    logo, copy, h = fit_lockup(zone_w, cap_h)
    total_h = h * 2 + gap
    y0 = (H - BAND_H - total_h) // 2
    im.paste(logo, (56, y0))
    im.paste(copy, (56, y0 + h + gap))
    return h, logo.width, copy.width

def save(im, name):
    out = os.path.join(OUT, f"ogp-{name}.png")
    im.convert("RGB").save(out, optimize=True)
    print(f"ogp-{name}: bytes={os.path.getsize(out)}")
    return out

# ---------- Variant 1: polished v5 - speed card close-up, standard size
def v1():
    im = base_canvas()
    layer, pad = phone_frame(FULL, 252, 505)
    paste_rgba(im, layer, pad, 892, 28)
    p, tw, th = panel(CARD, 412)
    im.paste(p, (610, 368), p)
    h, lw, cw2 = draw_lockup(im, 610 - 56 - 18, 86)
    print("v1 lockup h:", h, "logo w:", lw, "copy w:", cw2, "panel:", tw, th)
    return save(im, "01")

# ---------- Variant 2: phone shows the popup (speed text), card close-up below
def v2():
    im = base_canvas()
    layer, pad = phone_frame(POPSHOT, 252, 505)
    paste_rgba(im, layer, pad, 892, 28)
    p, tw, th = panel(CARD, 396)
    im.paste(p, (624, 378), p)
    h, lw, cw2 = draw_lockup(im, 624 - 56 - 18, 86)
    print("v2 lockup h:", h, "logo w:", lw, "copy w:", cw2, "panel:", tw, th)
    return save(im, "02")

# ---------- Variant 3: biggest phone, biggest card panel (most zoomed-in feel)
def v3():
    im = base_canvas()
    layer, pad = phone_frame(FULL, 270, 524, bias=0.30)
    paste_rgba(im, layer, pad, 874, 18)
    p, tw, th = panel(CARD, 452)
    im.paste(p, (578, 352), p)
    h, lw, cw2 = draw_lockup(im, 578 - 56 - 18, 82)
    print("v3 lockup h:", h, "logo w:", lw, "copy w:", cw2, "panel:", tw, th)
    return save(im, "03")

# ---------- Variant 4: popup close-up panel (photo + name + speed line)
def v4():
    im = base_canvas()
    layer, pad = phone_frame(FULL, 246, 495)
    paste_rgba(im, layer, pad, 898, 34)
    p, tw, th = panel(POP, 452)
    im.paste(p, (584, 302), p)
    h, lw, cw2 = draw_lockup(im, 584 - 56 - 18, 82)
    print("v4 lockup h:", h, "logo w:", lw, "copy w:", cw2, "panel:", tw, th)
    return save(im, "04")

# ---------- Variant 5: extra-large card panel, lowest position
def v5():
    im = base_canvas()
    layer, pad = phone_frame(FULL, 252, 505)
    paste_rgba(im, layer, pad, 892, 28)
    p, tw, th = panel(CARD, 488)
    im.paste(p, (562, 348), p)
    h, lw, cw2 = draw_lockup(im, 562 - 56 - 18, 80)
    print("v5 lockup h:", h, "logo w:", lw, "copy w:", cw2, "panel:", tw, th)
    return save(im, "05")

if __name__ == "__main__":
    v1(); v2(); v3(); v4(); v5()
