#!/usr/bin/env python3
# Thrift Map builder — eatmap-style multi-area guest page.
# Reads data.json, geocodes addresses via GSI, emits index.html.
import json, math, os, random, sys, urllib.parse, urllib.request
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
ACCENT = "#81660D"
PAGE_URL = "https://yukitchy.github.io/booking-trends-board/thrift-map/"

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

def fmt12(hhmm):
    h, m = map(int, hhmm.split(":"))
    ap = "AM" if h < 12 else "PM"
    h12 = h % 12 or 12
    return f"{h12}:{m:02d} {ap}" if m else f"{h12} {ap}"

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
    # buildings inside blocks
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
    # roads on top of block edges
    for x in xs[1:-1]:
        wdt = rnd.uniform(6, 12)
        out.append(f'<line x1="{x:.0f}" y1="0" x2="{x:.0f}" y2="{H}" stroke="#FFFFFF" stroke-width="{wdt:.0f}"/>')
    for y in ys[1:-1]:
        wdt = rnd.uniform(6, 12)
        out.append(f'<line x1="0" y1="{y:.0f}" x2="{W}" y2="{y:.0f}" stroke="#FFFFFF" stroke-width="{wdt:.0f}"/>')
    # two diagonal avenues
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
    # label on the segment whose midpoint is closest to the frame center
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
    # compass + scale
    svg.append(f'<g transform="translate({proj.W-34} 36)"><circle r="15" fill="#FFFFFF" opacity="0.85"/><path d="M0 -10 L4.5 3 L0 0 L-4.5 3 Z" fill="#141414"/><text y="-19" text-anchor="middle" font-size="11" font-weight="800" fill="#141414">N</text></g>')
    sb = 200 * proj.s
    svg.append(f'<g transform="translate(18 {proj.H-20})"><rect x="0" y="-4" width="{sb:.0f}" height="4" fill="#141414"/><text x="0" y="-9" font-size="10.5" font-weight="700" fill="#141414">200 m</text></g>')
    svg.append("</svg>")
    pins = []
    for i, sh in enumerate(area["shops"], 1):
        px, py = proj.pct(sh["lat"], sh["lng"])
        pins.append(f'<button type="button" class="pin" data-area="{area["key"]}" data-n="{i}" data-id="{sh["id"]}" '
                    f'style="left:{px:.2f}%;top:{py:.2f}%" aria-label="{escape(sh["en"])}">'
                    f'<span class="pinbox">{i}</span><span class="pintail"></span></button>')
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
        meta = [f'<div class="mrow"><span class="mic">🚶</span><span>{sh["walk"]} min from {escape(sh["sta"])} Sta.</span></div>',
                f'<div class="mrow"><span class="mic">🕐</span><span>{escape(sh["txt"])}</span><span class="openbadge" data-open="{sh["id"]}"></span></div>']
        if sh.get("gr"):
            meta.append(f'<div class="mrow"><span class="mic">★</span><span>{escape(sh["gr"])}</span></div>')
        if sh.get("closed"):
            meta.append(f'<div class="mrow"><span class="mic">📅</span><span>{escape(sh["closed"])}</span></div>')
        meta.append(f'<div class="mrow addr"><span class="mic">📍</span><span>{escape(sh["addr"])}</span></div>')
        src = f'<a class="srclink" href="{escape(sh["src"])}" target="_blank" rel="noopener">Official site ↗</a>' if sh.get("src") else ""
        cards.append(
            f'<article class="card" id="card-{sh["id"]}">'
            f'<div class="cardtop"><button type="button" class="numbadge" data-goto="{area["key"]}" data-n="{i}" data-id="{sh["id"]}">{i}</button>'
            f'<span class="genre">{escape(sh["genre"])}</span>'
            f'<a class="gmapbtn" href="{gmap}" target="_blank" rel="noopener" aria-label="Open {escape(sh["en"])} in Google Maps">'
            '<svg viewBox="0 0 24 24" width="17" height="17" aria-hidden="true"><path fill="currentColor" d="M12 2a7 7 0 0 0-7 7c0 5.2 7 13 7 13s7-7.8 7-13a7 7 0 0 0-7-7zm0 9.5A2.5 2.5 0 1 1 12 6a2.5 2.5 0 0 1 0 5.5z"/></svg></a></div>'
            f'<h3>{escape(sh["en"])}</h3><div class="jp">{escape(sh["jp"])}</div>'
            f'<p class="note">{escape(sh["note"])}</p>'
            f'<div class="meta">{"".join(meta)}</div>{src}</article>')
    return maphtml, "".join(cards), proj

