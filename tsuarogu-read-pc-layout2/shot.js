const { chromium } = require('playwright-core');
const BASE = 'http://127.0.0.1:8901';
const OUT = process.env.HOME + '/workspace/tsuarogu-read-pc-layout2/shots';

const MEASURE = `(() => {
  const r = {};
  const wrap = document.querySelector('.wrap');
  r.wrapW = wrap ? Math.round(wrap.getBoundingClientRect().width) : null;
  // 注記つき場面の本文カラム幅（代表値）
  let col = null, ef = null;
  document.querySelectorAll('.scene .pg').forEach(pg => {
    const e = pg.querySelector(':scope > .ef'), c = pg.querySelector(':scope > .col');
    if (e && c && !col) { col = c; ef = e; }
  });
  if (!col) col = document.querySelector('.scene .col');
  r.colW = col ? Math.round(col.getBoundingClientRect().width) : null;
  r.efW = ef ? Math.round(ef.getBoundingClientRect().width) : null;
  const rail = document.querySelector('.vrail');
  r.railVisible = rail ? (rail.offsetParent !== null || getComputedStyle(rail).position === 'fixed') && getComputedStyle(rail).display !== 'none' : false;
  r.railW = rail && getComputedStyle(rail).display !== 'none' ? Math.round(rail.getBoundingClientRect().width) : 0;
  const toc = document.getElementById('toclist');
  r.tocHidden = toc ? toc.hidden : null;
  r.chips = document.querySelectorAll('.tchip').length;
  r.sw = document.documentElement.scrollWidth;
  return r;
})()`;

(async () => {
  const exe = process.env.HOME + '/.cache/ms-playwright/chromium_headless_shell-1254/chrome-headless-shell-linux64/chrome-headless-shell';
  const b = await chromium.launch({ executablePath: exe });
  const targets = [
    ['prod', '/tsuarogu-guestbook-build/site/read/yulia.html'],
    ['v1', '/tsuarogu-read-pc-layout2/v1.html'],
    ['v2', '/tsuarogu-read-pc-layout2/v2.html'],
    ['v3', '/tsuarogu-read-pc-layout2/v3.html'],
    ['v4', '/tsuarogu-read-pc-layout2/v4.html'],
    ['v5', '/tsuarogu-read-pc-layout2/v5.html'],
  ];
  for (const [name, path] of targets) {
    const p = await b.newPage({ viewport: { width: 1440, height: 1000 } });
    const errs = [];
    p.on('pageerror', e => errs.push(String(e)));
    await p.goto(BASE + path);
    await p.waitForTimeout(1600);
    const m = await p.evaluate(MEASURE);
    console.log(name, JSON.stringify(m), 'errors:', errs.length ? errs : 'none');
    if (name !== 'prod') {
      await p.screenshot({ path: `${OUT}/${name}.png` });
      await p.evaluate("document.querySelector('#s3').scrollIntoView()");
      await p.waitForTimeout(700);
      await p.screenshot({ path: `${OUT}/${name}-scene.png` });
    }
    await p.close();
  }
  await b.close();
})();
