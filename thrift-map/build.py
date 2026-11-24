#!/usr/bin/env python3
# Thrift Map builder — eatmap-layout edition.
# Same composition as eatmap (akiba-where-to-eat): 640px column, area header
# with Open-now switch, hand-drawn sketch map with photo thumb pins, then
# eatmap-style cards (big number, genre chip, photo, icon strip, buttons).
# Reads data.json, geocodes addresses via GSI, emits index.html.
import json, math, os, random, sys, urllib.parse, urllib.request
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
ACCENT = "#81660D"
PAGE_URL = "https://yukitchy.github.io/booking-trends-board/thrift-map/"

SHORT = {
 "stickout":"STICK OUT","nyjoe":"NY JOE","secondshimo":"2nd STREET","chicagoshimo":"CHICAGO",
 "trefacshimo":"TreFacStyle","kinjishimo":"KINJI","flamingo":"FLAMINGO","desertsnow":"DESERT SNOW",
 "trefackoenji2":"TreFac No.2","trefacvintage":"TreFac Vintage","tripmens":"Trip Men's","tripkoenji":"Trip",
 "trefackoenji":"TreFacStyle","safari":"SAFARI","bigtime":"BIG TIME","slat":"SLAT",
 "berberjin":"BerBerJin","jam":"JAM","chicagoharajuku":"CHICAGO","kinjiharajuku":"KINJI","kindalharajuku":"Kindal",
 "penny":"PENNY","bazzstore":"BAZZSTORE","secondparco":"2nd STREET","grapefruit":"GRAPEFRUIT MOON",
 "nakata":"NAKATA","modeoff":"MODE OFF","magazines":"MAGAZINES","tanpopo":"TANPOPO"}

PHOTO_KIND = {
 "jam":"Outside","chicagoharajuku":"Outside","kinjiharajuku":"Outside","kindalharajuku":"Outside",
 "bazzstore":"Outside","grapefruit":"Outside","nakata":"Outside","magazines":"Outside","tanpopo":"Outside",
 "trefacvintage":"Outside","trefackoenji2":"Outside","tripmens":"Outside","tripkoenji":"Outside","trefackoenji":"Outside",
 "chicagoshimo":"Outside","flamingo":"Outside","kinjishimo":"Outside","stickout":"Outside","trefacshimo":"Outside",
 "penny":"Inside","modeoff":"Inside","safari":"Inside","slat":"Inside"}

def has_photo(sid):
    return os.path.exists(os.path.join(HERE, "img", "photos", sid + "-1.jpg"))

def geocode(addr):
    u = "https://msearch.gsi.go.jp/address-search/AddressSearch?q=" + urllib.parse.quote(addr)
    req = urllib.request.Request(u, headers={"User-Agent": "thrift-map-build/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        j = json.load(r)
    if j:
        lng, lat = j[0]["geometry"]["coordinates"]
        return float(lat), float(lng)
    return None

def haversine_m(a, b):
    R = 6371000.0
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    dp = math.radians(b[0] - a[0]); dl = math.radians(b[1] - a[1])
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))

class Proj:
    def __init__(self, pts, W=1000):
        lats = [p[0] for p in pts]; lngs = [p[1] for p in pts]
        clat = sum(lats) / len(lats)
        self.coslat = math.cos(math.radians(clat))
        pad = 0.12
        self.minlat, self.maxlat = min(lats), max(lats)
        self.minlng, self.maxlng = min(lngs), max(lngs)
        dlat = (self.maxlat - self.minlat) or 0.002
        dlng = (self.maxlng - self.minlng) or 0.002
        self.minlat -= dlat * pad; self.maxlat += dlat * pad
        self.minlng -= dlng * pad; self.maxlng += dlng * pad
        wm = (self.maxlng - self.minlng) * self.coslat * 111320.0
        hm = (self.maxlat - self.minlat) * 110540.0
        self.s = W / wm
        H = hm * self.s
        if H < 540:
            need_hm = 540.0 / self.s
            extra = (need_hm - hm) / 110540.0 / 2.0
            self.minlat -= extra; self.maxlat += extra
            H = 540.0
        elif H > 1040:
            self.s = 1040.0 / hm
            need_wm = W / self.s
            extra = (need_wm - wm) / (self.coslat * 111320.0) / 2.0
            self.minlng -= extra; self.maxlng += extra
            H = 1040.0
        self.W = W
        self.H = int(round(H))
    def xy(self, lat, lng):
        x = (lng - self.minlng) * self.coslat * 111320.0 * self.s
        y = self.H - (lat - self.minlat) * 110540.0 * self.s
        return x, y
    def pct(self, lat, lng):
        x, y = self.xy(lat, lng)
        return x / self.W * 100.0, y / self.H * 100.0

