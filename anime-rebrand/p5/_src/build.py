#!/usr/bin/env python3
"""P5文法 第2ラウンド g1〜g5 を生成する。
本文 = 第1ラウンドで照合済みの ../v2.html の <body>（herologo だけ差し替え）。
CSS  = 現行サイトの Astro CSS（_src/astro.css）＋ 共通キット ＋ 各案テーマ。
装飾要素は全部 aria-hidden（本文照合の対象外）。"""
import math, re, pathlib

P5 = pathlib.Path(__file__).resolve().parent.parent
SRC = (P5.parent / 'v2.html').read_text()
ASTRO = (P5 / '_src/astro.css').read_text()
BASE = 'https://yukitchy.github.io/booking-trends-board/anime-rebrand/p5/'


def star(n=16, inner=.78):
    pts = []
    for i in range(n * 2):
        r = 50 if i % 2 == 0 else 50 * inner
        a = math.pi * i / n - math.pi / 2
        pts.append(f'{50 + r * math.cos(a):.2f}% {50 + r * math.sin(a):.2f}%')
    return 'polygon(' + ','.join(pts) + ')'


KIT = """
:root{--maru:"Zen Kaku Gothic New","Noto Sans JP",sans-serif;--disp:"Anton","Zen Kaku Gothic New",sans-serif;--body:"Noto Sans JP","Hiragino Kaku Gothic ProN",sans-serif;--serif:"Noto Sans JP",sans-serif;
--star:%STAR%;--burst:%BURST%}
html,body{overflow-x:clip}
#v main .wrap>*,#v .hero-split>*{min-width:0}
#v main,#v .site-foot{overflow-x:clip}
#v .notes{--card:#fff;--bg:#fff;--bg-2:#f4f4f4;--line:#ddd;background:#fff}
#v .bk *{border-radius:0}
#v .proof div div{background:none}
#v .proof{border-radius:0}
#v h1,#v h2,#v h3,#v .btn,#v .eyebrow{font-family:var(--maru);font-weight:900}
#v .site-head .logo{display:block;line-height:0}
#v .site-head .logo img{height:46px;width:auto;display:block}
#v .btn,#v .btn-sm,#v .bk,#v .card,#v .qa,#v .bubble{border-radius:0}
#v .bk{--bg:#fff;--bg-2:#f3f3f3;--card:#fff;--line:#d9d9d9;--txt:#111;--sub:#555;color:#111}
#v .notes{--txt:#111;--sub:#555;color:#111}
.dz{position:absolute;inset:0;pointer-events:none;z-index:1}
.hlogo{display:block;width:min(340px,70%);height:auto;margin:0 0 14px}
@media (max-width:600px){#v .site-head .logo img{height:36px}}
.navi{position:fixed;right:max(14px,env(safe-area-inset-right));bottom:max(14px,env(safe-area-inset-bottom));z-index:60;display:flex;align-items:flex-end;gap:2px;transition:opacity .25s,transform .25s}
.navi.off{opacity:0;transform:translateY(12px);pointer-events:none}
.navi-b{display:block;max-width:190px;margin-bottom:34px;padding:9px 13px 10px;text-decoration:none;font:900 14px/1.35 var(--maru);background:var(--nb);color:var(--nt);border:var(--nbd);border-radius:var(--nr);box-shadow:var(--ns);position:relative;transform:var(--ntr,none)}
.navi-l{display:block}
.navi-k{display:block;font-size:12px;letter-spacing:.12em;color:var(--nk);margin-bottom:2px}
.navi-m{display:block;height:150px;width:auto;filter:var(--nf)}
.navi-x{position:absolute;top:-6px;right:-4px;width:26px;height:26px;border-radius:50%;border:0;background:var(--nxb);color:var(--nxt);font:700 15px/26px sans-serif;cursor:pointer;padding:0}
@media (max-width:600px){.navi{right:6px;bottom:6px}.navi-b{max-width:none;white-space:nowrap;margin-bottom:14px;padding:5px 9px;font-size:12px}.navi-k,.navi-l{display:none}.navi-m{height:72px}.navi-x{width:22px;height:22px;line-height:22px;font-size:13px}}
@media (prefers-reduced-motion:reduce){.navi{transition:none}}
""".replace('%STAR%', star(5, .45)).replace('%BURST%', star(18, .8))

