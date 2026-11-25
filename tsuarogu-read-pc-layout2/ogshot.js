const { chromium } = require('playwright-core');
(async () => {
  const exe = process.env.HOME + '/.cache/ms-playwright/chromium_headless_shell-1254/chrome-headless-shell-linux64/chrome-headless-shell';
  const b = await chromium.launch({ executablePath: exe });
  const p = await b.newPage({ viewport: { width: 1200, height: 630 } });
  await p.goto('http://127.0.0.1:8901/tsuarogu-read-pc-layout2/og.html');
  await p.waitForTimeout(1500);
  await p.screenshot({ path: process.env.HOME + '/workspace/tsuarogu-read-pc-layout2/og.jpg', type: 'jpeg', quality: 88 });
  await b.close();
  console.log('og done');
})();
