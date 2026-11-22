#!/usr/bin/env python3
"""Waisupi OGP round 3: base = board2 variant 4 composition
(logo ink height == 2-line copy ink height, green band at bottom),
plus a REAL screenshot of the live page (390 CSS px rendering)
shown in 5 different ways. 1200x630, white base.
Run on m2: /opt/homebrew/bin/python3 make_ogp5_v3.py
"""
import os
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

BASE = os.path.expanduser("~/booking-trends-board/wifi-map")
OUT = os.path.join(BASE, "ogp-board3")
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

SHOT = Image.open(os.path.join(OUT, "src-shot.png")).convert("RGB")  # 390x844 real capture
SHOT_WIDE = Image.open(os.path.join(OUT, "src-shot-wide.png")).convert("RGB")  # 760x844 real capture

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

def fit_lockup(zone_w, cap_h, stacked=True):
    """Return (logo_img, copy_img, h) with logo ink height == copy ink height,
    both fitting zone_w. For side-by-side, combined width must fit zone_w."""
    best = None
    for size in range(110, 29, -1):
        c = copy_image(size)
        if c.height > cap_h:
            continue
        lh = c.height
        lw = round(lh * ASPECT)
        if stacked:
            ok = (lw <= zone_w and c.width <= zone_w)
        else:
            ok = (lw + 44 + c.width <= zone_w)
        if ok:
            best = (LOGO.resize((lw, lh), Image.LANCZOS), c, lh)
            break
    assert best, "no fit"
    return best

def cover_crop(im, tw, th):
    """Scale/crop im to exactly tw x th (cover)."""
    s = max(tw / im.width, th / im.height)
    nw, nh = round(im.width * s), round(im.height * s)
    r = im.resize((nw, nh), Image.LANCZOS)
    x = (nw - tw) // 2
    y = (nh - th) // 2
    return r.crop((x, y, x + tw, y + th))

def rounded_mask(size, radius):
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius=radius, fill=255)
    return m

def phone_frame(fw, fh):
    """RGBA phone: dark frame + real screenshot inside, with soft shadow."""
    pad = 26                      # room for shadow
    cw, ch = fw + pad * 2, fh + pad * 2
    layer = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    # shadow
    sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ds = ImageDraw.Draw(sh)
    ds.rounded_rectangle([pad, pad + 10, pad + fw, pad + fh + 10], radius=36, fill=(0, 0, 0, 90))
    sh = sh.filter(ImageFilter.GaussianBlur(12))
    layer = Image.alpha_composite(layer, sh)
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([pad, pad, pad + fw, pad + fh], radius=36, fill=(18, 18, 18, 255))
    inset = 9
    iw, ih = fw - inset * 2, fh - inset * 2
    shot = cover_crop(SHOT, iw, ih)
    layer.paste(shot, (pad + inset, pad + inset), rounded_mask((iw, ih), 27))
    return layer, pad

def flat_panel(pw, ph, border=True):
    """RGBA flat screenshot panel with thin border + soft shadow."""
    pad = 26
    cw, ch = pw + pad * 2, ph + pad * 2
    layer = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ds = ImageDraw.Draw(sh)
    ds.rounded_rectangle([pad, pad + 8, pad + pw, pad + ph + 8], radius=14, fill=(0, 0, 0, 80))
    sh = sh.filter(ImageFilter.GaussianBlur(10))
    layer = Image.alpha_composite(layer, sh)
    shot = cover_crop(SHOT, pw, ph)
    layer.paste(shot, (pad, pad), rounded_mask((pw, ph), 14))
    if border:
        d = ImageDraw.Draw(layer)
        d.rounded_rectangle([pad, pad, pad + pw - 1, pad + ph - 1], radius=14, outline=(190, 195, 200, 255), width=2)
    return layer, pad

def base_canvas():
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    d.rectangle([0, H - BAND_H, W, H], fill=GREEN)
    d.text((56, H - BAND_H / 2), BAND_TEXT, font=font(7, 24), fill=INK, anchor="lm")
    return im

def paste_rgba(im, layer, pad, x, y):
    """Paste RGBA layer so its content box (inside pad) lands at (x, y)."""
    im.paste(layer, (x - pad, y - pad), layer)

def save(im, name):
    out = os.path.join(OUT, f"ogp-{name}.png")
    im.convert("RGB").save(out, optimize=True)
    print(f"ogp-{name}: bytes={os.path.getsize(out)}")
    return out