# ---------------------------------------------------------------- g1
G1 = dict(title='赤基調・斜め全開', deco='<i class="dz" aria-hidden="true"></i><img class="hlogo" src="logo-cut.webp" alt="" aria-hidden="true" width="627" height="296">', css="""
#v{--bg:#e0121a;--bg-2:#0c0c0c;--txt:#fff;--sub:#fff;--ac:#0c0c0c;--ac-deep:#0c0c0c;--ac-tint:rgba(0,0,0,.25);--line:#0c0c0c;--card:#fff;background:#e0121a;color:#fff;
--nb:#fff;--nt:#0c0c0c;--nbd:3px solid #0c0c0c;--nr:0;--ns:5px 5px 0 #0c0c0c;--nk:#e0121a;--nf:drop-shadow(4px 4px 0 #0c0c0c);--nxb:#0c0c0c;--nxt:#fff;--ntr:rotate(-6deg)}
#v .site-head{background:#0c0c0c;backdrop-filter:none;border-bottom:5px solid #fff}
#v .site-head nav a{font-family:var(--disp);font-weight:400;letter-spacing:.06em;text-transform:uppercase;font-size:15px;color:#fff}
#v .site-head nav a[aria-current]{background:#e0121a;color:#fff;transform:skewX(-6deg)}
#v .site-head .btn-sm{background:#fff;color:#e0121a;transform:skewX(-6deg);box-shadow:4px 4px 0 #e0121a}
#v .hero{clip-path:polygon(0 0,100% 0,100% calc(100% - 10.5vw),0 100%);padding-bottom:calc(64px + 10.5vw)}
#v .hero.photo:after{background:#e0121a;mix-blend-mode:multiply;opacity:.93}
#v .hero:before{background-image:radial-gradient(circle,#000 1.5px,transparent 1.7px);background-size:9px 9px;opacity:.55;mask-image:linear-gradient(174deg,transparent 0 55%,#000 56%)}
#v .hero .dz{background:#0c0c0c;clip-path:polygon(0 0,46% 0,30% 100%,0 100%);opacity:.9}
#v .hero .eyebrow{display:inline-block;background:#fff;color:#0c0c0c;padding:5px 12px;transform:rotate(-6deg);letter-spacing:.06em;box-shadow:5px 5px 0 #0c0c0c}
#v .hero h1{color:#fff;font-size:clamp(30px,6.8vw,58px);line-height:1.18;text-shadow:4px 4px 0 #0c0c0c}
#v .hero h1 em{display:inline-block;background:#fff;color:#e0121a;padding:0 .18em;transform:rotate(-6deg);text-shadow:none;box-shadow:6px 6px 0 #0c0c0c}
#v .hero .lead{color:#fff;font-weight:700}
#v .btn{background:#0c0c0c;color:#fff;border:3px solid #fff;transform:skewX(-6deg);box-shadow:6px 6px 0 #fff;font-size:17px}
#v .btn:hover{background:#fff;color:#e0121a}
#v .btn.ghost{background:#fff;color:#0c0c0c;border-color:#0c0c0c;box-shadow:6px 6px 0 #0c0c0c}
#v .m-cta p{color:#fff}
#v .hero-list a{color:#fff;border-bottom-color:#fff;font-family:var(--maru);font-weight:900}
#v .bk{border:4px solid #0c0c0c;box-shadow:12px 12px 0 #0c0c0c;transform:rotate(-1.5deg)}
#v .bk .btn{border-color:#0c0c0c;box-shadow:5px 5px 0 #e0121a;transform:none}
#v .bk .lbl{background:#e0121a;color:#fff;transform:skewX(-6deg)}
#v .proof{background:#0c0c0c;border:0;padding:18px 10px;margin-top:40px;box-shadow:8px 8px 0 #fff}
#v .proof>div{background:#0c0c0c}
#v .proof .stat-v{font-family:var(--disp);font-weight:400;color:#fff;font-size:clamp(26px,4vw,38px);letter-spacing:.02em}
#v .proof .stat-k{color:#e0121a;font-weight:900}
#v .sec{background:#e0121a;color:#fff}
#v .sec.tint{background:#0c0c0c;clip-path:polygon(0 10.5vw,100% 0,100% calc(100% - 10.5vw),0 100%);padding:calc(10.5vw + 40px) 0}
#v .sec h2{display:block;width:fit-content;max-width:100%;background:#fff;color:#0c0c0c;padding:.06em .45em;transform:rotate(-6deg);box-shadow:8px 8px 0 #0c0c0c;margin-bottom:22px}
#v .sec.tint h2{background:#e0121a;color:#fff;box-shadow:8px 8px 0 #fff}
#v .sec .lead,#v .sec p{color:inherit}
#v .sec .eyebrow{color:#0c0c0c;background:#fff;display:inline-block;padding:2px 10px;transform:skewX(-6deg)}
#v .sec.tint .eyebrow{background:#e0121a;color:#fff}
#v .card{background:#fff;color:#0c0c0c;border:4px solid #0c0c0c;box-shadow:8px 8px 0 #0c0c0c}
#v .sec.tint .card{box-shadow:8px 8px 0 #e0121a}
#v .card h3{color:#e0121a}
#v .card p{color:#222}
#v .notes{border:4px solid #0c0c0c;box-shadow:12px 12px 0 #0c0c0c;border-radius:0}
#v .shelfbook{border:3px solid #fff;box-shadow:6px 6px 0 #e0121a;border-radius:0}
#v .shelflv{background:#e0121a;color:#fff;transform:skewX(-6deg);border-radius:0}
#v .bubble{background:#fff;color:#0c0c0c;border:3px solid #0c0c0c;box-shadow:6px 6px 0 #0c0c0c}
#v .bubble p,#v .bubble .who{color:#222}
#v .stars{color:#e0121a}
#v .teacher .face{clip-path:polygon(10.5% 0,100% 0,89.5% 100%,0 100%);border-radius:0}
#v .teacher .who{color:#fff;font-weight:900}
#v .facts span{background:#e0121a;color:#fff;border:0;border-radius:0;transform:skewX(-6deg);font-weight:900}
#v .qa{background:#fff;color:#0c0c0c;border:3px solid #fff;box-shadow:6px 6px 0 #e0121a}
#v .qa summary{font-weight:900}
#v .qa[open] summary{background:#0c0c0c;color:#fff}
#v .qa p{color:#222}
#v .tour-band .btn.ghost{box-shadow:6px 6px 0 #fff}
#v .bkbar{background:#0c0c0c;color:#fff}
#v .bkbar .go{background:#e0121a;color:#fff;border-radius:0;transform:skewX(-6deg)}
#v .site-foot{background:#0c0c0c;color:#fff;border-top:6px solid #fff}
#v .site-foot a,#v .site-foot .h{color:#fff}
""")

