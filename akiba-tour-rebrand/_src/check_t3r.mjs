// t3r 検証: 320/390/1280 の横はみ出し・見出し1行・t3 との本文/リンク/画像の一致
import { createRequire } from 'module';
const require = createRequire(process.env.HOME + '/.dev-browser/node_modules/');
const { chromium } = require('playwright');
const base = process.argv[2] || 'http://localhost:8765/akiba-tour-rebrand/';
const b = await chromium.launch({ executablePath: process.env.HOME + '/Library/Caches/ms-playwright/chromium-1208/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing' });
let fail = 0;
const extract = () => {
  const skip = el => el.closest('[aria-hidden="true"],script,style,noscript,.navi,.site-head .logo,#jstClock');
  const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); const t = []; let n;
  while ((n = w.nextNode())) if (!skip(n.parentElement)) t.push(n.nodeValue);
  return { text: t.join(' ').replace(/\s+/g, ' ').trim(),
    links: [...document.querySelectorAll('a[href]')].filter(a => !skip(a)).map(a => a.getAttribute('href')),
    imgs: [...document.querySelectorAll('img')].filter(i => !skip(i)).map(i => i.getAttribute('src')) };
};
const got = {};
for (const p of ['t3', 't3r']) {
  for (const w of [320, 390, 1280]) {
    const ctx = await b.newContext({ viewport: { width: w, height: w > 600 ? 800 : 780 } });
    const pg = await ctx.newPage();
    await pg.goto(`${base}${p}.html`, { waitUntil: 'networkidle' });
    await pg.evaluate(() => document.fonts.ready); await pg.waitForTimeout(500);
    if (p === 't3r') {
      const r = await pg.evaluate(() => {
        const iw = innerWidth, sw = document.documentElement.scrollWidth;
        const multi = [...document.querySelectorAll('main h1, main h2')].filter(h => !h.dataset.wrap).filter(h => {
          const lh = parseFloat(getComputedStyle(h).lineHeight) || parseFloat(getComputedStyle(h).fontSize) * 1.4;
          return h.clientHeight > lh * 1.6 + parseFloat(getComputedStyle(h).paddingTop) + parseFloat(getComputedStyle(h).paddingBottom);
        }).map(h => h.textContent.trim());
        const wrapped = [...document.querySelectorAll('main [data-wrap]')].map(h => h.textContent.trim().slice(0, 22));
        return { iw, sw, multi, wrapped };
      });
      const ok = r.sw === r.iw && !r.multi.length; if (!ok) fail++;
      console.log(`t3r w=${w} scrollWidth=${r.sw}/${r.iw} ${ok ? 'OK' : 'NG'}${r.multi.length ? ' 2行:' + r.multi.join('|') : ''} 句折返し:${r.wrapped.join(' | ')}`);
    }
    if (w === 1280) got[p] = await pg.evaluate(extract);
    await ctx.close();
  }
}
const a = got.t3, c = got.t3r;
const same = a.text === c.text && JSON.stringify(a.links) === JSON.stringify(c.links) && JSON.stringify(a.imgs) === JSON.stringify(c.imgs);
if (!same) { fail++;
  for (const k of ['text', 'links', 'imgs']) { const x = JSON.stringify(a[k]), y = JSON.stringify(c[k]); let i = 0;
    while (i < x.length && x[i] === y[i]) i++;
    if (x !== y) console.log(k, '@' + i, 't3:', x.slice(i - 40, i + 40), ' t3r:', y.slice(i - 40, i + 40)); } }
console.log(`本文 ${same ? '一致' : 'NG'}: 文字 ${c.text.length}/${a.text.length} リンク ${c.links.length}/${a.links.length} 画像 ${c.imgs.length}/${a.imgs.length}`);
await b.close();
console.log(fail ? `FAIL ${fail}` : 'ALL OK'); process.exit(fail ? 1 : 0);
