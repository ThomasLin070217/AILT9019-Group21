/** Browser → local backend → Chat Completions adapter → local fake model → editable draft. */
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {createServer} from 'node:http';
import {mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';

const {chromium} = await import(process.env.PLAYWRIGHT_MODULE || 'playwright');
const root = mkdtempSync(join(tmpdir(), 'ailt-ai-integration-'));
const evidence = process.env.EVIDENCE_DIR || join(process.cwd(), 'var', 'evaluation', 'mock-browser');
mkdirSync(evidence, {recursive: true});
const seen = [];
const draft = {
  status: 'draft', title: 'A rainy Osaka visit',
  memory_text: 'I visited Osaka for two days. It rained on the first day.',
  warnings: [], questions: [],
};
const provider = createServer(async (request, response) => {
  const chunks = [];
  for await (const chunk of request) chunks.push(chunk);
  seen.push({path: request.url, authorization: request.headers.authorization, body: JSON.parse(Buffer.concat(chunks).toString())});
  response.writeHead(200, {'content-type': 'application/json'});
  response.end(JSON.stringify({model: 'local-fake-vision', choices: [{message: {content: JSON.stringify(draft)}}]}));
});
const listen = server => new Promise(resolve => server.listen(0, '127.0.0.1', () => resolve(server.address().port)));
const close = server => new Promise(resolve => server.close(resolve));
const reservePort = async () => {const server = createServer(); const port = await listen(server); await close(server); return port;};
let backend;
let browser;
let context;
let backendLog = '';
try {
  const providerPort = await listen(provider);
  const appPort = await reservePort();
  const base = `http://127.0.0.1:${appPort}`;
  backend = spawn(process.env.PYTHON_BIN || 'python3', ['-m', 'backend', '--port', String(appPort)], {
    cwd: process.cwd(),
    env: {
      ...process.env, PORT: String(appPort), AI_PROVIDER: 'responses', AI_API_KEY: 'test-only-local-key',
      AI_MODEL: 'local-fake-vision', AI_BASE_URL: `http://127.0.0.1:${providerPort}/v1`,
      NO_PROXY: '127.0.0.1,localhost',
      TMM_DB_PATH: join(root, 'travel.db'), TMM_MEDIA_DIR: join(root, 'media'), TMM_TMP_DIR: join(root, 'tmp'),
    },
    stdio: ['ignore', 'pipe', 'pipe'],
  });
  backend.stdout.on('data', chunk => {backendLog = (backendLog + chunk.toString()).slice(-4000);});
  backend.stderr.on('data', chunk => {backendLog = (backendLog + chunk.toString()).slice(-4000);});
  let ready = false;
  for (let attempt = 0; attempt < 100; attempt++) {
    if (backend.exitCode !== null) throw new Error(`Backend exited early: ${backendLog}`);
    try {const result = await fetch(base + '/api/health'); if (result.ok && (await result.json()).ai_configured) {ready = true; break;}} catch {}
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  if (!ready) throw new Error(`Backend did not become AI-ready: ${backendLog}`);

  browser = await chromium.launch({headless: true, ...(process.env.CHROMIUM_EXECUTABLE ? {executablePath: process.env.CHROMIUM_EXECUTABLE} : {})});
  context = await browser.newContext({viewport: {width: 1280, height: 900}});
  const page = await context.newPage();
  const pageErrors = [];
  page.on('pageerror', error => pageErrors.push(error.message));
  await page.goto(base + '/app/?mode=api&map=local', {waitUntil: 'networkidle'});
  await page.locator('.api-composer').waitFor();
  const choose = async id => {await page.locator(`#cities button[data-city-id="${id}"]`).click();};
  const createTrip = async (title, notes) => {
    await page.locator('.api-composer input[type=text]').fill(title);
    await page.locator('.api-composer textarea').fill(notes);
    await page.locator('.api-composer button[type=submit]').click();
    const card = page.locator('.trip-card').filter({hasText: title}).first();
    await card.waitFor();
    return card.getAttribute('data-trip-id');
  };
  const title = 'First fictional Osaka trip';
  const notes = 'I visited Osaka for two days. It rained on the first day.';
  await choose('jp-osaka');
  const selectedId = await createTrip(title, notes);
  assert.ok(selectedId);
  const fixture = readFileSync(new URL('../data/fixtures/T02/park-bench.png', import.meta.url));
  await page.locator(`.trip-card[data-trip-id="${selectedId}"] input[type=file]`).setInputFiles({name: 'park-bench.png', mimeType: 'image/png', buffer: fixture});
  await page.locator(`.trip-card[data-trip-id="${selectedId}"] .photo-strip img`).waitFor();
  await choose('jp-tokyo');
  const otherId = await createTrip('Other fictional trip', 'PRIVATE-SECOND-TRIP-DO-NOT-SEND');
  assert.ok(otherId);
  await choose('jp-osaka');
  const card = page.locator(`.trip-card[data-trip-id="${selectedId}"]`);
  const before = await (await fetch(`${base}/api/trips/${selectedId}`)).json();
  await card.getByRole('button', {name: 'Write with AI'}).click();
  const notice = await card.locator('.ai-notice').innerText();
  for (const fact of ['Osaka', title, notes, '1 sanitised photo']) assert.ok(notice.includes(fact), `Disclosure omitted ${fact}`);
  await card.getByRole('button', {name: 'Cancel'}).click();
  assert.equal(seen.length, 0, 'Cancel must not contact the model');
  await card.getByRole('button', {name: 'Write with AI'}).click();
  await card.getByRole('button', {name: 'Send this trip'}).click();
  const editor = card.locator('.memory-editor');
  try { await editor.waitFor({timeout: 10000}); }
  catch (error) {
    await page.screenshot({path: join(evidence, 'ai-error.png'), fullPage: true});
    console.error(JSON.stringify({providerCalls: seen.length, errorText: await page.locator('#error-text').innerText(), cardText: await card.innerText(), backendLog}));
    throw error;
  }
  assert.equal(await editor.locator('input[type=text]').inputValue(), draft.title);
  assert.equal(await editor.locator('textarea').nth(1).inputValue(), draft.memory_text);
  assert.equal(seen.length, 1, 'Only the confirmed request should reach the model');
  assert.equal(seen[0].path, '/v1/chat/completions');
  assert.equal(seen[0].authorization, 'Bearer test-only-local-key');
  const content = seen[0].body.messages[1].content;
  assert.ok(content[0].text.includes(notes));
  assert.ok(content[0].text.includes('Osaka'));
  assert.ok(!JSON.stringify(seen[0].body).includes('PRIVATE-SECOND-TRIP-DO-NOT-SEND'));
  assert.equal(content.filter(part => part.type === 'image_url').length, 1);
  const image = Buffer.from(content[1].image_url.url.split(',', 2)[1], 'base64');
  assert.equal(image.subarray(0, 2).toString('hex'), 'ffd8', 'Provider receives a prepared JPEG');
  assert.deepEqual(await (await fetch(`${base}/api/trips/${selectedId}`)).json(), before, 'Model result must remain unsaved');
  await page.screenshot({path: join(evidence, 'draft-before-save.png'), fullPage: true});
  await editor.getByRole('button', {name: 'Save reviewed draft'}).click();
  await page.waitForFunction(id => document.querySelector(`.trip-card[data-trip-id="${id}"]`)?.innerText.includes('A rainy Osaka visit'), selectedId);
  await page.reload({waitUntil: 'networkidle'});
  await choose('jp-osaka');
  const after = await (await fetch(`${base}/api/trips/${selectedId}`)).json();
  assert.equal(after.title, draft.title);
  assert.equal(after.memory_text, draft.memory_text);
  assert.equal((await (await fetch(`${base}/api/trips/${otherId}`)).json()).notes, 'PRIVATE-SECOND-TRIP-DO-NOT-SEND');
  assert.deepEqual(pageErrors, []);
  await page.screenshot({path: join(evidence, 'saved-after-reload.png'), fullPage: true});
  writeFileSync(join(evidence, 'results.json'), JSON.stringify({status: 'passed', provider: 'local fake; no cloud request', checks: [
    'AI-ready backend starts with isolated storage', 'Cancel sends nothing', 'Disclosure lists selected trip fields',
    'Only selected trip and one prepared JPEG reach Chat Completions', 'Draft remains unsaved until review',
    'Reviewed draft persists after save and reload', 'Other trip remains unchanged', 'No browser page errors',
  ]}, null, 2));
  console.log(JSON.stringify({status: 'passed', providerCalls: seen.length, evidence}));
} finally {
  if (context) await context.close();
  if (browser) await browser.close();
  if (backend && backend.exitCode === null) {
    backend.kill('SIGTERM');
    await Promise.race([new Promise(resolve => backend.once('exit', resolve)), new Promise(resolve => setTimeout(resolve, 3000))]);
    if (backend.exitCode === null) backend.kill('SIGKILL');
  }
  if (provider.listening) await close(provider);
  rmSync(root, {recursive: true, force: true});
}