# ---------------------------------------------------------------- g2
G2 = dict(title='黒基調・メニュー画面風', deco='<i class="dz" aria-hidden="true"><b></b><b></b></i>', css="""
#v{--bg:#0a0a0a;--bg-2:#151515;--txt:#f4f4f4;--sub:#c4c4c4;--ac:#e60012;--ac-deep:#ff3340;--ac-tint:rgba(230,0,18,.22);--line:#2c2c2c;--card:#151515;background:#0a0a0a;color:#f4f4f4;
--nb:#0a0a0a;--nt:#fff;--nbd:3px solid #fff;--nr:0;--ns:-5px 5px 0 #e60012;--nk:#e60012;--nf:drop-shadow(0 0 0 #000);--nxb:#e60012;--nxt:#fff;--ntr:skewX(-7deg)}
#v .site-head{background:#0a0a0a;backdrop-filter:none;border-bottom:3px solid #e60012}
#v .site-head nav a{font-family:var(--disp);font-weight:400;letter-spacing:.08em;text-transform:uppercase;font-size:16px;color:#fff;transform:skewX(-7deg)}
#v .site-head nav a:hover,#v .site-head nav a[aria-current]{background:#fff;color:#0a0a0a}
#v .site-head .btn-sm{background:#e60012;color:#fff}
#v .hero.photo:after{background:linear-gradient(100deg,rgba(10,10,10,.97) 0 48%,rgba(10,10,10,.82) 70%,rgba(10,10,10,.9))}
#v .hero:before{background-image:radial-gradient(circle,#e60012 1.4px,transparent 1.6px);background-size:10px 10px;opacity:.7;mask-image:linear-gradient(97deg,transparent 0 58%,#000 75%)}
#v .hero .dz b{position:absolute;display:block;background:#e60012;transform:skewX(-7deg)}
#v .hero .dz b:first-child{left:-5%;top:0;bottom:0;width:11%;opacity:.95}
#v .hero .dz b:last-child{left:7.5%;top:0;bottom:0;width:1.4%;background:#fff;opacity:.9}
@media (max-width:1100px){#v .hero .dz{display:none}}
#v .hero .eyebrow{color:#fff;font-family:var(--disp);font-weight:400;letter-spacing:.08em;position:relative;padding-left:22px}
#v .hero .eyebrow:before,#v .sec .eyebrow:before{content:"";position:absolute;left:0;top:50%;width:14px;height:16px;margin-top:-8px;background:#e60012;clip-path:polygon(0 0,100% 50%,0 100%)}
#v .hero h1{color:#fff;font-size:clamp(30px,6.6vw,56px);line-height:1.2}
#v .hero h1 em{display:inline-block;background:#fff;color:#0a0a0a;padding:0 .22em;transform:skewX(-7deg);box-shadow:-6px 6px 0 #e60012}
#v .hero .lead{color:#d6d6d6}
#v .btn{background:#e60012;color:#fff;border:0;transform:skewX(-7deg);box-shadow:-6px 6px 0 #fff;font-size:17px}
#v .btn:hover{background:#fff;color:#0a0a0a;box-shadow:-6px 6px 0 #e60012}
#v .btn.ghost{background:#0a0a0a;color:#fff;border:3px solid #fff}
#v .m-cta p{color:#c4c4c4}
#v .hero-list a{color:#fff;border-bottom-color:#e60012}
#v .bk{border:3px solid #fff;box-shadow:-12px 12px 0 #e60012;outline:3px solid #0a0a0a}
#v .bk .btn{box-shadow:-5px 5px 0 #0a0a0a;transform:none}
#v .bk .lbl{background:#0a0a0a;color:#fff}
#v .proof{border:0;gap:8px;background:none}
#v .proof>div{background:#151515;border-left:6px solid #e60012;transform:skewX(-7deg);padding:12px 16px}
#v .proof .stat-v{font-family:var(--disp);font-weight:400;color:#fff;font-size:clamp(24px,3.8vw,36px)}
#v .proof .stat-k{color:#e60012;font-weight:900;letter-spacing:.08em}
#v .sec{background:#0a0a0a}
#v .sec.tint{background:#151515;background-image:repeating-linear-gradient(-83deg,transparent 0 46px,rgba(255,255,255,.035) 46px 48px)}
#v .sec h2{position:relative;display:block;width:fit-content;max-width:100%;font-family:var(--disp);font-weight:400;text-transform:uppercase;letter-spacing:.04em;font-size:clamp(28px,5vw,48px);line-height:1.1;color:#0a0a0a;background:#fff;padding:.08em .4em .08em 1.15em;transform:rotate(-7deg) skewX(-7deg);transform-origin:left bottom;box-shadow:-8px 8px 0 #e60012;margin:18px 0 26px}
#v .sec h2:before{content:"";position:absolute;left:.3em;top:50%;width:.5em;height:.6em;margin-top:-.3em;background:#e60012;clip-path:polygon(0 0,100% 50%,0 100%)}
#v .sec .eyebrow{position:relative;padding-left:22px;color:#e60012;font-family:var(--disp);font-weight:400;letter-spacing:.1em}
#v .sec .lead,#v .sec p{color:#d0d0d0}
#v .grid.g3{grid-template-columns:1fr;gap:14px}
#v .card{position:relative;isolation:isolate;background:none;border:0;box-shadow:none;padding:18px 24px 18px 52px}
#v .card:before{content:"";position:absolute;inset:0;z-index:-1;background:#1d1d1d;border-left:6px solid #e60012;transform:skewX(-7deg)}
#v .card:nth-child(2){margin-left:4%}#v .card:nth-child(3){margin-left:8%}
#v .card:first-child:before,#v .card:hover:before{background:#fff}
#v .card:first-child h3,#v .card:first-child p,#v .card:hover h3,#v .card:hover p{color:#0a0a0a}
#v .card:first-child:after,#v .card:hover:after{content:"";position:absolute;left:14px;top:24px;width:18px;height:22px;background:#e60012;clip-path:polygon(0 0,100% 50%,0 100%)}
#v .card .ico{position:absolute;right:20px;top:14px;font-size:26px;margin:0}
#v .card h3{color:#fff;font-size:22px}
#v .card p{color:#cfcfcf;margin:6px 0 0}
#v .notes{border:3px solid #fff;box-shadow:-12px 12px 0 #e60012;border-radius:0}
#v .shelfbook{border:3px solid #fff;border-radius:0;transform:skewX(-7deg);box-shadow:-6px 6px 0 #e60012}
#v .shelflv{background:#e60012;color:#fff;border-radius:0}
#v .bubble{position:relative;isolation:isolate;background:none;border:0;box-shadow:none;color:#f4f4f4}
#v .bubble:before{content:"";position:absolute;inset:0;z-index:-1;background:#1d1d1d;border-left:6px solid #e60012;transform:skewX(-7deg)}
#v .bubble p{color:#e6e6e6}#v .bubble .who{color:#9a9a9a}
#v .stars{color:#e60012}
#v .rv .av{filter:grayscale(1) contrast(1.2)}
#v .teacher .face{border-radius:0;clip-path:polygon(12.3% 0,100% 0,87.7% 100%,0 100%)}
#v .teacher .who{color:#fff;font-family:var(--disp);font-weight:400;letter-spacing:.08em;text-transform:uppercase}
#v .facts span{background:#0a0a0a;color:#fff;border:2px solid #fff;border-radius:0;transform:skewX(-7deg)}
#v .qa{position:relative;isolation:isolate;background:none;border:0;margin:10px 0}
#v .qa:before{content:"";position:absolute;inset:0;z-index:-1;background:#1d1d1d;transform:skewX(-7deg)}
#v .qa summary{color:#fff;font-weight:900;padding-left:34px;position:relative}
#v .qa[open]:before{background:#fff}#v .qa[open] summary,#v .qa[open] p{color:#0a0a0a}
#v .qa[open] summary:before{content:"";position:absolute;left:10px;top:50%;width:14px;height:16px;margin-top:-8px;background:#e60012;clip-path:polygon(0 0,100% 50%,0 100%)}
#v .bkbar{background:#0a0a0a;color:#fff;border-top:3px solid #e60012}
#v .bkbar .go{background:#e60012;color:#fff;border-radius:0;transform:skewX(-7deg)}
#v .site-foot{background:#000;color:#ddd;border-top:3px solid #e60012}
#v .site-foot a{color:#fff}#v .site-foot .h{color:#e60012;font-family:var(--disp);font-weight:400;letter-spacing:.1em}
""")

