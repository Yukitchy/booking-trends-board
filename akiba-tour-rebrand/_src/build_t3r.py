#!/usr/bin/env python3
"""t3r = t3（白＋ハーフトーン漫画風）の総点検修正版。t1〜t5 は書き換えない。
本文・リンク・画像は build.py と同じ下ごしらえを使い、CSS・ロゴ・ナビゲーターだけ差し替える。"""
import build as B

KEY = 't3r'
SAY = "Pick a day — I'll plan the rest!"   # ナビゲーターの吹き出し（表示直後に1回だけ）

NAVI = ('<div class="navi" aria-label="Guide"><a class="navi-b" href="#finale" aria-label="Check dates and book">'
        f'<span class="navi-say" aria-hidden="true">{SAY}</span>'
        '<img class="navi-m" src="mascot-cut.webp" alt="" width="561" height="764"></a>'
        '<button class="navi-x" type="button" aria-label="Close guide">×</button></div>')

OLD_NAVI_JS = "if(b&&'IntersectionObserver'in window)new IntersectionObserver(e=>n.classList.toggle('off',e[0].isIntersecting),{threshold:.08}).observe(b)})();"
assert OLD_NAVI_JS in B.JS
JS = B.JS.replace(OLD_NAVI_JS, OLD_NAVI_JS[:-5] +
                  ";setTimeout(()=>n.classList.add('say'),600);setTimeout(()=>n.classList.remove('say'),4800)})();")

