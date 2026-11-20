#!/usr/bin/env python3
"""秋葉原ツアーLP リブランディング t1〜t5（P5のUI文法）。
本文 = 本番ビルド済み dist/akihabara-tour/index.html の <body> をそのまま（読むだけ）。
変えるのは CSS・ヘッダーロゴ・装飾（aria-hidden）・ナビゲーターだけ。計測タグは抜く。"""
import math, re, pathlib

OUT = pathlib.Path(__file__).resolve().parent.parent
SRC = pathlib.Path.home().joinpath('workspace/lesson-booking-plan/site/dist/akihabara-tour/index.html').read_text()
BASE = 'https://yukitchy.github.io/booking-trends-board/akiba-tour-rebrand/'
LIVE = 'https://www.animesenseijp.com/'


def star(n, inner):
    pts = []
    for i in range(n * 2):
        r = 50 if i % 2 == 0 else 50 * inner
        a = math.pi * i / n - math.pi / 2
        pts.append(f'{50 + r * math.cos(a):.2f}% {50 + r * math.sin(a):.2f}%')
    return 'polygon(' + ','.join(pts) + ')'


# ---------------------------------------------------------------- 本文の下ごしらえ
s = SRC
# 計測タグを除去（GA4・Meta Pixel・外部リンクのクリック計測・滞在計測・流入元記録・Clarity）
DROP = ('googletagmanager', "gtag('config'", 'META_PIXEL_ID', "closest('a[href]')", "/^\\/tips\\/./", 'utm_source', 'clarity')
def drop_script(m):
    return '' if any(k in m.group(0) for k in DROP) else m.group(0)
s = re.sub(r'<script\b[^>]*>.*?</script>', drop_script, s, flags=re.S)
s = re.sub(r'<!-- Meta Pixel noscript -->.*?<!-- /Meta Pixel noscript -->', '', s, flags=re.S)
s = re.sub(r'<!--(?!\[).*?-->', '', s, flags=re.S)
assert 'googletagmanager' not in s and 'fbevents' not in s and 'clarity.ms' not in s
# 本番ドメインの相対パスを絶対URLに（GitHub Pages から同じ写真・同じリンク先を指す）
s = re.sub(r'\b(href|src|poster|data-src)="/(?!/)', rf'\1="{LIVE}', s)

i = s.find('<body')
head, body = s[:i], s[i:]
head = re.sub(r'<style[^>]*>(.*?)</style>', '', head, flags=re.S)
ASTRO = re.search(r'<style[^>]*>(.*?)</style>', SRC, flags=re.S).group(1)
head = re.sub(r'<link href="https://fonts.googleapis.com/css2[^>]*>', '', head)   # M PLUS Rounded（丸ゴシック）を外す
head = re.sub(r'<meta (property="og:[^"]*"|name="twitter:[^"]*")[^>]*>\n?', '', head)
head = re.sub(r'<link rel="canonical"[^>]*>\n?', '', head)

# ヘッダーロゴ → タイポロゴ画像（照合対象外）
body, n = re.subn(r'<a class="logo" href="#top">.*?</a>',
                  '<a class="logo" href="#top"><img src="anime-logo-red.webp" alt="Anime Sensei" width="600" height="300"></a>', body, flags=re.S)
assert n == 1
# 見出しの <br> は禁止ルール。空白1つに置き換え（見える文字は同じ）
body = body.replace('READY TO START<br>YOUR ADVENTURE?', 'READY TO START YOUR ADVENTURE?')
# 長文見出しは句の切れ目でしか折れないよう nowrap で束ねる（文字は変えない）
PH = lambda *xs: ' '.join(f'<span class="ph">{x}</span>' for x in xs)
for a, b in [('YOUR AKIHABARA ANIME TOUR PACKAGE: A DAY OUT WITH A FRIEND WHO GETS IT.',
              PH('YOUR AKIHABARA ANIME TOUR PACKAGE:', 'A DAY OUT WITH A FRIEND', 'WHO GETS IT.')),
             ("STUDY THE LANGUAGE THROUGH THE ANIME YOU'RE ALREADY WATCHING.",
              PH('STUDY THE LANGUAGE', 'THROUGH THE ANIME', "YOU'RE ALREADY WATCHING.")),
             ('A TOKYO LOCAL WHO ACTUALLY WATCHES.', PH('A TOKYO LOCAL', 'WHO ACTUALLY WATCHES.'))]:
    assert a in body, a
    body = body.replace(a, b)
body = body.replace('<body>', '<body id="v">', 1)
body = body.replace('<section class="hero">', '<section class="hero">%HERODZ%', 1)
body = body.replace('<section class="finale" id="finale">', '<section class="finale" id="finale">%FINDZ%', 1)
assert '%HERODZ%' in body and '%FINDZ%' in body

NAVI = ('<div class="navi" aria-label="Guide"><a class="navi-b" href="#finale"><span class="navi-k">GUIDE</span>'
        '<span class="navi-l">New here? </span>Check dates →</a><img class="navi-m" src="mascot-cut.webp" alt="" width="561" height="764">'
        '<button class="navi-x" type="button" aria-label="Close guide">×</button></div>')
JS = r"""<script>
(()=>{const n=document.querySelector('.navi'),b=document.getElementById('finale');if(sessionStorage.navi==='x'){n.remove();return}
n.querySelector('.navi-x').onclick=()=>{sessionStorage.navi='x';n.remove()};
if(b&&'IntersectionObserver'in window)new IntersectionObserver(e=>n.classList.toggle('off',e[0].isIntersecting),{threshold:.08}).observe(b)})();
// 見出しを1行に: 入らなければ文字を縮める。最小16pxでも入らない長文見出しは句(.ph)単位で折る
(()=>{const MIN=16;const fit=()=>document.querySelectorAll('main h1,main h2').forEach(h=>{
 h.style.fontSize='';h.style.whiteSpace='';h.style.width='';delete h.dataset.wrap;
 const p=h.parentElement,ps=getComputedStyle(p),hs=getComputedStyle(h);
 const avail=(p.clientWidth-parseFloat(ps.paddingLeft)-parseFloat(ps.paddingRight)-parseFloat(hs.marginLeft)-parseFloat(hs.marginRight))*.94;
 const f=parseFloat(hs.fontSize),pad=parseFloat(hs.paddingLeft)+parseFloat(hs.paddingRight);
 h.style.whiteSpace='nowrap';h.style.width='max-content';h.style.maxWidth='none';const need=h.offsetWidth;h.style.width='';h.style.maxWidth='';
 if(need<=avail)return;
 const g=f*(avail-pad)/(need-pad),ph0=h.querySelector('.ph');if(g>=MIN&&!(ph0&&g<f*.75)){h.style.fontSize=g+'px';return}
 h.style.whiteSpace='';h.dataset.wrap='1';const ph=[...h.querySelectorAll('.ph')];if(!ph.length)return;
 const w=Math.max(...ph.map(x=>x.offsetWidth));if(w+pad>avail)h.style.fontSize=f*(avail-pad)/w+'px'});
 fit();document.fonts&&document.fonts.ready.then(fit);addEventListener('resize',fit)})();
</script>"""

