#!/usr/bin/env python3
# Thrift Map builder — eatmap-structure edition, round 2.
# Same structure and systems as eatmap (where-to-eat):
#  - root URL redirects to the default area; one area per page
#  - H1 area switcher (<details> + "Tap to change area" hint)
#  - header: small transparent logo left, language button (flag + code) right;
#    the button cycles EN -> JA -> ZH -> ES -> DE -> KO, swapping page text
#    from the __T dictionary (eatmap's engine, localStorage + ?lang=)
#  - hero: 3-photo collage + black status bar
#  - "I'm after" category chips that filter map pins and cards
#  - hand-drawn sketch map with photo thumb pins; eatmap-style cards whose
#    actions (Google Maps / official site) are white round icon buttons
#    overlaid on the photo's top-right (KAPITAL map style)
# Reads data.json (+ translations/*.json), geocodes via GSI, emits pages.
import glob, json, math, os, random, sys, urllib.parse, urllib.request
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
ACCENT = "#81660D"
PAGE_URL = "https://yukitchy.github.io/booking-trends-board/thrift-map/"

SLUGS = {
 "shimo": "shimokitazawa",
 "koenji": "koenji",
 "kichijoji": "kichijoji",
 "nakano": "nakano",
 "harajuku": "harajuku-shibuya",
 "akiba": "akihabara",
 "ikebukuro": "ikebukuro",
 "ueno": "ueno",
}
DEFAULT_SLUG = "shimokitazawa"

CATS = [
 ("vintage", "Vintage"),
 ("brand", "Brand resale"),
 ("recycle", "Recycle"),
 ("specialty", "Specialty"),
]

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
 "chicagoshimo":"Outside","flamingo":"Outside","kinjishimo":"Outside","trefacshimo":"Outside",
 "penny":"Inside","modeoff":"Inside","safari":"Inside","slat":"Inside","stickout":"Inside", "secondparco": "Inside"}

def photo_files(sid):
    out = []
    for n in (1, 2, 3):
        p = os.path.join(HERE, "img", "photos", f"{sid}-{n}.jpg")
        if os.path.exists(p):
            out.append(f"{sid}-{n}.jpg")
    return out

def has_photo(sid):
    return os.path.exists(os.path.join(HERE, "img", "photos", sid + "-1.jpg"))

def closed_badge(cv):
    """Red-badge text for a shop's regular closing days, or None.
    Weekly weekday closings -> 'CLOSED WED' / 'CLOSED TUE & WED'.
    Monthly (2nd Thursday etc.) and irregular closings -> 'CLOSED IRREGULAR'.
    Year-end-only closings are not regular closing days -> None."""
    if not cv:
        return None
    t = cv.lower()
    if "jan 1" in t or "new year" in t:
        return None
    if "irregular" in t:
        return "CLOSED IRREGULAR"
    days = [("monday", "MON"), ("tuesday", "TUE"), ("wednesday", "WED"),
            ("thursday", "THU"), ("friday", "FRI"), ("saturday", "SAT"), ("sunday", "SUN")]
    found = [abbr for name, abbr in days if name in t]
    if not found:
        return None
    if any(w in t for w in ("1st", "first", "2nd", "second", "3rd", "third", "4th", "fourth", "last")):
        return "CLOSED IRREGULAR"
    return "CLOSED " + " & ".join(found)

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

def clip_runs(pts, W, H):
    """Clip a polyline to the [0,W]x[0,H] rect (Liang-Barsky per segment);
    returns a list of point runs. Keeps drawn geometry inside the viewBox
    so out-of-frame line ends cannot leak scrollable overflow."""
    def clip(p, q):
        (x1, y1), (x2, y2) = p, q
        dx, dy = x2 - x1, y2 - y1
        t0, t1 = 0.0, 1.0
        for pk, qk in ((-dx, x1), (dx, W - x1), (-dy, y1), (dy, H - y1)):
            if pk == 0:
                if qk < 0:
                    return None
                continue
            t = qk / pk
            if pk < 0:
                if t > t1:
                    return None
                if t > t0:
                    t0 = t
            else:
                if t < t0:
                    return None
                if t < t1:
                    t1 = t
        return ((x1 + t0 * dx, y1 + t0 * dy), (x1 + t1 * dx, y1 + t1 * dy))
    runs, cur = [], []
    for i in range(len(pts) - 1):
        seg = clip(pts[i], pts[i + 1])
        if seg is None:
            if len(cur) > 1:
                runs.append(cur)
            cur = []
            continue
        a, b = seg
        if cur and abs(cur[-1][0] - a[0]) < 0.6 and abs(cur[-1][1] - a[1]) < 0.6:
            cur.append(b)
        else:
            if len(cur) > 1:
                runs.append(cur)
            cur = [a, b]
    if len(cur) > 1:
        runs.append(cur)
    return runs

def rail_svg(proj, line):
    pts = [proj.xy(lat, lng) for lat, lng in line["pts"]]
    pls = [" ".join(f"{x:.0f},{y:.0f}" for x, y in run) for run in clip_runs(pts, proj.W, proj.H)]
    s = []
    for pl in pls:
        s.append(f'<polyline points="{pl}" fill="none" stroke="#FFFFFF" stroke-width="13" opacity="0.85" stroke-linejoin="round"/>')
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
XCIRC_SVG = ('<svg viewBox="0 0 16 16" width="15" height="15" aria-hidden="true"><circle cx="8" cy="8" r="6.5" fill="none" stroke="currentColor" stroke-width="2"/>'
             '<path d="M5.8 5.8l4.4 4.4M10.2 5.8l-4.4 4.4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>')
CHEV_SVG = ('<svg class="chev" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 8l8 8 8-8" fill="none" '
            'stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></svg>')
PIN_SVG = ('<svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true"><path fill="currentColor" '
           'd="M12 2a7 7 0 0 0-7 7c0 5.2 7 13 7 13s7-7.8 7-13a7 7 0 0 0-7-7zm0 9.5A2.5 2.5 0 1 1 12 6a2.5 2.5 0 0 1 0 5.5z"/></svg>')
GLOBE_SVG = ('<svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="2">'
             '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.6 3.9 5.7 3.9 9S14.5 18.4 12 21c-2.5-2.6-3.9-5.7-3.9-9S9.5 5.6 12 3z"/></g></svg>')
CAT_ICONS = {
 "vintage": ('<svg viewBox="0 0 24 24" width="26" height="26" aria-hidden="true"><path fill="currentColor" d="M21.4 11.6l-9-9A2 2 0 0 0 11 2H4a2 2 0 0 0-2 2v7c0 .5.2 1 .6 1.4l9 9a2 2 0 0 0 2.8 0l7-7a2 2 0 0 0 0-2.8zM6.5 8A1.5 1.5 0 1 1 8 6.5 1.5 1.5 0 0 1 6.5 8z"/></svg>'),
 "brand": ('<svg viewBox="0 0 24 24" width="26" height="26" aria-hidden="true"><path fill="currentColor" d="M12 2l3.2 5.2L21 8l-4.5 4.6L17.8 19 12 16l-5.8 3 1.3-6.4L3 8l5.8-.8z"/></svg>'),
 "recycle": ('<svg viewBox="0 0 24 24" width="26" height="26" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M5 8a8 8 0 0 1 13.6-2.4L20 7"/><path d="M20 3v4h-4"/><path d="M19 16a8 8 0 0 1-13.6 2.4L4 17"/><path d="M4 21v-4h4"/></g></svg>'),
 "specialty": ('<svg viewBox="0 0 24 24" width="26" height="26" aria-hidden="true"><path fill="currentColor" d="M12 2.5l2.9 6 6.6.9-4.8 4.6 1.2 6.5L12 17.4l-5.9 3.1 1.2-6.5L2.5 9.4l6.6-.9z"/></svg>'),
}

FLAG_SVGS = (
 '<svg class="f on" data-l="en" aria-hidden="true" viewBox="0 0 24 16"><rect width="24" height="16" fill="#fff"/>'
 '<rect y="0.00" width="24" height="1.23" fill="#B22234"/><rect y="2.46" width="24" height="1.23" fill="#B22234"/>'
 '<rect y="4.92" width="24" height="1.23" fill="#B22234"/><rect y="7.38" width="24" height="1.23" fill="#B22234"/>'
 '<rect y="9.85" width="24" height="1.23" fill="#B22234"/><rect y="12.31" width="24" height="1.23" fill="#B22234"/>'
 '<rect y="14.77" width="24" height="1.23" fill="#B22234"/><rect width="10" height="8.6" fill="#3C3B6E"/></svg>'
 '<svg class="f" data-l="ja" aria-hidden="true" viewBox="0 0 24 16"><rect width="24" height="16" fill="#fff"/>'
 '<circle cx="12" cy="8" r="4.6" fill="#BC002D"/></svg>'
 '<svg class="f" data-l="zh" aria-hidden="true" viewBox="0 0 24 16"><rect width="24" height="16" fill="#DE2910"/>'
 '<polygon points="5,2.2 5.9,4.9 8.7,4.9 6.4,6.5 7.3,9.2 5,7.5 2.7,9.2 3.6,6.5 1.3,4.9 4.1,4.9" fill="#FFDE00"/></svg>'
 '<svg class="f" data-l="es" aria-hidden="true" viewBox="0 0 24 16"><rect width="24" height="16" fill="#AA151B"/>'
 '<rect y="4" width="24" height="8" fill="#F1BF00"/></svg>'
 '<svg class="f" data-l="de" aria-hidden="true" viewBox="0 0 24 16"><rect width="24" height="16" fill="#FFCE00"/>'
 '<rect width="24" height="5.34" fill="#000"/><rect y="5.33" width="24" height="5.34" fill="#DD0000"/></svg>'
 '<svg class="f" data-l="ko" aria-hidden="true" viewBox="0 0 24 16"><rect width="24" height="16" fill="#fff"/>'
 '<circle cx="12" cy="8" r="3.6" fill="#CD2E3A"/>'
 '<path d="M8.4 8a3.6 3.6 0 0 0 7.2 0a1.8 1.8 0 0 0-3.6 0a1.8 1.8 0 0 1-3.6 0z" fill="#0047A0"/>'
 '<g stroke="#000" stroke-width="1"><path d="M3 3.3l2.6-1.6M3.6 4.5l2.6-1.6M3 5.7l2.6-1.6"/>'
 '<path d="M18.4 12.6l2.6-1.6M17.8 13.8l2.6-1.6M18.4 14.5l2.6-1.6" opacity=".0"/></g></svg>')

