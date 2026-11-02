/** Repeatable API-mode release smoke check. Run against an isolated local backend. */
import assert from 'node:assert/strict';
import {mkdirSync, readFileSync, rmSync, writeFileSync} from 'node:fs';
import {join} from 'node:path';

const {chromium} = await import(process.env.PLAYWRIGHT_MODULE || 'playwright');
const base = process.env.BASE_URL || 'http://127.0.0.1:8019';
const out = process.env.EVIDENCE_DIR || '/tmp/travel-map-final-workflow';
mkdirSync(out, {recursive: true});
const rawVideoDir = join(out, '.raw-video');
mkdirSync(rawVideoDir, {recursive: true});
const browser = await chromium.launch({
  headless: true,
  ...(process.env.CHROMIUM_EXECUTABLE ? {executablePath: process.env.CHROMIUM_EXECUTABLE} : {}),
});
const context = await browser.newContext({
  viewport: {width: 1440, height: 900},
  recordVideo: {dir: rawVideoDir, size: {width: 1440, height: 900}},
});
const page = await context.newPage();
const errors = [];
const checks = [];
const createdIds = [];
page.on('pageerror', error => errors.push(error.message));
const cardFor = title => page.locator('.trip-card').filter({hasText: title}).first();
const selectNanjing = async () => {
  await page.locator('#cities button[data-city-id="cn-nanjing"]').click();
  await page.waitForFunction(() => document.querySelector('#city-name')?.textContent === 'Nanjing');
};
const createTrip = async (title, notes) => {
  await page.locator('.api-composer input[type=text]').fill(title);
  await page.locator('.api-composer textarea').fill(notes);
  await page.locator('.api-composer button[type=submit]').click();
  await page.waitForFunction(t => [...document.querySelectorAll('.trip-card h3')].some(h => h.textContent === t), title);
  const id = await cardFor(title).getAttribute('data-trip-id');
  assert.ok(id, 'Trip has a server-generated ID');
  createdIds.push(id);
  return id;
};
try {
  await page.goto(base + '/app/?mode=api&map=local', {waitUntil: 'networkidle'});
  await page.locator('.api-composer').waitFor();
  await selectNanjing();
  await page.waitForTimeout(900);
  const first = 'A fictional Nanjing afternoon';
  await createTrip(first, 'A fictional test trip. We saw a park bench.');
  assert.equal(await page.locator('.city-region[data-city-id="cn-nanjing"]').getAttribute('data-tier'), '1');
  assert.match(await page.locator('#map-selection').innerText(), /Nanjing · 1 trip saved · area lit/);
  checks.push('First saved trip creates one card and lights the city area');
  await page.waitForTimeout(1000);

  const fixture = readFileSync(new URL('../data/fixtures/T02/park-bench.png', import.meta.url));
  await cardFor(first).locator('input[type=file]').setInputFiles({name: 'park-bench.png', mimeType: 'image/png', buffer: fixture});
  await cardFor(first).locator('.photo-strip img').waitFor({state: 'visible'});
  checks.push('Synthetic photo is uploaded and displayed from local storage');
  await page.waitForTimeout(900);

  await cardFor(first).getByRole('button', {name: 'Edit memory'}).click();
  const editor = cardFor(first).locator('.memory-editor');
  await editor.locator('textarea').nth(1).fill('An edited fictional memory, saved after the trip.');
  await editor.getByRole('button', {name: 'Save memory'}).click();
  await page.waitForFunction(t => [...document.querySelectorAll('.trip-card')].some(c => c.querySelector('h3')?.textContent === t && c.innerText.includes('An edited fictional memory')), first);
  assert.equal(await page.locator('.city-region[data-city-id="cn-nanjing"]').getAttribute('data-tier'), '1');
  checks.push('Editing a card does not add a visit');
  await page.waitForTimeout(900);
  await page.screenshot({path: join(out, 'first-trip-desktop.png'), fullPage: true});

  const second = 'A second fictional Nanjing visit';
  await createTrip(second, 'A separate fictional trip to the same city.');
  assert.equal(await page.locator('.city-region[data-city-id="cn-nanjing"]').getAttribute('data-tier'), '2');
  assert.match(await page.locator('#map-selection').innerText(), /Nanjing · 2 trips saved · area lit/);
  assert.equal(await page.locator('.trip-card').count(), 2);
  checks.push('Second trip creates a separate card and brighter visit tier');
  await page.waitForTimeout(1200);
  await page.screenshot({path: join(out, 'two-trips-desktop.png'), fullPage: true});
  await page.locator('#view-album').click();
  await page.screenshot({path: join(out, 'album-desktop.png'), fullPage: true});
  await page.locator('#view-map').click();

  await page.reload({waitUntil: 'networkidle'});
  await page.locator('.api-composer').waitFor();
  await selectNanjing();
  assert.equal(await page.locator('.trip-card').count(), 2);
  assert.match(await cardFor(first).innerText(), /An edited fictional memory/);
  await cardFor(first).locator('.photo-strip img').waitFor({state: 'visible'});
  assert.equal(await page.locator('.city-region[data-city-id="cn-nanjing"]').getAttribute('data-tier'), '2');
  checks.push('Cards, photo, edit and visit tier survive reload');
  await page.waitForTimeout(900);

  await cardFor(first).getByRole('button', {name: 'Write with AI'}).click();
  await cardFor(first).locator('.ai-notice').waitFor();
  const notice = await cardFor(first).locator('.ai-notice').innerText();
  assert.match(notice, /Nanjing/);
  assert.match(notice, /A fictional Nanjing afternoon/);
  assert.match(notice, /A fictional test trip/);
  assert.match(notice, /1 sanitised photo/);
  await page.waitForTimeout(1200);
  await cardFor(first).getByRole('button', {name: 'Send this trip'}).click();
  await page.locator('#error:not([hidden])').waitFor();
  assert.match(await page.locator('#error-text').innerText(), /AI draft failed|No AI provider|configured/i);
  assert.match(await cardFor(first).innerText(), /An edited fictional memory/);
  checks.push('AI disclosure appears; missing provider fails without changing saved text');
  await page.waitForTimeout(1200);

  await page.setViewportSize({width: 390, height: 844});
  assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
  await page.screenshot({path: join(out, 'two-trips-mobile.png'), fullPage: true});
  await page.locator('#view-album').click();
  await page.locator('.trip-card').first().scrollIntoViewIfNeeded();
  await page.screenshot({path: join(out, 'album-mobile.png')});
  checks.push('Mobile view has no horizontal overflow');

  assert.deepEqual(errors, []);
  writeFileSync(join(out, 'results.json'), JSON.stringify({status: 'passed', checks, errors, base, fixture: 'T02 synthetic park-bench.png'}, null, 2));
  console.log(JSON.stringify({status: 'passed', checks: checks.length, out}));
} finally {
  const video = page.video();
  await context.close();
  if (video) await video.saveAs(join(out, 'workflow.webm'));
  rmSync(rawVideoDir, {recursive: true, force: true});
  for (const id of createdIds) {
    try { await fetch(base + '/api/trips/' + id, {method: 'DELETE'}); } catch { /* leave cleanup for isolated temp database */ }
  }
  await browser.close();
}