def map_background(proj, seedkey):
    rnd = random.Random("thrift-" + seedkey)
    W, H = proj.W, proj.H
    out = [f'<rect x="0" y="0" width="{W}" height="{H}" fill="#E9E8E4"/>']
    xs = [0.0]
    while xs[-1] < W:
        xs.append(xs[-1] + rnd.uniform(58, 118))
    ys = [0.0]
    while ys[-1] < H:
        ys.append(ys[-1] + rnd.uniform(58, 118))
    for i in range(len(xs) - 1):
        for j in range(len(ys) - 1):
            bx, by = xs[i], ys[j]
            bw, bh = xs[i + 1] - xs[i], ys[j + 1] - ys[j]
            n = rnd.randint(1, 3)
            for _ in range(n):
                w = rnd.uniform(0.35, 0.8) * bw
                h = rnd.uniform(0.35, 0.8) * bh
                x = bx + rnd.uniform(3, max(4, bw - w - 3))
                y = by + rnd.uniform(3, max(4, bh - h - 3))
                fill = rnd.choice(["#D9D8D3", "#D5D4CF", "#CFCEC9", "#DBDAD5"])
                out.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" rx="2" fill="{fill}"/>')
    for x in xs[1:-1]:
        wdt = rnd.uniform(6, 12)
        out.append(f'<line x1="{x:.0f}" y1="0" x2="{x:.0f}" y2="{H}" stroke="#FFFFFF" stroke-width="{wdt:.0f}"/>')
    for y in ys[1:-1]:
        wdt = rnd.uniform(6, 12)
        out.append(f'<line x1="0" y1="{y:.0f}" x2="{W}" y2="{y:.0f}" stroke="#FFFFFF" stroke-width="{wdt:.0f}"/>')
    for _ in range(2):
        x1, y1 = rnd.uniform(0, W * 0.4), rnd.choice([0, H])
        x2, y2 = rnd.uniform(W * 0.6, W), (H if y1 == 0 else 0)
        out.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="#FFFFFF" stroke-width="10"/>')
    return "".join(out)

def rail_svg(proj, line):
    pts = [proj.xy(lat, lng) for lat, lng in line["pts"]]
    pl = " ".join(f"{x:.0f},{y:.0f}" for x, y in pts)
    s = [f'<polyline points="{pl}" fill="none" stroke="#FFFFFF" stroke-width="13" opacity="0.85" stroke-linejoin="round"/>']
    s.append(f'<polyline points="{pl}" fill="none" stroke="#141414" stroke-width="9" stroke-linejoin="round"/>')
    s.append(f'<polyline points="{pl}" fill="none" stroke="#FFFFFF" stroke-width="5" stroke-linejoin="round"/>')
    s.append(f'<polyline points="{pl}" fill="none" stroke="#141414" stroke-width="1.6" stroke-dasharray="7 6"/>')
    best, bd = None, 1e18
    for i in range(len(pts) - 1):
        mx0 = (pts[i][0] + pts[i + 1][0]) / 2; my0 = (pts[i][1] + pts[i + 1][1]) / 2
        dd = (mx0 - proj.W / 2) ** 2 + (my0 - proj.H / 2) ** 2
        if dd < bd: bd, best = dd, (pts[i], pts[i + 1], pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1])
    (x1, y1), (x2, y2), dx, dy = best
    mx = min(max((x1 + x2) / 2, 70), proj.W - 70)
    my = min(max((y1 + y2) / 2, 30), proj.H - 30)
    ang = math.degrees(math.atan2(dy, dx))
    if ang > 90: ang -= 180
    if ang < -90: ang += 180
    label = escape(line["label"])
    wch = 8.2 * len(label) + 18
    s.append(f'<g transform="translate({mx:.0f} {my:.0f}) rotate({ang:.1f})">'
             f'<rect x="{-wch/2:.0f}" y="-11" width="{wch:.0f}" height="22" rx="11" fill="#141414"/>'
             f'<text x="0" y="4.5" text-anchor="middle" font-size="12.5" font-weight="700" fill="#FFFFFF" letter-spacing="0.4">{label}</text></g>')
    return "".join(s)

def station_svg(proj, st):
    x, y = proj.xy(st["lat"], st["lng"])
    name = escape(st["name"])
    return (f'<g><rect x="{x-19:.0f}" y="{y-6:.0f}" width="38" height="12" rx="6" fill="#141414"/>'
            f'<circle cx="{x:.0f}" cy="{y:.0f}" r="3.6" fill="#FFFFFF"/>'
            f'<text x="{x:.0f}" y="{y-16:.0f}" text-anchor="middle" font-size="16.5" font-weight="800" fill="#141414" '
            f'style="paint-order:stroke" stroke="#E9E8E4" stroke-width="4.5">{name}</text>'
            f'<text x="{x:.0f}" y="{y+24:.0f}" text-anchor="middle" font-size="10.5" font-weight="700" fill="#55524C" '
            f'style="paint-order:stroke" stroke="#E9E8E4" stroke-width="3.5">STATION</text></g>')