# ---------------------------------------------------------------- g3
G3 = dict(title='白＋ハーフトーン漫画風', deco='<i class="dz" aria-hidden="true"></i><img class="hlogo" src="logo-cut.webp" alt="" aria-hidden="true" width="627" height="296">', css="""
#v{--bg:#fff;--bg-2:#fff;--txt:#111;--sub:#333;--ac:#e1121b;--ac-deep:#b50c13;--ac-tint:#ffdfe0;--line:#111;--card:#fff;background:#fff;color:#111;
--dots:radial-gradient(circle,#111 1.1px,transparent 1.3px);
--nb:#fff;--nt:#111;--nbd:3px solid #111;--nr:22px;--ns:4px 4px 0 #111;--nk:#e1121b;--nf:none;--nxb:#111;--nxt:#fff}
.navi-b:after{content:"";position:absolute;right:-13px;bottom:14px;width:16px;height:14px;background:#111;clip-path:polygon(0 0,100% 60%,0 100%)}
#v .site-head{background:#fff;backdrop-filter:none;color:#111;border-bottom:4px solid #111}
#v .site-head nav a{color:#111;font-weight:900;font-family:var(--maru)}
#v .site-head nav a[aria-current]{background:#111;color:#fff}
#v .site-head .btn-sm{background:#e1121b;color:#fff;border:3px solid #111;box-shadow:3px 3px 0 #111}
#v .hero{border-bottom:4px solid #111}
#v .hero.photo:after{background:linear-gradient(rgba(255,255,255,.35),rgba(255,255,255,.55))}
#v .hero:before{background-image:var(--dots);background-size:7px 7px;opacity:.5;mask-image:none}
#v .hero .dz{background:#e1121b;clip-path:polygon(64% 0,100% 0,100% 100%,52% 100%);opacity:.9;mix-blend-mode:multiply}
#v .hero-split>div:first-child{background:#fff;border:4px solid #111;padding:26px 26px 22px;box-shadow:10px 10px 0 #111}
#v .hero .eyebrow{display:inline-block;position:relative;background:#fff;border:3px solid #111;border-radius:20px;padding:4px 14px;color:#111}
#v .hero .eyebrow:after{content:"";position:absolute;left:26px;bottom:-12px;width:16px;height:12px;background:#111;clip-path:polygon(0 0,100% 0,0 100%)}
#v .hero h1{color:#111;font-size:clamp(28px,6vw,52px);line-height:1.22}
#v .hero h1 em{color:#e1121b;display:inline-block;transform:rotate(-3deg);text-shadow:3px 3px 0 #111}
#v .hero .lead{color:#222}
#v .btn{background:#e1121b;color:#fff;border:3px solid #111;box-shadow:5px 5px 0 #111;font-size:17px}
#v .btn:hover{transform:translate(-2px,-2px);box-shadow:7px 7px 0 #111}
#v .btn.ghost{background:#fff;color:#111}
#v .hero-list a{color:#111;border-bottom:3px solid #e1121b}
#v .bk{border:4px solid #111;box-shadow:10px 10px 0 #111}
#v .bk .btn{box-shadow:4px 4px 0 #111}
#v .bk .lbl{background:#111;color:#fff}
#v .proof{background:#fff;border:4px solid #111;box-shadow:8px 8px 0 #e1121b}
#v .proof>div+div{border-left:3px solid #111}
#v .proof .stat-v{font-family:var(--disp);font-weight:400;color:#e1121b;font-size:clamp(26px,4vw,38px)}
#v .proof .stat-k{color:#111;font-weight:900}
#v .sec{background:#fff;border-bottom:4px solid #111}
#v .sec.tint{background:#fff radial-gradient(circle,rgba(0,0,0,.16) 1.2px,transparent 1.4px) 0 0/8px 8px}
#v .sec h2{position:relative;display:block;width:fit-content;max-width:100%;color:#111;background:#fff;border:4px solid #111;padding:.06em .45em;transform:rotate(-3deg);box-shadow:8px 8px 0 #e1121b;margin:10px 0 24px}
#v .sec .eyebrow{color:#e1121b;font-weight:900}
#v .sec .lead{color:#222}
#v .card{background:#fff;border:4px solid #111;box-shadow:none;position:relative}
#v .card:after{content:"";position:absolute;right:-4px;bottom:-4px;width:46%;height:42%;background:var(--dots) 0 0/6px 6px;opacity:.35;pointer-events:none;clip-path:polygon(100% 0,100% 100%,0 100%)}
#v .card .ico{display:inline-grid;place-items:center;width:58px;height:58px;background:#fff;border:3px solid #111;border-radius:50%}
#v .card h3{color:#111}
#v .card h3:first-letter{color:#e1121b}
#v .notes{border:4px solid #111;box-shadow:10px 10px 0 #111;border-radius:0}
#v .shelfbook{border:3px solid #111;border-radius:0;box-shadow:5px 5px 0 #111}
#v .shelflv{background:#fff;color:#111;border:3px solid #111;border-radius:50%}
#v .bubble{background:#fff;border:3px solid #111;border-radius:26px;box-shadow:none;position:relative}
#v .bubble:before{content:"";position:absolute;left:-17px;top:22px;width:18px;height:16px;background:#111;clip-path:polygon(100% 0,0 50%,100% 100%)}
#v .bubble:after{content:"";position:absolute;left:-10px;top:25px;width:12px;height:10px;background:#fff;clip-path:polygon(100% 0,0 50%,100% 100%)}
#v .stars{color:#e1121b}
#v .rv .av{border:3px solid #111;border-radius:50%;background:#fff}
#v .teacher .face{border:4px solid #111;border-radius:0;box-shadow:10px 10px 0 #111;transform:rotate(-3deg)}
#v .teacher .who{font-weight:900}
#v .facts span{background:#fff;border:3px solid #111;border-radius:999px;color:#111;font-weight:900}
#v .qa{background:#fff;border:3px solid #111;box-shadow:5px 5px 0 #111;margin:12px 0}
#v .qa summary{font-weight:900}
#v .qa[open]{box-shadow:5px 5px 0 #e1121b}
#v .narrow[style*="center"]{position:relative;padding:96px 72px}
@media (max-width:600px){#v .narrow[style*="center"]{padding:84px 34px}}
#v .narrow[style*="center"]:before{content:"";position:absolute;inset:0;z-index:-1;background:#111;clip-path:var(--burst)}
#v .narrow[style*="center"]:after{content:"";position:absolute;inset:6px;z-index:-1;background:#fff;clip-path:var(--burst)}
#v .narrow[style*="center"]{isolation:isolate}
#v .bkbar{background:#fff;color:#111;border-top:4px solid #111}
#v .bkbar .go{background:#e1121b;color:#fff;border:3px solid #111;border-radius:0}
#v .site-foot{background:#111;color:#eee}
#v .site-foot a{color:#fff}#v .site-foot .h{color:#ff5a60}
""")

