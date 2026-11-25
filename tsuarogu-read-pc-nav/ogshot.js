const { chromium } = require('playwright-core');
(async () => {
  const exe = process.env.HOME + '/.cache/ms-playwright/chromium_headless_shell-1254/chrome-headless-shell-linux64/chrome-headless-shell';
  const b = await chromium.launch({ executablePath: exe });
  const p = await b.newPage({ viewport: { width: 1200, height: 630 } });
  await p.goto('http://127.0.0.1:8902/tsuarogu-read-pc-nav/og.html');
  await p.waitForTimeout(1500);
  await p.screenshot({ path: process.env.HOME + '/workspace/tsuarogu-read-pc-nav/og.jpg', type: 'jpeg', quality: 88 });
  // ボード本体の確認用スクショ
  const p2 = await b.newPage({ viewport: { width: 1440, height: 1000 } });
  await p2.goto('http://127.0.0.1:8902/tsuarogu-read-pc-nav/index.html');
  await p2.waitForTimeout(1500);
  await p2.screenshot({ path: process.env.HOME + '/workspace/tsuarogu-read-pc-nav/shots/board.png' });
  await b.close();
  console.log('og done');
})();