FIX = """
/* ===== t3r 修正 ===== */
/* ロゴ: 透過版。余白を切ったぶん高さを詰める */
#v .site-head .logo{padding:6px 0}
#v .site-head .logo img{height:40px}
@media (max-width:600px){#v .site-head .logo img{height:32px}}
#v .site-head nav a:not(.btn-sm){min-height:44px;align-items:center}
@media(min-width:821px){#v .site-head nav a:not(.btn-sm){display:inline-flex}}
#v .clock b,#v .clock i{font-size:11px}
/* 小見出しラベルを1種類に（12px・字間.16em・黒地・見出しとの間14px） */
#v .eyebrow,#v .guide .who,#v .center>.chip{display:inline-block;font:900 12px/1.4 var(--maru);letter-spacing:.16em;padding:5px 12px;margin:0 0 14px;background:#111;color:#fff;border:0;border-radius:0;box-shadow:none}
#v .center>.chip{margin-bottom:0}
/* 見出しは全部大文字の Anton で揃える（文字そのものは変えない） */
#v main h2{text-transform:uppercase}
#v .hero .hook{text-wrap:balance}
@media(max-width:600px){#v .hero .hook{max-width:12.5em}}
/* 手順カード: gap 10px に合わせて幅を計算し直し、左端を本文と揃える */
#v .steps>*{flex:1 1 100%}
@media(min-width:640px){#v .steps>*{flex:0 1 calc(50% - 5px)}}
@media(min-width:1000px){#v .steps>*{flex:0 1 calc(25% - 7.5px)}}
/* 番号を写真の上から写真と本文の境目へ（顔に掛からない） */
#v .step .n{top:144px;left:14px}
/* 実績4枚: 他のカードと同じ 10px 格子で全幅に */
#v .proofs{grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;justify-content:stretch;justify-items:stretch}
@media(min-width:700px){#v .proofs{grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}}
#v .pf,#v .pf:nth-child(n){width:auto;aspect-ratio:auto;padding:28px 12px 26px}
/* 12px 未満の文字をなくす */
#v .pf .s,#v .figcap{font-size:12px}
#v .review .src{font-size:11px;letter-spacing:.08em;padding:3px 8px}
#v .bk-note,#v .booker .bk-note *{font-size:12.5px}
#v .bk-t span{font-size:12px!important;border-radius:0!important;padding:4px 8px!important;letter-spacing:.02em}
@media(min-width:1280px){#v .seals .seal{width:118px}}
/* スマホ: 丸シールが見出し・札に重なっていた（t3 から）。シールを詰め、本文の開始を下げて避ける */
@media(max-width:600px){#v .seals .seal{width:94px;padding:8px 6px}#v .seals .seal b{font-size:20px}#v .hero .in{padding-top:66px}}
@media(max-width:379px){#v .hero .in{padding-top:122px}}
@media(min-width:601px) and (max-width:1279px){#v .hero .in{padding-top:90px}}
@media(min-width:900px) and (max-width:1279px){#v .hero .in{padding-top:134px}}
#v .seals .seal em{font-size:11px;letter-spacing:.06em}
#v .seals .seal small{font-size:11px;letter-spacing:.02em}
#v .face-wrap .seal small{font-size:11px}
/* 赤ベタのカード: 見出しが黒(3.9:1)になっていたので白に。網点は角だけ */
#v .card.hot h3{color:#fff}
#v .card.hot::before{opacity:.22;-webkit-mask-image:linear-gradient(135deg,transparent 45%,#000);mask-image:linear-gradient(135deg,transparent 45%,#000)}
#v .card.hot a{display:inline-flex;align-items:center;min-height:44px}
/* FAQ: 見出しの左端に揃える。＋/− を読める大きさに */
#v .faq{margin-left:0;margin-right:0;max-width:880px}
#v .faq summary{display:flex;align-items:center;min-height:52px;padding-top:12px;padding-bottom:12px}
#v .faq summary::after{content:"+";top:50%;transform:translateY(-50%);width:30px;height:30px;font:900 20px/1 var(--maru);display:grid;place-items:center;padding:0 0 2px}
#v .faq details[open] summary::after{content:"−"}
/* 押せる大きさ（44px） */
#v .bk-step button{width:44px;height:44px;font-size:18px}
#v #choose .center a{display:inline-flex;align-items:center;min-height:44px;padding:0 4px}
/* 締め: 放射線を下半分だけに。上の白文字の背後を明るくしない */
#v .finale .dz{-webkit-mask-image:linear-gradient(180deg,transparent 0 30%,#000 62%);mask-image:linear-gradient(180deg,transparent 0 30%,#000 62%)}
#v .finale .lead{color:#fff}
#v .site-foot .legal{max-width:none}
/* スマホ下端の予約タブ: 丸い波形(別の赤 #E0342A)を t3 の四角い札と同じ赤に */
#v .sc,#v .sc-panel,#v .sc-open{--sc-accent:#e3121b;--sc-ink:#111}
#v .sc-handle svg{display:none}
#v .sc-handle{background:linear-gradient(transparent 24px,#111 24px 27px,#e3121b 27px)}
#v .sc-open{background:linear-gradient(transparent 24px,#111 24px 27px,#e3121b 27px)}
#v .sc-handle span{background:#e3121b;border:3px solid #111;border-bottom:0;padding:5px 16px 3px;margin-top:2px;font-size:13px;font-weight:900;letter-spacing:.03em}
#v .sc-panel .booker{box-shadow:5px 5px 0 #111}
#v .step .body{padding-top:30px}
/* 案内役の吹き出し: しっぽをレビューと同じ塗りの三角に（細い山形になっていた） */
#v .bubble::before{left:34px;top:-21px;width:26px;height:21px;border:0;background:#111;clip-path:polygon(0 100%,14% 0,100% 100%)}
#v .bubble::after{left:37px;top:-15px;width:20px;height:16px;border:0;background:#fff;clip-path:polygon(0 100%,12% 0,100% 100%);z-index:1}
/* フォーカス */
#v a:focus-visible,#v button:focus-visible,#v summary:focus-visible{outline:3px solid var(--R);outline-offset:3px}
#v .finale a:focus-visible,#v .finale button:focus-visible,#v .hero a:focus-visible{outline-color:#111;box-shadow:0 0 0 6px #fff}
/* ===== ナビゲーター: 表示直後だけ吹き出し、あとはアイコンだけ ===== */
.navi-b{display:block;position:relative;max-width:none;margin:0;padding:0;background:none;border:0;box-shadow:none;transform:none;line-height:0}
.navi-b:after{content:none}
.navi-say{position:absolute;z-index:1;right:calc(100% - 4px);bottom:46%;white-space:nowrap;padding:8px 13px 9px;font:900 14px/1.3 var(--maru);color:#111;background:#fff;border:3px solid #111;box-shadow:4px 4px 0 var(--R);
 opacity:0;visibility:hidden;transform:translateY(8px) scale(.94);transform-origin:100% 100%;transition:opacity .5s ease,transform .5s cubic-bezier(.2,.9,.25,1),visibility 0s linear .5s;pointer-events:none}
.navi-say:before{content:"";position:absolute;right:-16px;bottom:7px;width:16px;height:18px;background:#111;clip-path:polygon(0 0,100% 58%,0 100%)}
.navi-say:after{content:"";position:absolute;right:-10px;bottom:11px;width:11px;height:10px;background:#fff;clip-path:polygon(0 0,100% 58%,0 100%)}
.navi.say .navi-say{opacity:1;visibility:visible;transform:none;transition:opacity .35s ease,transform .45s cubic-bezier(.2,.9,.25,1)}
.navi-m{height:132px}
.navi-x{top:-4px;right:-4px}
.navi-x:before{content:"";position:absolute;inset:-10px}
@media (max-width:600px){.navi{right:4px}.navi-b{margin:0;padding:0;font-size:inherit}.navi-m{height:72px}
 .navi-say{font-size:12.5px;padding:6px 10px 7px;right:2px;bottom:calc(100% + 16px);transform-origin:90% 100%}
 .navi-say:before{right:20px;bottom:-16px;width:18px;height:16px;clip-path:polygon(0 0,100% 0,72% 100%)}
 .navi-say:after{right:23px;bottom:-10px;width:12px;height:11px;clip-path:polygon(0 0,100% 0,72% 100%)}
 .navi-x{width:24px;height:24px;line-height:20px}}
@media (prefers-reduced-motion:reduce){.navi-say,.navi.say .navi-say{transition:none;transform:none}}
"""

if __name__ == '__main__':
    url = f'{B.BASE}{KEY}.html'
    meta = ('<meta name="robots" content="noindex,nofollow">'
            '<meta property="og:type" content="website"><meta property="og:title" content="Akihabara tour rebrand t3r — 白＋ハーフトーン漫画風（修正版）">'
            f'<meta property="og:image" content="{B.BASE}anime-logo-red.webp"><meta property="og:url" content="{url}">'
            '<meta name="twitter:card" content="summary_large_image">')
    h = B.head.replace('</head>', meta + B.FONTS + '<style>' + B.ASTRO + B.KIT + B.T3['css'] + FIX + '</style></head>')
    body = B.body.replace('<img src="anime-logo-red.webp" alt="Anime Sensei" width="600" height="300">',
                          '<img src="anime-logo-red-cut.webp" alt="Anime Sensei" width="629" height="300">', 1)
    assert 'anime-logo-red-cut.webp' in body
    b = body.replace('%HERODZ%', B.T3['hero']).replace('%FINDZ%', B.T3['fin']).replace('</body>', NAVI + JS + '</body>')
    (B.OUT / f'{KEY}.html').write_text(h + b)
    print('wrote', KEY, len(h + b))