# ---------- Variant 1: phone frame standing at right, logo+copy stacked left
def v1():
    im = base_canvas()
    zone_w = 774
    logo, copy, h = fit_lockup(zone_w, 100, stacked=True)
    total_h = h * 2 + 38
    y0 = (H - BAND_H - total_h) // 2
    im.paste(logo, (56, y0))
    im.paste(copy, (56, y0 + h + 38))
    layer, pad = phone_frame(258, 540)
    paste_rgba(im, layer, pad, 1200 - 56 - 258, (H - BAND_H - 540) // 2)
    print("v1 lockup h:", h, "logo w:", logo.width, "copy w:", copy.width)
    return save(im, "01")

# ---------- Variant 2: big tilted phone overlapping the band
def v2():
    im = base_canvas()
    zone_w = 700
    logo, copy, h = fit_lockup(zone_w, 92, stacked=True)
    total_h = h * 2 + 34
    y0 = (H - BAND_H - total_h) // 2
    im.paste(logo, (56, y0))
    im.paste(copy, (56, y0 + h + 34))
    layer, pad = phone_frame(268, 540)
    rot = layer.rotate(6, resample=Image.BICUBIC, expand=True)  # counterclockwise: top leans left
    # place so the phone center lands near (958, 292)
    cx, cy = 958, 292
    im.paste(rot, (cx - rot.width // 2, cy - rot.height // 2), rot)
    print("v2 lockup h:", h, "logo w:", logo.width, "copy w:", copy.width, "rot size:", rot.size)
    return save(im, "02")

# ---------- Variant 3: phone overlapping the green band
def v3():
    im = base_canvas()
    zone_w = 754
    logo, copy, h = fit_lockup(zone_w, 104, stacked=True)
    total_h = h * 2 + 38
    y0 = (H - BAND_H - total_h) // 2
    im.paste(logo, (56, y0))
    im.paste(copy, (56, y0 + h + 38))
    layer, pad = phone_frame(268, 560)
    paste_rgba(im, layer, pad, 1200 - 70 - 268, 30)   # bottom = 590 -> 30px over the band
    print("v3 lockup h:", h, "logo w:", logo.width, "copy w:", copy.width)
    return save(im, "03")

# ---------- Variant 4: wide flat panel at right (tablet-width capture), logo+copy stacked left
def v4():
    im = base_canvas()
    panel_w, panel_h = 460, 500
    panel_x = 1200 - 56 - panel_w
    zone_w = panel_x - 56 - 24
    logo, copy, h = fit_lockup(zone_w, 88, stacked=True)
    total_h = h * 2 + 34
    y0 = (H - BAND_H - total_h) // 2
    im.paste(logo, (56, y0))
    im.paste(copy, (56, y0 + h + 34))
    # flat panel built from the wide capture
    pad = 26
    layer = Image.new("RGBA", (panel_w + pad * 2, panel_h + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 8, pad + panel_w, pad + panel_h + 8], radius=14, fill=(0, 0, 0, 80))
    sh = sh.filter(ImageFilter.GaussianBlur(10))
    layer = Image.alpha_composite(layer, sh)
    shot = cover_crop(SHOT_WIDE, panel_w, panel_h)
    layer.paste(shot, (pad, pad), rounded_mask((panel_w, panel_h), 14))
    ImageDraw.Draw(layer).rounded_rectangle([pad, pad, pad + panel_w - 1, pad + panel_h - 1], radius=14, outline=(190, 195, 200, 255), width=2)
    paste_rgba(im, layer, pad, panel_x, (H - BAND_H - panel_h) // 2)
    print("v4 lockup h:", h, "logo w:", logo.width, "copy w:", copy.width, "zone:", zone_w)
    return save(im, "04")

# ---------- Variant 5: phone + enlarged spot-card close-up panel
def v5():
    im = base_canvas()
    zone_w = 566
    logo, copy, h = fit_lockup(zone_w, 84, stacked=True)
    total_h = h * 2 + 32
    y0 = (H - BAND_H - total_h) // 2
    im.paste(logo, (56, y0))
    im.paste(copy, (56, y0 + h + 32))
    layer, pad = phone_frame(250, 500)
    paste_rgba(im, layer, pad, 1200 - 56 - 250, 30)
    # card close-up: crop the bottom strip of the real screenshot, enlarge
    crop = SHOT.crop((6, 686, 384, 840))                    # 378x154: cards area
    cw2 = 348
    ch2 = round(crop.height * cw2 / crop.width)
    card = crop.resize((cw2, ch2), Image.LANCZOS)
    panel = Image.new("RGBA", (cw2 + 12, ch2 + 12), (0, 0, 0, 0))
    sh = Image.new("RGBA", panel.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([6, 12, cw2 + 6, ch2 + 12], radius=12, fill=(0, 0, 0, 85))
    sh = sh.filter(ImageFilter.GaussianBlur(8))
    panel = Image.alpha_composite(panel, sh)
    panel.paste(card, (6, 6), rounded_mask((cw2, ch2), 10))
    ImageDraw.Draw(panel).rounded_rectangle([6, 6, cw2 + 5, ch2 + 5], radius=10, outline=(255, 255, 255, 255), width=3)
    im.paste(panel, (618, 392), panel)
    print("v5 lockup h:", h, "logo w:", logo.width, "copy w:", copy.width, "card:", card.size)
    return save(im, "05")

if __name__ == "__main__":
    v1(); v2(); v3(); v4(); v5()