KIT = """
:root{--disp:"Anton","Zen Kaku Gothic New","Noto Sans JP",sans-serif;--maru:"Noto Sans JP","Zen Kaku Gothic New","Hiragino Kaku Gothic ProN",sans-serif;
--star:%STAR%;--burst:%BURST%;--dots:radial-gradient(circle,currentColor 1.3px,transparent 1.5px)}
html,body{overflow-x:clip}
#v main,#v .sec,#v .finale{overflow-x:clip}
#v{font-family:var(--maru)}
#v .ph{white-space:nowrap}
#v main h2[data-wrap]{transform:none!important;line-height:1.1!important}
#v h1,#v h2{text-wrap:balance}
#v .hero h1 .l2{display:inline}
#v .site-head .logo{display:block;line-height:0;flex:none}
#v .site-head .logo img{height:44px;width:auto;display:block}
@media (max-width:600px){#v .site-head .logo img{height:36px}}
#v .wrap>*,#v .feature>*,#v .guide>*{min-width:0}
#v .rev-strip{scrollbar-width:none}
.dz{position:absolute;inset:0;pointer-events:none;z-index:1;display:block}
.navi{position:fixed;right:max(12px,env(safe-area-inset-right));bottom:max(12px,env(safe-area-inset-bottom));z-index:900;display:flex;align-items:flex-end;gap:0;transition:opacity .25s,transform .25s}
.navi.off{opacity:0;transform:translateY(14px);pointer-events:none}
.navi-b{display:block;max-width:180px;margin-bottom:40px;margin-right:-6px;padding:9px 13px 10px;text-decoration:none;font:900 14px/1.35 var(--maru);background:var(--nb);color:var(--nt);border:var(--nbd);box-shadow:var(--ns);position:relative;transform:var(--ntr,none)}
.navi-b:after{content:"";position:absolute;right:-12px;bottom:12px;width:16px;height:14px;background:inherit;clip-path:polygon(0 0,100% 60%,0 100%)}
.navi-l{display:block}
.navi-k{display:block;font:400 12px/1 var(--disp);letter-spacing:.14em;color:var(--nk);margin-bottom:4px}
.navi-m{display:block;height:150px;width:auto;filter:drop-shadow(2px 0 0 #fff) drop-shadow(-2px 0 0 #fff) drop-shadow(0 2px 0 #fff) drop-shadow(0 -2px 0 #fff) drop-shadow(5px 5px 0 #111)}
.navi-x{position:absolute;top:-8px;right:-4px;width:26px;height:26px;border-radius:50%;border:2px solid #fff;background:#111;color:#fff;font:700 15px/22px sans-serif;cursor:pointer;padding:0}
@media (max-width:1024px){.navi{bottom:calc(52px + env(safe-area-inset-bottom))}}
@media (max-width:600px){.navi{right:6px}.navi-b{max-width:none;white-space:nowrap;margin-bottom:12px;padding:5px 9px;font-size:12px}.navi-k,.navi-l{display:none}.navi-m{height:70px}.navi-x{width:22px;height:22px;line-height:18px;font-size:13px}}
@media (prefers-reduced-motion:reduce){.navi{transition:none}}
""".replace('%STAR%', star(5, .45)).replace('%BURST%', star(16, .74))

