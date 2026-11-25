#!/usr/bin/env python3
# つあろぐ読み物ページ PC版「下部タブバーの置き換え」5案モック生成。
# 本番 yulia.html（生成済みサイト側）を土台に、パス書き換え＋案ごとの
# ナビHTML/CSS/JSを注入する。本番ファイルには一切触らない。
# 全案共通：PC幅（min-width:1024px）で .tabbar を消し、.pcnav を出す。
# .pcnav は基本 display:none なのでスマホ表示は本番のまま変わらない。
import pathlib
import re

SRC = pathlib.Path.home() / "workspace/tsuarogu-guestbook-build/site/read/yulia.html"
OUT = pathlib.Path.home() / "workspace/tsuarogu-read-pc-nav"

html = SRC.read_text(encoding="utf-8")
html = html.replace("../favicon-bubble.png", "favicon-bubble.png")
html = html.replace("../img/ep-yulia.jpg", "img/ep-yulia.jpg")
html = html.replace("../mark-bubble.png", "mark-bubble.png")
html = html.replace('href="../"', 'href="../tsuarogu-guestbook/"')

# 案5のドロップダウン用に、本番の目次リスト（全20場面のアンカー）を抜き出す
m = re.search(r'<div class="toclist" id="toclist" hidden>(.*?)</div></div>', html, re.S)
TOC_ANCHORS = m.group(1) if m else ""

IC = {
    "toc": '<svg viewBox="0 0 24 24"><path d="M8 6h12M8 12h12M8 18h12M4 6h.01M4 12h.01M4 18h.01"/></svg>',
    "list": '<svg viewBox="0 0 24 24"><rect x="4" y="4" width="6" height="6"/><rect x="14" y="4" width="6" height="6"/><rect x="4" y="14" width="6" height="6"/><rect x="14" y="14" width="6" height="6"/></svg>',
    "photo": '<svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="9" cy="11" r="1.5"/><path d="M21 16l-5-5-8 8"/></svg>',
    "doc": '<svg viewBox="0 0 24 24"><path d="M6 3h9l4 4v14H6z"/><path d="M14 3v5h5"/></svg>',
    "set": '<svg viewBox="0 0 24 24"><path d="M4 7h10M18 7h2M4 17h2M10 17h10"/><circle cx="16" cy="7" r="2"/><circle cx="8" cy="17" r="2"/></svg>',
    "chev": '<svg viewBox="0 0 24 24"><path d="M5 9l7 7 7-7"/></svg>',
}

ITEMS = (
    f'<a class="nv on" href="#toc">{IC["toc"]}<span>目次</span></a>'
    f'<a class="nv" href="../tsuarogu-guestbook/">{IC["list"]}<span>一覧</span></a>'
    f'<a class="nv" href="#topphoto">{IC["photo"]}<span>写真</span></a>'
    f'<span class="nv">{IC["doc"]}<span>原文</span></span>'
    f'<span class="nv">{IC["set"]}<span>設定</span></span>'
)

BRAND = (
    '<a class="nvbrand" href="#topphoto"><img src="mark-bubble.png" alt="">'
    '<span class="nvbt"><i>TOUR LOG</i><b>つあろぐ</b></span></a>'
)

BASE_CSS = """
.pcnav,.tocdrop{display:none}
.pcnav svg{stroke:currentColor;fill:none;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
"""

# 上部固定ヘッダー（案1・案5共通の骨格）
HEADER_CSS = """
 .tabbar{display:none}
 .headrow{display:none}
 .wrap{margin-top:58px}
 .vrail{top:74px;max-height:calc(100vh - 88px)}
 .pcnav{display:block;position:fixed;top:0;left:0;right:0;z-index:40;background:var(--bg);border-bottom:3px solid var(--fg)}
 .pcnav .nin{max-width:1280px;margin:0 auto;padding:0 40px;height:58px;display:flex;align-items:center}
 .nvbrand{display:flex;align-items:center;gap:10px;text-decoration:none;color:var(--fg)}
 .nvbrand img{width:34px;height:34px;display:block}
 .nvbt{display:flex;flex-direction:column;line-height:1.15}
 .nvbt i{font-family:var(--lat);font-style:normal;font-weight:900;letter-spacing:.26em;font-size:10px;color:var(--acc)}
 .nvbt b{font-size:17px;font-weight:900}
 .pcnav .nvs{margin-left:auto;display:flex;align-items:center;gap:28px}
 .pcnav .nv{display:flex;align-items:center;gap:7px;padding:6px 0;font-size:13.5px;font-weight:700;color:var(--mute);text-decoration:none;background:none;border:0;font-family:inherit;cursor:pointer}
 .pcnav .nv svg{width:18px;height:18px}
 .pcnav .nv.on{color:var(--acc);box-shadow:inset 0 -3px 0 var(--acc)}
"""