# ---------------------------------------------------------------- g4
G4 = dict(title='バーストと星のポップ全開', deco='<i class="dz" aria-hidden="true"><b></b><b></b><b></b></i><img class="hlogo" src="logo-cut.webp" alt="" aria-hidden="true" width="627" height="296">', css="""
#v{--bg:#fff;--bg-2:#0b0b0b;--txt:#0b0b0b;--sub:#333;--ac:#e5121b;--ac-deep:#b80d14;--ac-tint:#ffe0e1;--line:#0b0b0b;--card:#fff;background:#fff;color:#0b0b0b;
--nb:#e5121b;--nt:#fff;--nbd:3px solid #0b0b0b;--nr:0;--ns:4px 4px 0 #0b0b0b;--nk:#fff;--nf:drop-shadow(3px 3px 0 #0b0b0b);--nxb:#0b0b0b;--nxt:#fff;--ntr:rotate(-8deg)}
#v .site-head{background:#0b0b0b;backdrop-filter:none;border-bottom:4px solid #e5121b}
#v .site-head nav a{color:#fff;font-family:var(--disp);font-weight:400;letter-spacing:.06em;text-transform:uppercase;font-size:15px}
#v .site-head nav a[aria-current]{color:#e5121b}
#v .site-head .btn-sm{background:#e5121b;color:#fff;transform:rotate(-8deg)}
#v .hero.photo:after{background:repeating-conic-gradient(from 0deg at 72% 38%,#e5121b 0 7.5deg,#ff4048 7.5deg 15deg);mix-blend-mode:multiply;opacity:.95}
#v .hero:before{background-image:radial-gradient(circle,#0b0b0b 1.6px,transparent 1.8px);background-size:10px 10px;opacity:.5;mask-image:radial-gradient(60% 60% at 72% 38%,transparent 40%,#000 100%)}
#v .hero .dz b{position:absolute;display:block;clip-path:var(--star);background:#fff}
#v .hero .dz b:nth-child(1){width:90px;height:90px;left:3%;top:14%;transform:rotate(-8deg)}
#v .hero .dz b:nth-child(2){width:46px;height:46px;left:44%;top:6%;background:#0b0b0b;transform:rotate(-8deg)}
#v .hero .dz b:nth-child(3){width:64px;height:64px;left:40%;bottom:20%;transform:rotate(-8deg)}
#v .hero .eyebrow{display:inline-block;background:#0b0b0b;color:#fff;padding:5px 14px;transform:rotate(-8deg);letter-spacing:.05em}
#v .hero h1{color:#fff;font-size:clamp(30px,6.8vw,58px);line-height:1.18;text-shadow:4px 4px 0 #0b0b0b}
#v .hero h1 em{color:#0b0b0b;text-shadow:3px 3px 0 #fff}
#v .hero .lead{color:#fff;font-weight:700;text-shadow:0 2px 0 rgba(0,0,0,.35)}
#v .btn{position:relative;background:#0b0b0b;color:#fff;border:3px solid #fff;box-shadow:5px 5px 0 #e5121b;font-size:17px}
#v .btn:hover{background:#e5121b}
#v .btn.ghost{background:#fff;color:#0b0b0b;border-color:#0b0b0b;box-shadow:5px 5px 0 #0b0b0b}
#v .m-cta p{color:#fff}
#v .hero-list a{color:#fff;border-bottom-color:#fff}
#v .bk{border:4px solid #0b0b0b;box-shadow:10px 10px 0 #0b0b0b}
#v .bk .btn{box-shadow:4px 4px 0 #e5121b}
#v .bk .lbl{background:#e5121b;color:#fff}
#v .bk-price .big{display:inline-grid;place-items:center;width:104px;height:104px;background:#e5121b;color:#fff;clip-path:var(--burst);font-family:var(--disp);font-weight:400;transform:rotate(-8deg)}
#v .bk-price .big:empty{display:none}
#v .proof{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;background:none;border:0;box-shadow:none;margin-top:34px}
#v .proof>div{aspect-ratio:1;display:grid;place-content:center;text-align:center;background:#fff;clip-path:var(--burst);padding:12%;border:0;transform:rotate(-8deg)}
#v .proof>div:nth-child(even){background:#0b0b0b;transform:rotate(8deg)}
#v .proof>div:nth-child(even) .stat-v{color:#fff}
#v .proof .stat-v{font-family:var(--disp);font-weight:400;color:#e5121b;font-size:clamp(24px,4vw,40px);line-height:1}
#v .proof .stat-k{font-weight:900;font-size:12px;line-height:1.25;color:#e5121b;overflow-wrap:normal;word-break:normal}
#v .sec{background:repeating-conic-gradient(from 0deg at 50% 0,#fff 0 5deg,#f1f1f1 5deg 10deg)}
#v .sec.tint{background:repeating-conic-gradient(from 0deg at 50% 0,#0b0b0b 0 5deg,#191919 5deg 10deg);color:#fff}
#v .sec.tint .lead,#v .sec.tint p,#v .sec.tint .eyebrow{color:#eee}
#v .sec h2{position:relative;display:block;width:fit-content;max-width:100%;font-family:var(--disp);font-weight:400;text-transform:uppercase;letter-spacing:.03em;font-size:clamp(28px,5vw,50px);line-height:1.1;color:#0b0b0b;padding-left:1.25em;margin-bottom:18px}
#v .sec h2:before{content:"";position:absolute;left:0;top:50%;width:1em;height:1em;margin-top:-.55em;background:#e5121b;clip-path:var(--star);transform:rotate(-8deg)}
#v .sec.tint h2{color:#fff}
#v .sec .eyebrow{display:inline-block;background:#e5121b;color:#fff !important;padding:2px 12px;transform:rotate(-8deg)}
#v .card{background:#fff;color:#0b0b0b;border:4px solid #0b0b0b;box-shadow:8px 8px 0 #e5121b;position:relative;padding-top:56px}
#v .card .ico{position:absolute;left:18px;top:-30px;display:grid;place-items:center;width:76px;height:76px;background:#e5121b;clip-path:var(--burst);font-size:30px;margin:0}
#v .card h3{color:#0b0b0b}
#v .card p{color:#333 !important}
#v .grid.g3{margin-top:44px}
#v .notes{border:4px solid #0b0b0b;box-shadow:10px 10px 0 #e5121b;border-radius:0}
#v .shelfbook{border:3px solid #fff;border-radius:0;box-shadow:6px 6px 0 #e5121b;overflow:visible}
#v .shelflv{display:grid;place-items:center;width:52px;height:52px;padding:0;background:#e5121b;color:#fff;clip-path:var(--burst);border-radius:0;font-family:var(--disp);font-weight:400;font-size:18px;transform:rotate(-8deg)}
#v .bubble{background:#fff;border:3px solid #0b0b0b;box-shadow:6px 6px 0 #0b0b0b;position:relative}
#v .bubble:before{content:"";position:absolute;left:-16px;top:20px;width:16px;height:16px;background:#0b0b0b;clip-path:polygon(100% 0,0 50%,100% 100%)}
#v .stars{color:#e5121b}
#v .teacher>div:first-child{position:relative;isolation:isolate}
#v .teacher>div:first-child:before{content:"";position:absolute;left:-6%;top:-6%;width:112%;aspect-ratio:1;z-index:-1;background:#e5121b;clip-path:var(--burst);transform:rotate(-8deg)}
#v .teacher .face{border-radius:50%;border:5px solid #0b0b0b}
#v .teacher .who{color:#fff;font-weight:900}
#v .facts{gap:16px 12px}#v .facts span{background:#0b0b0b;color:#fff;border:0;border-radius:0;transform:rotate(-8deg);font-weight:900}
#v .facts span:nth-child(odd){background:#e5121b}
#v .qa{background:#fff;color:#0b0b0b;border:3px solid #0b0b0b;box-shadow:5px 5px 0 #e5121b}
#v .qa p{color:#333 !important}
#v .qa summary{font-weight:900}
#v .narrow[style*="center"] .btn{font-size:19px;padding:18px 30px}
#v .bkbar{background:#0b0b0b;color:#fff}
#v .bkbar .go{background:#e5121b;color:#fff;border-radius:0;transform:rotate(-8deg)}
#v .site-foot{background:#0b0b0b;color:#ddd;border-top:6px solid #e5121b}
#v .site-foot a{color:#fff}#v .site-foot .h{color:#e5121b}
@media (max-width:820px){#v .proof{grid-template-columns:repeat(2,minmax(0,150px));justify-content:center}#v .hero .dz{display:none}#v .teacher>div:first-child:before{width:300px;left:calc(50% - 150px);top:-24px}}
""")