TAG_SVG = ('<svg viewBox="0 0 24 24" width="26" height="26" aria-hidden="true">'
           '<path fill="#FFFFFF" d="M21.4 11.6l-9-9A2 2 0 0 0 11 2H4a2 2 0 0 0-2 2v7c0 .5.2 1 .6 1.4l9 9a2 2 0 0 0 2.8 0l7-7a2 2 0 0 0 0-2.8zM6.5 8A1.5 1.5 0 1 1 8 6.5 1.5 1.5 0 0 1 6.5 8z"/></svg>')
CLOCK_SVG = ('<svg viewBox="0 0 16 16" width="15" height="15" aria-hidden="true"><circle cx="8" cy="8" r="6.5" fill="none" stroke="currentColor" stroke-width="2"/>'
             '<path d="M8 4.5V8l2.5 1.8" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>')
WALK_SVG = ('<svg viewBox="0 0 16 16" width="15" height="15" aria-hidden="true"><circle cx="9.6" cy="2.4" r="1.7" fill="currentColor"/>'
            '<path d="M6 7.9 8.8 5.8 11.6 7.7M8.8 5.8 7.8 9.6M7.8 9.6 10.6 12 10.2 15M7.8 9.6 5.8 12.4 3.6 14" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>')
STAR_SVG = ('<svg viewBox="0 0 16 16" width="15" height="15" aria-hidden="true"><path fill="currentColor" d="M8 1.2l2.1 4.3 4.7.7-3.4 3.3 1 4.7L8 12l-4.4 2.2 1-4.7L1.2 6.2l4.7-.7z"/></svg>')

def build_area(area):
    stations = area.get("stations") or [area["station"]]
    pts = [(s["lat"], s["lng"]) for s in stations]
    for sh in area["shops"]:
        pts.append((sh["lat"], sh["lng"]))
    proj = Proj(pts)
    svg = [f'<svg class="mapsvg" viewBox="0 0 {proj.W} {proj.H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{escape(area["name"])} area map">']
    svg.append(map_background(proj, area["key"]))
    for line in area["rail"]:
        svg.append(rail_svg(proj, line))
    for st in stations:
        svg.append(station_svg(proj, st))
    svg.append(f'<g transform="translate({proj.W-34} 36)"><circle r="15" fill="#FFFFFF" opacity="0.85"/><path d="M0 -10 L4.5 3 L0 0 L-4.5 3 Z" fill="#141414"/><text y="-19" text-anchor="middle" font-size="11" font-weight="800" fill="#141414">N</text></g>')
    sb = 200 * proj.s
    svg.append(f'<g transform="translate(18 {proj.H-20})"><rect x="0" y="-4" width="{sb:.0f}" height="4" fill="#141414"/><text x="0" y="-9" font-size="10.5" font-weight="700" fill="#141414">200 m</text></g>')
    svg.append("</svg>")
    pins = []
    for i, sh in enumerate(area["shops"], 1):
        px, py = proj.pct(sh["lat"], sh["lng"])
        short = escape(SHORT.get(sh["id"], sh["en"]))
        if has_photo(sh["id"]):
            photo = f'<span class="thumb-photo" style="background-image:url(\'img/photos/{sh["id"]}-1.jpg\')"></span>'
        else:
            photo = f'<span class="thumb-photo nophoto">{TAG_SVG}</span>'
        pins.append(f'<button type="button" class="pin" data-area="{area["key"]}" data-n="{i}" data-id="{sh["id"]}" '
                    f'style="left:{px:.2f}%;top:{py:.2f}%" aria-label="{escape(sh["en"])}">'
                    f'<span class="thumb-card"><span class="thumb-head"><b>{i}</b>{short}</span>{photo}'
                    f'<span class="thumb-tail"></span></span></button>')
    maphtml = (f'<div class="mapwrap" data-area="{area["key"]}"><div class="pz"><div class="pz-inner">'
               + "".join(svg) + '<div class="pins">' + "".join(pins) + "</div></div></div>"
               '<div class="pz-btns"><button type="button" class="pzb in" aria-label="Zoom in">+</button>'
               '<button type="button" class="pzb out" aria-label="Zoom out">−</button>'
               '<button type="button" class="pzb reset" aria-label="Reset view">⟲</button></div>'
               '<div class="maphint">Drag to pan · Pinch or scroll to zoom · Tap a pin</div></div>')
    cards = []
    for i, sh in enumerate(area["shops"], 1):
        q = urllib.parse.quote(sh["jp"] + " " + sh["addr"])
        gmap = f"https://www.google.com/maps/search/?api=1&query={q}"
        car = ""
        if has_photo(sh["id"]):
            kind = PHOTO_KIND.get(sh["id"], "Outside")
            car = (f'<div class="car"><img class="ph" src="img/photos/{sh["id"]}-1.jpg" alt="{escape(sh["en"])}" loading="lazy" referrerpolicy="no-referrer">'
                   f'<span class="st" data-st="{sh["id"]}"></span>'
                   f'<span class="cn"><b>{kind}</b></span></div>')
        strip = [f'<span class="hr">{CLOCK_SVG}<b class="today" data-today="{sh["id"]}">{escape(sh["txt"])}</b></span>',
                 f'<span class="wk">{WALK_SVG}{sh["walk"]} min walk · {escape(sh["sta"])} Sta.</span>']
        if sh.get("gr"):
            strip.append(f'<span class="rt">{STAR_SVG}{escape(sh["gr"])}</span>')
        hrs = escape(sh["txt"]) + "."
        if sh.get("closed"):
            hrs += f' Closed: {escape(sh["closed"])}.'
        hrs += f' {escape(sh["addr"])}'
        src = f'<a class="btn tg" href="{escape(sh["src"])}" target="_blank" rel="noopener">Official site <i>→</i></a>' if sh.get("src") else ""
        cards.append(
            f'<article class="card" id="card-{sh["id"]}" data-id="{sh["id"]}">'
            f'<div class="hd"><button type="button" class="big" data-goto="{area["key"]}" data-n="{i}" data-id="{sh["id"]}" aria-label="Find {escape(sh["en"])} on the map">{i:02d}</button>'
            f'<div class="hdtx"><span class="genre">{escape(sh["genre"])}</span><h3>{escape(sh["en"])}</h3>'
            f'<div class="jp">{escape(sh["jp"])}</div></div></div>'
            f'{car}'
            f'<p class="tx">{escape(sh["note"])}</p>'
            f'<p class="strip">{"".join(strip)}</p>'
            f'<p class="hrs">{hrs}</p>'
            f'<div class="bt"><a class="btn" href="{gmap}" target="_blank" rel="noopener">Google Maps <i>→</i></a>{src}</div></article>')
    return maphtml, "".join(cards), proj

