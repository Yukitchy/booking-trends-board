// 幅検証(320/390/1280)・見出し1行・本文照合・サムネ撮影。
// 使い方: node check.mjs <baseURL> <liveURL> [shotsDir]
import { createRequire } from 'module';
const require = createRequire(process.env.HOME + '/.dev-browser/node_modules/');
const { chromium } = require('playwright');
const [base, live, shots] = process.argv.slice(2);
const pages = ['t1','t2','t3','t4','t5'];
const b = await chromium.launch({ executablePath: process.env.HOME + '/Library/Caches/ms-playwright/chromium-1208/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing' });
let fail = 0;

// 本文の同一性: 見える文字（aria-hidden・script・style・ヘッダーロゴ・ナビゲーター除外）＋リンク先＋写真の src
const extract = () => {
  const skip = el => el.closest('[aria-hidden="true"],script,style,noscript,.navi,.site-head .logo,#jstClock');
  const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const t = []; let n;
  while ((n = w.nextNode())) if (!skip(n.parentElement)) t.push(n.nodeValue);
  const abs = u => new URL(u, 'https://www.animesenseijp.com/').href.replace(/\/$/, '');
  return {
    text: t.join(' ').replace(/\s+/g, ' ').trim(),
    links: [...document.querySelectorAll('a[href]')].filter(a => !skip(a)).map(a => abs(a.getAttribute('href'))),
    imgs: [...document.querySelectorAll('img')].filter(i => !skip(i)).map(i => abs(i.getAttribute('src'))),
  };
};
const ctx0 = await b.newContext();
const lp = await ctx0.newPage();
await lp.goto(live, { waitUntil: 'domcontentloaded' });
const ref = await lp.evaluate(extract);

for (const p of pages) {
  for (const w of [320, 390, 1280]) {
    const ctx = await b.newContext({ viewport: { width: w, height: w > 600 ? 800 : 780 }, deviceScaleFactor: 1 });
    const pg = await ctx.newPage();
    await pg.goto(`${base}${p}.html`, { waitUntil: 'networkidle' });
    await pg.evaluate(() => document.fonts.ready);
    await pg.evaluate(async()=>{document.querySelectorAll('img[loading=lazy]').forEach(i=>i.loading='eager');for(let y=0;y<document.body.scrollHeight;y+=600){scrollTo(0,y);await new Promise(r=>setTimeout(r,60))}scrollTo(0,0)});
    await pg.waitForTimeout(800);
    const r = await pg.evaluate(() => {
      const iw = innerWidth, sw = document.documentElement.scrollWidth;
      const multi = [...document.querySelectorAll('main h1, main h2')].filter(h => !h.dataset.wrap).filter(h => {
        const lh = parseFloat(getComputedStyle(h).lineHeight) || parseFloat(getComputedStyle(h).fontSize) * 1.4;
        return h.clientHeight > lh * 1.6 + parseFloat(getComputedStyle(h).paddingTop) + parseFloat(getComputedStyle(h).paddingBottom);
      }).map(h => h.textContent.trim());
      // 見出しが画面外に出ていないか（回転後の外接矩形）
      const out = [...document.querySelectorAll('main h1, main h2')].filter(h => {
        const r = h.getBoundingClientRect(); return r.left < -2 || r.right > iw + 2;
      }).map(h => h.textContent.trim());
      const wrapped=[...document.querySelectorAll('main [data-wrap]')].map(h=>h.textContent.trim().slice(0,30)); return { iw, sw, multi, out, wrapped };
    });
    const ok = r.sw === r.iw && !r.multi.length && !r.out.length;
    if (!ok) fail++;
    console.log(`${p} w=${w} scrollWidth=${r.sw} ${ok ? 'OK' : 'NG'}${r.multi.length ? ' 2行:' + r.multi.join('|') : ''}${r.out.length ? ' 画面外:' + r.out.join('|') : ''}${r.wrapped.length ? ' 句折返し:' + r.wrapped.join('|') : ''}`);
    if (w === 1280) {
      const got = await pg.evaluate(extract);
      const same = got.text === ref.text && JSON.stringify(got.links) === JSON.stringify(ref.links) && JSON.stringify(got.imgs) === JSON.stringify(ref.imgs);
      if (!same) {
        fail++;
        let i = 0; while (got.text[i] === ref.text[i]) i++;
        console.log(`${p} 本文NG text@${i}: live「${ref.text.slice(i, i + 60)}」 vs 「${got.text.slice(i, i + 60)}」 links ${got.links.length}/${ref.links.length} imgs ${got.imgs.length}/${ref.imgs.length}`);
      } else console.log(`${p} 本文一致 文字${got.text.length} リンク${got.links.length} 画像${got.imgs.length}`);
      if (shots) await pg.screenshot({ path: `${shots}/${p}-pc.png` });
      if (shots) await pg.screenshot({ path: `${shots}/${p}-pcfull.png`, fullPage: true });
    }
    if (w === 390 && shots) {
      await pg.screenshot({ path: `${shots}/${p}-sp.png` });
      await pg.screenshot({ path: `${shots}/${p}-spfull.png`, fullPage: true });
    }
    await ctx.close();
  }
}
await b.close();
console.log(fail ? `FAIL ${fail}` : 'ALL OK');
process.exit(fail ? 1 : 0);
