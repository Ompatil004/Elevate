const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });

  console.log('Navigating to login...');
  await page.goto('http://localhost:5174/login', { waitUntil: 'networkidle2' });

  console.log('Logging in...');
  await page.type('input[type="email"]', 'test@test.com');
  await page.type('input[type="password"]', 'password123');
  await page.click('button[type="submit"]');

  console.log('Waiting for dashboard to load...');
  await page.waitForNavigation({ waitUntil: 'networkidle2' });
  // Wait an extra second for animations
  await new Promise(r => setTimeout(r, 2000));

  console.log('Taking screenshot...');
  const screenshotPath = 'C:/Users/2004o/.gemini/antigravity-ide/brain/918508ee-5b73-47cb-bf26-8f52669b8938/dashboard_layout_bug.png';
  await page.screenshot({ path: screenshotPath, fullPage: true });

  console.log('Screenshot saved to: ' + screenshotPath);
  await browser.close();
})();