CSS = """
:root{--bg:#F1EFEA;--ink:#121212;--ac:#81660D;--ac2:#D9B44A;--mu:#5D5A54}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);color-scheme:light;font:16px/1.5 Archivo,"Noto Sans JP",sans-serif;-webkit-font-smoothing:antialiased}
.col{max-width:640px;margin:0 auto;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
h1,h2,h3,.big{font-family:Archivo,"Noto Sans JP",sans-serif;font-stretch:62%;font-weight:900;letter-spacing:-.01em;text-transform:uppercase}
.top{display:flex;justify-content:space-between;font-weight:800;font-size:13px;letter-spacing:.14em;padding:18px 0 8px;border-bottom:4px solid var(--ink)}
.hero{padding:22px 0 2px;text-align:left}
.hero img.logo{width:min(430px,86vw);height:auto;display:block}
.tagline{margin:12px 0 0;font-size:17px;font-weight:800}
.subline{margin:4px 0 0;font-size:13px;color:var(--mu);font-weight:700}
.areanav{display:flex;flex-wrap:wrap;gap:8px;margin:16px 0 2px}
.areanav a{display:inline-block;padding:7px 13px;background:#fff;border:2px solid var(--ink);color:var(--ink);font-size:12.5px;font-weight:800;text-decoration:none;text-transform:uppercase;letter-spacing:.05em}
.areanav a b{color:var(--ac)}
.howto{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:16px 0 4px}
.howto div{background:#fff;border:2px solid var(--ink);padding:10px 12px;font-size:12.5px;line-height:1.55}
.howto b{display:block;font-size:12px;letter-spacing:.08em;color:var(--ac);margin-bottom:2px}
section.area{margin-top:14px;scroll-margin-top:10px}
.maphd{display:flex;align-items:flex-end;justify-content:space-between;gap:12px;margin:30px 0 10px}
.maphd h2.map{margin:0;font-size:34px;line-height:1}
.maphd .ajp{font-size:14px;font-weight:800;color:var(--mu);margin-left:8px}
.nowmini{display:inline-flex;align-items:center;gap:8px;font:800 13px/1 Archivo,sans-serif;letter-spacing:.1em;text-transform:uppercase;color:var(--ink);padding-bottom:6px;white-space:nowrap}
.sw{position:relative;width:44px;height:24px;flex:none;border:0;background:#c9c5bc;cursor:pointer;padding:0}
.sw:after{content:"";position:absolute;top:3px;left:3px;width:18px;height:18px;background:#fff;transition:left .15s}
.sw[aria-checked=true]{background:var(--ac)}
.sw[aria-checked=true]:after{left:23px}
.nowlist{margin:0 0 10px;font-size:14px;font-weight:700;color:var(--ac)}
.nowlist.off{display:none}
section.filter .card.closed,section.filter .pin.closed{display:none}
.access{background:#fff;border:2px solid var(--ink);padding:13px 15px;margin:0 0 14px;font-size:13.5px;line-height:1.6}
.access .lab{display:inline-block;font-size:10.5px;font-weight:800;letter-spacing:.08em;color:#fff;background:var(--ac);padding:2px 7px;margin-right:8px;vertical-align:1px}
.access p{margin:0 0 8px}.access p:last-child{margin-bottom:0}
.mapwrap{position:relative;border:4px solid var(--ink);background:#E9E8E4;overflow:hidden}
.pz{overflow:hidden;touch-action:none;cursor:grab}
.pz:active{cursor:grabbing}
.pz-inner{position:relative;transform-origin:0 0;will-change:transform}
svg.mapsvg{display:block;width:100%;height:auto}
.pins{position:absolute;inset:0}
.pin{position:absolute;transform:translate(-50%,-100%) scale(var(--pk,1));background:none;border:0;padding:0;cursor:pointer;z-index:3;font:inherit}
.thumb-card{display:flex;flex-direction:column;width:64px;background:#fff;border:2px solid var(--ink);box-shadow:0 2px 6px rgba(18,18,18,.35);position:relative}
.thumb-head{display:flex;align-items:center;gap:4px;background:var(--ac);color:#fff;font:800 9.5px/1 Archivo,sans-serif;letter-spacing:.02em;padding:4px 5px;white-space:nowrap;overflow:hidden}
.thumb-head b{background:#fff;color:var(--ac);font-size:10px;padding:1px 4px;flex:none}
.thumb-photo{display:block;height:40px;background-size:cover;background-position:center;background-color:#E9E8E4}
.thumb-photo.nophoto{background:var(--ac2);display:flex;align-items:center;justify-content:center}
.thumb-tail{position:absolute;left:50%;bottom:-8px;transform:translateX(-50%);width:0;height:0;border-left:7px solid transparent;border-right:7px solid transparent;border-top:8px solid var(--ink)}
.pin.hl .thumb-card{outline:3px solid var(--ink);animation:pinpulse .5s ease-in-out 3}
@keyframes pinpulse{50%{transform:scale(1.18)}}
.pz-btns{position:absolute;right:10px;bottom:10px;display:flex;flex-direction:column;gap:6px;z-index:5}
.pzb{width:34px;height:34px;border-radius:50%;border:2px solid var(--ink);background:#fff;font-size:17px;font-weight:700;color:var(--ink);cursor:pointer;line-height:1}
.maphint{position:absolute;left:10px;bottom:10px;z-index:5;background:rgba(255,255,255,.9);padding:4px 10px;font-size:10.5px;font-weight:700;color:#55524C}
.card{padding:22px 0 24px;border-bottom:4px solid var(--ink);scroll-margin-top:8px}
.card.hit{outline:4px solid var(--ac);outline-offset:6px}
.hd{display:flex;gap:12px;align-items:flex-start;margin-bottom:10px}
.big{font-size:64px;line-height:.85;color:var(--ac);background:none;border:0;padding:0;cursor:pointer;font-family:Archivo,"Noto Sans JP",sans-serif;font-stretch:62%;font-weight:900;letter-spacing:-.01em}
.hdtx{min-width:0}
.genre{display:inline-block;background:var(--ac);color:#fff;font:900 12.5px/1 Archivo,sans-serif;letter-spacing:.08em;text-transform:uppercase;padding:6px 9px}
.hd h3{margin:7px 0 0;font-size:22px;line-height:1.05}
.hd .jp{color:var(--mu);font-size:12.5px;font-weight:700;margin-top:3px}
.car{position:relative;aspect-ratio:16/10;background:#222;margin:0 0 4px}
.ph{display:block;width:100%;height:100%;object-fit:cover}
.st{position:absolute;right:8px;top:8px;z-index:2;font:800 11px/1 Archivo,sans-serif;letter-spacing:.08em;padding:5px 7px;background:#fff;color:var(--ink)}
.st.o{background:#1F8A4C;color:#fff}
.st.c{background:#c9c5bc;color:#3a3833}
.cn{position:absolute;left:0;bottom:0;background:rgba(18,18,18,.78);color:#fff;font:700 12px/1 Archivo,sans-serif;letter-spacing:.08em;text-transform:uppercase;padding:7px 10px}
.tx{margin:10px 0;font-size:16px;line-height:1.55}
.strip{display:flex;flex-wrap:wrap;gap:4px 0;margin:0;background:var(--ink);color:#fff;padding:9px 10px;font-size:14px;font-weight:700;line-height:1.3}
.strip span{display:inline-flex;align-items:center;gap:6px}
.strip span+span:before{content:"";display:inline-block;width:4px;height:4px;background:var(--ac2);margin:0 8px;flex:none}
.strip svg{flex:none;color:var(--ac2)}
.strip .today{font-weight:800}
.hrs{margin:6px 0 0;font-size:13px;color:var(--mu);line-height:1.55}
.bt{display:flex;gap:6px;margin-top:10px}
.bt>*{flex:1 1 0;min-width:0}
.btn{display:flex;align-items:center;justify-content:center;gap:6px;min-height:46px;padding:0 8px;background:var(--ink);color:#fff;text-decoration:none;font:800 13px Archivo,sans-serif;letter-spacing:.04em;text-transform:uppercase;border:0;cursor:pointer;white-space:nowrap}
.btn i{font-style:normal;color:var(--ac2)}
.btn.tg{background:transparent;color:var(--ink);box-shadow:inset 0 0 0 3px var(--ink)}
.btn.tg i{color:var(--ac)}
.know{background:var(--ink);color:#fff;margin-top:34px;padding:28px 0 32px}
.know h2{margin:0 0 10px;font-size:30px;color:#fff}
.know ul{margin:0;padding-left:20px}
.know li{margin:8px 0;font-size:15px;line-height:1.6}
footer{padding:20px 0 40px;color:var(--mu);font-size:12.5px;line-height:1.8}
footer .brand{color:var(--ac);font-weight:800}
@media (max-width:560px){.howto{grid-template-columns:1fr}.maphd h2.map{font-size:27px}.big{font-size:52px}.hd h3{font-size:19px}}
@media (min-width:700px){.col{max-width:760px}}
"""

