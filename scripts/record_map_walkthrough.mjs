/** Record a genuine local map/count walkthrough using disposable, labelled test trips. No AI calls. */
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {once} from 'node:events';
import {mkdtemp,mkdir,readFile,writeFile,rm} from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
const {chromium}=await import(process.env.PLAYWRIGHT_MODULE||'playwright');
const root=path.resolve(new URL('..',import.meta.url).pathname),storage=await mkdtemp(path.join(os.tmpdir(),'travel-map-walkthrough-'));
const evidence=path.resolve(process.env.EVIDENCE_DIR||path.join(root,'.context/map-walkthrough'));await mkdir(evidence,{recursive:true});
let server,browser;
try{
 server=spawn('python3',['-u','serve.py','--port','0','--data-dir',storage],{cwd:root,stdio:['ignore','pipe','pipe']});
 const base=await new Promise((resolve,reject)=>{let output='';const timer=setTimeout(()=>reject(new Error('Server startup timed out')),10000);server.stdout.on('data',chunk=>{output+=chunk;const match=output.match(/http:\/\/127\.0\.0\.1:\d+/);if(match){clearTimeout(timer);resolve(match[0]);}});server.once('error',reject);server.once('exit',()=>{clearTimeout(timer);reject(new Error('Server stopped'));});});
 browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_EXECUTABLE||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
 const context=await browser.newContext({viewport:{width:1440,height:1000},recordVideo:{dir:path.join(evidence,'raw-video'),size:{width:1440,height:1000}}});
 const page=await context.newPage(),video=page.video(),checks=[];const errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('dialog',d=>d.accept());
 const count=async(n,tier)=>{await page.waitForFunction(expected=>document.querySelector('#city-count').textContent.startsWith(`${expected} visit`),n);assert.equal(await page.locator('.trip-card').count(),n);assert.equal(await page.locator(`.marker[data-city-id="jp-osaka"] .tier-${tier}`).count(),1);};
 await page.goto(base+'/app/?mode=local&map=local');await count(0,0);await page.waitForTimeout(1000);
 for(let n=1;n<=4;n++){
  await page.locator('#new-trip').click();await page.locator('#trip-title').fill(`Demo visit ${n} — fictional test data`);await page.locator('#trip-date').fill(`2026-10-${String(16+n).padStart(2,'0')}`);await page.locator('#trip-notes').fill('Public example photograph and fictional notes for a visit-count demonstration.');await page.locator('#trip-photos').setInputFiles(path.join(root,'data/demo-covers/osaka-castle-2.jpg'));await page.waitForSelector('.photo-previews img');await page.locator('#save-trip').click();await count(n,n===1?1:n<4?2:3);await page.locator('#memories').evaluate(el=>el.scrollTop=0);await page.waitForTimeout(1200);
 }
 checks.push('Real form submissions create four separate trips; counts 0→1→2→3→4 and tiers 0→1→2→2→3 match');
 await page.screenshot({path:path.join(evidence,'four-visits.png'),fullPage:true});
 let trip=(await(await context.request.get(base+'/api/trips')).json()).at(-1);let card=page.locator(`[data-trip-id="${trip.id}"]`);
 await card.getByRole('button',{name:'Edit trip',exact:true}).click();await card.getByLabel('Title',{exact:true}).fill('Demo visit 4 — edited, still one visit');await card.getByRole('button',{name:'Save changes',exact:true}).click();await card.locator('.real-trip-editor').waitFor({state:'detached'});await count(4,3);await page.waitForTimeout(1200);
 checks.push('Editing the existing title keeps four IDs, four cards and tier3');
 trip=(await(await context.request.get(base+'/api/trips')).json()).find(t=>t.id===trip.id);const response=await context.request.patch(base+'/api/trips/'+trip.id,{data:{expected_revision:trip.revision,memory_text:'Manually reviewed text for this test; no model request was made.'}});assert.equal(response.status(),200);await page.locator('#refresh').click();await page.waitForFunction(()=>document.querySelector('#trip-list').textContent.includes('Manually reviewed text'));await count(4,3);
 checks.push('Saving reviewed memory through the real update API retains identity/count; live AI generation is covered by the separate recorded live check');
 for(const n of [3,2,1,0]){
  card=page.locator('.trip-card').first();await card.getByRole('button',{name:'Delete trip',exact:true}).click();await card.getByRole('button',{name:'Delete permanently',exact:true}).click();await count(n,n===0?0:n===1?1:2);await page.locator('#memories').evaluate(el=>el.scrollTop=0);await page.waitForTimeout(1000);
 }
 checks.push('Confirmed deletions produce counts 3→2→1→0 and tiers2→2→1→0');await page.screenshot({path:path.join(evidence,'zero-visits.png'),fullPage:true});await page.waitForTimeout(1000);assert.deepEqual(errors,[]);checks.push('No uncaught browser errors; no user album or real AI request used');
 await context.close();await video.saveAs(path.join(evidence,'walkthrough.webm'));
 const result={status:'passed',checks,real_backend:true,live_ai:false,fixture:'data/demo-covers/osaka-castle-2.jpg; public licensed photo, fictional test trips',video:'walkthrough.webm'};await writeFile(path.join(evidence,'results.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
}finally{await browser?.close();if(server?.exitCode===null){const done=once(server,'exit');server.kill('SIGTERM');await done;}await rm(storage,{recursive:true,force:true});}
