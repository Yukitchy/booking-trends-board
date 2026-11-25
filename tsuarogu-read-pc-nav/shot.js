const { chromium } = require('playwright-core');
const BASE = 'http://127.0.0.1:8902';
const OUT = process.env.HOME + '/workspace/tsuarogu-read-pc-nav/shots';

const MEASURE = `(() => {
  const r = {};
  const tb = document.querySelector('.tabbar');
  r.tabbar = tb ? getComputedStyle(tb).display : 'missing';
  const nav = document.querySelector('.pcnav');
  if (nav) {
    const b = nav.getBoundingClientRect();
    r.nav = { display: getComputedStyle(nav).display, x: Math.round(b.x), y: Math.round(b.y), w: Math.round(b.width), h: Math.round(b.height) };
  } else r.nav = null;
  r.sw = document.documentElement.scrollWidth;
  return r;
})()`;

(async () => {
  const exe = process.env.HOME + '/.cache/ms-playwright/chromium_headless_shell-1254/chrome-headless-shell-linux64/chrome-headless-shell';
  const b = await chromium.launch({ executablePath: exe });
  for (const name of ['v1', 'v2', 'v3', 'v4', 'v5']) {
    const p = await b.newPage({ viewport: { width: 1440, height: 1000 } });
    const errs = [];
    p.on('pageerror', e => errs.push(String(e)));
    await p.goto(BASE + '/tsuarogu-read-pc-nav/' + name + '.html');
    await p.waitForTimeout(1600);
    if (name === 'v5') {
      await p.screenshot({ path: `${OUT}/v5-closed.png` });
      await p.click('#nvtocbtn');
      await p.waitForTimeout(500);
      const d = await p.evaluate(`(() => { const el = document.getElementById('tocdrop'); const b = el.getBoundingClientRect(); return { hidden: el.hidden, h: Math.round(b.height), rows: el.querySelectorAll('.r').length }; })()`);
      console.log('v5 dropdown', JSON.stringify(d));
    }
    const m = await p.evaluate(MEASURE);
    console.log(name, JSON.stringify(m), 'errors:', errs.length ? errs : 'none');
    await p.screenshot({ path: `${OUT}/${name}.png` });
    await p.close();
  }
  await b.close();
})();
