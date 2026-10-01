/** Map/album handoff and viewport regressions; start serve.py first. */
import assert from 'node:assert/strict';
import {mkdirSync,writeFileSync} from 'node:fs';
const {chromium}=await import(process.env.PLAYWRIGHT_MODULE||'playwright');
const out=process.env.EVIDENCE_DIR||'/tmp/travel-map-views';mkdirSync(out,{recursive:true});
const base=process.env.BASE_URL||'http://127.0.0.1:8019';
const browser=await chromium.launch({headless:true,...(process.env.CHROMIUM_EXECUTABLE?{executablePath:process.env.CHROMIUM_EXECUTABLE}:{})});
const checks=[],errors=[];
try{
 const p=await browser.newPage({viewport:{width:1440,height:1000}});p.on('pageerror',e=>errors.push(e.message));
 await p.goto(base+'/app/?map=local');await p.waitForSelector('.trip-card');
 await p.getByRole('button',{name:'Edit sample text',exact:true}).first().click();await p.locator('textarea').fill('A draft across map and album views');
 const count=await p.locator('#city-count').innerText();
 const mapPhotoWidth=(await p.locator('.cover-button').first().boundingBox()).width;
 await p.locator('#view-album').click();assert.ok((await p.locator('.cover-button').first().boundingBox()).width>mapPhotoWidth*1.3,'Album should enlarge two photos rather than leave a phantom grid column');assert.equal(await p.locator('.map-panel').isVisible(),false);assert.equal(await p.locator('#view-album').getAttribute('aria-pressed'),'true');assert.equal(await p.locator('#city-count').innerText(),count);assert.equal(await p.locator('textarea').inputValue(),'A draft across map and album views');
 await p.reload();await p.waitForSelector('textarea');assert.equal(await p.locator('.map-panel').isVisible(),false);assert.equal(await p.locator('textarea').inputValue(),'A draft across map and album views');
 await p.locator('#view-map').click();assert.equal(await p.locator('#map').isVisible(),true);assert.equal(await p.locator('#city-count').innerText(),count);checks.push('Map / Album switching and reload preserve the current trip count and draft');
 for(const width of [320,390,540,541,768,850,851,1024,1440]){
  await p.setViewportSize({width,height:900});await p.evaluate(()=>document.fonts.ready);
  for(const mode of ['map','album']){
   await p.locator('#view-'+mode).click();assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,`${width}px ${mode} overflow`);
  }
 }checks.push('No document overflow at 320–1440px in either view');
 await p.setViewportSize({width:1440,height:1000});await p.locator('#search').fill('none');assert.match(await p.locator('#city-name').innerText(),/Keep exploring/);await p.locator('#search').fill('大阪');assert.equal(await p.locator('.trip-card').count(),2);checks.push('Album mode retains search, empty state and separate repeat-visit cards');
 assert.deepEqual(errors,[]);writeFileSync(out+'/views-results.json',JSON.stringify({status:'passed',checks,errors},null,2));console.log(JSON.stringify({status:'passed',checks:checks.length,out}));
}finally{await browser.close()}