LANGSW_HTML = ('<button type="button" class="langsw" aria-label="Change language"><span class="fl">'
               + FLAG_SVGS + '</span><b class="lc">EN</b></button>')

def build_area(area, prefix):
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
        short = escape(SHORT.get(sh["id"]) or sh.get("short") or sh["en"])
        _files = photo_files(sh["id"])
        if _files:
            photo = f'<span class=\"thumb-photo\" style=\"background-image:url(\'{prefix}img/photos/{_files[0]}\')\"></span>'
        else:
            photo = f'<span class="thumb-photo nophoto">{TAG_SVG}</span>'
        pins.append(f'<button type="button" class="pin" data-area="{area["key"]}" data-n="{i}" data-id="{sh["id"]}" data-cat="{sh["cat"]}" '
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
        acts = [f'<a class="icon-btn maps-btn" href="{gmap}" target="_blank" rel="noopener" aria-label="Google Maps — {escape(sh["en"])}" title="Google Maps">{PIN_SVG}</a>']
        if sh.get("src"):
            acts.append(f'<a class="icon-btn site-btn" href="{escape(sh["src"])}" target="_blank" rel="noopener" aria-label="Official site — {escape(sh["en"])}" title="Official site">{GLOBE_SVG}</a>')
        actions = f'<div class="photo-actions">{"".join(acts)}</div>'
        _files = photo_files(sh["id"])
        if _files:
            _labels = {"1": "Outside", "2": "Inside", "3": "Items"}
            _lab = [_labels[f.rsplit("-", 1)[1].split(".")[0]] for f in _files]
            _imgs = "".join(
                f'<img src="{prefix}img/photos/{fn}" alt="{escape(sh["en"])}" loading="lazy" referrerpolicy="no-referrer" draggable="false" data-l="{lb}">'
                for fn, lb in zip(_files, _lab))
            _btns = ''
            _cn = f'<span class="cn"><b>{_lab[0]}</b></span>'
            if len(_files) > 1:
                _btns = ('<button type="button" class="cb pv" aria-label="Previous photo">&lsaquo;</button>'
                         '<button type="button" class="cb nx" aria-label="Next photo">&rsaquo;</button>')
                _cn = f'<span class="cn"><b>{_lab[0]}</b> 1/{len(_files)}</span>'
            car = (f'<div class="car"><div class="trk">{_imgs}</div>{_btns}'
                   f'{actions}'
                   f'<span class="st" data-st="{sh["id"]}"></span>{_cn}</div>')
        else:
            car = (f'<div class="car nophoto"><span class="pholder">{TAG_SVG}</span>'
                   f'{actions}'
                   f'<span class="st" data-st="{sh["id"]}"></span></div>')
        strip = [f'<span class="hr">{CLOCK_SVG}<b class="today" data-today="{sh["id"]}">{escape(sh["txt"])}</b></span>',
                 f'<span class="wk">{WALK_SVG}<span class="wkt">{sh["walk"]} min walk</span><span class="wks"> · {escape(sh["sta"])} Sta.</span></span>']
        _badge = closed_badge(sh.get("closed"))
        if _badge:
            strip.append(f'<span class="clb">{escape(_badge)}</span>')
        if sh.get("gr"):
            strip.append(f'<span class="rt">{STAR_SVG}{escape(sh["gr"])}</span>')
        cards.append(
            f'<article class="card" id="card-{sh["id"]}" data-id="{sh["id"]}" data-cat="{sh["cat"]}">'
            f'<div class="hd"><button type="button" class="big" data-goto="{area["key"]}" data-n="{i}" data-id="{sh["id"]}" aria-label="Find {escape(sh["en"])} on the map">{i:02d}</button>'
            f'<div class="hdtx"><span class="genre">{escape(sh["genre"])}</span><h3>{escape(sh["en"])}</h3>'
            f'<div class="adr">{escape(sh["adr"])}</div></div></div>'
            f'{car}'
            f'<p class="tx">{escape(sh["note"])}</p>'
            f'<p class="strip">{"".join(strip)}</p>'
            f'</article>')
    return maphtml, "".join(cards), proj

def jpeg_long_edge(path):
    try:
        with open(path, "rb") as fh:
            data = fh.read()
    except OSError:
        return 0
    i = 2
    while i < len(data) - 9:
        if data[i] != 0xFF:
            i += 1
            continue
        m = data[i + 1]
        if m in (0xC0, 0xC1, 0xC2):
            h = int.from_bytes(data[i + 5:i + 7], "big")
            w = int.from_bytes(data[i + 7:i + 9], "big")
            return max(w, h)
        if m in (0xD8, 0xD9) or 0xD0 <= m <= 0xD7:
            i += 2
            continue
        ln = int.from_bytes(data[i + 2:i + 4], "big")
        if ln < 2:
            break
        i += 2 + ln
    return 0

def hero_photo_files(area):
    """Hero slots only take photos whose long edge is at least 1200px."""
    out = []
    for s in area["shops"]:
        for f in photo_files(s["id"]):
            p = os.path.join(HERE, "img", "photos", f)
            if jpeg_long_edge(p) >= 1200:
                out.append((s, f))
    return out

def build_hero(area, prefix):
    imgs = hero_photo_files(area)
    chosen = []
    seen = set()
    for s, f in imgs:
        if s["id"] not in seen:
            chosen.append((s, f)); seen.add(s["id"])
        if len(chosen) == 3:
            break
    if len(chosen) < 3:
        for s, f in imgs:
            if (s, f) not in chosen:
                chosen.append((s, f))
            if len(chosen) == 3:
                break
    n = max(1, len(chosen))
    anchors = "".join(
        f'<a href="#card-{s["id"]}" aria-label="Go to {escape(s["en"])}">'
        f'<img src="{prefix}img/photos/{f}" alt="" referrerpolicy="no-referrer"></a>'
        for s, f in chosen)
    mos = (f'<div class="hero mos n{n}">{anchors}'
           f'<div class="vt">{escape(area["jp"])}</div></div>')
    walks = [s["walk"] for s in area["shops"]]
    near = sum(1 for w in walks if w <= 5)
    far = len(walks) - near
    sta = escape(area["station"]["name"])
    if len(walks) == 1:
        left = f'1 shop · {walks[0]} min from {escape(area["shops"][0]["sta"])} Sta.'
        right = "Worth the short walk"
    elif far == 0:
        left = f'All {len(walks)} within {max(walks)} min of the station'
        right = f'{sta} Sta.'
    elif near == 0:
        left = f'{len(walks)} shops, a short stroll from the station'
        right = f'{sta} Sta.'
    else:
        left = f'{near} within a 5 min walk'
        right = f'{far} a bit further out'
    return mos + f'<div class="hb"><span>{left}</span><b>{right}</b></div>'

def build_mood(area):
    counts = {}
    for sh in area["shops"]:
        counts[sh["cat"]] = counts.get(sh["cat"], 0) + 1
    chips = []
    for key, label in CATS:
        c = counts.get(key, 0)
        dis = " disabled" if c == 0 else ""
        chips.append(
            f'<button type="button" data-cat="{key}" aria-pressed="false"{dis}>'
            f'{CAT_ICONS[key]}{label}<small>{c}</small></button>')
    return (f'<div class="mood"><p class="mt">I\'m after</p>'
            f'<div class="chips" role="group" aria-label="Filter shops by category">{"".join(chips)}</div>'
            f'<p class="mn"></p></div>')

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
:root{--ink:#121212;--paper:#F1EFEA;--card:#FFFFFF;--mut:#57534A;--ac:#81660D;--line:#E2DED3;--open:#2E7D32;--pop:#FFF7DB;--popb:#E9C46A}
html{scroll-behavior:smooth}
html,body{overflow-x:hidden}
body{font-family:'Noto Sans JP',system-ui,sans-serif;background:var(--paper);color:var(--ink);-webkit-text-size-adjust:100%}
img{max-width:100%}
.wrap{max-width:860px;margin:0 auto;padding:0 16px 40px}
.top{display:flex;align-items:center;justify-content:space-between;gap:14px;padding:14px 0 4px}
.top img.logo{height:clamp(24px,7.5vw,34px);width:auto;display:block;flex:none}
.langsw{margin-left:auto;align-self:center;display:inline-flex;align-items:center;gap:7px;background:var(--ac);color:#fff;border:0;border-radius:999px;padding:8px 11px;font:inherit;font-weight:900;font-size:15px;line-height:1;cursor:pointer;box-shadow:0 2px 6px rgba(0,0,0,.18)}
.langsw .fl{position:relative;width:24px;height:16px;border-radius:2px;overflow:hidden;flex:none;box-shadow:0 0 0 1px rgba(0,0,0,.25)}
.langsw .fl svg{position:absolute;inset:0;width:100%;height:100%;display:none}
.langsw .fl svg.on{display:block}
.langsw .lc{font-family:'Archivo',sans-serif;font-weight:900;letter-spacing:.04em}
h1{position:relative;font-family:'Archivo','Noto Sans JP',sans-serif;font-weight:900;font-size:clamp(20px,6.6vw,72px);line-height:.92;letter-spacing:-.01em;text-transform:uppercase;margin:14px 0 18px}
h1 .kindsw{display:inline-block;vertical-align:baseline}
h1 .kindsw summary{display:inline-block;background:var(--ac);color:#fff;padding:.02em .14em .06em;border-radius:.12em;cursor:pointer;list-style:none;white-space:nowrap}
h1 .kindsw summary::-webkit-details-marker{display:none}
h1 .kindsw ul{position:absolute;z-index:60;margin-top:.1em;background:var(--ink);border-radius:10px;padding:.12em 0;box-shadow:0 12px 30px rgba(0,0,0,.35);list-style:none;min-width:5.2em}
h1 .kindsw ul a{display:block;color:#fff;font-family:'Archivo','Noto Sans JP',sans-serif;font-weight:900;font-size:.62em;text-transform:uppercase;text-decoration:none;padding:.22em .5em;white-space:nowrap}
h1 .kindsw ul a:hover{background:var(--ac)}
h1 .areasw{display:inline-block;vertical-align:baseline;max-width:100%;position:relative}
h1 .areasw summary{position:relative;display:inline-flex;align-items:center;gap:.08em;background:var(--ink);color:#fff;padding:.02em .12em .06em .16em;border-radius:.12em;cursor:pointer;list-style:none;max-width:100%}
h1 .areasw summary::-webkit-details-marker{display:none}
h1 .areasw summary em{font-style:normal;white-space:nowrap}
h1 .areasw .chev{width:.34em;height:.34em;flex:none}
h1 .areasw ul{position:absolute;z-index:60;margin-top:.1em;background:var(--ink);border-radius:10px;padding:.12em 0;box-shadow:0 12px 30px rgba(0,0,0,.35);list-style:none}
h1 .areasw ul a{display:block;color:#fff;font-family:'Archivo','Noto Sans JP',sans-serif;font-weight:900;font-size:.62em;text-transform:uppercase;text-decoration:none;padding:.22em .5em;white-space:nowrap}
h1 .areasw ul a:hover{background:var(--ac)}
h1 .areasw ul a::after{content:' →'}
.hint{position:absolute;left:calc(100% + 10px);top:0;bottom:0;z-index:61;display:flex;align-items:center;gap:.3em;background:#FFFFFF;color:var(--ink);border:2.5px solid var(--ink);border-radius:999px;padding:0 5px;font-family:'Archivo','Noto Sans JP',sans-serif;font-weight:800;font-size:min(.33em,12px);line-height:1;letter-spacing:.01em;text-transform:uppercase;box-shadow:3px 3px 0 rgba(18,18,18,.9);pointer-events:none;white-space:nowrap}
.hint::after{content:'';position:absolute;left:-8px;top:50%;width:10px;height:10px;background:#FFFFFF;border-left:2.5px solid var(--ink);border-bottom:2.5px solid var(--ink);transform:translateY(-50%) rotate(45deg)}
details[open ] .hint{display:none}
.intro{font-size:15.5px;line-height:1.65;color:var(--ink);max-width:640px}
.intro b{background:linear-gradient(transparent 62%,#F2CE5F 62%);font-weight:800}
.station{margin-top:16px;border:3px solid var(--ink);background:var(--card);box-shadow:6px 6px 0 rgba(18,18,18,.9)}
.station .hd2{background:var(--ink);color:#fff;font-family:'Archivo','Noto Sans JP',sans-serif;font-weight:900;font-size:15px;letter-spacing:.14em;padding:7px 12px 6px}
.station .bd{padding:10px 14px 12px;display:grid;gap:6px}
.station .r{display:flex;gap:10px;font-size:14px;line-height:1.5}
.station .r b{flex:none;width:118px;font-family:'Archivo','Noto Sans JP',sans-serif;font-weight:900;font-size:12.5px;letter-spacing:.08em;padding-top:2px}
.hero{position:relative;margin-top:18px;border:3px solid var(--ink);box-shadow:6px 6px 0 rgba(18,18,18,.9);background:#DDD9CF}
.hero.mos{display:grid;grid-template-columns:2fr 1fr;grid-template-rows:1fr 1fr;height:340px}
.hero.mos a{display:block;overflow:hidden}
.hero.mos a:first-child{grid-row:1/3}
.hero.mos.n1{grid-template-columns:1fr;grid-template-rows:1fr}
.hero.mos.n1 a:first-child{grid-row:auto}
.hero.mos.n2{grid-template-columns:1fr 1fr;grid-template-rows:1fr}
.hero.mos.n2 a:first-child{grid-row:auto}
.hero.mos img{width:100%;height:100%;object-fit:cover;display:block}
.hero .vt{position:absolute;top:0;left:0;background:var(--ac);color:#fff;font-weight:900;font-size:15px;letter-spacing:.3em;padding:8px 5px;writing-mode:vertical-rl;z-index:2}
.hb{display:flex;justify-content:space-between;align-items:center;gap:12px;background:var(--ink);color:#fff;font-family:'Archivo','Noto Sans JP',sans-serif;font-weight:900;font-size:14.5px;letter-spacing:.06em;text-transform:uppercase;padding:9px 12px 8px;margin-top:0}
.hb b{color:#F2CE5F;font-weight:900;text-align:right}
.mood{margin-top:18px}
.mood .mt{font-family:'Archivo','Noto Sans JP',sans-serif;font-weight:900;font-size:19px;letter-spacing:.02em;text-transform:uppercase;margin-bottom:8px}
.mood .chips{display:grid;grid-template-columns:repeat(auto-fill,minmax(118px,1fr));gap:8px}
.mood .chips button{display:flex;align-items:center;gap:7px;background:var(--card);border:2.5px solid var(--ink);border-radius:12px;padding:8px 10px;font:inherit;font-family:'Archivo','Noto Sans JP',sans-serif;font-weight:900;font-size:14px;color:var(--ink);cursor:pointer;text-align:left;box-shadow:3px 3px 0 rgba(18,18,18,.85)}
.mood .chips button svg{color:var(--ac);flex:none}
.mood .chips button small{margin-left:auto;font-size:12.5px;color:var(--mut);font-weight:900}
.mood .chips button[aria-pressed="true"]{background:var(--ink);color:#fff}
.mood .chips button[aria-pressed="true"] svg{color:#F2CE5F}
.mood .chips button[aria-pressed="true"] small{color:#F2CE5F}
.mood .chips button:disabled{opacity:.38;cursor:default;box-shadow:none}
.mood .mn{margin-top:8px;font-size:13.5px;font-weight:700;color:var(--mut);min-height:1.2em}
.maphd{display:flex;justify-content:space-between;align-items:center;gap:12px;margin:22px 0 8px;flex-wrap:wrap}
.maphd h2{font-family:'Archivo','Noto Sans JP',sans-serif;font-weight:900;font-size:24px;text-transform:uppercase;letter-spacing:.01em}
.sw{display:inline-flex;align-items:center;gap:8px;font-family:'Archivo','Noto Sans JP',sans-serif;font-weight:900;font-size:13px;letter-spacing:.06em;cursor:pointer}
.sw input{position:absolute;opacity:0;width:0;height:0}
.sw .trk{width:46px;height:26px;border-radius:999px;background:#CFCBC0;border:2.5px solid var(--ink);position:relative;transition:background .15s;flex:none}
.sw .trk::after{content:'';position:absolute;top:2px;left:2px;width:17px;height:17px;border-radius:50%;background:#fff;border:2.5px solid var(--ink);transition:left .15s}
.sw input:checked+.trk{background:var(--open)}
.sw input:checked+.trk::after{left:20px}
.mapwrap{position:relative;border:3px solid var(--ink);background:#E9E8E4;box-shadow:6px 6px 0 rgba(18,18,18,.9);overflow:hidden;touch-action:none}
.pz{overflow:hidden;cursor:grab}
.pz.grabbing{cursor:grabbing}
.pz-inner{position:relative;transform-origin:0 0;will-change:transform}
.mapsvg{display:block;width:100%;height:auto}
.pins{position:absolute;inset:0}
.pin{position:absolute;transform:translate(-50%,-100%);background:none;border:0;padding:0;cursor:pointer;z-index:3;font:inherit}
.pin:hover,.pin:focus-visible{z-index:6}
.pin.sel{z-index:7}
.thumb-card{position:relative;display:block;width:118px;background:var(--card);border:2.5px solid var(--ink);border-radius:9px;box-shadow:2.5px 2.5px 0 rgba(18,18,18,.85);overflow:visible;transition:transform .12s ease}
.pin:hover .thumb-card,.pin:focus-visible .thumb-card,.pin.sel .thumb-card{transform:scale(1.07)}
.pin.sel .thumb-card{outline:3px solid var(--ac);outline-offset:1px}
.thumb-head{display:flex;align-items:center;gap:5px;background:var(--ink);color:#fff;border-radius:6px 6px 0 0;padding:3.5px 7px 3px;font-family:'Archivo','Noto Sans JP',sans-serif;font-weight:900;font-size:10.5px;letter-spacing:.02em;white-space:nowrap;overflow:hidden}
.thumb-head b{background:#fff;color:var(--ink);border-radius:50%;width:16px;height:16px;line-height:16px;text-align:center;font-size:10.5px;flex:none}
.thumb-photo{display:block;width:100%;height:74px;background-size:cover;background-position:center;border-top:2px solid var(--ink);border-radius:0 0 6px 6px}
.thumb-photo.nophoto{display:flex;align-items:center;justify-content:center;background:linear-gradient(140deg,#A8841A,#6E560B);height:74px}
.thumb-tail{position:absolute;left:50%;bottom:-9px;transform:translateX(-50%);width:14px;height:14px;background:var(--card);border-right:2.5px solid var(--ink);border-bottom:2.5px solid var(--ink);rotate:45deg}
.pz-btns{position:absolute;right:10px;top:10px;display:flex;flex-direction:column;gap:6px;z-index:8}
.pzb{width:34px;height:34px;border-radius:9px;border:2.5px solid var(--ink);background:#fff;font-size:17px;font-weight:900;line-height:1;cursor:pointer;box-shadow:2px 2px 0 rgba(18,18,18,.8)}
.maphint{position:absolute;left:10px;bottom:8px;z-index:8;background:rgba(255,255,255,.92);border:2px solid var(--ink);border-radius:999px;padding:3px 10px;font-size:11px;font-weight:700}
.hide{display:none !important}
.cards{display:grid;gap:20px;margin-top:20px}
.card{background:var(--card);border:3px solid var(--ink);box-shadow:6px 6px 0 rgba(18,18,18,.9);padding:14px 14px 12px;scroll-margin-top:14px}
.card.flash{animation:flash 1.4s ease}
@keyframes flash{0%,55%{background:var(--pop);border-color:var(--popb)}100%{background:var(--card)}}
.hd{display:flex;gap:12px;align-items:flex-start}
.big{font-family:'Archivo',sans-serif;font-weight:900;font-size:44px;line-height:.95;color:var(--ac);background:none;border:0;padding:0;cursor:pointer;flex:none}
.big:hover{text-decoration:underline}
.hdtx{flex:1;min-width:0}
.genre{display:inline-block;background:var(--ac);color:#fff;font-family:'Archivo','Noto Sans JP',sans-serif;font-weight:900;font-size:11.5px;letter-spacing:.1em;text-transform:uppercase;padding:3px 8px 2px;border-radius:4px}
.card h3{font-family:'Archivo','Noto Sans JP',sans-serif;font-weight:900;font-size:23px;line-height:1.15;margin-top:5px}
.adr{font-size:13px;color:var(--mut);font-weight:700;margin-top:2px;line-height:1.45}
.car{position:relative;margin-top:10px;border:2.5px solid var(--ink);background:#E9E8E4;height:214px;overflow:hidden}
.car .trk{display:flex;height:100%;overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:none;-webkit-overflow-scrolling:touch;cursor:grab}
.car .trk::-webkit-scrollbar{display:none}
.car .trk img{flex:0 0 100%;width:100%;height:100%;object-fit:cover;scroll-snap-align:start;display:block}
.car .trk.drag{cursor:grabbing;scroll-snap-type:none}
.car .trk.drag img{pointer-events:none}
.cb{position:absolute;top:50%;transform:translateY(-50%);z-index:4;width:34px;height:46px;border:0;background:rgba(18,18,18,.55);color:#fff;font-size:26px;line-height:1;cursor:pointer;display:flex;align-items:center;justify-content:center;padding:0;font-family:inherit}
.cb:hover{background:rgba(18,18,18,.82)}
.cb.pv{left:0;border-radius:0 8px 8px 0}
.cb.nx{right:0;border-radius:8px 0 0 8px}
.car.nophoto{height:120px;display:flex;align-items:center;justify-content:center;background:linear-gradient(140deg,#A8841A,#6E560B)}
.car .pholder{display:flex}
.car .pholder svg{width:52px;height:52px}
.st{position:absolute;right:8px;bottom:8px;background:var(--ink);color:#fff;font-family:'Archivo','Noto Sans JP',sans-serif;font-weight:900;font-size:11.5px;letter-spacing:.08em;padding:4px 8px 3px;border-radius:4px;z-index:2}
.st.open{background:var(--open)}
.st:empty{display:none}
.cn{position:absolute;left:8px;bottom:8px;z-index:2;background:rgba(18,18,18,.82);color:#fff;font-size:11.5px;font-weight:700;padding:4px 8px 3px;border-radius:4px}
.photo-actions{position:absolute;top:.5rem;right:.5rem;display:flex;gap:.45rem;z-index:3}
.icon-btn{width:44px;height:44px;min-height:44px;border-radius:50%;background:#fff;border:none;box-shadow:0 2px 8px rgba(18,18,18,.35),0 0 0 1px rgba(18,18,18,.08);display:inline-flex;align-items:center;justify-content:center;cursor:pointer;text-decoration:none;padding:0;flex:none;color:var(--ink)}
.icon-btn svg{width:24px;height:24px;display:block}
.icon-btn:active{transform:scale(.94)}
.tx{font-size:14.5px;line-height:1.6;margin-top:10px}
.strip{display:flex;flex-wrap:wrap;align-items:center;column-gap:16px;row-gap:5px;background:var(--ink);color:#fff;margin:11px -14px 0;padding:8px 14px;font-size:13.5px}
.strip>span{display:inline-flex;align-items:center;gap:6px}
.strip .clb{background:#C1272D;color:#fff;font-weight:900;font-size:11.5px;letter-spacing:.06em;padding:3px 8px 2px;border-radius:4px}
.strip .today{font-weight:700}
.strip .rt{margin-left:auto}
.know{margin-top:26px;background:var(--ink);color:#fff;padding:18px 18px 14px;box-shadow:6px 6px 0 rgba(18,18,18,.35)}
.know h2{font-family:'Archivo','Noto Sans JP',sans-serif;font-weight:900;font-size:21px;text-transform:uppercase;margin-bottom:8px}
.know li{font-size:14px;line-height:1.6;margin:0 0 6px 18px}
footer{margin-top:22px;font-size:12.5px;color:var(--mut);line-height:1.7}
footer .areas a{color:var(--ink);font-weight:800;text-decoration:none;border-bottom:2px solid var(--ac)}
@media (max-width:560px){
.hero.mos{height:240px}
.card h3{font-size:20px}
.big{font-size:36px}
.thumb-card{width:96px}
.thumb-photo{height:60px}
.thumb-photo.nophoto{height:60px}
.photo-actions{top:.35rem;right:.35rem;gap:.25rem}
.strip .rt{margin-left:0}
.station .r b{width:92px}
}
"""

KNOW_HTML = """
<h2>Good to know</h2>
<ul>
<li><b>Cash still matters.</b> Most chains take cards and IC, but small vintage shops may be cash only — carry a few thousand yen.</li>
<li><b>Condition is graded on the tag.</b> Japanese second-hand shops grade strictly; a B-rank here is often cleaner than "like new" elsewhere.</li>
<li><b>Tax-free:</b> larger chains (2nd STREET, TREASURE FACTORY, Kindal) do tax-free for visitors — bring your passport.</li>
<li><b>Shimokitazawa and Koenji are dense enough to wander.</b> The other areas reward a plan: check the OPEN NOW switch before you go.</li>
</ul>"""

LANG_JS = r"""
<script>
/* Language switch — same system as eatmap: the button cycles
   EN -> JA -> ZH -> ES -> DE -> KO, swapping visible text from the
   __T dictionary. Choice persists in localStorage; ?lang= wins. */
window.__T = __T_DICT__;
(function(){
var LANGS=['en','ja','zh','es','de','ko'];
var orig=new WeakMap();
function tr(s,L){
  if(L==='en')return s;
  var t=window.__T[s],m;
  if(t&&t[L])return t[L];
  if(m=s.match(/^(\d+) min walk$/)){t=window.__T['{n} min walk'];if(t&&t[L])return t[L].replace('{n}',m[1]);}
  if(m=s.match(/^Open now: (\d+) of (\d+) shops in this area$/)){t=window.__T['Open now: {a} of {b} shops in this area'];if(t&&t[L])return t[L].replace('{a}',m[1]).replace('{b}',m[2]);}
  if(m=s.match(/^Showing (\d+) shops$/)){t=window.__T['Showing {n} shops'];if(t&&t[L])return t[L].replace('{n}',m[1]);}
  if(m=s.match(/^Google ★([\d.]+) · ([\d,]+) reviews$/)){t=window.__T['Google ★{r} · {n} reviews'];if(t&&t[L])return t[L].replace('{r}',m[1]).replace('{n}',m[2]);}
  if(m=s.match(/^All (\d+) within (\d+) min of the station$/)){t=window.__T['All {n} within {m} min of the station'];if(t&&t[L])return t[L].replace('{n}',m[1]).replace('{m}',m[2]);}
  if(m=s.match(/^(\d+) within a 5 min walk$/)){t=window.__T['{n} within a 5 min walk'];if(t&&t[L])return t[L].replace('{n}',m[1]);}
  if(m=s.match(/^(\d+) a bit further out$/)){t=window.__T['{n} a bit further out'];if(t&&t[L])return t[L].replace('{n}',m[1]);}
  if(m=s.match(/^(\d+) shops, a short stroll from the station$/)){t=window.__T['{n} shops, a short stroll from the station'];if(t&&t[L])return t[L].replace('{n}',m[1]);}
  if(m=s.match(/^1 shop · (\d+) min from (.+) Sta\.$/)){t=window.__T['1 shop · {n} min from {s} Sta.'];if(t&&t[L]){var nm=tr(m[2],L);return t[L].replace('{n}',m[1]).replace('{s}',nm);}}
  if(m=s.match(/^· (.+) Sta\.$/)){t=window.__T['{s} Sta.'];if(t&&t[L]){var nm2=tr(m[1],L);return '· '+t[L].replace('{s}',nm2);}}
  if(m=s.match(/^(.+) Sta\.$/)){t=window.__T['{s} Sta.'];if(t&&t[L]){var nm3=tr(m[1],L);return t[L].replace('{s}',nm3);}}
  var pre=[['Today ','Today'],['Opens ','Opens'],['Closes ','Closes'],['Closed: ','Closed:']];
  for(var i=0;i<pre.length;i++){if(s.indexOf(pre[i][0])===0){t=window.__T[pre[i][1]];if(t&&t[L])return t[L]+s.slice(pre[i][0].length-1);}}
  var days={Mon:'MON',Tue:'TUE',Wed:'WED',Thu:'THU',Fri:'FRI',Sat:'SAT',Sun:'SUN'};
  if(/^(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\b/.test(s)){var k=s.slice(0,3);t=window.__T[days[k]];if(t&&t[L])return t[L]+s.slice(3);}
  return s;
}
var mo=null;
function apply(L){
  if(mo)mo.disconnect();
  document.documentElement.lang=(L==='zh'?'zh-CN':L);
  var w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
  var nodes=[];while(w.nextNode())nodes.push(w.currentNode);
  nodes.forEach(function(n){
    if(!orig.has(n))orig.set(n,n.nodeValue);
    var el=n.parentElement;
    if(el&&(el.closest('script,style,svg,.langsw,.big')||el.closest('.no')))return;
    var raw=orig.get(n),lead=raw.match(/^\s*/)[0],tail=raw.match(/\s*$/)[0],core=raw.trim();
    if(!core)return;
    var nv=lead+tr(core,L)+tail;
    if(n.nodeValue!==nv)n.nodeValue=nv;
  });
  document.querySelectorAll('.langsw .fl svg').forEach(function(sv){sv.classList.toggle('on',sv.getAttribute('data-l')===L);});
  var lc=document.querySelector('.langsw .lc');if(lc&&lc.textContent!==L.toUpperCase())lc.textContent=L.toUpperCase();
  if(mo)mo.observe(document.body,{childList:true,subtree:true,characterData:true});
}
var start='en';
try{var q=new URLSearchParams(location.search).get('lang');var saved=localStorage.getItem('thriftmap_lang');
if(q&&LANGS.indexOf(q)>=0)start=q;else if(saved&&LANGS.indexOf(saved)>=0)start=saved;}catch(e){}
if(start!=='en')apply(start);
var btn=document.querySelector('.langsw');
if(btn)btn.addEventListener('click',function(){
  var cur=document.documentElement.lang||'en';if(cur==='zh-CN')cur='zh';
  var nx=LANGS[(LANGS.indexOf(cur)+1)%LANGS.length];
  apply(nx);
  try{localStorage.setItem('thriftmap_lang',nx);}catch(e){}
});
mo=new MutationObserver(function(){var L=document.documentElement.lang;if(L&&L!=='en')apply(L==='zh-CN'?'zh':L);});
mo.observe(document.body,{childList:true,subtree:true,characterData:true});
})();
</script>
"""

UI_DICT = {
"Where to": {"ja": "Where to", "zh": "Where to", "es": "Where to", "de": "Where to", "ko": "Where to"},
"Thrift": {"ja": "Thrift", "zh": "Thrift", "es": "Thrift", "de": "Thrift", "ko": "Thrift"},
"in": {"ja": "in", "zh": "in", "es": "in", "de": "in", "ko": "in"},
"Tap to": {"ja": "タップで", "zh": "点按", "es": "Toca para", "de": "Tippen:", "ko": "탭해서"},
"change area": {"ja": "エリア切替", "zh": "切换区域", "es": "cambiar zona", "de": "Gebiet wechseln", "ko": "지역 변경"},
"Shimokitazawa": {"ja": "下北沢", "zh": "下北泽", "es": "Shimokitazawa", "de": "Shimokitazawa", "ko": "시모키타자와"},
"Koenji": {"ja": "高円寺", "zh": "高圆寺", "es": "Koenji", "de": "Koenji", "ko": "고엔지"},
"Kichijoji": {"ja": "吉祥寺", "zh": "吉祥寺", "es": "Kichijoji", "de": "Kichijoji", "ko": "기치조지"},
"Nakano": {"ja": "中野", "zh": "中野", "es": "Nakano", "de": "Nakano", "ko": "나카노"},
"Harajuku & Shibuya": {"ja": "原宿・渋谷", "zh": "原宿·涩谷", "es": "Harajuku y Shibuya", "de": "Harajuku & Shibuya", "ko": "하라주쿠·시부야"},
"Akihabara": {"ja": "秋葉原", "zh": "秋叶原", "es": "Akihabara", "de": "Akihabara", "ko": "아키하바라"},
"Ikebukuro": {"ja": "池袋", "zh": "池袋", "es": "Ikebukuro", "de": "Ikebukuro", "ko": "이케부쿠로"},
"Ueno & Ameyoko": {"ja": "上野・アメ横", "zh": "上野·阿美横", "es": "Ueno y Ameyoko", "de": "Ueno & Ameyoko", "ko": "우에노·아메요코"},
"SHIMOKITAZAWA": {"ja": "下北沢", "zh": "下北泽", "es": "SHIMOKITAZAWA", "de": "SHIMOKITAZAWA", "ko": "시모키타자와"},
"KOENJI": {"ja": "高円寺", "zh": "高圆寺", "es": "KOENJI", "de": "KOENJI", "ko": "고엔지"},
"KICHIJOJI": {"ja": "吉祥寺", "zh": "吉祥寺", "es": "KICHIJOJI", "de": "KICHIJOJI", "ko": "기치조지"},
"NAKANO": {"ja": "中野", "zh": "中野", "es": "NAKANO", "de": "NAKANO", "ko": "나카노"},
"HARAJUKU & SHIBUYA": {"ja": "原宿・渋谷", "zh": "原宿·涩谷", "es": "HARAJUKU Y SHIBUYA", "de": "HARAJUKU & SHIBUYA", "ko": "하라주쿠·시부야"},
"AKIHABARA": {"ja": "秋葉原", "zh": "秋叶原", "es": "AKIHABARA", "de": "AKIHABARA", "ko": "아키하바라"},
"IKEBUKURO": {"ja": "池袋", "zh": "池袋", "es": "IKEBUKURO", "de": "IKEBUKURO", "ko": "이케부쿠로"},
"UENO & AMEYOKO": {"ja": "上野・アメ横", "zh": "上野·阿美横", "es": "UENO Y AMEYOKO", "de": "UENO & AMEYOKO", "ko": "우에노·아메요코"},
"Okachimachi": {"ja": "御徒町", "zh": "御徒町", "es": "Okachimachi", "de": "Okachimachi", "ko": "오카치마치"},
"Harajuku": {"ja": "原宿", "zh": "原宿", "es": "Harajuku", "de": "Harajuku", "ko": "하라주쿠"},
"Ueno": {"ja": "上野", "zh": "上野", "es": "Ueno", "de": "Ueno", "ko": "우에노"},
"GETTING THERE": {"ja": "アクセス", "zh": "交通", "es": "CÓMO LLEGAR", "de": "ANFAHRT", "ko": "가는 법"},
"THE AREA": {"ja": "エリア", "zh": "区域", "es": "LA ZONA", "de": "DAS VIERTEL", "ko": "지역"},
"STATION": {"ja": "最寄り駅", "zh": "车站", "es": "ESTACIÓN", "de": "BAHNHOF", "ko": "역"},
"Open now": {"ja": "営業中のみ", "zh": "营业中", "es": "Abierto ahora", "de": "Jetzt geöffnet", "ko": "영업 중"},
"I'm after": {"ja": "探しているのは", "zh": "我想找", "es": "Busco", "de": "Ich suche", "ko": "찾는 것"},
"Vintage": {"ja": "ヴィンテージ", "zh": "复古", "es": "Vintage", "de": "Vintage", "ko": "빈티지"},
"Brand resale": {"ja": "ブランド買取", "zh": "品牌二手", "es": "Marcas", "de": "Marken-Resale", "ko": "브랜드 리세일"},
"Recycle": {"ja": "リサイクル", "zh": "回收店", "es": "Reciclaje", "de": "Recycling", "ko": "리사이클"},
"Specialty": {"ja": "専門店", "zh": "专门店", "es": "Especialidad", "de": "Spezial", "ko": "전문점"},
"Drag to pan · Pinch or scroll to zoom · Tap a pin": {"ja": "ドラッグで移動 · ピンチ/スクロールで拡大 · ピンをタップ", "zh": "拖动平移 · 捏合或滚动缩放 · 点按图钉", "es": "Arrastra para mover · Pellizca o desplázate para ampliar · Toca un pin", "de": "Ziehen zum Verschieben · Pinchen oder Scrollen zum Zoomen · Pin antippen", "ko": "드래그로 이동 · 핀치/스크롤로 확대 · 핀 탭"},
"Outside": {"ja": "外観", "zh": "外观", "es": "Exterior", "de": "Außen", "ko": "외관"},
"Inside": {"ja": "店内", "zh": "店内", "es": "Interior", "de": "Innen", "ko": "실내"},
"OPEN NOW": {"ja": "営業中", "zh": "营业中", "es": "ABIERTO", "de": "GEÖFFNET", "ko": "영업 중"},
"CLOSED": {"ja": "営業時間外", "zh": "已打烊", "es": "CERRADO", "de": "GESCHLOSSEN", "ko": "영업 종료"},
"Closed today": {"ja": "本日休業", "zh": "今日休息", "es": "Cerrado hoy", "de": "Heute geschlossen", "ko": "오늘 휴무"},
"Today": {"ja": "本日", "zh": "今天", "es": "Hoy", "de": "Heute", "ko": "오늘"},
"Opens": {"ja": "開店", "zh": "开门", "es": "Abre", "de": "Öffnet", "ko": "오픈"},
"Closes": {"ja": "閉店", "zh": "关门", "es": "Cierra", "de": "Schließt", "ko": "마감"},
"Closed:": {"ja": "定休日：", "zh": "休息日：", "es": "Cerrado:", "de": "Ruhetag:", "ko": "휴무:"},
"MON": {"ja": "月曜", "zh": "周一", "es": "lun", "de": "Mo", "ko": "월"},
"TUE": {"ja": "火曜", "zh": "周二", "es": "mar", "de": "Di", "ko": "화"},
"WED": {"ja": "水曜", "zh": "周三", "es": "mié", "de": "Mi", "ko": "수"},
"THU": {"ja": "木曜", "zh": "周四", "es": "jue", "de": "Do", "ko": "목"},
"FRI": {"ja": "金曜", "zh": "周五", "es": "vie", "de": "Fr", "ko": "금"},
"SAT": {"ja": "土曜", "zh": "周六", "es": "sáb", "de": "Sa", "ko": "토"},
"SUN": {"ja": "日曜", "zh": "周日", "es": "dom", "de": "So", "ko": "일"},
"{n} min walk": {"ja": "徒歩{n}分", "zh": "步行{n}分钟", "es": "{n} min a pie", "de": "{n} Min. zu Fuß", "ko": "도보 {n}분"},
"{s} Sta.": {"ja": "{s}駅", "zh": "{s}站", "es": "Est. {s}", "de": "Bh. {s}", "ko": "{s}역"},
"Open now: {a} of {b} shops in this area": {"ja": "営業中：このエリアの{b}店中{a}店", "zh": "营业中：本区{b}家中的{a}家", "es": "Abiertas: {a} de {b} tiendas de la zona", "de": "Jetzt geöffnet: {a} von {b} Läden hier", "ko": "영업 중: 이 지역 {b}곳 중 {a}곳"},
"Showing {n} shops": {"ja": "{n}店を表示中", "zh": "显示{n}家店", "es": "Mostrando {n} tiendas", "de": "{n} Läden angezeigt", "ko": "{n}곳 표시 중"},
"Google ★{r} · {n} reviews": {"ja": "Google ★{r} · レビュー{n}件", "zh": "Google ★{r} · {n}条评价", "es": "Google ★{r} · {n} reseñas", "de": "Google ★{r} · {n} Bewertungen", "ko": "Google ★{r} · 리뷰 {n}개"},
"All {n} within {m} min of the station": {"ja": "全{n}店が駅から徒歩{m}分以内", "zh": "全部{n}家都在车站步行{m}分钟内", "es": "Las {n} a menos de {m} min de la estación", "de": "Alle {n} max. {m} Min. vom Bahnhof", "ko": "전 {n}곳이 역에서 도보 {m}분 이내"},
"{n} within a 5 min walk": {"ja": "徒歩5分以内が{n}店", "zh": "步行5分钟内{n}家", "es": "{n} a menos de 5 min a pie", "de": "{n} max. 5 Min. zu Fuß", "ko": "도보 5분 이내 {n}곳"},
"{n} a bit further out": {"ja": "少し歩く店が{n}店", "zh": "稍远的有{n}家", "es": "{n} un poco más lejos", "de": "{n} etwas weiter weg", "ko": "조금 먼 곳 {n}곳"},
"{n} shops, a short stroll from the station": {"ja": "駅から少し歩く{n}店", "zh": "离车站稍远的{n}家店", "es": "{n} tiendas, a un paseo de la estación", "de": "{n} Läden, kurzer Spaziergang vom Bahnhof", "ko": "역에서 조금 걷는 {n}곳"},
"1 shop · {n} min from {s} Sta.": {"ja": "1店 · {s}駅から徒歩{n}分", "zh": "1家店 · 离{s}站步行{n}分钟", "es": "1 tienda · {n} min desde la est. {s}", "de": "1 Laden · {n} Min. ab Bh. {s}", "ko": "1곳 · {s}역에서 도보 {n}분"},
"Worth the short walk": {"ja": "歩く価値あり", "zh": "值得一走", "es": "Vale la pena el paseo", "de": "Den Weg wert", "ko": "걸을 가치 있음"},
"Good to know": {"ja": "知っておくと便利", "zh": "实用贴士", "es": "Bueno saber", "de": "Gut zu wissen", "ko": "알아두면 좋아요"},
"Cash still matters.": {"ja": "現金はまだ大事。", "zh": "现金仍然重要。", "es": "El efectivo sigue importando.", "de": "Bargeld zählt weiterhin.", "ko": "현금은 여전히 필수."},
"Most chains take cards and IC, but small vintage shops may be cash only — carry a few thousand yen.": {"ja": "大手チェーンはカード・IC対応だが、小さな古着屋は現金のみの場合がある。数千円は持っておくと安心。", "zh": "大型连锁店可刷卡和交通卡，但小型复古店可能只收现金，建议带几千日元。", "es": "Las cadenas aceptan tarjeta e IC, pero las tiendas vintage pequeñas pueden ser solo efectivo: lleva unos miles de yenes.", "de": "Ketten nehmen Karten und IC, kleine Vintage-Läden oft nur Bargeld — ein paar Tausend Yen einpacken.", "ko": "대형 체인은 카드·IC 가능하지만 작은 빈티지 숍은 현금만 받는 곳도 있으니 몇천 엔은 챙기세요."},
"Condition is graded on the tag.": {"ja": "状態は値札のランクで表示。", "zh": "成色在价签上分级。", "es": "El estado se indica en la etiqueta.", "de": "Der Zustand steht am Etikett.", "ko": "상태는 태그에 등급으로 표시."},
"Japanese second-hand shops grade strictly; a B-rank here is often cleaner than \"like new\" elsewhere.": {"ja": "日本のリサイクルショップの査定は厳しめで、Bランクでも他国の「新品同様」よりきれいなことが多い。", "zh": "日本二手店分级严格，B级往往比其他地方的“几乎全新”还干净。", "es": "Las tiendas japonesas de segunda mano califican con rigor; un grado B aquí suele estar más limpio que un \"como nuevo\" en otros lugares.", "de": "Japanische Secondhand-Läden bewerten streng; ein B-Rang ist hier oft sauberer als \"wie neu\" anderswo.", "ko": "일본 중고 숍은 등급이 엄격해서 B등급도 다른 나라의 '새것 수준'보다 깨끗한 경우가 많아요."},
"Tax-free:": {"ja": "免税：", "zh": "免税：", "es": "Tax-free:", "de": "Tax-free:", "ko": "면세:"},
"larger chains (2nd STREET, TREASURE FACTORY, Kindal) do tax-free for visitors — bring your passport.": {"ja": "大手チェーン（2nd STREET、トレファク、Kindal）は免税対応。パスポートを持参して。", "zh": "大型连锁店（2nd STREET、TREASURE FACTORY、Kindal）为游客提供免税，请带护照。", "es": "las cadenas grandes (2nd STREET, TREASURE FACTORY, Kindal) ofrecen tax-free a visitantes: trae tu pasaporte.", "de": "große Ketten (2nd STREET, TREASURE FACTORY, Kindal) bieten Tax-free für Besucher — Pass mitbringen.", "ko": "대형 체인(2nd STREET, TREASURE FACTORY, Kindal)은 면세 가능. 여권을 가져오세요."},
"Shimokitazawa and Koenji are dense enough to wander.": {"ja": "下北沢と高円寺はぶらぶら歩くだけで回れる密度。", "zh": "下北泽和高圆寺店铺密集，适合随意逛。", "es": "Shimokitazawa y Koenji son densos para pasear sin plan.", "de": "Shimokitazawa und Koenji sind dicht genug zum Schlendern.", "ko": "시모키타자와와 고엔지는 그냥 걸어다니기만 해도 될 만큼 밀집해 있어요."},
"The other areas reward a plan: check the OPEN NOW switch before you go.": {"ja": "他のエリアは計画性が大事。出発前に OPEN NOW スイッチで営業中を確認して。", "zh": "其他区域建议先计划：出发前用 OPEN NOW 开关确认营业状态。", "es": "Las demás zonas recompensan un plan: revisa el interruptor OPEN NOW antes de ir.", "de": "Andere Viertel belohnen Planung: vor dem Losgehen den OPEN-NOW-Schalter prüfen.", "ko": "다른 지역은 계획이 중요해요. 출발 전에 OPEN NOW 스위치로 영업 여부를 확인하세요."},
"Areas:": {"ja": "エリア：", "zh": "区域：", "es": "Zonas:", "de": "Gebiete:", "ko": "지역:"},
"— a guest guide by Anime Sensei": {"ja": "— Anime Sensei のゲストガイド", "zh": "— Anime Sensei 的游客指南", "es": "— guía para invitados de Anime Sensei", "de": "— ein Gästeguide von Anime Sensei", "ko": "— Anime Sensei의 게스트 가이드"},
"Shop details checked on official sites and Google listings on Nov 24, 2026.": {"ja": "店舗情報は2026年11月24日に公式サイトと Google 掲載情報で確認済み。", "zh": "店铺信息已于2026年11月24日通过官方网站和 Google 商家信息核实。", "es": "Datos de tiendas verificados en sitios oficiales y fichas de Google el 24 de nov. de 2026.", "de": "Ladendaten am 24. Nov. 2026 auf offiziellen Seiten und Google-Einträgen geprüft.", "ko": "매장 정보는 2026년 11월 24일 공식 사이트와 Google 정보로 확인했습니다."},
"Map sketches are schematic. Coordinates: GSI address search. Always confirm the exact spot with the map pin button on each card.": {"ja": "地図スケッチは模式図。座標は国土地理院の住所検索による。正確な場所は各カードの地図ピンボタンで確認して。", "zh": "地图草图为示意图。坐标来自 GSI 地址搜索。请用每张卡片上的地图图钉按钮确认确切位置。", "es": "Los mapas son esquemáticos. Coordenadas: búsqueda de direcciones GSI. Confirma el lugar exacto con el botón de pin de cada tarjeta.", "de": "Die Kartenskizzen sind schematisch. Koordinaten: GSI-Adresssuche. Den genauen Ort mit dem Pin-Button auf jeder Karte bestätigen.", "ko": "지도 스케치는 개략도입니다. 좌표는 GSI 주소 검색 기준. 정확한 위치는 각 카드의 지도 핀 버튼으로 확인하세요."},
"Tokyo's thrift capital. Eight shops within a few minutes of the station — vintage dens, recycle chains and tiny curated stores packed into the lanes on both sides of the tracks.": {"ja": "東京の古着の中心地。駅から数分の範囲に8店。ヴィンテージの名店、リサイクルチェーン、路地の小さなセレクト店が線路の両側に密集している。"},
"Vintage without the Shimokitazawa crowds. Eight shops around the station and its covered shopping streets, strong on American vintage and budget recycle racks.": {"ja": "下北沢ほどの混雑なしにヴィンテージを楽しめる。高円寺駅周辺と商店街に8店。アメリカ古着と手頃なリサイクルが強いエリア。"},
"A local favorite west of the center. Eight shops between the Sun Road arcade and Harmonica Yokocho, mixing big recycle chains with small vintage picks.": {"ja": "都心の西側、地元に愛される街。サンロードとハーモニカ横丁の間に8店。大型リサイクルチェーンと小さなヴィンテージ店が混ざる。"},
"Broadway is a treasure building. Eight clothing shops in and around Nakano Broadway and the Sun Mall arcade — come for the hobby floors, stay for the vintage.": {"ja": "ブロードウェイは宝のビル。中野ブロードウェイとサンモール商店街の内外に古着店8店。ホビーフロアのついでにヴィンテージも楽しめる。"},
"The famous end of Tokyo vintage. Five shops around Harajuku and Shibuya — big-name vintage, brand resale and a huge recycle floor.": {"ja": "東京ヴィンテージの有名どころ。原宿・渋谷周辺に5店。有名ヴィンテージ、ブランド買取、巨大なリサイクルフロアが揃う。"},
"One specialist stop. PENNY TOKYO deals in American vintage a short walk from Akihabara Station — worth the detour between the arcades.": {"ja": "専門店が1店。PENNY TOKYO は秋葉原駅から少し歩くアメリカ古着の店。ゲームセンター巡りの合間に寄る価値がある。"},
"West-side value. Three shops around Ikebukuro Station, including a big 2nd STREET inside P'PARCO.": {"ja": "西側のお得エリア。池袋駅周辺に3店。P'PARCO 内の大型 2nd STREET も入っている。"},
"Ameyoko bargains. Four shops in and around the Ameyoko market streets — workwear, outdoor vintage and recycle racks under the tracks.": {"ja": "アメ横の掘り出し物。アメ横市場の内外に4店。ワークウェア、アウトドア古着、線路下のリサイクルラックが揃う。"},
}

STATUS_JS = """
<script>
const SHOPS = __SHOPS_JSON__;
const DAYN = ['SUN','MON','TUE','WED','THU','FRI','SAT'];
function mins(t){const[a,b]=t.split(':').map(Number);return a*60+b;}
function fmt(m){let h=Math.floor(m/60),mm=m%60;const ap=h>=12?'PM':'AM';h=h%12;if(h===0)h=12;return h+':'+String(mm).padStart(2,'0')+' '+ap;}
function statusFor(sh,now){
  const day=(now.getDay()+6)%7,cur=now.getHours()*60+now.getMinutes();
  const h=sh.hours;
  const ent=h.find(e=>e.d.includes(day));
  if(ent){const o=mins(ent.o);let c=mins(ent.c);if(c<=o)c+=1440;
    if(cur>=o&&cur<c)return{open:true,today:'Today '+fmt(o)+' \\u2013 '+fmt(c%1440)};
    if(cur<o)return{open:false,today:'Today '+fmt(o)+' \\u2013 '+fmt(c%1440)};}
  for(let k=1;k<=7;k++){const d2=(day+k)%7;const e2=h.find(e=>e.d.includes(d2));
    if(e2)return{open:false,today:null};}
  return null;
}
let nowOpenCount=0;
const _now=new Date();
for(const id in SHOPS){
  const sh=SHOPS[id],st=statusFor(sh,_now);
  if(st&&st.open)nowOpenCount++;
  sh._st=st;
  document.querySelectorAll('[data-st="'+id+'"]').forEach(el=>{if(st){el.textContent=st.open?'OPEN NOW':'CLOSED';el.classList.toggle('open',st.open);}else{el.remove();}});
  document.querySelectorAll('[data-today="'+id+'"]').forEach(el=>{if(st&&st.today)el.textContent=st.today;});
}
const nowEl=document.getElementById('nowline');
if(nowEl)nowEl.textContent='Open now: '+nowOpenCount+' of '+Object.keys(SHOPS).length+' shops in this area';
let activeCat=null,onlyOpen=false;
function applyFilters(){
  document.querySelectorAll('.card').forEach(c=>{
    const sh=SHOPS[c.dataset.id];
    const okC=!activeCat||c.dataset.cat===activeCat;
    const okO=!onlyOpen||(sh&&sh._st&&sh._st.open);
    c.classList.toggle('hide',!(okC&&okO));
  });
  document.querySelectorAll('.pin').forEach(p=>{
    const sh=SHOPS[p.dataset.id];
    const okC=!activeCat||p.dataset.cat===activeCat;
    const okO=!onlyOpen||(sh&&sh._st&&sh._st.open);
    p.classList.toggle('hide',!(okC&&okO));
  });
  const vis=document.querySelectorAll('.card:not(.hide)').length;
  const mn=document.querySelector('.mood .mn');
  if(mn)mn.textContent=(activeCat||onlyOpen)?('Showing '+vis+' shops'):'';
}
const openSw=document.getElementById('opensw');
if(openSw)openSw.addEventListener('change',()=>{onlyOpen=openSw.checked;applyFilters();});
document.querySelectorAll('.areasw,.kindsw').forEach(dw=>{
  document.addEventListener('click',e=>{if(!dw.contains(e.target))dw.removeAttribute('open');});
  document.addEventListener('keydown',e=>{if(e.key==='Escape')dw.removeAttribute('open');});
});
document.querySelectorAll('.mood .chips button').forEach(b=>{
  b.addEventListener('click',()=>{
    const cat=b.dataset.cat;
    if(activeCat===cat){activeCat=null;b.setAttribute('aria-pressed','false');}
    else{activeCat=cat;document.querySelectorAll('.mood .chips button').forEach(x=>x.setAttribute('aria-pressed',x===b?'true':'false'));}
    applyFilters();
  });
});
</script>
"""

PINZOOM_JS = """
<script>
document.querySelectorAll('.mapwrap').forEach(wrap=>{
  const pz=wrap.querySelector('.pz'),inner=wrap.querySelector('.pz-inner');
  let scale=1,tx=0,ty=0;
  const pointers=new Map();let pinchD=0,pinchS=1;
  function clampT(){
    const r=pz.getBoundingClientRect();
    const w=inner.offsetWidth*scale,h=inner.offsetHeight*scale;
    tx=w<=r.width?(r.width-w)/2:Math.min(0,Math.max(r.width-w,tx));
    ty=h<=r.height?(r.height-h)/2:Math.min(0,Math.max(r.height-h,ty));
  }
  function apply(){clampT();inner.style.transform='translate('+tx+'px,'+ty+'px) scale('+scale+')';}
  function fit(){
    const r=pz.getBoundingClientRect();
    scale=Math.max(1,r.width/inner.offsetWidth);
    tx=(r.width-inner.offsetWidth*scale)/2;
    ty=0;apply();
  }
  function zoomAt(cx,cy,f){
    const r=pz.getBoundingClientRect();
    const x=cx-r.left,y=cy-r.top;
    const ns=Math.min(4,Math.max(1,scale*f));
    const k=ns/scale;
    tx=x-(x-tx)*k;ty=y-(y-ty)*k;scale=ns;apply();
  }
  pz.addEventListener('pointerdown',e=>{pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});pz.setPointerCapture(e.pointerId);pz.classList.add('grabbing');if(pointers.size===2){const p=[...pointers.values()];pinchD=Math.hypot(p[0].x-p[1].x,p[0].y-p[1].y);pinchS=scale;}});
  pz.addEventListener('pointermove',e=>{
    if(!pointers.has(e.pointerId))return;
    const prev=pointers.get(e.pointerId);
    pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});
    if(pointers.size===1){tx+=e.clientX-prev.x;ty+=e.clientY-prev.y;apply();}
    else if(pointers.size===2){const p=[...pointers.values()];const d=Math.hypot(p[0].x-p[1].x,p[0].y-p[1].y);if(pinchD>0){const cx=(p[0].x+p[1].x)/2,cy=(p[0].y+p[1].y)/2;const target=pinchS*d/pinchD;const f=target/scale;zoomAt(cx,cy,f);}}
  });
  function release(e){pointers.delete(e.pointerId);if(pointers.size===0)pz.classList.remove('grabbing');}
  pz.addEventListener('pointerup',release);pz.addEventListener('pointercancel',release);
  pz.addEventListener('wheel',e=>{e.preventDefault();zoomAt(e.clientX,e.clientY,e.deltaY<0?1.15:1/1.15);},{passive:false});
  pz.addEventListener('click',e=>{if(e.target.closest('.pin'))e.stopPropagation();},true);
  wrap.querySelector('.pzb.in').addEventListener('click',()=>{const r=pz.getBoundingClientRect();zoomAt(r.left+r.width/2,r.top+r.height/2,1.35);});
  wrap.querySelector('.pzb.out').addEventListener('click',()=>{const r=pz.getBoundingClientRect();zoomAt(r.left+r.width/2,r.top+r.height/2,1/1.35);});
  wrap.querySelector('.pzb.reset').addEventListener('click',fit);
  wrap.querySelectorAll('.pin').forEach(pin=>{
    pin.addEventListener('click',ev=>{
      ev.stopPropagation();
      wrap.querySelectorAll('.pin.sel').forEach(p=>p.classList.remove('sel'));
      pin.classList.add('sel');
      const card=document.getElementById('card-'+pin.dataset.id);
      if(card){card.scrollIntoView({behavior:'smooth',block:'start'});card.classList.remove('flash');void card.offsetWidth;card.classList.add('flash');}
    });
  });
  document.querySelectorAll('[data-goto="'+wrap.dataset.area+'"]').forEach(btn=>{
    btn.addEventListener('click',()=>{
      const pin=wrap.querySelector('.pin[data-id="'+btn.dataset.id+'"]');
      if(!pin)return;
      wrap.scrollIntoView({behavior:'smooth',block:'start'});
      const r=pz.getBoundingClientRect();
      const px=parseFloat(pin.style.left)/100*inner.offsetWidth;
      const py=parseFloat(pin.style.top)/100*inner.offsetHeight;
      scale=Math.max(scale,1.9);
      tx=r.width/2-px*scale;ty=r.height/2-py*scale;apply();
      wrap.querySelectorAll('.pin.sel').forEach(p=>p.classList.remove('sel'));
      pin.classList.add('sel');
    });
  });
  window.addEventListener('resize',()=>{apply();});
  fit();
});
</script>
<script>
document.querySelectorAll('.car').forEach(function(c){
  var trk=c.querySelector('.trk');if(!trk)return;
  var imgs=trk.querySelectorAll('img'),cn=c.querySelector('.cn');
  function upd(){if(!imgs.length)return;var i=Math.round(trk.scrollLeft/Math.max(1,trk.clientWidth));if(i<0)i=0;if(i>imgs.length-1)i=imgs.length-1;if(cn&&imgs.length>1)cn.innerHTML='<b>'+imgs[i].dataset.l+'</b> '+(i+1)+'/'+imgs.length;}
  function go(d){trk.scrollBy({left:d*Math.max(1,trk.clientWidth),behavior:'smooth'});}
  var pv=c.querySelector('.cb.pv'),nx=c.querySelector('.cb.nx');
  if(pv)pv.addEventListener('click',function(){go(-1);});
  if(nx)nx.addEventListener('click',function(){go(1);});
  var raf=0;trk.addEventListener('scroll',function(){if(raf)return;raf=requestAnimationFrame(function(){raf=0;upd();});},{passive:true});
  var dn=false,sx=0,sl=0,pid=null;
  trk.addEventListener('pointerdown',function(e){if(e.pointerType!=='mouse')return;dn=true;pid=e.pointerId;sx=e.clientX;sl=trk.scrollLeft;trk.classList.add('drag');});
  trk.addEventListener('pointermove',function(e){if(!dn||e.pointerId!==pid)return;trk.scrollLeft=sl-(e.clientX-sx);});
  function end(e){if(!dn)return;dn=false;trk.classList.remove('drag');}
  trk.addEventListener('pointerup',end);trk.addEventListener('pointercancel',end);
  upd();
});
</script>
"""

INTROS = {
 "shimo": "Tokyo's thrift capital. Eight shops within a few minutes of the station — vintage dens, recycle chains and tiny curated stores packed into the lanes on both sides of the tracks.",
 "koenji": "Vintage without the Shimokitazawa crowds. Eight shops around the station and its covered shopping streets, strong on American vintage and budget recycle racks.",
 "kichijoji": "A local favorite west of the center. Eight shops between the Sun Road arcade and Harmonica Yokocho, mixing big recycle chains with small vintage picks.",
 "nakano": "Broadway is a treasure building. Eight clothing shops in and around Nakano Broadway and the Sun Mall arcade — come for the hobby floors, stay for the vintage.",
 "harajuku": "The famous end of Tokyo vintage. Five shops around Harajuku and Shibuya — big-name vintage, brand resale and a huge recycle floor.",
 "akiba": "One specialist stop. PENNY TOKYO deals in American vintage a short walk from Akihabara Station — worth the detour between the arcades.",
 "ikebukuro": "West-side value. Three shops around Ikebukuro Station, including a big 2nd STREET inside P'PARCO.",
 "ueno": "Ameyoko bargains. Four shops in and around the Ameyoko market streets — workwear, outdoor vintage and recycle racks under the tracks.",
}

def load_translations():
    t = {}
    for path in sorted(glob.glob(os.path.join(HERE, "translations", "*.json"))):
        try:
            with open(path, encoding="utf-8") as f:
                t.update(json.load(f))
        except Exception as e:
            print("WARN: translations file skipped:", path, e, file=sys.stderr)
    t.update(UI_DICT)
    return t

def area_page(data, area, trans):
    slug = SLUGS[area["key"]]
    url = PAGE_URL + slug + "/"
    total = len(data["areas"])
    desc = (f"Thrift Map — {area['name']}: {len(area['shops'])} second-hand and vintage clothing shops "
            f"around {area['station']['name']} Station, Tokyo — hours, ratings and how far each is on foot. "
            f"One of {total} areas on the map.")
    title = f"Thrift Map — {area['name']} | Anime Sensei"
    kind_urls = {"Eat": "https://yukitchy.github.io/where-to-eat/"}
    others_kind = "".join(f'<li><a href="{kind_urls.get(k, PAGE_URL)}">{k}</a></li>' for k in
                          ["Eat", "Drink", "Thrift", "Shop", "Stay"])
    areas_lis = "".join(
        f'<li><a href="../{SLUGS[a["key"]]}/">{escape(a["name"].upper())}</a></li>'
        for a in data["areas"] if a["key"] != area["key"])
    name = area["name"]
    n = len(name)
    emscale = 1.25 if n <= 10 else (1.02 if n <= 14 else 0.85)
    # Cap leaves room on the band's line for the hint bubble to its right
    # (band + 10px gap + hint <= viewport - wrap padding, checked at 320px).
    vwcap = 47.6 / (0.64 * n + 0.3)
    emstyle = f"font-size:min({emscale}em,{vwcap:.1f}vw)"
    h1 = (
        '<h1><span>Where to</span> '
        '<details class="kindsw"><summary>Thrift</summary><ul>'
        + others_kind +
        '</ul></details> '
        '<span>in</span> '
        f'<details class="areasw"><summary><em style="{emstyle}">{escape(name.upper())}</em>{CHEV_SVG}'
        '<span class="hint"><span>Tap to</span><span>change area</span></span></summary>'
        f'<ul>{areas_lis}</ul></details></h1>')
    maphtml, cards, _proj = build_area(area, "../")
    hero = build_hero(area, "../")
    mood = build_mood(area)
    _sts = area.get("stations") or [area["station"]]
    stations_rows = "".join(
        f'<div class="r"><b>STATION</b><span>{escape(s["name"])}'
        + (f' — <span>{escape(area["lines"])}</span>' if i == 0 else "")
        + '</span></div>'
        for i, s in enumerate(_sts))
    station = (f'<div class="station"><div class="hd2">GETTING THERE</div><div class="bd">'
               f'<div class="r"><b>THE AREA</b><span>{escape(area["access"])}</span></div>'
               f'{stations_rows}'
               f'<div class="r"><b>ON FOOT</b><span>{escape(area["walk"])}</span></div>'
               f'</div></div>')
    areas_links = " · ".join(
        f'<a href="../{SLUGS[a["key"]]}/">{escape(a["name"])}</a>' for a in data["areas"])
    shops_json = json.dumps({s["id"]: {"hours": s["hours"]} for s in area["shops"]},
                            ensure_ascii=False, separators=(",", ":"))
    status_js = STATUS_JS.replace("__SHOPS_JSON__", shops_json)
    lang_js = LANG_JS.replace("__T_DICT__", json.dumps(trans, ensure_ascii=False, separators=(",", ":")))
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{escape(title)}</title>
<meta name="description" content="{escape(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Thrift Map — Anime Sensei">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{PAGE_URL}img/og-shimokitazawa-v2.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" sizes="512x512" href="../img/favicon-v2-512.png">
<link rel="icon" type="image/png" sizes="32x32" href="../img/favicon-v2-32.png">
<link rel="icon" type="image/png" sizes="16x16" href="../img/favicon-v2-16.png">
<link rel="apple-touch-icon" href="../img/apple-touch-icon-v2.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@700;900&family=Noto+Sans+JP:wght@400;700;900&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
<header class="top"><img class="logo" src="../img/logo-1line-v3.png" alt="Thrift Map">{LANGSW_HTML}</header>
{h1}
<p class="intro">{INTROS[area['key']]}</p>
{station}
{hero}
{mood}
<div class="maphd"><h2>{escape(name)}</h2><label class="sw"><input type="checkbox" id="opensw"><span class="trk"></span>Open now</label></div>
<p class="nowline" id="nowline" style="font-size:13.5px;font-weight:700;color:var(--mut);margin:-2px 0 8px"></p>
{maphtml}
<section class="cards">{cards}</section>
<section class="know">{KNOW_HTML}</section>
<footer><p class="areas">Areas: {areas_links}</p>
<p>{escape(data['checked'])}<br>Map sketches are schematic. Coordinates: GSI address search. Always confirm the exact spot with the map pin button on each card.<br>Thrift Map — a guest guide by Anime Sensei</p></footer>
</div>
{status_js}
{PINZOOM_JS}
{lang_js}
</body>
</html>
"""

def root_page(data):
    total_shops = sum(len(a["shops"]) for a in data["areas"])
    desc = (f"Thrift Map — Tokyo second-hand and vintage clothing, area by area: "
            f"{total_shops} shops across {len(data['areas'])} Tokyo neighborhoods, "
            f"with hours, ratings and walking times from the station.")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta http-equiv="refresh" content="0; url={DEFAULT_SLUG}/">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Thrift Map — Tokyo vintage &amp; second-hand clothing | Anime Sensei</title>
<meta name="description" content="{escape(desc)}">
<link rel="canonical" href="{PAGE_URL}">
<meta name="robots" content="noindex">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Thrift Map — Anime Sensei">
<meta property="og:title" content="Thrift Map — Tokyo vintage &amp; second-hand clothing | Anime Sensei">
<meta property="og:description" content="{escape(desc)}">
<meta property="og:url" content="{PAGE_URL}">
<meta property="og:image" content="{PAGE_URL}img/og-shimokitazawa-v2.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" sizes="512x512" href="img/favicon-v2-512.png">
<link rel="icon" type="image/png" sizes="32x32" href="img/favicon-v2-32.png">
<link rel="icon" type="image/png" sizes="16x16" href="img/favicon-v2-16.png">
<link rel="apple-touch-icon" href="img/apple-touch-icon-v2.png">
</head>
<body><p>Thrift Map — <a href="{DEFAULT_SLUG}/">enter the map</a></p></body>
</html>
"""

def main():
    with open(os.path.join(HERE, "data.json"), encoding="utf-8") as f:
        data = json.load(f)
    trans = load_translations()
    all_shops = [sh for a in data["areas"] for sh in a["shops"]]
    for sh in all_shops:
        if not sh.get("fb"):
            got = geocode(sh["addr"])
            if not got:
                print("GEOCODE FAILED:", sh["id"], sh["addr"], file=sys.stderr)
                sys.exit(1)
            sh["fb"] = [got[0], got[1]]
        sh["lat"], sh["lng"] = sh["fb"]
    for a in data["areas"]:
        for sh in a["shops"]:
            cand = a.get("stations") or [a["station"]]
            best = min(cand, key=lambda s: haversine_m((sh["lat"], sh["lng"]), (s["lat"], s["lng"])))
            d = haversine_m((sh["lat"], sh["lng"]), (best["lat"], best["lng"]))
            sh["sta"] = best["name"]
            sh["walk"] = max(1, round(d / 80.0))
    outdir = os.path.join(HERE, "out")
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "index.html"), "w", encoding="utf-8") as f:
        f.write(root_page(data))
    for a in data["areas"]:
        d = os.path.join(outdir, SLUGS[a["key"]])
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
            f.write(area_page(data, a, trans))
        print("built", SLUGS[a["key"]], len(a["shops"]), "shops")
    print("total shops:", len(all_shops), "areas:", len(data["areas"]))

if __name__ == "__main__":
    main()