VARIANTS = {}

# 案1 上部固定ヘッダーバー型
VARIANTS["v1"] = (
    "@media (min-width:1024px){" + HEADER_CSS + "}",
    f'<header class="pcnav"><div class="nin">{BRAND}<nav class="nvs">{ITEMS}</nav></div></header>',
    "body",
    "",
)

# 案2 左サイドレール型
VARIANTS["v2"] = (
    """
@media (min-width:1024px){
 .tabbar{display:none}
 .rd{padding-left:78px}
 .pcnav{display:flex;position:fixed;left:0;top:0;bottom:0;width:78px;z-index:40;background:#fff;border-right:3px solid var(--fg);flex-direction:column;padding:16px 0}
 .nvbrand{display:flex;justify-content:center;text-decoration:none;margin-bottom:12px}
 .nvbrand img{width:36px;height:36px;display:block}
 .nvbt{display:none}
 .pcnav .nvs{display:flex;flex-direction:column}
 .pcnav .nv{display:flex;flex-direction:column;align-items:center;gap:4px;padding:12px 0;font-size:10px;font-weight:700;color:var(--mute);text-decoration:none}
 .pcnav .nv svg{width:22px;height:22px}
 .pcnav .nv.on{color:var(--acc);background:#fff4ec;box-shadow:inset 3px 0 0 var(--acc)}
}
""",
    f'<nav class="pcnav">{BRAND}<div class="nvs">{ITEMS}</div></nav>',
    "body",
    "",
)

# 案3 右サイドレール型
VARIANTS["v3"] = (
    """
@media (min-width:1024px){
 .tabbar{display:none}
 .rd{padding-right:78px}
 .pcnav{display:flex;position:fixed;right:0;top:0;bottom:0;width:78px;z-index:40;background:#fff;border-left:3px solid var(--fg);flex-direction:column;padding:16px 0}
 .nvbrand{display:flex;justify-content:center;text-decoration:none;margin-bottom:12px}
 .nvbrand img{width:36px;height:36px;display:block}
 .nvbt{display:none}
 .pcnav .nvs{display:flex;flex-direction:column}
 .pcnav .nv{display:flex;flex-direction:column;align-items:center;gap:4px;padding:12px 0;font-size:10px;font-weight:700;color:var(--mute);text-decoration:none}
 .pcnav .nv svg{width:22px;height:22px}
 .pcnav .nv.on{color:var(--acc);background:#fff4ec;box-shadow:inset -3px 0 0 var(--acc)}
}
""",
    f'<nav class="pcnav">{BRAND}<div class="nvs">{ITEMS}</div></nav>',
    "body",
    "",
)

# 案4 タイトルカード統合型（ヒーロー直下にタブ列、固定バーなし）
VARIANTS["v4"] = (
    """
@media (min-width:1024px){
 .tabbar{display:none}
 .pcnav{display:block;grid-column:1/-1;margin-top:26px;background:#fff;border:3px solid var(--fg)}
 .pcnav .nvs{display:flex}
 .pcnav .nv{flex:1;display:flex;align-items:center;justify-content:center;gap:8px;padding:13px 0;font-size:14px;font-weight:900;color:var(--mute);text-decoration:none;border-left:2px solid var(--line)}
 .pcnav .nv:first-child{border-left:0}
 .pcnav .nv svg{width:19px;height:19px}
 .pcnav .nv.on{color:var(--fg);box-shadow:inset 0 -4px 0 var(--acc)}
}
""",
    f'<nav class="pcnav"><div class="nvs">{ITEMS}</div></nav>',
    "hero",
    "",
)