CSS = """
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:#F5F3EE;color:#1C1B17;font-family:-apple-system,BlinkMacSystemFont,"Helvetica Neue","Hiragino Sans","Noto Sans JP",sans-serif;-webkit-font-smoothing:antialiased}
.wrap{max-width:1080px;margin:0 auto;padding:0 14px 44px}
header.hero{text-align:center;padding:30px 6px 4px}
header.hero img.logo{width:min(430px,84vw);height:auto;display:block;margin:0 auto}
.tagline{margin:10px 0 0;font-size:16px;font-weight:700;color:#3B382E}
.subline{margin:5px 0 0;font-size:12.5px;color:#8A8578}
.areanav{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin:18px 0 2px}
.areanav a{display:inline-block;padding:7px 13px;border-radius:999px;background:#FFFFFF;border:1px solid #DDD6C2;color:#5C5322;font-size:12.5px;font-weight:700;text-decoration:none}
.areanav a b{color:#81660D}
.howto{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:16px 0 4px}
.howto div{background:#FFFFFF;border:1px solid #E7E1CF;border-radius:12px;padding:10px 12px;font-size:12.5px;line-height:1.5;color:#3B382E}
.howto b{display:block;font-size:12px;letter-spacing:.06em;color:#81660D;margin-bottom:2px}
section.area{margin-top:36px;scroll-margin-top:12px}
.areahead{display:flex;align-items:baseline;gap:10px;border-bottom:3px solid #81660D;padding-bottom:6px}
.areahead h2{margin:0;font-size:25px;letter-spacing:.01em}
.areahead .ajp{color:#8A8578;font-size:14px;font-weight:700}
.areahead .cnt{margin-left:auto;font-size:12px;color:#8A8578;font-weight:700}
.access{background:#FFFFFF;border:1px solid #E7E1CF;border-radius:14px;padding:13px 15px;margin-top:13px;font-size:13.5px;line-height:1.6;color:#33322E}
.access .lab{display:inline-block;font-size:10.5px;font-weight:800;letter-spacing:.08em;color:#FFFFFF;background:#81660D;border-radius:5px;padding:2px 7px;margin-right:8px;vertical-align:1px}
.access p{margin:0 0 8px}.access p:last-child{margin-bottom:0}
.mapwrap{position:relative;margin-top:13px;border-radius:18px;overflow:hidden;border:1px solid #DDD9CF;background:#E9E8E4}
.pz{overflow:hidden;touch-action:none;cursor:grab}
.pz:active{cursor:grabbing}
.pz-inner{position:relative;transform-origin:0 0;will-change:transform}
svg.mapsvg{display:block;width:100%;height:auto}
.pins{position:absolute;inset:0}
.pin{position:absolute;transform:translate(-50%,-100%) scale(var(--pk,1));background:none;border:0;padding:0;cursor:pointer;display:flex;flex-direction:column;align-items:center;z-index:3}
.pinbox{display:flex;align-items:center;justify-content:center;width:30px;height:30px;border-radius:9px;background:#81660D;color:#FFFFFF;font-size:15px;font-weight:800;box-shadow:0 2px 6px rgba(20,20,20,.35);border:2px solid #FFFFFF}
.pintail{width:0;height:0;border-left:6px solid transparent;border-right:6px solid transparent;border-top:8px solid #81660D;margin-top:-1px}
.pin.hl .pinbox{background:#141414;animation:pinpulse .5s ease-in-out 3}
@keyframes pinpulse{50%{transform:scale(1.25)}}
.pz-btns{position:absolute;right:10px;bottom:10px;display:flex;flex-direction:column;gap:6px;z-index:5}
.pzb{width:34px;height:34px;border-radius:50%;border:1px solid #DDD9CF;background:#FFFFFF;font-size:17px;font-weight:700;color:#33322E;box-shadow:0 1px 4px rgba(20,20,20,.18);cursor:pointer;line-height:1}
.maphint{position:absolute;left:10px;bottom:10px;z-index:5;background:rgba(255,255,255,.88);border-radius:999px;padding:4px 10px;font-size:10.5px;font-weight:700;color:#55524C}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:13px;margin-top:14px}
.card{background:#FFFFFF;border:1px solid #E7E1CF;border-radius:14px;padding:13px 15px 14px;box-shadow:0 1px 4px rgba(20,20,20,.06)}
.card.flash{animation:cardflash 1.6s ease}
@keyframes cardflash{0%,60%{box-shadow:0 0 0 3px #81660D}100%{box-shadow:0 1px 4px rgba(20,20,20,.06)}}
.cardtop{display:flex;align-items:center;gap:8px}
.numbadge{width:26px;height:26px;flex:none;border:0;border-radius:7px;background:#81660D;color:#FFFFFF;font-size:14px;font-weight:800;cursor:pointer}
.genre{margin-right:auto;font-size:10px;font-weight:800;letter-spacing:.07em;color:#81660D;border:1.4px solid #81660D;border-radius:999px;padding:3px 8px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.gmapbtn{width:31px;height:31px;flex:none;border-radius:50%;background:#141414;color:#FFFFFF;display:flex;align-items:center;justify-content:center;text-decoration:none}
.card h3{margin:9px 0 0;font-size:16.5px;line-height:1.3}
.card .jp{color:#8A8578;font-size:12px;margin-top:1px}
.card .note{font-size:13.5px;line-height:1.6;color:#33322E;margin:8px 0 0}
.meta{margin-top:9px;font-size:12.5px;color:#3B382E}
.mrow{display:flex;gap:7px;margin-top:4px;align-items:baseline}
.mic{width:16px;flex:none;text-align:center}
.mrow.addr{color:#8A8578;font-size:11.5px}
.openbadge{margin-left:2px;font-size:10.5px;font-weight:800;padding:2px 8px;border-radius:999px;white-space:nowrap}
.openbadge.on{background:#E3F1E3;color:#1E7D32}
.openbadge.off{background:#EFEDE8;color:#8A8578}
.openbadge.soon{background:#FDF3D7;color:#8A6D00}
.srclink{display:inline-block;margin-top:9px;font-size:12.5px;font-weight:700;color:#81660D;text-decoration:none}
footer{margin-top:44px;text-align:center;color:#8A8578;font-size:12px;line-height:1.8}
footer .brand{color:#5C5322;font-weight:800}
@media (max-width:560px){.howto{grid-template-columns:1fr}.cards{grid-template-columns:1fr}.areahead h2{font-size:22px}}
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
    if(cur>=o&&cur<c){return c-cur<=45?['soon','Closes '+t12(c%1440)]:['on','Open now · until '+t12(c%1440)]}
    if(cur<o)return ['off','Opens '+t12(o)+' today'];}
  for(let k=1;k<=7;k++){const d2=(day+k)%7;const e2=h.find(e=>e.d.includes(d2));
    if(e2){const o2=+e2.o.split(':')[0]*60+(+e2.o.split(':')[1]);
      return ['off',(k===1?'Opens '+t12(o2)+' tomorrow':'Opens '+t12(o2))];}}
  return null;}
document.querySelectorAll('[data-open]').forEach(el=>{
  const rec=HOURS[el.dataset.open];const st=rec&&statusFor(rec.h);
  if(!st){el.remove();return}
  el.className='openbadge '+st[0];el.textContent=st[1];});
function focusPin(wrap,area,n){
  const pin=wrap.querySelector('.pin[data-n="'+n+'"]');if(!pin)return;
  const pz=wrap.querySelector('.pz'),inner=wrap.querySelector('.pz-inner');
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
  inner.style.setProperty('--pk',Math.max(.5,1/st.k));}
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
      card.classList.remove('flash');void card.offsetWidth;card.classList.add('flash');}});});
document.querySelectorAll('.numbadge').forEach(b=>{
  b.addEventListener('click',()=>{
    const wrap=document.querySelector('.mapwrap[data-area="'+b.dataset.goto+'"]');
    if(wrap){wrap.scrollIntoView({behavior:'smooth',block:'center'});
      setTimeout(()=>focusPin(wrap,b.dataset.goto,b.dataset.n),450);}});});
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
            f'<div class="areahead"><h2>{escape(area["name"])}</h2><span class="ajp">{escape(area["jp"])}</span>'
            f'<span class="cnt">{len(area["shops"])} shops</span></div>'
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
<div class="wrap">
<header class="hero">
<img class="logo" src="img/logo.png" alt="THRIFT MAP">
<p class="tagline">{escape(data["tagline"])}</p>
<p class="subline">{total} shops · 6 areas · {counts}</p>
<nav class="areanav">{"".join(nav)}</nav>
<div class="howto">
<div><b>HOW TO USE</b>Tap a numbered pin on a map to jump to that shop's card. Tap the number on a card to find it back on the map.</div>
<div><b>OPEN NOW</b>The badge on each card is live — it reads the shop's hours and tells you if it is open right now.</div>
<div><b>GOOD TO KNOW</b>Many Tokyo thrift shops open at 11 AM or noon, and small ones close early. Hours were checked on Nov 24, 2026 — a quick look at the Google listing before a long trip is wise.</div>
</div>
</header>
{"".join(sections)}
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
    print(f"built {out}: {total} shops, {len(data['areas'])} areas")
    if fallbacks:
        print("fallback coords used:", ", ".join(fallbacks))

if __name__ == "__main__":
    main()