JS = """
const HOURS = __HOURS__;
function pad(n){return String(n).padStart(2,'0')}
function t12(mins){let h=Math.floor(mins/60)%24,m=mins%60;const ap=h<12?'AM':'PM';h=h%12||12;return h+(m?':'+pad(m):'')+' '+ap}
function statusFor(h){
  if(!h||!h.length)return null;
  const now=new Date();const day=(now.getDay()+6)%7;const cur=now.getHours()*60+now.getMinutes();
  const ent=h.find(e=>e.d.includes(day));
  if(ent){const o=+ent.o.split(':')[0]*60+(+ent.o.split(':')[1]);let c=+ent.c.split(':')[0]*60+(+ent.c.split(':')[1]);if(c<=o)c+=1440;
    if(cur>=o&&cur<c)return{open:true,today:'Today '+t12(o)+' \\u2013 '+t12(c%1440),label:c-cur<=45?'Closes '+t12(c%1440):'Open now'};
    if(cur<o)return{open:false,today:'Today '+t12(o)+' \\u2013 '+t12(c%1440),label:'Opens '+t12(o)};}
  for(let k=1;k<=7;k++){const d2=(day+k)%7;const e2=h.find(e=>e.d.includes(d2));
    if(e2){const o2=+e2.o.split(':')[0]*60+(+e2.o.split(':')[1]);
      return{open:false,today:null,label:k===1?'Opens '+t12(o2)+' tomorrow':'Closed today'};}}
  return null;}
document.querySelectorAll('section.area').forEach(sec=>{
  let openN=0,totalN=0;
  sec.querySelectorAll('.card').forEach(card=>{
    const id=card.dataset.id;const rec=HOURS[id];const st=rec&&statusFor(rec.h);
    totalN++;
    const badge=card.querySelector('[data-st]');
    const todayEl=card.querySelector('[data-today]');
    if(st){
      if(st.today&&todayEl)todayEl.textContent=st.today;
      if(badge){badge.textContent=st.open?'OPEN NOW':'CLOSED';badge.classList.add(st.open?'o':'c');}
      if(st.open)openN++;else{
        card.classList.add('closed');
        const pin=sec.querySelector('.pin[data-id="'+id+'"]');if(pin)pin.classList.add('closed');}
    } else { if(badge)badge.remove(); openN++; }
  });
  const nl=sec.querySelector('.nowlist');
  if(nl)nl.textContent='Open now: '+openN+' of '+totalN+' shops in this area';
  const sw=sec.querySelector('.sw');
  if(sw)sw.addEventListener('click',()=>{
    const on=sw.getAttribute('aria-checked')!=='true';
    sw.setAttribute('aria-checked',on);sec.classList.toggle('filter',on);
    if(nl)nl.classList.toggle('off',false);});
});
function focusPin(wrap,n){
  const pin=wrap.querySelector('.pin[data-n="'+n+'"]');if(!pin)return;
  const pz=wrap.querySelector('.pz');
  const st=wrap._pz;const k=2.1;
  const px=parseFloat(pin.style.left)/100*pz.clientWidth, py=parseFloat(pin.style.top)/100*pz.clientHeight;
  st.k=k;st.x=pz.clientWidth/2-px*k;st.y=pz.clientHeight/2-py*k;clampPZ(wrap);applyPZ(wrap,true);
  wrap.querySelectorAll('.pin').forEach(p=>p.classList.remove('hl'));pin.classList.add('hl');
  setTimeout(()=>pin.classList.remove('hl'),1700);}
function clampPZ(wrap){const pz=wrap.querySelector('.pz');const st=wrap._pz;
  const W=pz.clientWidth,H=pz.clientHeight;
  if(st.k<=1){st.x=0;st.y=0;st.k=1;return}
  st.x=Math.min(0,Math.max(W-W*st.k,st.x));st.y=Math.min(0,Math.max(H-H*st.k,st.y));}
function applyPZ(wrap,anim){const inner=wrap.querySelector('.pz-inner');const st=wrap._pz;
  inner.style.transition=anim?'transform .38s ease':'';
  inner.style.transform='translate('+st.x+'px,'+st.y+'px) scale('+st.k+')';
  inner.style.setProperty('--pk',Math.max(.55,1/Math.sqrt(st.k)));}
document.querySelectorAll('.mapwrap').forEach(wrap=>{
  wrap._pz={k:1,x:0,y:0};
  const pz=wrap.querySelector('.pz');
  const ptrs=new Map();let lastD=0;
  pz.addEventListener('pointerdown',e=>{ptrs.set(e.pointerId,{x:e.clientX,y:e.clientY});pz.setPointerCapture(e.pointerId);});
  pz.addEventListener('pointermove',e=>{
    if(!ptrs.has(e.pointerId))return;
    const prev=ptrs.get(e.pointerId);ptrs.set(e.pointerId,{x:e.clientX,y:e.clientY});
    const st=wrap._pz;
    if(ptrs.size===1){st.x+=e.clientX-prev.x;st.y+=e.clientY-prev.y;clampPZ(wrap);applyPZ(wrap,false);}
    else if(ptrs.size===2){const p=[...ptrs.values()];
      const d=Math.hypot(p[0].x-p[1].x,p[0].y-p[1].y);
      if(lastD>0){const r=pz.getBoundingClientRect();
        const mx=(p[0].x+p[1].x)/2-r.left,my=(p[0].y+p[1].y)/2-r.top;
        const nk=Math.min(6,Math.max(1,st.k*d/lastD));
        st.x=mx-(mx-st.x)*(nk/st.k);st.y=my-(my-st.y)*(nk/st.k);st.k=nk;clampPZ(wrap);applyPZ(wrap,false);}
      lastD=d;}});
  const end=e=>{ptrs.delete(e.pointerId);if(ptrs.size<2)lastD=0;};
  pz.addEventListener('pointerup',end);pz.addEventListener('pointercancel',end);
  pz.addEventListener('wheel',e=>{e.preventDefault();const st=wrap._pz;const r=pz.getBoundingClientRect();
    const mx=e.clientX-r.left,my=e.clientY-r.top;
    const nk=Math.min(6,Math.max(1,st.k*Math.exp(-e.deltaY*0.0016)));
    st.x=mx-(mx-st.x)*(nk/st.k);st.y=my-(my-st.y)*(nk/st.k);st.k=nk;clampPZ(wrap);applyPZ(wrap,false);},{passive:false});
  wrap.querySelector('.pzb.in').addEventListener('click',()=>{const st=wrap._pz;const pz2=wrap.querySelector('.pz');
    const nk=Math.min(6,st.k*1.45);st.x=pz2.clientWidth/2-(pz2.clientWidth/2-st.x)*(nk/st.k);
    st.y=pz2.clientHeight/2-(pz2.clientHeight/2-st.y)*(nk/st.k);st.k=nk;clampPZ(wrap);applyPZ(wrap,true);});
  wrap.querySelector('.pzb.out').addEventListener('click',()=>{const st=wrap._pz;const pz2=wrap.querySelector('.pz');
    const nk=Math.max(1,st.k/1.45);st.x=pz2.clientWidth/2-(pz2.clientWidth/2-st.x)*(nk/st.k);
    st.y=pz2.clientHeight/2-(pz2.clientHeight/2-st.y)*(nk/st.k);st.k=nk;clampPZ(wrap);applyPZ(wrap,true);});
  wrap.querySelector('.pzb.reset').addEventListener('click',()=>{wrap._pz={k:1,x:0,y:0};applyPZ(wrap,true);});
});
document.querySelectorAll('.pin').forEach(pin=>{
  pin.addEventListener('pointerdown',e=>e.stopPropagation());
  pin.addEventListener('click',()=>{
    const card=document.getElementById('card-'+pin.dataset.id);
    if(card){card.scrollIntoView({behavior:'smooth',block:'center'});
      card.classList.remove('hit');void card.offsetWidth;card.classList.add('hit');
      setTimeout(()=>card.classList.remove('hit'),1800);}});});
document.querySelectorAll('.big').forEach(b=>{
  b.addEventListener('click',()=>{
    const wrap=document.querySelector('.mapwrap[data-area="'+b.dataset.goto+'"]');
    if(wrap){wrap.scrollIntoView({behavior:'smooth',block:'center'});
      setTimeout(()=>focusPin(wrap,b.dataset.n),450);}});});
"""

