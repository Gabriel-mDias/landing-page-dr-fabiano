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
    const result = await page.evaluate(async () => {
      await Promise.all([...document.images].map(async (image) => {
        if (!image.complete) await new Promise((resolve) => image.addEventListener('load', resolve, { once: true }));
        await image.decode().catch(() => {});
      }));
      return {
        innerWidth: window.innerWidth,
        scrollWidth: document.documentElement.scrollWidth,
        imagesBroken: [...document.images].filter((image) => !image.complete || image.naturalWidth === 0).length,
        h1Count: document.querySelectorAll('h1').length,
        menuDisplay: getComputedStyle(document.querySelector('[data-menu-button]')).display
      };
    });

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

      const firstChapter = page.locator('[data-care-chapter]').first();
      await firstChapter.hover();
      await page.waitForTimeout(250);
      if (!(await firstChapter.locator('video').evaluate((video) => video.paused))) {
        errors.push('vídeo iniciou por hover no layout mobile');
      }
    }

    const screenshot = join(tmpdir(), `dr-fabiano-carvalho-${current.name}.png`);
    await page.screenshot({ path: screenshot, fullPage: true });

    if (current.name === 'desktop') {
      const chapters = page.locator('[data-care-chapter]');
      const firstVideo = chapters.nth(0).locator('video');
      const secondVideo = chapters.nth(1).locator('video');
      await chapters.nth(0).hover();
      await page.waitForTimeout(350);
      const preview = await firstVideo.evaluate((video) => ({ paused: video.paused, muted: video.muted }));
      if (preview.paused || !preview.muted) errors.push('prévia desktop não iniciou muda no hover');

      await page.mouse.move(4, 4);
      await page.waitForTimeout(150);
      const restored = await firstVideo.evaluate((video) => ({ paused: video.paused, time: video.currentTime }));
      if (!restored.paused || restored.time > 0.1) errors.push('saída do hover não restaurou o poster');

      await firstVideo.evaluate((video) => video.play());
      const firstVideoBox = await firstVideo.boundingBox();
      await firstVideo.click({ position: { x: firstVideoBox.width * .8, y: 8 } });
      if (await firstVideo.getAttribute('data-pinned') !== 'true') errors.push('clique não fixou a reprodução');
      await page.mouse.move(4, 4);
      await page.waitForTimeout(150);
      if (await firstVideo.evaluate((video) => video.paused)) errors.push('vídeo fixado pausou ao sair do hover');
      await secondVideo.evaluate((video) => video.play());
      await page.waitForTimeout(100);
      if (!(await firstVideo.evaluate((video) => video.paused))) errors.push('reprodução exclusiva não pausou o primeiro vídeo');

      const firstAudio = chapters.nth(0).locator('[data-audio-toggle]');
      const secondAudio = chapters.nth(1).locator('[data-audio-toggle]');
      await firstAudio.click();
      const firstSound = await firstVideo.evaluate((video) => ({ paused: video.paused, muted: video.muted }));
      if (firstSound.paused || firstSound.muted) errors.push('botão de som não ativou áudio e reprodução');
      if (await firstAudio.getAttribute('aria-pressed') !== 'true') errors.push('botão de som não atualizou aria-pressed');
      await secondAudio.click();
      await page.waitForTimeout(100);
      const exclusiveSound = await firstVideo.evaluate((video) => ({ paused: video.paused, muted: video.muted, time: video.currentTime }));
      if (!exclusiveSound.paused || !exclusiveSound.muted || exclusiveSound.time > 0.1) errors.push('troca de áudio não restaurou o vídeo anterior');
      if (await firstAudio.getAttribute('aria-pressed') !== 'false') errors.push('botão anterior não restaurou aria-pressed');
    }

    await page.close();

    if (errors.length) throw new Error(`${current.name}: ${errors.join('; ')}`);
    console.log(`${current.name}: ${result.innerWidth}px, sem overflow/erros, screenshot ${screenshot}`);
  }


  const reducedPage = await browser.newPage({ viewport: { width: 1440, height: 1000 }, reducedMotion: 'reduce' });
  await reducedPage.goto(baseUrl, { waitUntil: 'networkidle' });
  const reducedChapter = reducedPage.locator('[data-care-chapter]').first();
  await reducedChapter.hover();
  await reducedPage.waitForTimeout(250);
  if (!(await reducedChapter.locator('video').evaluate((video) => video.paused))) {
    throw new Error('reduced-motion: vídeo iniciou automaticamente no hover');
  }
  await reducedChapter.locator('video').focus();
  if (!(await reducedChapter.locator('video').evaluate((video) => video.paused))) {
    throw new Error('teclado: foco iniciou reprodução automaticamente');
  }
  const reducedAudio = reducedChapter.locator('[data-audio-toggle]');
  await reducedAudio.focus();
  await reducedPage.keyboard.press('Enter');
  await reducedPage.waitForTimeout(100);
  const keyboardSound = await reducedChapter.locator('video').evaluate((video) => ({ paused: video.paused, muted: video.muted }));
  if (keyboardSound.paused || keyboardSound.muted || await reducedAudio.getAttribute('aria-pressed') !== 'true') {
    throw new Error('teclado: botão não ativou áudio explícito em reduced-motion');
  }
  await reducedPage.keyboard.press('Enter');
  if (await reducedAudio.getAttribute('aria-pressed') !== 'false') {
    throw new Error('teclado: botão não restaurou o estado silencioso');
  }
  await reducedPage.close();
  console.log('reduced-motion: sem autoplay e sem erros');
} finally {
  await browser.close();
}
