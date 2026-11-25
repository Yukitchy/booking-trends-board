#!/usr/bin/env python3
# つあろぐ読み物ページ PC版カラム幅バランス 5案モック生成。
# 本番 yulia.html（生成済みサイト側）を土台に、パス書き換え＋案ごとの上書きCSS/JSを注入する。
# 本番ファイルには一切触らない。
import pathlib

SRC = pathlib.Path.home() / "workspace/tsuarogu-guestbook-build/site/read/yulia.html"
OUT = pathlib.Path.home() / "workspace/tsuarogu-read-pc-layout2"

html = SRC.read_text(encoding="utf-8")
html = html.replace("../favicon-bubble.png", "favicon-bubble.png")
html = html.replace("../img/ep-yulia.jpg", "img/ep-yulia.jpg")
html = html.replace("../mark-bubble.png", "mark-bubble.png")
html = html.replace('href="../"', 'href="index.html"')

# 目次を上部へ移して折りたたむ（案1・案5共通）
COLLAPSE_JS = """
<script>
if(window.matchMedia('(min-width:1024px)').matches){
  var rail=document.querySelector('.vrail'), main=document.querySelector('.vmain');
  if(rail&&main){ main.parentNode.insertBefore(rail, main); }
  var tl=document.getElementById('toclist'), tb=document.getElementById('toc'), th=document.getElementById('tochd');
  if(tl){ tl.hidden=true; tb.classList.remove('open'); if(th) th.setAttribute('aria-expanded','false'); }
}
</script>
"""

RAIL_TOP_CSS = """
 .wrap{grid-template-columns:minmax(0,1fr)}
 .vmain{grid-column:1}
 .vrail{grid-column:1;position:static;max-height:none;overflow:visible;margin-top:26px}
 .vrail .tocbox{border:3px solid var(--fg)}
"""

VARIANTS = {
    # 案1 本文2倍ワイド型：目次=折りたたみ（上部・既定は閉）、注記は細カラム230pxへ
    "v1": (
        """
@media (min-width:1024px){
""" + RAIL_TOP_CSS + """
 .rd .scene .pg:has(> .ef){grid-template-columns:minmax(0,1fr) 230px}
}
""",
        COLLAPSE_JS,
    ),
    # 案2 注記インライン型：目次=固定・細レール210px、注記は場面末尾に本文幅で横並び
    "v2": (
        """
@media (min-width:1024px){
 .wrap{grid-template-columns:minmax(0,1fr) 210px;column-gap:32px}
 .toclist{padding:0 10px 8px}
 .tocbox .r{padding:6px 2px;flex-wrap:wrap;row-gap:1px;column-gap:8px}
 .tocbox .x{flex:1 1 100%;order:3}
 .tocbox .bd{order:2;margin-left:auto}
 .tocbox .x{font-size:12px;line-height:1.5}
 .tocbox .t b{font-size:15px}
 .tocbox .t small{font-size:9.5px}
 .tocbox .bd{font-size:9.5px;padding:1px 6px}
 .rd .scene .pg:has(> .ef){display:block}
 .rd .scene .ef{flex-direction:row;flex-wrap:wrap;margin-top:16px}
 .rd .scene .ef>div{flex:1 1 250px}
}
""",
        """
<script>
// DOM では注記(.ef)が本文(.col)より前にあるため、インライン配置では末尾へ移す
if(window.matchMedia('(min-width:1024px)').matches){
  document.querySelectorAll('.scene .pg').forEach(function(pg){
    var ef=pg.querySelector(':scope > .ef'), col=pg.querySelector(':scope > .col');
    if(ef&&col){ pg.appendChild(ef); }
  });
}
</script>
""",
    ),
    # 案3 目次コンパクト型：目次=固定190px（時刻＋短い見出しのみ）、本文:注記=7:3
    "v3": (
        """
@media (min-width:1024px){
 .wrap{grid-template-columns:minmax(0,1fr) 190px;column-gap:32px}
 .toclist{padding:0 10px 8px}
 .tocbox .r{padding:5px 2px;flex-wrap:wrap;row-gap:1px;column-gap:8px}
 .tocbox .x{flex:1 1 100%;order:3}
 .tocbox .t small{display:none}
 .tocbox .bd{display:none}
 .tocbox .t i{font-size:9px}
 .tocbox .t b{font-size:13.5px}
 .tocbox .x{font-size:11.5px;line-height:1.45}
 .rd .scene .pg:has(> .ef){grid-template-columns:minmax(0,7fr) minmax(0,3fr)}
}
""",
        "",
    ),
    # 案4 注記右端分離型：目次=上部チップ（常時表示）、注記は右端230pxに罫で分離、画面幅も少し広げる
    "v4": (
        """
@media (min-width:1024px){
 .wrap{grid-template-columns:minmax(0,1fr);max-width:1344px}
 .vrail{display:none}
 .tochips{grid-column:1/-1;display:flex;gap:8px;overflow-x:auto;padding:16px 2px 4px;scrollbar-width:thin}
 .tchip{flex:none;display:flex;align-items:baseline;gap:8px;border:2px solid var(--fg);background:#fff;color:var(--fg);text-decoration:none;padding:7px 12px;max-width:250px}
 .tchip b{font-family:var(--lat);font-weight:900;color:var(--acc);font-size:12.5px;white-space:nowrap}
 .tchip span{font-size:12px;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
 .rd .scene .pg:has(> .ef){grid-template-columns:minmax(0,1fr) 230px}
 .rd .scene .ef{border-left:1px solid var(--line);padding-left:20px}
}
""",
        """
<script>
if(window.matchMedia('(min-width:1024px)').matches){
  var hero=document.querySelector('.hero');
  var links=document.querySelectorAll('.tocbox .r');
  var bar=document.createElement('div'); bar.className='tochips';
  links.forEach(function(a){
    var t=a.querySelector('.t b'), ap=a.querySelector('.t i'), x=a.querySelector('.x');
    var c=document.createElement('a'); c.className='tchip'; c.href=a.getAttribute('href');
    c.innerHTML='<b>'+(ap?ap.textContent+' ':'')+(t?t.textContent:'')+'</b><span>'+(x?x.textContent:'')+'</span>';
    bar.appendChild(c);
  });
  if(hero){ hero.after(bar); }
}
</script>
""",
    ),
    # 案5 目次上部バー型：目次=折りたたみ（上部バー・開くと2カラム一覧）、注記は280px
    "v5": (
        """
@media (min-width:1024px){
""" + RAIL_TOP_CSS + """
 .vrail .toclist:not([hidden]){display:grid;grid-template-columns:1fr 1fr;column-gap:28px}
 .rd .scene .pg:has(> .ef){grid-template-columns:minmax(0,1fr) 280px}
}
""",
        COLLAPSE_JS,
    ),
}

for name, (css, js) in VARIANTS.items():
    out = html.replace("</head>", "<style>" + css + "</style></head>", 1)
    if js:
        out = out.replace("</body>", js + "</body>", 1)
    (OUT / f"{name}.html").write_text(out, encoding="utf-8")
    print("wrote", name)