def main():
    data = json.load(open(os.path.join(HERE, "data.json"), encoding="utf-8"))
    total = 0
    fallbacks = []
    for area in data["areas"]:
        stations = area.get("stations") or [area["station"]]
        for sh in area["shops"]:
            got = None
            try:
                got = geocode(sh["addr"])
            except Exception as e:
                print(f"geocode error {sh['id']}: {e}", file=sys.stderr)
            if got:
                sh["lat"], sh["lng"] = got
            elif sh.get("fb"):
                sh["lat"], sh["lng"] = sh["fb"]
                fallbacks.append(sh["id"])
            else:
                print(f"FATAL: no coords for {sh['id']}", file=sys.stderr)
                sys.exit(1)
            best = min(stations, key=lambda s: haversine_m((sh["lat"], sh["lng"]), (s["lat"], s["lng"])))
            d = haversine_m((sh["lat"], sh["lng"]), (best["lat"], best["lng"]))
            sh["walk"] = max(1, round(d * 1.3 / 80))
            sh["sta"] = best["name"]
            total += 1
    hours_js = {sh["id"]: {"h": sh["hours"], "closed": sh.get("closed")}
                for area in data["areas"] for sh in area["shops"]}
    sections = []
    nav = []
    for area in data["areas"]:
        maphtml, cards, proj = build_area(area)
        nav.append(f'<a href="#area-{area["key"]}">{escape(area["name"])} <b>{len(area["shops"])}</b></a>')
        sections.append(
            f'<section class="area" id="area-{area["key"]}">'
            f'<div class="maphd"><h2 class="map">{escape(area["name"])}<span class="ajp">{escape(area["jp"])}</span></h2>'
            f'<span class="nowmini">Open now <button type="button" class="sw" role="switch" aria-checked="false" aria-label="Show only shops open now in {escape(area["name"])}"></button></span></div>'
            f'<p class="nowlist off"></p>'
            f'<div class="access"><p><span class="lab">GETTING THERE</span>{escape(area["access"])}</p>'
            f'<p><span class="lab">THE AREA</span>{escape(area["walk"])}</p>'
            f'<p><span class="lab">STATION</span>{escape(area["station"]["name"])} — {escape(area["lines"])}</p></div>'
            f'{maphtml}<div class="cards">{cards}</div></section>')
    counts = " · ".join(f'{a["name"]} {len(a["shops"])}' for a in data["areas"])
    js = JS.replace("__HOURS__", json.dumps(hours_js))
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Thrift Map — Tokyo Vintage &amp; Thrift Shops</title>
<meta name="description" content="A hand-drawn map of Tokyo's best vintage and thrift shops: Shimokitazawa, Koenji, Harajuku, Akihabara, Ikebukuro and Ueno — {total} shops, checked November 2026.">
<link rel="icon" type="image/png" href="img/favicon.png">
<link rel="apple-touch-icon" href="img/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;700;800;900&family=Noto+Sans+JP:wght@500;700;900&display=swap" rel="stylesheet">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Anime Sensei">
<meta property="og:title" content="Thrift Map — Tokyo Vintage &amp; Thrift Shops">
<meta property="og:description" content="{total} vintage &amp; thrift shops across 6 Tokyo neighborhoods, on hand-drawn maps. Shimokitazawa &amp; Koenji first.">
<meta property="og:url" content="{PAGE_URL}">
<meta property="og:image" content="{PAGE_URL}img/ogp1.jpg">
<meta name="twitter:card" content="summary_large_image">
<style>{CSS}</style>
</head>
<body>
<div class="col">
<div class="top"><span>ANIME SENSEI</span><span>TOKYO GUIDE</span></div>
<header class="hero">
<img class="logo" src="img/logo.png" alt="THRIFT MAP">
<p class="tagline">{escape(data["tagline"])}</p>
<p class="subline">{total} shops · 6 areas · {counts}</p>
<nav class="areanav">{"".join(nav)}</nav>
<div class="howto">
<div><b>HOW TO USE</b>Tap a photo pin on a map to jump to that shop's card. Tap the big number on a card to find it back on the map.</div>
<div><b>OPEN NOW</b>Flip the switch next to an area name to hide shops that are closed right now. The badge on each photo is live, too.</div>
<div><b>PHOTOS</b>Shop photos come from the shops' own sites and listings, checked on Nov 24, 2026.</div>
</div>
</header>
{"".join(sections)}
</div>
<div class="know"><div class="col">
<h2>Good to know</h2>
<ul>
<li>Many Tokyo thrift shops open at 11 AM or noon, and small ones close early — check the live badge before a long trip.</li>
<li>Shimokitazawa and Koenji are dense enough to cover on foot in one afternoon each. Start with the shops marked OPEN NOW.</li>
<li>Most shops take cards, but small vintage stores may be cash only. Tax-free shopping is rare in thrift stores.</li>
<li>Hours were checked on Nov 24, 2026 — a quick look at the Google listing before you go is wise.</li>
</ul>
</div></div>
<div class="col">
<footer>
<p><span class="brand">THRIFT MAP</span> — a guest guide by Anime Sensei<br>
{escape(data["checked"])}<br>
Map sketches are schematic. Coordinates: GSI address search. Always confirm the exact spot with the Google Maps button on each card.</p>
</footer>
</div>
<script>{js}</script>
</body>
</html>"""
    out = os.path.join(HERE, "index.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    nophoto = [sh["id"] for area in data["areas"] for sh in area["shops"] if not has_photo(sh["id"])]
    print(f"built {out}: {total} shops, {len(data['areas'])} areas, photos {total - len(nophoto)}/{total}")
    if nophoto:
        print("no photo (tag-icon pin, no photo block):", ", ".join(nophoto))
    if fallbacks:
        print("fallback coords used:", ", ".join(fallbacks))

if __name__ == "__main__":
    main()
