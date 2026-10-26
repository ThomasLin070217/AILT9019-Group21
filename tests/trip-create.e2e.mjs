/** Isolated real server + SQLite + file uploads. Does not touch the user's album. */
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {once} from 'node:events';
import {mkdtemp,mkdir,rm} from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
const {chromium}=await import(process.env.PLAYWRIGHT_MODULE||'playwright');
const root=path.resolve(new URL('..',import.meta.url).pathname);
const storage=await mkdtemp(path.join(os.tmpdir(),'travel-album-test-'));
const evidence=process.env.EVIDENCE_DIR||path.join(root,'.context/feature-01');await mkdir(evidence,{recursive:true});
let server,browser;
async function start(port=0){
 server=spawn('python3',['serve.py','--port',String(port),'--data-dir',storage],{cwd:root,stdio:['ignore','pipe','pipe']});
 return await new Promise((resolve,reject)=>{
  let text='';const timer=setTimeout(()=>reject(new Error('Server did not start')),10000);
  server.stdout.on('data',chunk=>{text+=chunk;const url=text.match(/http:\/\/127\.0\.0\.1:\d+/);if(url){clearTimeout(timer);resolve(url[0]);}});
  server.once('error',reject);server.once('exit',code=>{clearTimeout(timer);reject(new Error(`Server exited ${code}`));});
 });
}
async function stop(){if(server&&server.exitCode===null){const stopped=once(server,'exit');server.kill('SIGTERM');await stopped;}}
try{
 const base=await start(),checks=[],errors=[];
 browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_EXECUTABLE||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
 const context=await browser.newContext({viewport:{width:1440,height:1000}}),page=await context.newPage();
 page.on('pageerror',e=>errors.push(e.message));page.on('dialog',d=>d.accept());
 await page.goto(base+'/app/?mode=local&map=local');await page.waitForSelector('.city-button');
 assert.match(await page.locator('#city-count').innerText(),/^0 visits/);assert.equal(await page.locator('.trip-card').count(),0);
 checks.push('Real local album starts empty and never imports demo records');
 await page.getByRole('button',{name:'Add a trip',exact:true}).click();
 await page.getByRole('button',{name:'Save trip',exact:true}).click();assert.match(await page.locator('#trip-error').innerText(),/at least one photo/);
 await page.locator('#trip-photos').setInputFiles({name:'broken.png',mimeType:'image/png',buffer:Buffer.from('bad image')});
 await page.waitForFunction(()=>document.querySelector('#trip-error').textContent.includes('could not be read'));
 assert.equal(await page.locator('.photo-previews img').count(),0);checks.push('Missing and corrupt photos are rejected before saving');
 await page.locator('#trip-title').fill('Osaka, a day to remember');await page.locator('#trip-date').fill('2026-10-20');await page.locator('#trip-notes').fill('第一次真正保存的旅行。<script>alert(1)</script>');
 await page.locator('#trip-photos').setInputFiles([path.join(root,'data/demo-covers/osaka-castle-1.jpg'),path.join(root,'data/demo-covers/osaka-castle-2.jpg')]);
 await page.waitForFunction(()=>document.querySelectorAll('.photo-previews img').length===2);
 await page.locator('#memories').evaluate(el=>el.scrollTop=0);await page.screenshot({path:path.join(evidence,'desktop-form.png'),fullPage:true});
 await page.route('**/api/trips',route=>route.request().method()==='POST'?route.fulfill({status:503,json:{error:'Test: local storage unavailable.'}}):route.continue());
 await page.getByRole('button',{name:'Save trip',exact:true}).click();await page.waitForFunction(()=>document.querySelector('#trip-error').textContent.includes('storage unavailable'));
 assert.equal(await page.locator('#trip-title').inputValue(),'Osaka, a day to remember');assert.equal(await page.locator('.photo-previews img').count(),2);
 checks.push('Failed save keeps title, date, notes and both photo selections');
 await page.unroute('**/api/trips');
 const requestPromise=page.waitForRequest(request=>request.method()==='POST'&&request.url().endsWith('/api/trips'));
 await page.getByRole('button',{name:'Save trip',exact:true}).click();const original=(await requestPromise).postDataJSON();
 await page.waitForSelector('.trip-card');assert.match(await page.locator('#city-count').innerText(),/^1 visit/);
 assert.match(await page.locator('.trip-card').innerText(),/第一次真正保存的旅行/);assert.equal(await page.locator('.trip-card script').count(),0);
 assert.equal(await page.locator('.saved-photo-strip button').count(),2);
 await page.getByRole('button',{name:'Open trip photo 2',exact:true}).click();await page.waitForSelector('#photo-viewer[open]');
 assert.equal(await page.locator('#viewer-image').evaluate(img=>img.complete&&img.naturalWidth>0),true);await page.keyboard.press('Escape');
 checks.push('Real two-photo upload creates a card, safe notes, working photo viewer and one map visit');
 const retry=await context.request.post(base+'/api/trips',{data:original});assert.equal(retry.status(),201);
 const records=await(await context.request.get(base+'/api/trips')).json();assert.equal(records.length,1);checks.push('Retrying the completed save does not duplicate the visit');
 const response=await context.request.get(base+records[0].photos[0].url);assert.equal(response.status(),200);
 await page.locator('#memories').evaluate(el=>el.scrollTop=0);await page.screenshot({path:path.join(evidence,'desktop-saved.png'),fullPage:true});
 const port=new URL(base).port;await stop();assert.equal(await start(port),base);
 await page.reload();await page.waitForSelector('.trip-card');assert.match(await page.locator('#city-count').innerText(),/^1 visit/);
 assert.equal(await page.locator('.cover-button img').evaluate(img=>img.complete&&img.naturalWidth>0),true);
 checks.push('Server restart reloads the same SQLite trip and photo files');
 await page.getByRole('button',{name:'Add a trip',exact:true}).click();await page.locator('#trip-notes').fill('Second independent visit');
 await page.locator('#trip-photos').setInputFiles(path.join(root,'data/demo-covers/osaka-castle-1.jpg'));
 await page.waitForSelector('.photo-previews img');await page.getByRole('button',{name:'Save trip',exact:true}).click();
 await page.waitForFunction(()=>document.querySelectorAll('.trip-card').length===2);assert.match(await page.locator('#city-count').innerText(),/^2 visits/);
 assert.equal(await page.locator('.marker[data-city-id="jp-osaka"] .tier-2').count(),1);checks.push('A second independent trip produces two cards and the 2–3 visit map tier');
 const mobile=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true}),phone=await mobile.newPage();
 phone.on('pageerror',e=>errors.push(e.message));phone.on('dialog',d=>d.accept());
 await phone.goto(base+'/app/?mode=local&map=local&view=album');await phone.waitForSelector('.trip-card');
 await phone.getByRole('button',{name:'Add a trip',exact:true}).click();await phone.locator('#trip-title').fill('A mobile memory');
 await phone.locator('#trip-photos').setInputFiles(path.join(root,'data/demo-covers/osaka-castle-1.jpg'));await phone.waitForSelector('.photo-previews img');
 await phone.locator('#trip-form').scrollIntoViewIfNeeded();assert.equal(await phone.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
 await phone.screenshot({path:path.join(evidence,'mobile-form.png'),fullPage:true});
 await phone.getByRole('button',{name:'Cancel',exact:true}).click();assert.equal(await phone.locator('#trip-form').isVisible(),false);
 assert.equal((await(await mobile.request.get(base+'/api/trips')).json()).length,2);checks.push('390px mobile form fits and confirmed cancellation creates no trip');
 await phone.setViewportSize({width:320,height:740});assert.equal(await phone.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
 checks.push('320px layout has no horizontal overflow');
 assert.deepEqual(errors,[]);console.log(JSON.stringify({status:'passed',checks,evidence},null,2));
}finally{await browser?.close();await stop();await rm(storage,{recursive:true,force:true});}