# ================================================================ t1 赤基調・斜め全開（角度は -6° の1種類だけ）
T1 = dict(key='t1', title='赤基調・斜め全開', line='赤地に黒の斜めスラブ。見出しは白い札を-6°で切り込み、セクションの境目も全部斜めに切る最も攻撃的な案',
 hero='<i class="dz" aria-hidden="true"></i>', fin='<i class="dz" aria-hidden="true"></i>', css="""
#v{--A:-6deg;--R:#e50914;--K:#0b0b0b;--bg:#e50914;--bg-2:#0b0b0b;--txt:#fff;--sub:#fff;--ink:#0b0b0b;--ac:#e50914;--ac-deep:#b8000b;--ac-tint:#fff;--line:#0b0b0b;--card:#fff;background:#e50914;color:#fff;
--nb:#fff;--nt:#0b0b0b;--nbd:3px solid #0b0b0b;--ns:5px 5px 0 #0b0b0b;--nk:#e50914;--ntr:rotate(-6deg)}
#v .site-head{background:var(--K);border-bottom:5px solid #fff}
#v .site-head nav a{font:400 15px/1 var(--disp);letter-spacing:.07em;text-transform:uppercase;padding:6px 8px}
#v .site-head nav a:hover{background:var(--R);color:#fff}
#v .site-head .btn-sm{background:#fff;color:var(--R);border:0;border-radius:0;transform:skewX(var(--A));box-shadow:4px 4px 0 var(--R);padding:9px 16px;background-image:none}
#v .clock b,#v .clock i{color:var(--R)}
#v .hero{clip-path:polygon(0 0,100% 0,100% calc(100% - 7vw),0 100%);min-height:min(92svh,820px)}
#v .hero::after{background:linear-gradient(180deg,rgba(229,9,20,.35),rgba(229,9,20,.15) 30%,rgba(229,9,20,.92) 78%);mix-blend-mode:multiply}
#v .hero .dz{z-index:1;color:#000;background:var(--dots);background-size:9px 9px;opacity:.5;-webkit-mask-image:linear-gradient(174deg,transparent 0 48%,#000 49%);mask-image:linear-gradient(174deg,transparent 0 48%,#000 49%)}
#v .hero .dz:after{content:"";position:absolute;left:0;bottom:0;width:58%;height:62%;background:var(--K);clip-path:polygon(0 18%,100% 0,78% 100%,0 100%);opacity:.92}
#v .hero .in{padding-bottom:calc(60px + 7vw)}
#v .tag{background:#fff;color:var(--K);border:0;border-radius:0;transform:rotate(var(--A));box-shadow:5px 5px 0 var(--R);font-family:var(--disp);font-weight:400;font-size:15px;letter-spacing:.1em}
#v .hero h1{font:400 clamp(48px,12vw,128px)/.95 var(--disp);letter-spacing:.01em;transform:rotate(var(--A));transform-origin:left bottom;text-shadow:6px 6px 0 var(--K)}
#v .hero h1 .l2{background:#fff;color:var(--R);text-shadow:none;padding:0 .14em;box-shadow:8px 8px 0 var(--K)}
#v .hero .sub{font-family:var(--maru);font-weight:900;margin-top:22px}
#v .hero .hook{font-size:clamp(20px,4.4vw,32px)}
#v .btn{border-radius:0;transform:skewX(var(--A));font-family:var(--maru);font-weight:900}
#v .btn.white{background:#fff;color:var(--R);border:3px solid var(--K);box-shadow:7px 7px 0 var(--K);font-size:18px}
#v .btn.red{background:var(--K);color:#fff;border:3px solid #fff;box-shadow:7px 7px 0 #fff}
#v .btn:hover{transform:skewX(var(--A)) translate(-2px,-3px)}
#v .seal{border-radius:0;clip-path:var(--burst);border:0;box-shadow:none;background:#fff;width:clamp(110px,24vw,150px)!important;padding:18px}
#v .seal em{color:var(--R)}#v .seal b{color:var(--K)}
#v .ticker{background:#fff;color:var(--K);transform:rotate(var(--A)) scale(1.1);margin:-2vw 0 3vw;position:relative;z-index:3;border:0;box-shadow:0 6px 0 var(--K)}
#v .ticker span i{color:var(--R)}
#v .sec{background:var(--R);color:#fff;position:relative}
#v .sec p.center a{color:#fff!important;text-decoration:underline}
#v .sec.tint{background:var(--K);clip-path:polygon(0 6vw,100% 0,100% calc(100% - 6vw),0 100%);padding:calc(6vw + 56px) 0}
#v .sec.tint::before{content:"";position:absolute;inset:0;color:var(--R);background:var(--dots);background-size:10px 10px;opacity:.35;-webkit-mask-image:linear-gradient(100deg,#000,transparent 40%);mask-image:linear-gradient(100deg,#000,transparent 40%);pointer-events:none}
#v .sec>.wrap{position:relative}
#v .sec h2,#v .finale h2{display:block;width:fit-content;max-width:100%;background:#fff;color:var(--K);padding:.08em .4em .02em;transform:rotate(var(--A));box-shadow:8px 8px 0 var(--K);font:400 clamp(30px,6vw,60px)/1.05 var(--disp);letter-spacing:.01em;margin:6px 0 30px;transform-origin:left bottom}
#v .sec.tint h2{background:var(--R);color:#fff;box-shadow:8px 8px 0 #fff}
#v .center h2{margin-left:auto;margin-right:auto}
#v .sec .lead,#v .feature p:not(.eyebrow),#v .guide p{color:#fff;font-weight:500}
#v .eyebrow,#v .guide .who{display:inline-block;display:inline-block;background:var(--K);color:#fff;border-radius:0;transform:skewX(var(--A));font:400 14px/1 var(--disp);letter-spacing:.14em;padding:7px 12px}
#v .sec.tint .eyebrow{background:#fff;color:var(--K)}
#v .pop,#v .card,#v .review,#v .step{border:4px solid var(--K);border-radius:0;box-shadow:9px 9px 0 var(--K);background:#fff;color:var(--K)}
#v .sec.tint .pop{box-shadow:9px 9px 0 var(--R)}
#v .pop p,#v .card p,#v .review p,#v .step p{color:#222}
#v .card h3,#v .step h3{font-weight:900;color:var(--K)}
#v .card.phrase h3{font-family:var(--disp);color:var(--R)}
#v .card.hot{background:var(--K);color:#fff}#v .card.hot h3,#v .card.hot a{color:#fff}
#v .review .stars{color:var(--R)}#v .review .src{background:var(--R);border-radius:0}
#v .step,#v .step:nth-child(n){transform:rotate(0)}
#v .step img{clip-path:polygon(0 0,100% 0,100% 82%,0 100%)}
#v .step .n{border-radius:0;clip-path:var(--star);border:0;width:58px;height:58px;background:var(--R);box-shadow:none;transform:none;font-size:22px;padding-top:4px}
#v .pf,#v .pf:nth-child(n){border-radius:0;background:#fff;border:0;box-shadow:none;transform:rotate(var(--A));clip-path:polygon(8% 0,100% 0,92% 100%,0 100%);width:min(200px,40vw);aspect-ratio:4/3}
#v .pf b{color:var(--R)}#v .pf b i{color:#555}#v .pf .k{color:var(--K);font-weight:900}#v .pf .s{color:#444}
#v .fig,#v .feature.rev .fig,#v .face-wrap{transform:rotate(var(--A))}
#v .fig img,#v .face-wrap img,#v .banner img,#v .video-embed{border:5px solid #fff;border-radius:0;box-shadow:12px 12px 0 var(--K)}
#v .figcap{border-radius:0;background:var(--K);color:#fff;border:0;box-shadow:none;font-family:var(--disp);font-weight:400;letter-spacing:.12em}
#v .banner{transform:rotate(var(--A)) scale(.96)}
#v .ticks li{color:#fff}
#v .ticks li::before{border-radius:0;background:#fff;color:var(--R);border:0;clip-path:polygon(15% 0,100% 0,85% 100%,0 100%)}
#v .chip{border-radius:0;background:#fff;color:var(--K);border:0;box-shadow:4px 4px 0 var(--K);transform:skewX(var(--A))}
#v .sec.tint .chip{box-shadow:4px 4px 0 var(--R)}
#v .bubble{border-radius:0;background:#fff;border:4px solid var(--K);box-shadow:8px 8px 0 var(--R);transform:rotate(var(--A))}
#v .bubble p{color:var(--K)}#v .bubble::after{border-bottom-color:#fff}
#v .face-wrap .seal{transform:none}
#v .ig-grid a{border:4px solid #fff;border-radius:0;box-shadow:6px 6px 0 var(--K)}
#v .ig-grid a:nth-child(odd){transform:rotate(var(--A))}
#v .faq details{background:#fff;color:var(--K)}
#v .faq summary{font-weight:900}
#v .faq details[open] summary{background:var(--K);color:#fff}
#v .faq summary::after{border-radius:0;background:var(--R);border:0;clip-path:polygon(15% 0,100% 0,85% 100%,0 100%)}
#v .faq details>p{color:#222}
#v .finale{background:var(--K);clip-path:polygon(0 6vw,100% 0,100% 100%,0 100%);padding-top:calc(6vw + 60px);border:0}
#v .finale::before{display:none}
#v .finale .dz{background:var(--R);clip-path:polygon(0 0,40% 0,22% 100%,0 100%);opacity:1;z-index:0}
#v .finale .dz:after{content:"";position:absolute;inset:0;color:#000;background:var(--dots);background-size:9px 9px;opacity:.35}
#v .finale h2{margin:0 auto 10px;background:var(--R);color:#fff;box-shadow:8px 8px 0 #fff}
#v .booker{border-radius:0;border:5px solid #fff;box-shadow:14px 14px 0 var(--R)}
#v .booker .bk-t{font-family:var(--disp);color:var(--K)}
#v .bk-mount{border-radius:0;box-shadow:6px 6px 0 var(--R)}
#v .bk-step button{border-radius:0}
#v .site-foot{background:var(--K);border-top:6px solid var(--R)}
#v .site-foot .h{color:var(--R)}
#v .adprice{background:var(--K)}#v .ap-cell{border-radius:0}
""")