# 案5 ヘッダー＋目次ドロップダウン型
ITEMS5 = (
    f'<button type="button" class="nv" id="nvtocbtn" aria-expanded="false" aria-controls="tocdrop">{IC["toc"]}<span>目次</span>{IC["chev"]}</button>'
    f'<a class="nv" href="../tsuarogu-guestbook/">{IC["list"]}<span>一覧</span></a>'
    f'<a class="nv" href="#topphoto">{IC["photo"]}<span>写真</span></a>'
    f'<span class="nv">{IC["doc"]}<span>原文</span></span>'
    f'<span class="nv">{IC["set"]}<span>設定</span></span>'
)
DROP5 = (
    '<div class="tocdrop" id="tocdrop" hidden><div class="tdin"><div class="tdpanel">'
    '<div class="tdhd"><b>目次</b><span>全20場面</span></div>'
    f'<div class="tdgrid">{TOC_ANCHORS}</div>'
    "</div></div></div>"
)
VARIANTS["v5"] = (
    "@media (min-width:1024px){" + HEADER_CSS + """
 .pcnav .nv .chev2{transition:transform .18s}
 .tocdrop{display:block;position:fixed;top:58px;left:0;right:0;z-index:39}
 .tocdrop[hidden]{display:none}
 .tocdrop .tdin{max-width:1280px;margin:0 auto;padding:0 40px}
 .tocdrop .tdpanel{background:#fff;border:3px solid var(--fg);border-top:0;box-shadow:8px 8px 0 rgba(21,21,21,.85);padding:16px 22px 18px}
 .tdhd{display:flex;align-items:baseline;gap:12px;border-bottom:3px solid var(--fg);padding-bottom:8px;margin-bottom:8px}
 .tdhd b{font-size:16px;font-weight:900}
 .tdhd span{font-family:var(--lat);font-size:11.5px;color:var(--mute);letter-spacing:.08em}
 .tdgrid{display:grid;grid-template-columns:1fr 1fr;column-gap:36px}
 .tdgrid .r{display:flex;align-items:center;gap:10px;padding:6px 2px;text-decoration:none;color:var(--fg);border-bottom:1px solid var(--line)}
 .tdgrid .r .t{font-family:var(--lat);font-size:11px;color:var(--mute);white-space:nowrap;display:flex;gap:4px;align-items:baseline}
 .tdgrid .r .t b{font-size:12.5px;color:var(--fg)}
 .tdgrid .r .t i{font-style:normal}
 .tdgrid .r .t small{font-size:10px}
 .tdgrid .r .x{font-size:12.5px;font-weight:700;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
 .tdgrid .r .bd{margin-left:auto;flex:none;font-size:10px;font-weight:900;color:#c22f1d;border:1.5px solid #c22f1d;padding:1px 6px}
}
""",
    f'<header class="pcnav"><div class="nin">{BRAND}<nav class="nvs">{ITEMS5}</nav></div></header>' + DROP5,
    "body",
    """
<script>
(function(){
  var btn=document.getElementById('nvtocbtn'), drop=document.getElementById('tocdrop');
  if(!btn||!drop) return;
  function set(open){ drop.hidden=!open; btn.setAttribute('aria-expanded',String(open)); btn.classList.toggle('on',open); }
  btn.addEventListener('click',function(e){ e.stopPropagation(); set(drop.hidden); });
  document.addEventListener('click',function(e){ if(!drop.hidden && !drop.contains(e.target)) set(false); });
  drop.addEventListener('click',function(e){ if(e.target.closest('a')) set(false); });
})();
</script>
""",
)

HERO_TAG = '<div class="hero" id="topphoto"><img src="img/ep-yulia.jpg" alt=""></div>'

for name, (css, nav_html, where, js) in VARIANTS.items():
    doc = html
    if where == "hero":
        assert HERO_TAG in doc, "hero tag not found"
        doc = doc.replace(HERO_TAG, HERO_TAG + nav_html, 1)
    else:
        doc = doc.replace('<body class="rd">', '<body class="rd">' + nav_html, 1)
    style = "<style>" + BASE_CSS + css + "</style>"
    doc = doc.replace("</head>", style + "</head>", 1)
    if js:
        doc = doc.replace("</body>", js + "</body>", 1)
    (OUT / f"{name}.html").write_text(doc, encoding="utf-8")
    print("wrote", name)
