import { chromium } from 'playwright-core';
import { existsSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const baseUrl = process.argv[2] || 'http://127.0.0.1:4173/';
const candidates = [
  'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
  'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
  '/usr/bin/google-chrome',
  '/usr/bin/chromium'
];
const executablePath = candidates.find(existsSync);
if (!executablePath) throw new Error('Chrome/Chromium não encontrado para o smoke test local.');

const browser = await chromium.launch({ executablePath, headless: true });
const cases = [
  { name: 'mobile', width: 390, height: 844 },
  { name: 'tablet', width: 768, height: 1024 },
  { name: 'desktop', width: 1440, height: 1000 }
];

try {
  for (const current of cases) {
    const page = await browser.newPage({ viewport: { width: current.width, height: current.height } });
    const errors = [];
    page.on('pageerror', (error) => errors.push(error.message));
    page.on('console', (message) => {
      if (message.type() === 'error') errors.push(message.text());
    });

    await page.goto(baseUrl, { waitUntil: 'networkidle' });
    const images = page.locator('img');
    for (let index = 0; index < await images.count(); index += 1) {
      await images.nth(index).scrollIntoViewIfNeeded();
    }
    await page.waitForTimeout(150);
    const result = await page.evaluate(() => ({
      innerWidth: window.innerWidth,
      scrollWidth: document.documentElement.scrollWidth,
      imagesBroken: [...document.images].filter((image) => !image.complete || image.naturalWidth === 0).length,
      h1Count: document.querySelectorAll('h1').length,
      menuDisplay: getComputedStyle(document.querySelector('[data-menu-button]')).display
    }));

    if (result.scrollWidth > result.innerWidth) {
      errors.push(`overflow horizontal: ${result.scrollWidth}px > ${result.innerWidth}px`);
    }
    if (result.imagesBroken) errors.push(`${result.imagesBroken} imagem(ns) quebrada(s)`);
    if (result.h1Count !== 1) errors.push(`esperado 1 H1, encontrado ${result.h1Count}`);

    if (current.name === 'mobile') {
      if (result.menuDisplay === 'none') errors.push('botão do menu mobile não está visível');
      await page.locator('[data-menu-button]').click();
      if (await page.locator('[data-menu-button]').getAttribute('aria-expanded') !== 'true') {
        errors.push('menu mobile não atualizou aria-expanded');
      }
    }

    const screenshot = join(tmpdir(), `landing-page-sample-${current.name}.png`);
    await page.screenshot({ path: screenshot, fullPage: true });
    await page.close();

    if (errors.length) throw new Error(`${current.name}: ${errors.join('; ')}`);
    console.log(`${current.name}: ${result.innerWidth}px, sem overflow/erros, screenshot ${screenshot}`);
  }
} finally {
  await browser.close();
}