# ================================================================ t2 黒基調・メニュー画面風（skew -8° の1種類）
T2 = dict(key='t2', title='黒基調・メニュー画面風', line='黒地にメニュー項目のように傾いた白帯。赤い三角カーソルと反転ハイライトで「選んでいる」感を出す案',
 hero='<i class="dz" aria-hidden="true"><b></b><b></b></i>', fin='<i class="dz" aria-hidden="true"></i>', css="""
#v{--A:-8deg;--R:#ff1a1a;--K:#070707;--bg:#070707;--bg-2:#111;--txt:#f2f2f2;--sub:#bdbdbd;--ink:#000;--ac:#ff1a1a;--ac-deep:#ff1a1a;--ac-tint:#1b1b1b;--line:#2a2a2a;--card:#121212;background:#070707;color:#f2f2f2;
--nb:#070707;--nt:#fff;--nbd:3px solid #fff;--ns:-5px 5px 0 #ff1a1a;--nk:#ff1a1a;--ntr:skewX(-8deg)}
#v .site-head{background:#000;border-bottom:3px solid var(--R)}
#v .site-head nav{gap:4px}
#v .site-head nav a{font:400 16px/1 var(--disp);letter-spacing:.08em;text-transform:uppercase;padding:8px 12px;transform:skewX(var(--A))}
#v .site-head nav a:hover{background:#fff;color:#000}
#v .site-head .btn-sm{background:var(--R);color:#fff;border:0;border-radius:0;box-shadow:-4px 4px 0 #fff;background-image:none;margin-left:8px}
#v .clock b,#v .clock i{color:var(--R)}
#v .hero::after{background:linear-gradient(100deg,rgba(0,0,0,.94) 0 46%,rgba(0,0,0,.55) 72%,rgba(0,0,0,.75))}
#v .hero .dz{z-index:2}
#v .hero .dz b{position:absolute;display:block;top:-10%;bottom:-10%;transform:skewX(var(--A))}
#v .hero .dz b:first-child{left:-6%;width:13%;background:var(--R)}
#v .hero .dz b:last-child{left:8.5%;width:1.2%;background:#fff}
#v .hero .dz:after{content:"";position:absolute;inset:0;color:var(--R);background:var(--dots);background-size:10px 10px;opacity:.6;-webkit-mask-image:linear-gradient(97deg,transparent 0 62%,#000 82%);mask-image:linear-gradient(97deg,transparent 0 62%,#000 82%)}
@media (max-width:1100px){#v .hero .dz b{display:none}}
@media (min-width:1101px){#v .hero .in{padding-left:max(20px,calc((100vw - 1060px)/2 + 40px))}}
#v .tag{background:none;border:0;box-shadow:none;transform:none;color:#fff;font:400 16px/1 var(--disp);letter-spacing:.16em;padding:0 0 0 24px;position:relative}
#v .tag::before,#v .eyebrow::before,#v .guide .who::before{content:"";position:absolute;left:0;top:50%;width:15px;height:17px;margin-top:-9px;background:var(--R);clip-path:polygon(0 0,100% 50%,0 100%)}
#v .hero h1{font:400 clamp(48px,11vw,120px)/.98 var(--disp);text-shadow:none}
#v .hero h1 .l2{display:inline-block;background:#fff;color:#000;padding:0 .16em;transform:skewX(var(--A));box-shadow:-8px 8px 0 var(--R)}
#v .hero .sub{font-family:var(--maru);font-weight:700;color:#ddd}
#v .btn{border-radius:0;transform:skewX(var(--A));font-family:var(--maru);font-weight:900;border:0}
#v .btn.white,#v .btn.red{background:var(--R);color:#fff;box-shadow:-7px 7px 0 #fff;font-size:17px}
#v .btn.white:hover,#v .btn.red:hover{background:#fff;color:#000;box-shadow:-7px 7px 0 var(--R)}
#v .seal{border-radius:0;background:#000;border:3px solid #fff;box-shadow:-6px 6px 0 var(--R);transform:skewX(var(--A))!important;aspect-ratio:auto;padding:12px 16px}
#v .seal em{color:var(--R)}#v .seal b{color:#fff}#v .seal small{color:#bbb}#v .seal b i{color:#888}
#v .ticker{background:var(--R);border:0}#v .ticker span i{color:#000}
#v .sec{background:var(--K)}
#v .sec.tint{background:#101010;position:relative}
#v .sec.tint::before{content:"";position:absolute;left:0;right:0;top:0;height:6px;background:linear-gradient(90deg,var(--R) 0 30%,#fff 30% 31%,transparent 31%)}
#v .eyebrow,#v .guide .who{display:inline-block;position:relative;background:none;color:var(--R);font:400 15px/1 var(--disp);letter-spacing:.18em;padding:0 0 0 24px;border-radius:0}
#v .sec h2,#v .finale h2{position:relative;display:block;width:fit-content;max-width:100%;font:400 clamp(30px,6vw,62px)/1.05 var(--disp);color:#fff;background:none;padding:.06em .3em .02em 0;margin:4px 0 26px}
#v .sec h2::after{content:"";position:absolute;left:-.3em;right:-.1em;bottom:-.12em;height:.22em;background:var(--R);transform:skewX(var(--A));z-index:-1}
#v .sec h2{z-index:0}
#v .center h2{margin-left:auto;margin-right:auto}
#v .sec .lead,#v .feature p:not(.eyebrow),#v .guide p:not(.who),#v .ticks li{color:#c8c8c8}
#v .pop,#v .card,#v .review,#v .step{border:0;border-left:6px solid var(--R);border-radius:0;box-shadow:none;background:#141414;color:#f2f2f2;transition:background .15s,color .15s,transform .15s}
#v .card:hover,#v .review:hover{background:#fff;color:#000;transform:skewX(-2deg)}
#v .card:hover p,#v .review:hover p,#v .card:hover h3{color:#000}
#v .card h3,#v .step h3{color:#fff;font-weight:900}
#v .card p,#v .review p,#v .step p{color:#bdbdbd}
#v .card.phrase h3{font-family:var(--disp);color:var(--R)}#v .card.phrase .kana{color:#fff}
#v .card.hot{background:var(--R);border-left-color:#fff}#v .card.hot h3,#v .card.hot a{color:#fff}
#v .review .stars{color:var(--R)}#v .review .src{background:#fff;color:#000;border-radius:0}
#v .review figcaption{color:#999}
#v .step,#v .step:nth-child(n){transform:none}
#v .step .n{border-radius:0;transform:skewX(var(--A));background:#fff;color:#000;border:0;box-shadow:-4px 4px 0 var(--R)}
#v .step .body{border-top:3px solid var(--R)}
#v .proofs{display:grid;grid-template-columns:1fr;gap:10px;justify-content:stretch;justify-items:stretch;max-width:760px}
@media(min-width:700px){#v .proofs{grid-template-columns:1fr 1fr}}
#v .proofs>:last-child:nth-child(odd){grid-column:auto}
#v .pf,#v .pf:nth-child(n){width:auto;aspect-ratio:auto;border-radius:0;border:0;border-left:8px solid var(--R);background:#151515;box-shadow:none;transform:skewX(var(--A));display:grid;grid-template-columns:auto 1fr;grid-template-rows:auto auto;column-gap:16px;align-items:baseline;text-align:left;padding:14px 22px}
#v .pf b{grid-row:1/3;font-size:clamp(34px,6vw,48px);color:#fff}#v .pf b i{color:#777}
#v .pf .k{color:var(--R);font:400 16px/1 var(--disp);letter-spacing:.1em;margin:0}#v .pf .s{color:#aaa;margin:0}
#v .pf:hover{background:#fff;transform:skewX(var(--A)) translateX(8px)}#v .pf:hover b{color:#000}
#v .fig,#v .feature.rev .fig,#v .face-wrap{transform:none}
#v .fig img,#v .face-wrap img,#v .banner img,#v .video-embed{border:0;border-radius:0;box-shadow:-12px 12px 0 var(--R);clip-path:polygon(4% 0,100% 0,96% 100%,0 100%)}
#v .video-embed{clip-path:none;border:3px solid #fff}
#v .figcap{border-radius:0;background:#fff;color:#000;border:0;box-shadow:-4px 4px 0 var(--R);transform:skewX(var(--A));font-family:var(--disp);font-weight:400}
#v .ticks li::before{content:"";border-radius:0;background:var(--R);border:0;clip-path:polygon(0 0,100% 50%,0 100%);width:14px;height:16px;top:6px}
#v .chip{border-radius:0;background:#fff;color:#000;border:0;box-shadow:-4px 4px 0 var(--R);transform:skewX(var(--A))}
#v .bubble{border-radius:0;background:#fff;border:0;box-shadow:-8px 8px 0 var(--R);transform:skewX(var(--A))}
#v .bubble p{color:#000}#v .bubble::before{display:none}#v .bubble::after{border-bottom-color:#fff}
#v .face-wrap .seal{transform:skewX(var(--A))!important}
#v .ig-grid a{border:0;border-radius:0;box-shadow:none;transform:skewX(var(--A));outline:3px solid transparent;outline-offset:3px}
#v .ig-grid a:hover{outline-color:var(--R)}
#v .faq{gap:6px}
#v .faq details{background:#121212;border:0;box-shadow:none;border-radius:0}
#v .faq summary{padding-left:38px;color:#fff}
#v .faq summary::before{content:"";position:absolute;left:14px;top:22px;width:12px;height:14px;background:#555;clip-path:polygon(0 0,100% 50%,0 100%)}
#v .faq details:hover summary::before,#v .faq details[open] summary::before{background:var(--R)}
#v .faq details[open] summary,#v .faq summary:hover{background:#fff;color:#000}
#v .faq summary::after{border-radius:0;background:none;border:0;color:var(--R)}
#v .faq details>p{color:#c4c4c4;border-top:0}#v .faq a{color:var(--R)}
#v .finale{background:#000;border:0;border-top:4px solid var(--R)}
#v .finale::before{color:var(--R);background:var(--dots);background-size:10px 10px;opacity:.45}
#v .finale h2{margin:0 auto 10px}#v .finale h2::after{content:"";position:absolute;left:-.3em;right:-.1em;bottom:-.12em;height:.22em;background:var(--R);transform:skewX(var(--A));z-index:-1}
#v .finale h2{z-index:0}
#v .booker{border-radius:0;border:3px solid #fff;box-shadow:-14px 14px 0 var(--R)}
#v .booker,#v .booker *{--txt:#111;--sub:#555;--line:#ddd;--ac-tint:#f3f3f3}
#v .bk-mount{border-radius:0;box-shadow:-6px 6px 0 var(--R)}#v .bk-step button{border-radius:0}
#v .site-foot{background:#000;border-top:3px solid var(--R)}#v .site-foot .h{color:var(--R)}
#v .adprice{background:#111}#v .ap-cell{border-radius:0;background:#1a1a1a}#v .ap-cell b{color:#fff}
""")