# ---------------------------------------------------------------- g5
G5 = dict(title='斜め帯と引用の編集系', deco='<i class="dz" aria-hidden="true"></i>', css="""
#v{--bg:#fff;--bg-2:#f4f3f1;--txt:#141414;--sub:#4a4a4a;--ac:#d7141c;--ac-deep:#a90f15;--ac-tint:#fbe3e4;--line:#141414;--card:#fff;background:#fff;color:#141414;
--nb:#fff;--nt:#141414;--nbd:2px solid #141414;--nr:0;--ns:none;--nk:#d7141c;--nf:none;--nxb:#141414;--nxt:#fff}
.navi-b{border-top:6px solid #d7141c}
#v .site-head{background:#fff;backdrop-filter:none;color:#141414;border-bottom:2px solid #141414}
#v .site-head nav a{color:#141414;font-weight:700;letter-spacing:.04em}
#v .site-head nav a[aria-current]{box-shadow:inset 0 -4px 0 #d7141c}
#v .site-head .btn-sm{background:#141414;color:#fff}
#v .hero.photo:after{background:linear-gradient(94deg,#fff 0 50%,rgba(255,255,255,.12) 50.1%)}
#v .hero:before{background-image:radial-gradient(circle,#d7141c 1.2px,transparent 1.4px);background-size:8px 8px;opacity:.55;mask-image:linear-gradient(94deg,transparent 0 50%,#000 50.1%)}
#v .hero .dz{background:#d7141c;clip-path:polygon(0 calc(100% - 7vw - 14px),100% calc(100% - 14px),100% 100%,0 calc(100% - 7vw + 0px))}
#v .hero{padding-bottom:calc(58px + 7vw)}
#v .hero .eyebrow{color:#d7141c;font-weight:900;letter-spacing:.14em;border-top:2px solid #141414;padding-top:10px;display:inline-block}
#v .hero h1{font-size:clamp(30px,6.2vw,56px);line-height:1.2;color:#141414}
#v .hero h1 em{display:inline-block;background:#d7141c;color:#fff;padding:0 .2em;transform:rotate(-4deg)}
#v .hero .lead{color:#333}
#v .btn{background:#d7141c;color:#fff;border:0;box-shadow:none;font-size:17px;letter-spacing:.02em}
#v .btn:hover{background:#141414}
#v .btn.ghost{background:#fff;color:#141414;border:2px solid #141414}
#v .hero-list a{color:#141414;border-bottom:2px solid #d7141c}
#v .bk{border:2px solid #141414;box-shadow:none;border-top:8px solid #d7141c}
#v .bk .lbl{background:#141414;color:#fff}
#v .proof{background:none;border:0;border-top:2px solid #141414;border-bottom:2px solid #141414;box-shadow:none;border-radius:0}
#v .proof>div+div{border-left:1px solid #141414}
#v .proof .stat-v{font-family:var(--disp);font-weight:400;font-size:clamp(28px,4.2vw,44px);color:#141414}
#v .proof .stat-k{color:#d7141c;font-weight:900;letter-spacing:.12em}
#v .sec{background:#fff}
#v .sec.tint{background:#f4f3f1}
#v .sec h2{position:relative;display:block;width:fit-content;max-width:100%;color:#fff;background:#d7141c;padding:.08em .5em .08em 0;transform:rotate(-4deg);transform-origin:left center;margin:14px 0 26px}
#v .sec h2:before{content:"";position:absolute;right:100%;top:0;bottom:0;width:100vw;background:#d7141c}
#v .sec .eyebrow{color:#141414;font-weight:900;letter-spacing:.16em;border-bottom:2px solid #141414;display:inline-block;padding-bottom:4px}
#v .sec .lead{color:#333}
#v .grid.g3{gap:0;border-top:2px solid #141414}
#v .card{background:none;border:0;box-shadow:none;border-radius:0;padding:20px 22px 8px 0}
#v .card+.card{border-left:1px solid #141414;padding-left:22px}
#v .card .ico{font-size:24px}
#v .card h3{font-size:20px;color:#141414}
#v .card h3:after{content:"";display:block;width:36px;height:4px;background:#d7141c;margin-top:8px}
#v .notes{border:2px solid #141414;box-shadow:none;border-radius:0}
#v .shelfbook{border-radius:0;box-shadow:none;border:1px solid #141414}
#v .shelflv{background:#141414;color:#fff;border-radius:0}
#v .reviews{gap:0 48px}
#v .rv{border-top:2px solid #141414;padding-top:14px}
#v .rv .av{display:none}
#v .bubble{background:none;border:0;box-shadow:none;padding:0;position:relative}
#v .bubble:before{content:"\\201C";display:block;font-family:var(--disp);color:#d7141c;font-size:72px;line-height:1;height:40px;overflow:hidden}
#v .bubble p{margin-top:14px;font-family:var(--maru);font-weight:700;font-size:19px;line-height:1.75;color:#141414}
#v .bubble .who{color:#d7141c;font-weight:900;letter-spacing:.06em}
#v .stars{color:#141414;letter-spacing:.2em;font-size:13px}
#v .teacher .face{border-radius:0;clip-path:polygon(0 0,100% 0,100% 93%,0 100%)}
#v .teacher .who{font-weight:900;border-top:2px solid #141414;padding-top:6px}
#v .facts span{background:none;border:0;border-left:4px solid #d7141c;border-radius:0;padding:2px 10px;font-weight:700}
#v .qa{background:none;border:0;border-bottom:1px solid #141414;border-radius:0;box-shadow:none}
#v .qa summary{font-weight:900}
#v .narrow[style*="center"]{position:relative;isolation:isolate;padding:64px 22px}
#v .narrow[style*="center"]:before{content:"";position:absolute;left:-50vw;right:-50vw;top:0;bottom:0;z-index:-1;background:#141414;transform:skewY(-4deg)}
#v .narrow[style*="center"] h2{margin-left:auto;margin-right:auto}
#v .narrow[style*="center"] .lead{color:#fff}
#v .bkbar{background:#fff;color:#141414;border-top:2px solid #141414}
#v .bkbar .go{background:#d7141c;color:#fff;border-radius:0}
#v .site-foot{background:#141414;color:#ddd}
#v .site-foot a{color:#fff}#v .site-foot .h{color:#ff5a60;letter-spacing:.14em}
@media (max-width:820px){#v .hero.photo:after{background:linear-gradient(rgba(255,255,255,.93),rgba(255,255,255,.97))}#v .hero:before{mask-image:linear-gradient(transparent 0 70%,#000)}#v .card+.card{border-left:0;padding-left:0;border-top:1px solid #141414}#v .reviews{gap:8px}}
""")

