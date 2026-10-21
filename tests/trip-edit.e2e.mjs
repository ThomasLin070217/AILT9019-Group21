/** Real saved-card editing against an isolated server and album. */
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {once} from 'node:events';
import {mkdtemp,mkdir,rm,readFile,writeFile} from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
const {chromium}=await import(process.env.PLAYWRIGHT_MODULE||'playwright');
const root=path.resolve(new URL('..',import.meta.url).pathname),storage=await mkdtemp(path.join(os.tmpdir(),'travel-edit-test-'));
const evidence=process.env.EVIDENCE_DIR||path.join(root,'.context/feature-02');await mkdir(evidence,{recursive:true});
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
 const context=await browser.newContext({viewport:{width:1440,height:1100}}),page=await context.newPage();
 context.setDefaultTimeout(15000);context.setDefaultNavigationTimeout(20000);
 page.on('pageerror',e=>errors.push(e.message));page.on('dialog',d=>d.accept());
 const photo=(await readFile(path.join(root,'data/demo-covers/osaka-castle-1.jpg'))).toString('base64');
 const create=async(title,date)=>{const response=await context.request.post(base+'/api/trips',{data:{request_id:crypto.randomUUID(),city_id:'jp-osaka',title,trip_date:date,notes:'A walk around Osaka Castle.',photos:[{data:photo}]}});assert.equal(response.status(),201);return response.json();};
 const trip=await create('An autumn afternoon','2026-10-19');await create('Another independent visit','2026-10-20');
 const card=()=>page.locator(`[data-trip-id="${trip.id}"]`),form=()=>card().locator('.real-trip-editor');
 const records=async()=> (await context.request.get(base+'/api/trips')).json();
 const originalPhoto=await(await context.request.get(base+trip.photos[0].url)).body();
 await page.goto(base+'/app/?mode=local&map=local');await page.waitForSelector('.trip-card');
 await card().getByRole('button',{name:'Edit trip',exact:true}).click();
 assert.equal(await form().getByLabel('Title',{exact:true}).inputValue(),trip.title);
 await form().getByLabel('Title',{exact:true}).fill('Osaka in the autumn light');await form().getByLabel('Trip date',{exact:true}).fill('2026-10-21');await form().getByLabel('Your notes',{exact:true}).fill('在大阪城散步，记住了秋天的阳光。');
 await page.locator('.city-button[data-city-id="jp-tokyo"]').click();await page.locator('.city-button[data-city-id="jp-osaka"]').click();
 assert.equal(await form().getByLabel('Title',{exact:true}).inputValue(),'Osaka in the autumn light');
 await page.locator('#view-album').click();await page.locator('#view-map').click();assert.equal(await form().getByLabel('Trip date',{exact:true}).inputValue(),'2026-10-21');
 await page.reload();await page.waitForSelector('.real-trip-editor');assert.equal(await form().getByLabel('Your notes',{exact:true}).inputValue(),'在大阪城散步，记住了秋天的阳光。');
 checks.push('Title, date and notes are prefilled; drafts survive city/view switches and tab reload');
 await page.locator('#view-album').click();await form().screenshot({path:path.join(evidence,'desktop-editor.png')});
 await page.route('**/api/trips/*',route=>route.request().method()==='PATCH'?route.fulfill({status:500,json:{error:'Test: storage unavailable.'}}):route.continue());
 await form().getByRole('button',{name:'Save changes',exact:true}).click();await page.waitForFunction(()=>document.querySelector('.real-trip-editor .form-error')?.textContent.includes('storage unavailable'));
 assert.equal(await form().getByLabel('Title',{exact:true}).inputValue(),'Osaka in the autumn light');assert.equal((await records()).find(row=>row.id===trip.id).title,trip.title);
 checks.push('A failed edit keeps the draft and leaves the saved trip unchanged');await page.unroute('**/api/trips/*');
 const savedRequest=page.waitForRequest(r=>r.method()==='PATCH');await form().getByRole('button',{name:'Save changes',exact:true}).click();const patch=(await savedRequest).postDataJSON();
 await form().waitFor({state:'detached'});const saved=(await records()).find(row=>row.id===trip.id);
 assert.equal(saved.title,'Osaka in the autumn light');assert.equal(saved.trip_date,'2026-10-21');assert.deepEqual(saved.photos,trip.photos);assert.equal(saved.id,trip.id);assert.equal((await records()).length,2);
 assert.equal(await page.locator('.trip-card').first().getAttribute('data-trip-id'),trip.id);assert.match(await page.locator('#city-count').innerText(),/^2 visits/);
 assert.deepEqual(await(await context.request.get(base+trip.photos[0].url)).body(),originalPhoto);
 await card().screenshot({path:path.join(evidence,'desktop-saved.png')});
 checks.push('Saving updates text/date and card order without changing ID, photo bytes or two-visit count');
 const retry=await context.request.patch(base+'/api/trips/'+trip.id,{data:patch});assert.equal(retry.status(),200);assert.equal((await records()).length,2);assert.equal((await retry.json()).revision,2);
 checks.push('Retrying the completed edit is idempotent');
 await card().getByRole('button',{name:'Edit trip',exact:true}).click();await form().getByLabel('Title',{exact:true}).fill('Do not save this');
 await form().getByRole('button',{name:'Cancel',exact:true}).click();await form().waitFor({state:'detached'});assert.equal((await records()).find(row=>row.id===trip.id).title,saved.title);
 checks.push('Confirmed cancel discards only the draft');
 await card().getByRole('button',{name:'Edit trip',exact:true}).click();await form().getByLabel('Your notes',{exact:true}).fill('My draft from this tab');
 const other=await context.request.patch(base+'/api/trips/'+trip.id,{data:{title:'A title saved in another tab',expected_revision:2}});assert.equal(other.status(),200);
 await form().getByRole('button',{name:'Save changes',exact:true}).click();await page.waitForFunction(()=>document.querySelector('.real-trip-editor .form-error')?.textContent.includes('another tab'));
 assert.equal(await form().getByLabel('Your notes',{exact:true}).inputValue(),'My draft from this tab');assert.equal((await records()).find(row=>row.id===trip.id).title,'A title saved in another tab');
 await form().getByRole('button',{name:'Reload saved version',exact:true}).click();await form().waitFor({state:'detached'});assert.match(await card().innerText(),/A title saved in another tab/);
 checks.push('Stale-tab conflict preserves both the newer saved record and the local draft until explicit reload');
 const mobile=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true}),phone=await mobile.newPage();phone.on('pageerror',e=>errors.push(e.message));phone.on('dialog',d=>d.accept());
 await phone.goto(base+'/app/?mode=local&map=local&view=album');await phone.waitForSelector('.trip-card');const mc=phone.locator(`[data-trip-id="${trip.id}"]`),mf=mc.locator('.real-trip-editor');
 await mc.getByRole('button',{name:'Edit trip',exact:true}).click();await mf.getByLabel('Title',{exact:true}).fill('A memory edited on mobile');
 await mf.getByLabel('Your notes',{exact:true}).fill('手机编辑后的随笔。');await mf.screenshot({path:path.join(evidence,'mobile-editor.png')});
 assert.equal(await phone.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
 await phone.setViewportSize({width:320,height:740});assert.equal(await phone.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
 await mf.getByRole('button',{name:'Save changes',exact:true}).click();await mf.waitFor({state:'detached'});assert.match(await mc.innerText(),/手机编辑后的随笔/);assert.match(await phone.locator('#city-count').innerText(),/^2 visits/);
 checks.push('390px and 320px editing fits the screen and saves on mobile without adding visits');
 const port=new URL(base).port;await stop();await start(port);await page.reload();await page.waitForSelector('.trip-card');
 assert.match(await card().innerText(),/A memory edited on mobile/);assert.match(await page.locator('#city-count').innerText(),/^2 visits/);assert.equal((await records()).length,2);
 assert.deepEqual(errors,[]);checks.push('Edited data and original photos survive a server restart; no JavaScript errors');
 const result={status:'passed',checks,evidence};await writeFile(path.join(evidence,'results.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));
}catch(error){const failedPage=browser?.contexts()[0]?.pages()[0];if(failedPage){await failedPage.screenshot({path:path.join(evidence,'failure.png'),fullPage:true}).catch(()=>{});console.error((await failedPage.locator('body').innerText().catch(()=>'' )).slice(-7000));}throw error;}finally{await browser?.close();await stop();await rm(storage,{recursive:true,force:true});}