# ================================================================ t3 白＋ハーフトーン漫画風（-3° の1種類）
T3 = dict(key='t3', title='白＋ハーフトーン漫画風', line='白地に網点と吹き出し。カードを漫画のコマ割りのように黒枠で区切った、いちばん読みやすい案',
 hero='<i class="dz" aria-hidden="true"></i>', fin='<i class="dz" aria-hidden="true"></i>', css="""
#v{--A:-3deg;--R:#e3121b;--K:#111;--bg:#fff;--bg-2:#fff;--txt:#111;--sub:#3d3d3d;--ink:#111;--ac:#e3121b;--ac-deep:#c40c14;--ac-tint:#fff;--line:#111;--card:#fff;background:#fff;color:#111;
--nb:#fff;--nt:#111;--nbd:3px solid #111;--ns:4px 4px 0 #111;--nk:#e3121b;--ntr:none}
#v .site-head{background:#fff;color:#111;border-bottom:4px solid #111}
#v .site-head nav a{color:#111;font-weight:900;font-size:14px}
#v .site-head nav a:hover{color:var(--R)}
#v .site-head .btn-sm{background:var(--R);color:#fff;border:3px solid #111;border-radius:0;box-shadow:3px 3px 0 #111;background-image:none}
#v .clock b,#v .clock i{color:#666}#v .clock span{color:#111}
#v .hero{margin:14px;border:5px solid #111;min-height:min(84svh,760px)}
#v .hero::after{background:linear-gradient(180deg,rgba(0,0,0,.15) 0%,rgba(0,0,0,.45) 35%,rgba(0,0,0,.85) 90%)}
#v .hero .dz{z-index:1;color:#fff;background:var(--dots);background-size:8px 8px;opacity:.28;-webkit-mask-image:radial-gradient(ellipse 60% 60% at 100% 0,#000,transparent 70%);mask-image:radial-gradient(ellipse 60% 60% at 100% 0,#000,transparent 70%)}
#v .tag{background:#fff;color:#111;border:3px solid #111;border-radius:0;box-shadow:4px 4px 0 var(--R);transform:rotate(var(--A));font-weight:900}
#v .hero h1{font:400 clamp(46px,11vw,112px)/.98 var(--disp);text-shadow:5px 5px 0 var(--R)}
#v .hero .hook{display:inline-block;position:relative;background:#fff;color:#111;text-shadow:none;border:3px solid #111;border-radius:22px;padding:10px 18px;margin-top:18px;font-size:clamp(17px,3.6vw,24px)}
#v .hero .hook::after{content:"";position:absolute;left:30px;bottom:-16px;width:20px;height:16px;background:#fff;border:solid #111;border-width:0 3px 0 0;clip-path:polygon(0 0,100% 0,100% 100%);transform:skewX(-20deg)}
#v .hero .sub{font-family:var(--maru);font-weight:700}
#v .btn{border-radius:0;font-family:var(--maru);font-weight:900;border:3px solid #111}
#v .btn.white{background:var(--R);color:#fff;box-shadow:5px 5px 0 #111;border-color:#fff}
#v .btn.red{background:var(--R);color:#fff;box-shadow:5px 5px 0 #111}
#v .seal{border-radius:50%;background:#fff;border:3px solid #111;box-shadow:4px 4px 0 var(--R)}
#v .seal em{color:var(--R)}
#v .ticker{background:#111;border:0;margin-top:0}#v .ticker span i{color:var(--R)}
#v .sec{background:#fff;position:relative}
#v .sec.tint{background:#fff;border-top:4px solid #111;border-bottom:4px solid #111}
#v .sec.tint::before{content:"";position:absolute;inset:0;color:#111;background:var(--dots);background-size:7px 7px;opacity:.09;pointer-events:none}
#v .sec>.wrap{position:relative}
#v .eyebrow,#v .guide .who{display:inline-block;background:#111;color:#fff;border-radius:0;font-weight:900;letter-spacing:.16em}
#v .sec h2,#v .finale h2{font:400 clamp(32px,6.4vw,62px)/1.04 var(--disp);color:#111;letter-spacing:.005em;position:relative;display:block;width:fit-content;max-width:100%}
#v .sec h2::after{content:"";display:block;height:.16em;width:2.2em;background:var(--R);margin-top:.14em;transform:skewX(-20deg)}
#v .center h2{margin-left:auto;margin-right:auto}#v .center h2::after{margin:.14em auto 0}
#v .sec .lead,#v .feature p:not(.eyebrow),#v .guide p:not(.who),#v .ticks li{color:#333}
#v .pop,#v .card,#v .step{border:4px solid #111;border-radius:0;box-shadow:none;background:#fff}
#v .grid3,#v .grid4,#v .steps,#v .ig-grid{gap:10px}
#v .card h3,#v .step h3{font-weight:900;color:#111}
#v .card.phrase h3{font-family:var(--disp);color:var(--R)}
#v .card.hot{background:var(--R)}#v .card.hot::before{content:"";position:absolute;inset:0;color:#fff;background:var(--dots);background-size:8px 8px;opacity:.25}
#v .card.hot{position:relative}#v .card.hot>*{position:relative}
#v .step,#v .step:nth-child(n){transform:none;border-radius:0}
#v .step .n{border-radius:50%;background:#fff;color:#111;border:3px solid #111;box-shadow:3px 3px 0 var(--R);transform:none}
#v .step .body{border-top:4px solid #111}
#v .review{position:relative;border:3px solid #111;border-radius:26px;box-shadow:none;background:#fff;margin-bottom:22px;overflow:visible}
#v .review::after{content:"";position:absolute;left:34px;bottom:-21px;width:26px;height:21px;background:#111;clip-path:polygon(0 0,100% 0,10% 100%)}
#v .review::before{content:"";position:absolute;left:37px;bottom:-14px;width:20px;height:16px;background:#fff;clip-path:polygon(0 0,100% 0,8% 100%);z-index:1}
#v .review:nth-child(even){border-radius:26px;background:#fff}
#v .review .stars{color:var(--R)}#v .review .src{background:#111;border-radius:0}
#v .rev-strip .review{margin-bottom:26px}
#v .pf,#v .pf:nth-child(n){border-radius:0;border:4px solid #111;box-shadow:none;transform:none;background:#fff;aspect-ratio:1;width:min(180px,40vw);overflow:hidden}
#v .pf::before{content:"";position:absolute;inset:0;color:var(--R);background:var(--dots);background-size:8px 8px;opacity:.22;-webkit-mask-image:linear-gradient(135deg,#000,transparent 55%);mask-image:linear-gradient(135deg,#000,transparent 55%)}
#v .pf b{color:var(--R)}#v .pf .k{font-weight:900}
#v .fig,#v .feature.rev .fig,#v .face-wrap{transform:none}
#v .fig img,#v .face-wrap img,#v .banner img,#v .video-embed{border:4px solid #111;border-radius:0;box-shadow:none}
#v .figcap{border-radius:0;background:#fff;color:#111;border:3px solid #111;box-shadow:none}
#v .ticks li::before{border-radius:0;background:var(--R);border:2px solid #111}
#v .chip{border-radius:0;border:3px solid #111;box-shadow:3px 3px 0 var(--R)}
#v .bubble{border-radius:28px;background:#fff;border:3px solid #111;box-shadow:none}
#v .bubble::after{border-bottom-color:#fff}
#v .face-wrap .seal{transform:rotate(var(--A))}
#v .ig-grid a{border:4px solid #111;border-radius:0;box-shadow:none}
#v .faq details{border:3px solid #111;border-radius:0;box-shadow:none}
#v .faq details[open]{box-shadow:5px 5px 0 var(--R)}
#v .faq summary::after{border-radius:50%;background:#fff;color:#111;border:3px solid #111}
#v .faq details>p{border-top:3px solid #111}
#v .finale{background:var(--R);border-top:5px solid #111;border-bottom:5px solid #111}
#v .finale::before{display:none}
#v .finale .dz{color:#fff;background:repeating-conic-gradient(from 0deg at 50% 110%,rgba(255,255,255,.14) 0 4deg,transparent 4deg 12deg);z-index:0}
#v .finale .dz:after{content:"";position:absolute;inset:0;color:#000;background:var(--dots);background-size:8px 8px;opacity:.12}
#v .finale h2{color:#fff;text-shadow:5px 5px 0 #111;margin:0 auto}
#v .booker{border-radius:0;border:5px solid #111;box-shadow:10px 10px 0 #111}
#v .bk-mount{border-radius:0;box-shadow:none;border:3px solid #111}#v .bk-step button{border-radius:0}
#v .site-foot{background:#111}#v .site-foot .h{color:#fff}
#v .adprice{background:#fff}#v .ap-cell{border-radius:0}
""")