THEMES = [G1, G2, G3, G4, G5]
FONTS = '<link href="https://fonts.googleapis.com/css2?family=Anton&family=Noto+Sans+JP:wght@400;700;900&family=Zen+Kaku+Gothic+New:wght@700;900&display=swap" rel="stylesheet">'

i = SRC.find('<body')
head, body = SRC[:i], SRC[i:]
head = re.sub(r'<style[^>]*>.*?</style>', '', head, flags=re.S)
head = re.sub(r'<link href="https://fonts.googleapis.com/css2[^>]*>', '', head)
head = re.sub(r'<meta (property="og:[^"]*"|name="twitter:[^"]*")[^>]*>', '', head)
body = re.sub(r'<img class="herologo"[^>]*>', '%DECO%', body)
assert '%DECO%' in body and body.count('%DECO%') == 1
body = body.replace('<section class="hero photo" data-astro-cid-lcdefpme>', '<section class="hero photo" data-astro-cid-lcdefpme>%HERODZ%', 1)
assert '%HERODZ%' in body

for n, t in enumerate(THEMES, 1):
    dz, _, hl = t['deco'].partition('</i>')
    dz = dz + '</i>' if dz else ''
    url = f'{BASE}g{n}.html'
    og = (f'<meta property="og:type" content="website"><meta property="og:title" content="Anime Sensei rebrand R2 g{n} — {t["title"]}">'
          f'<meta property="og:image" content="{BASE}anime-logo-red.webp"><meta property="og:url" content="{url}">'
          '<meta name="twitter:card" content="summary_large_image">')
    h = head.replace('</head>', og + FONTS + '<style>' + ASTRO + KIT + t['css'] + '</style></head>')
    b = body.replace('%HERODZ%', dz).replace('%DECO%', hl)
    (P5 / f'g{n}.html').write_text(h + b)
    print('wrote', f'g{n}.html', len(h + b))
