/** Deletion confirmation, real storage, map thresholds and failure recovery. */
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {once} from 'node:events';
import {mkdtemp,mkdir,rm,readFile,writeFile} from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
const {chromium}=await import(process.env.PLAYWRIGHT_MODULE||'playwright');
const root=path.resolve(new URL('..',import.meta.url).pathname),storage=await mkdtemp(path.join(os.tmpdir(),'travel-delete-test-'));
const evidence=process.env.EVIDENCE_DIR||path.join(root,'.context/feature-03');await mkdir(evidence,{recursive:true});
let server,browser;
async function start(port=0){
 server=spawn('python3',['serve.py','--port',String(port),'--data-dir',storage],{cwd:root,stdio:['ignore','pipe','pipe']});
 return new Promise((resolve,reject)=>{
  let text='';const timer=setTimeout(()=>reject(new Error('Server did not start')),10000);
  server.stdout.on('data',chunk=>{text+=chunk;const url=text.match(/http:\/\/127\.0\.0\.1:\d+/);if(url){clearTimeout(timer);resolve(url[0]);}});
  server.once('error',reject);server.once('exit',code=>{clearTimeout(timer);reject(new Error(`Server exited ${code}`));});
 });
}
async function stop(){if(server&&server.exitCode===null){const done=once(server,'exit');server.kill('SIGTERM');await done;}}
try{
 const base=await start(),checks=[],errors=[];
 browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_EXECUTABLE||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
 const context=await browser.newContext({viewport:{width:1440,height:1100}}),page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));page.on('dialog',d=>d.accept());
 const photo=(await readFile(path.join(root,'data/demo-covers/osaka-castle-1.jpg'))).toString('base64');
 const create=async(title,city='jp-osaka')=>{const response=await context.request.post(base+'/api/trips',{data:{request_id:crypto.randomUUID(),city_id:city,title,trip_date:'2026-10-20',notes:'A memory saved for this deletion test.',photos:[{data:photo}]}});assert.equal(response.status(),201);return response.json();};
 const trips=[];for(const title of ['An autumn afternoon','A second visit','A third visit','A fourth visit'])trips.push(await create(title));const other=await create('A separate city','jp-tokyo');
 const card=id=>page.locator(`[data-trip-id="${id}"]`),panel=id=>card(id).locator('.delete-trip-confirmation');
 const records=async()=> (await context.request.get(base+'/api/trips')).json();
 const count=async(n,tier)=>{assert.match(await page.locator('#city-count').innerText(),new RegExp(`^${n} visits?`));assert.equal(await page.locator(`.marker[data-city-id="jp-osaka"] .tier-${tier}`).count(),1);};
 await page.goto(base+'/app/?mode=local&map=local');await page.waitForSelector('.trip-card');await count(4,3);
 const target=trips[0];
 await card(target.id).getByRole('button',{name:'Edit trip',exact:true}).click();await card(target.id).getByLabel('Your notes',{exact:true}).fill('Keep this unsaved edit if deletion is cancelled.');
 await card(target.id).getByRole('button',{name:'Delete trip',exact:true}).click();assert.match(await panel(target.id).innerText(),/unsaved edits/);
 assert.equal(await panel(target.id).getByRole('button',{name:'Keep trip',exact:true}).evaluate(el=>el===document.activeElement),true);
 await panel(target.id).getByRole('button',{name:'Keep trip',exact:true}).click();assert.equal(await card(target.id).getByLabel('Your notes',{exact:true}).inputValue(),'Keep this unsaved edit if deletion is cancelled.');assert.equal((await records()).length,5);await count(4,3);
 checks.push('Delete requires a second explicit action; Keep trip preserves the record, photos, count and edit draft');
 await card(target.id).getByRole('button',{name:'Delete trip',exact:true}).click();await panel(target.id).screenshot({path:path.join(evidence,'desktop-confirmation.png')});
 await page.route('**/api/trips/*',route=>route.request().method()==='DELETE'?route.fulfill({status:500,json:{error:'Test: storage unavailable.'}}):route.continue());
 await panel(target.id).getByRole('button',{name:'Delete permanently',exact:true}).click();await page.waitForFunction(()=>document.querySelector('.delete-trip-confirmation .form-error')?.textContent.includes('storage unavailable'));
 assert.equal((await records()).length,5);assert.equal((await context.request.get(base+target.photos[0].url)).status(),200);await count(4,3);
 assert.equal(await card(target.id).getByLabel('Your notes',{exact:true}).inputValue(),'Keep this unsaved edit if deletion is cancelled.');checks.push('Failed delete preserves the saved trip, photos, map count and unsaved editor');await page.unroute('**/api/trips/*');
 await panel(target.id).getByRole('button',{name:'Delete permanently',exact:true}).click();await card(target.id).waitFor({state:'detached'});await count(3,2);
 assert.equal((await context.request.get(base+target.photos[0].url)).status(),404);assert.equal((await records()).length,4);assert.ok((await records()).some(row=>row.id===other.id));
 assert.equal(await page.evaluate(id=>JSON.parse(sessionStorage.getItem('travel-memory-map.local-edits.v1')).some(([key])=>key===id),target.id),false);
 checks.push('Confirmed delete removes the target, local photo access and its draft; 4 visits become 3 and other trips remain');
 const retry=await context.request.delete(base+'/api/trips/'+target.id,{data:{expected_revision:1}});assert.equal(retry.status(),200);assert.equal((await records()).length,4);checks.push('Repeated deletion is idempotent and never removes another visit');
 const stale=trips[1];const update=await context.request.patch(base+'/api/trips/'+stale.id,{data:{title:'Updated in another tab',expected_revision:1}});assert.equal(update.status(),200);
 await card(stale.id).getByRole('button',{name:'Delete trip',exact:true}).click();await panel(stale.id).getByRole('button',{name:'Delete permanently',exact:true}).click();await page.waitForFunction(()=>document.querySelector('.delete-trip-confirmation .form-error')?.textContent.includes('another tab'));
 assert.equal((await records()).length,4);await panel(stale.id).getByRole('button',{name:'Keep trip',exact:true}).click();await page.locator('#refresh').click();await page.waitForFunction(()=>document.querySelector('#trip-list').textContent.includes('Updated in another tab'));
 checks.push('A stale tab cannot delete a newer version without refreshing and reviewing it');
 await card(stale.id).getByRole('button',{name:'Delete trip',exact:true}).click();
 await page.route('**/api/trips/*',async route=>{if(route.request().method()==='DELETE'){await route.fetch();await route.abort('failed');}else await route.continue();});
 await panel(stale.id).getByRole('button',{name:'Delete permanently',exact:true}).click();await page.waitForFunction(()=>document.querySelector('.delete-trip-confirmation .form-error')?.textContent.includes('interrupted'));
 assert.equal((await records()).length,3);await page.unroute('**/api/trips/*');await panel(stale.id).getByRole('button',{name:'Delete permanently',exact:true}).click();await card(stale.id).waitFor({state:'detached'});await count(2,2);
 checks.push('Lost response after a committed delete can be retried safely and reconciles the displayed count');
 for(const [trip,n,tier] of [[trips[2],1,1],[trips[3],0,0]]){
  await card(trip.id).getByRole('button',{name:'Delete trip',exact:true}).click();await panel(trip.id).getByRole('button',{name:'Delete permanently',exact:true}).click();await card(trip.id).waitFor({state:'detached'});await count(n,tier);
 }
 assert.match(await page.locator('#trip-list').innerText(),/Your first memory/);assert.match(await page.locator('#progress').innerText(),/1 city visited/);await page.screenshot({path:path.join(evidence,'desktop-empty.png'),fullPage:true});checks.push('2→1→0 recalculates brightness and returns the city to its empty unvisited state');
 const mobileTrip=await create('A mobile memory');const mobile=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true}),phone=await mobile.newPage();phone.on('pageerror',e=>errors.push(e.message));
 await phone.goto(base+'/app/?mode=local&map=local&view=album');await phone.waitForSelector('.trip-card');const mc=phone.locator(`[data-trip-id="${mobileTrip.id}"]`);
 await mc.getByRole('button',{name:'Delete trip',exact:true}).click();await mc.locator('.delete-trip-confirmation').screenshot({path:path.join(evidence,'mobile-confirmation.png')});assert.equal(await phone.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
 await phone.setViewportSize({width:320,height:740});assert.equal(await phone.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
 await mc.getByRole('button',{name:'Delete permanently',exact:true}).click();await mc.waitFor({state:'detached'});assert.match(await phone.locator('#city-count').innerText(),/^0 visits/);checks.push('390px and 320px confirmation fits; deleting the last trip works on mobile');
 const port=new URL(base).port;await stop();await start(port);await page.reload();await page.waitForSelector('.city-button');await count(0,0);assert.deepEqual((await records()).map(row=>row.id),[other.id]);assert.equal((await context.request.get(base+target.photos[0].url)).status(),404);
 assert.deepEqual(errors,[]);checks.push('Deleted trips stay deleted after restart, other-city records remain, and no JavaScript errors occur');
 const result={status:'passed',checks,evidence};await writeFile(path.join(evidence,'results.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));
}finally{await browser?.close();await stop();await rm(storage,{recursive:true,force:true});}