# ================================================================ t4 バーストと星のポップ全開（-8° の1種類）
T4 = dict(key='t4', title='バーストと星のポップ全開', line='星型バーストと放射線が主役。評価・実績・料金をバーストの中に入れて、数字で殴る案',
 hero='<i class="dz" aria-hidden="true"><b></b><b></b></i>', fin='<i class="dz" aria-hidden="true"><b></b></i>', css="""
#v{--A:-8deg;--R:#e8101a;--K:#0a0a0a;--bg:#fff;--bg-2:#0a0a0a;--txt:#111;--sub:#333;--ink:#0a0a0a;--ac:#e8101a;--ac-deep:#c00a12;--ac-tint:#fff;--line:#0a0a0a;--card:#fff;background:#fff;color:#111;
--nb:var(--R);--nt:#fff;--nbd:3px solid #0a0a0a;--ns:5px 5px 0 #0a0a0a;--nk:#fff;--ntr:rotate(-8deg)}
#v .site-head{background:var(--R);border-bottom:4px solid var(--K)}
#v .site-head nav a{font:400 15px/1 var(--disp);letter-spacing:.06em;text-transform:uppercase}
#v .site-head .btn-sm{background:#fff;color:var(--K);border:3px solid var(--K);border-radius:0;transform:rotate(var(--A));box-shadow:4px 4px 0 var(--K);background-image:none}
#v .hero::after{background:radial-gradient(ellipse 80% 70% at 20% 85%,rgba(10,10,10,.9),rgba(10,10,10,.35) 70%)}
#v .hero .dz b{position:absolute;display:block}
#v .hero .dz{z-index:1}
#v .hero .dz b:first-child{left:-40%;bottom:-70%;width:120vmax;aspect-ratio:1;background:repeating-conic-gradient(from 0deg at 50% 50%,rgba(232,16,26,.5) 0 6deg,transparent 6deg 15deg);-webkit-mask-image:radial-gradient(circle,#000 20%,transparent 60%);mask-image:radial-gradient(circle,#000 20%,transparent 60%)}
#v .hero .dz b:last-child{right:4%;bottom:10%;width:clamp(120px,22vw,300px);aspect-ratio:1;background:#fff;clip-path:var(--star);transform:rotate(14deg);opacity:.95;display:none}
#v .tag{background:#fff;color:var(--R);border:3px solid var(--K);border-radius:0;transform:rotate(var(--A));box-shadow:5px 5px 0 var(--K);font:400 16px/1 var(--disp);letter-spacing:.1em;padding:9px 16px}
#v .hero h1{font:400 clamp(50px,12vw,128px)/.95 var(--disp);color:#fff;text-shadow:5px 5px 0 var(--R),10px 10px 0 var(--K);transform:rotate(var(--A));transform-origin:left bottom}
#v .hero .hook{font-size:clamp(20px,4.4vw,30px);color:#fff}
#v .hero .sub{font-family:var(--maru);font-weight:900}
#v .btn{border-radius:0;font-family:var(--maru);font-weight:900;border:3px solid var(--K)}
#v .btn.white{background:var(--R);color:#fff;box-shadow:6px 6px 0 #fff;border-color:#fff;font-size:18px;transform:rotate(var(--A))}
#v .btn.red{background:var(--R);color:#fff;box-shadow:6px 6px 0 var(--K)}
#v .seals .seal,#v .seal{border-radius:0;clip-path:var(--burst);border:0;box-shadow:none;background:#fff;width:clamp(124px,26vw,190px)!important;padding:22px;filter:drop-shadow(6px 6px 0 var(--K))}
#v .seals{filter:drop-shadow(5px 5px 0 var(--R))}
@media(min-width:940px){#v .seals{top:auto;bottom:150px;right:5vw}}
#v .hero h1{font-size:clamp(50px,9.4vw,120px)}
#v .seal b{font-size:clamp(28px,6vw,46px)!important;color:var(--R)}#v .seal em{color:var(--K);font-size:10px!important}#v .seal small{font-size:10px!important}
#v .ticker{background:var(--K);border:0}#v .ticker span i{color:var(--R);display:inline-block;transform:scale(1.4)}
#v .sec{position:relative;overflow:clip;padding-top:96px}
#v .finale{padding-top:110px}
#v .sec.tint{background:var(--R);color:#fff}
#v .sec.tint::before{content:"";position:absolute;left:50%;top:50%;width:160vmax;aspect-ratio:1;translate:-50% -50%;background:repeating-conic-gradient(from 0deg at 50% 50%,rgba(255,255,255,.1) 0 6deg,transparent 6deg 15deg);pointer-events:none}
#v .sec>.wrap{position:relative}
#v .eyebrow,#v .guide .who{display:inline-block;background:var(--K);color:#fff;border-radius:0;transform:rotate(var(--A));font:400 14px/1 var(--disp);letter-spacing:.14em;padding:7px 12px}
#v .sec h2,#v .finale h2{font:400 clamp(32px,6.4vw,64px)/1.02 var(--disp);color:var(--K);transform:rotate(var(--A));transform-origin:left bottom;width:fit-content;max-width:100%;text-shadow:3px 3px 0 var(--R);margin:4px 0 34px}
#v .sec.tint h2{color:#fff;text-shadow:4px 4px 0 var(--K)}
#v .center h2{margin-left:auto;margin-right:auto;transform-origin:center}
#v .sec.tint .lead,#v .sec.tint .guide p:not(.who):not(.jp),#v .sec.tint .ticks li{color:#fff}
#v .pop,#v .card,#v .review,#v .step{border:4px solid var(--K);border-radius:0;box-shadow:8px 8px 0 var(--K);background:#fff;color:#111}
#v .sec.tint .pop{box-shadow:8px 8px 0 #fff}
#v .card h3,#v .step h3{font-weight:900}
#v .card.phrase h3{font-family:var(--disp);color:var(--R)}
#v .card.hot{background:var(--K);color:#fff}#v .card.hot h3,#v .card.hot a{color:#fff}
#v .review .stars{color:var(--R);font-size:22px;letter-spacing:.04em}#v .review .src{background:var(--R);border-radius:0}
#v .step .n{border-radius:0;clip-path:var(--star);border:0;box-shadow:none;width:64px;height:64px;background:var(--R);color:#fff;font-size:24px;padding-top:6px;transform:none}
#v .proofs{gap:14px 8px}
#v .pf,#v .pf:nth-child(n){border-radius:0;border:0;box-shadow:none;clip-path:var(--burst);background:#fff;width:min(220px,44vw);padding:28px}
#v .pf:nth-child(even){background:var(--K)}#v .pf:nth-child(even) b,#v .pf:nth-child(even) .k{color:#fff}#v .pf:nth-child(even) .s{color:#ccc}
#v .pf:nth-child(odd) b{color:var(--R)}
#v .pf:nth-child(2n){transform:rotate(-8deg)}#v .pf:nth-child(3n){transform:rotate(8deg)}
#v .pf b{font-size:clamp(30px,7vw,48px)}#v .pf .k{font-weight:900}
#v .fig,#v .feature.rev .fig,#v .face-wrap{transform:rotate(var(--A)) scale(.96)}
#v .fig img,#v .face-wrap img,#v .banner img,#v .video-embed{border:5px solid var(--K);border-radius:0;box-shadow:10px 10px 0 var(--R)}
#v .figcap{border-radius:0;background:var(--R);color:#fff;border:3px solid var(--K)}
#v .ticks li::before{content:"";border-radius:0;clip-path:var(--star);border:0;background:var(--R);width:22px;height:22px}
#v .chip{border-radius:0;border:3px solid var(--K);box-shadow:4px 4px 0 var(--K);transform:rotate(var(--A))}
#v .bubble{border-radius:0;background:#fff;border:4px solid var(--K);box-shadow:8px 8px 0 var(--K)}
#v .bubble::after{border-bottom-color:#fff}
#v .sec .bubble p{color:#111}
#v .ig-grid a{border:4px solid var(--K);border-radius:0;box-shadow:5px 5px 0 #fff}
#v .faq details{border:4px solid var(--K);border-radius:0;box-shadow:6px 6px 0 var(--R)}
#v .faq summary::after{border-radius:0;clip-path:var(--star);border:0;width:30px;height:30px;padding-top:3px}
#v .finale{background:var(--K);border:0}
#v .finale::before{display:none}
#v .finale .dz{z-index:0}
#v .finale .dz b{position:absolute;left:50%;top:100%;width:160vmax;aspect-ratio:1;translate:-50% -50%;background:repeating-conic-gradient(from 0deg at 50% 50%,rgba(232,16,26,.45) 0 6deg,transparent 6deg 15deg);display:block}
#v .finale h2{color:#fff;text-shadow:5px 5px 0 var(--R);margin:0 auto}
#v .booker{border-radius:0;border:5px solid var(--K);box-shadow:12px 12px 0 var(--R);overflow:visible}
#v .booker .bk-t span{display:inline-grid!important;place-content:center;clip-path:var(--burst);border-radius:0!important;width:150px;aspect-ratio:1;text-align:center;font-size:12px!important;line-height:1.3;padding:20px!important;vertical-align:middle;margin:-30px 0 -30px 8px!important;background:var(--R)!important}
#v .bk-price b{font-size:34px;color:var(--R)}
#v .bk-mount{border-radius:0;box-shadow:6px 6px 0 var(--K)}#v .bk-step button{border-radius:0}
#v .site-foot{background:var(--K);border-top:6px solid var(--R)}#v .site-foot .h{color:var(--R)}
#v .adprice{background:var(--K)}#v .ap-cell{border-radius:0}#v .ap-cell b{color:var(--R)}
""")

# ================================================================ t5 斜め帯と引用の編集系（-4° の1種類）
T5 = dict(key='t5', title='斜め帯と引用の編集系', line='見出しを全幅の斜め帯に載せ、レビューを誌面のプルクオートとして組む。赤は差し色に絞った落ち着いた編集系の案',
 hero='<i class="dz" aria-hidden="true"></i>', fin='<i class="dz" aria-hidden="true"></i>', css="""
#v{--A:-4deg;--R:#d7141c;--K:#141414;--bg:#fbfaf7;--bg-2:#f1efe9;--txt:#141414;--sub:#4a4a4a;--ink:#141414;--ac:#d7141c;--ac-deep:#b80f16;--ac-tint:#fff;--line:#d6d3cc;--card:#fff;background:#fbfaf7;color:#141414;
--nb:#141414;--nt:#fff;--nbd:0;--ns:none;--nk:#ff5a5f;--ntr:none}
#v .site-head{background:#fbfaf7;color:#141414;border-bottom:1px solid #141414}
#v .site-head nav a{color:#141414;font-weight:700;font-size:14px;letter-spacing:.02em}
#v .site-head nav a:hover{color:var(--R)}
#v .site-head .btn-sm{background:#141414;color:#fff;border:0;border-radius:0;box-shadow:none;background-image:none}
#v .clock b,#v .clock i{color:#888}#v .clock span{color:#141414}
#v .hero{min-height:min(86svh,780px)}
#v .hero::after{background:linear-gradient(180deg,rgba(20,20,20,.1) 20%,rgba(20,20,20,.86) 90%)}
#v .hero .dz{z-index:1}
#v .hero .dz:after{content:"";position:absolute;left:-5%;right:-5%;bottom:-2px;height:9vw;background:#fbfaf7;clip-path:polygon(0 70%,100% 0,100% 100%,0 100%)}
#v .hero .in{padding-bottom:calc(44px + 6vw)}
#v .tag{background:var(--R);color:#fff;border:0;border-radius:0;box-shadow:none;transform:none;letter-spacing:.2em}
#v .hero h1{font:400 clamp(46px,10.5vw,116px)/.96 var(--disp);text-shadow:none;letter-spacing:.01em}
#v .hero .hook{font-family:var(--maru);font-weight:900;border-left:4px solid var(--R);padding-left:14px}
#v .hero .sub{font-family:var(--maru);font-weight:500}
#v .btn{border-radius:0;font-family:var(--maru);font-weight:900;border:0;letter-spacing:.02em}
#v .btn.white,#v .btn.red{background:var(--R);color:#fff;box-shadow:none}
#v .btn.white:hover,#v .btn.red:hover{background:#141414;box-shadow:none}
#v .seal{border-radius:0;background:#fbfaf7;border:0;box-shadow:none;transform:none!important;aspect-ratio:auto;padding:12px 16px;border-top:4px solid var(--R)}
#v .seal em{color:var(--R)}
#v .ticker{background:#fbfaf7;color:#141414;border-top:1px solid #141414;border-bottom:1px solid #141414}#v .ticker span i{color:var(--R)}
#v .sec{background:#fbfaf7}
#v .sec.tint{background:var(--bg-2)}
#v .eyebrow,#v .guide .who{display:inline-block;background:none;color:var(--R);border-radius:0;padding:0;font-weight:900;letter-spacing:.22em;font-size:12px}
#v .sec h2,#v .finale h2{position:relative;font:400 clamp(30px,5.6vw,56px)/1.06 var(--disp);color:#fff;z-index:0;padding:.22em 0 .16em;margin:6px 0 28px;letter-spacing:.01em}
#v .sec h2,#v .finale h2{width:fit-content;max-width:100%}
#v .sec h2::before,#v .finale h2::before{content:"";position:absolute;z-index:-1;top:0;bottom:0;left:-100vw;right:-1.1em;background:#141414;clip-path:polygon(0 0,100% 0,calc(100% - .7em) 100%,0 100%)}
#v .sec.tint h2::before{background:var(--R)}
#v .sec .lead{color:#3a3a3a}
#v .feature p:not(.eyebrow),#v .guide p:not(.who),#v .ticks li{color:#3a3a3a}
#v .pop,#v .card,#v .step{border:0;border-top:3px solid #141414;border-radius:0;box-shadow:none;background:transparent}
#v .card{padding-left:0;padding-right:0}
#v .card h3,#v .step h3{font-weight:900}
#v .card.phrase{padding-right:50px}#v .card.phrase h3{font-family:var(--disp);color:var(--R)}
#v .card.hot{background:var(--R);padding:20px}
#v .step,#v .step:nth-child(n){transform:none}
#v .step .n{border-radius:0;background:var(--R);border:0;box-shadow:none;transform:none;font-size:20px}
#v .step .body{border-top:0;padding-left:0;padding-right:0}
#v .review{position:relative;border:0;border-radius:0;box-shadow:none;background:transparent;padding:46px 0 0}
#v .review::before{content:"";position:absolute;left:0;top:0;width:36px;height:30px;background:var(--R);clip-path:polygon(0 40%,20% 0,40% 0,28% 40%,40% 40%,40% 100%,0 100%,60% 40%,80% 0,100% 0,88% 40%,100% 40%,100% 100%,60% 100%);clip-path:path('M0 30 V14 Q0 0 14 0 V7 Q7 7 7 14 H14 V30 Z M20 30 V14 Q20 0 34 0 V7 Q27 7 27 14 H34 V30 Z')}
#v .review p{font-family:var(--maru);font-weight:700;font-size:17px;line-height:1.7;color:#141414}
#v .review .stars{position:absolute;top:8px;left:50px;color:var(--R)}
#v .review figcaption{border-top:1px solid #141414;padding-top:10px;color:#555}
#v .review .src{background:none;color:var(--R);padding:0;font-weight:900}
#v .rev-grid{gap:36px 40px}
#v .rev-grid .review:first-child{grid-column:1/-1}
#v .rev-grid .review:first-child p{font:400 clamp(20px,3vw,30px)/1.35 var(--disp);letter-spacing:.01em}
#v .pf,#v .pf:nth-child(n){border-radius:0;border:0;border-top:4px solid #141414;box-shadow:none;transform:none;background:none;aspect-ratio:auto;width:min(200px,40vw);padding:14px 0 0;text-align:left;place-content:start}
#v .pf b{color:#141414;font-size:clamp(34px,6vw,52px)}#v .pf .k{color:var(--R);font-weight:900}
#v .fig,#v .feature.rev .fig,#v .face-wrap{transform:none}
#v .fig img,#v .face-wrap img,#v .banner img,#v .video-embed{border:0;border-radius:0;box-shadow:none}
#v .banner img{clip-path:polygon(0 0,100% 0,100% 86%,0 100%)}
#v .figcap{border-radius:0;background:#141414;color:#fff;border:0;box-shadow:none;left:0;bottom:-12px}
#v .ticks li::before{content:"";border-radius:0;background:var(--R);border:0;width:14px;height:3px;top:13px}
#v .chip{border-radius:0;border:1px solid #141414;box-shadow:none;background:none}
#v .bubble{border-radius:0;background:none;border:0;border-left:4px solid var(--R);box-shadow:none;padding:4px 0 4px 18px}
#v .bubble::before,#v .bubble::after{display:none}
#v .bubble p{font:400 clamp(20px,3vw,28px)/1.3 var(--disp)}
#v .face-wrap .seal{right:-10px}
#v .ig-grid a{border:0;border-radius:0;box-shadow:none}
#v .faq{gap:0}
#v .faq details{border:0;border-top:1px solid #141414;border-radius:0;box-shadow:none;background:none}
#v .faq details:last-child{border-bottom:1px solid #141414}
#v .faq summary{padding-left:0;font-size:16px}
#v .faq summary::after{border-radius:0;background:none;color:var(--R);border:0}
#v .faq details>p{border-top:0;padding-left:0}
#v .finale{background:#141414;border:0;overflow:clip}
#v .finale::before{display:none}
#v .finale .dz{background:var(--R);clip-path:polygon(0 0,100% 0,100% 30%,0 50%);z-index:0}
#v .finale h2{color:#141414;text-shadow:none;margin:0 auto;width:fit-content;max-width:100%}
#v .finale h2::before{background:#fbfaf7;left:-1.1em;right:-1.1em;clip-path:polygon(.7em 0,100% 0,calc(100% - .7em) 100%,0 100%)}
#v .booker{border-radius:0;border:0;box-shadow:none}
#v .bk-mount{border-radius:0;box-shadow:none;border:1px solid #141414}#v .bk-step button{border-radius:0}
#v .site-foot{background:#141414}#v .site-foot .h{color:#fff}
#v .adprice{background:var(--bg-2)}#v .ap-cell{border-radius:0}
""")

THEMES = [T1, T2, T3, T4, T5]
FONTS = '<link href="https://fonts.googleapis.com/css2?family=Anton&family=Noto+Sans+JP:wght@400;500;700;900&family=Zen+Kaku+Gothic+New:wght@700;900&display=swap" rel="stylesheet">'

if __name__ == '__main__':
    for t in THEMES:
        url = f'{BASE}{t["key"]}.html'
        meta = ('<meta name="robots" content="noindex,nofollow">'
                f'<meta property="og:type" content="website"><meta property="og:title" content="Akihabara tour rebrand {t["key"]} — {t["title"]}">'
                f'<meta property="og:image" content="{BASE}anime-logo-red.webp"><meta property="og:url" content="{url}">'
                '<meta name="twitter:card" content="summary_large_image">')
        h = head.replace('</head>', meta + FONTS + '<style>' + ASTRO + KIT + t['css'] + '</style></head>')
        b = body.replace('%HERODZ%', t['hero']).replace('%FINDZ%', t['fin']).replace('</body>', NAVI + JS + '</body>')
        (OUT / f'{t["key"]}.html').write_text(h + b)
        print('wrote', t['key'], len(h + b))
