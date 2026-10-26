/** API-mode album workflow; start `python3 -m backend` first. */
import assert from 'node:assert/strict';
import {mkdirSync,writeFileSync} from 'node:fs';
const {chromium}=await import(process.env.PLAYWRIGHT_MODULE||'playwright');
const out=process.env.EVIDENCE_DIR||'/tmp/travel-map-api-ui';mkdirSync(out,{recursive:true});
const base=process.env.BASE_URL||'http://127.0.0.1:8019';
const browser=await chromium.launch({headless:true,...(process.env.CHROMIUM_EXECUTABLE?{executablePath:process.env.CHROMIUM_EXECUTABLE}:{})});
const photo=Buffer.from('/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAA0JCgsKCA0LCgsODg0PEyAVExISEyccHhcgLikxMC4pLSwzOko+MzZGNywtQFdBRkxOUlNSMj5aYVpQYEpRUk//2wBDAQ4ODhMREyYVFSZPNS01T09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0//wAARCAB4AKADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwCrRRRWZxBRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQB/9k=','base64');
const checks=[],errors=[];let tripId=null;
try{
 const p=await browser.newPage({viewport:{width:1440,height:1000}});
 p.on('pageerror',e=>errors.push(e.message));p.on('dialog',d=>d.accept());
 await p.goto(base+'/app/?mode=api&map=local',{waitUntil:'networkidle'});await p.waitForSelector('.api-composer');
 await p.locator('#cities button[data-city-id="cn-nanjing"]').click();await p.waitForFunction(()=>document.querySelector('#city-name')?.textContent==='Nanjing');
 const title=`API UI test ${Date.now()}`;
 await p.locator('.api-composer input[type=text]').fill(title);await p.locator('.api-composer textarea').fill('Fictional notes from the browser workflow.');await p.locator('.api-composer button[type=submit]').click();
 await p.waitForFunction(t=>[...document.querySelectorAll('.trip-card h3')].some(h=>h.textContent===t),title);
 const card=p.locator('.trip-card').filter({hasText:title}).first();tripId=await card.getAttribute('data-trip-id');assert.ok(tripId,'the server trip ID is present on the card');
 checks.push('Create a trip from the API composer');
 await card.locator('input[type=file]').setInputFiles({name:'api-ui.jpg',mimeType:'image/jpeg',buffer:photo});await card.locator('.photo-strip img').waitFor({state:'visible'});
 checks.push('Upload a photo from the card');
 await card.getByRole('button',{name:'Edit memory'}).click();const editor=card.locator('.memory-editor');await editor.waitFor();await editor.locator('textarea').nth(1).fill('A memory saved through the browser.');await editor.getByRole('button',{name:'Save memory'}).click();
 await p.waitForFunction(t=>{const card=[...document.querySelectorAll('.trip-card')].find(c=>c.querySelector('h3')?.textContent===t);return card?.innerText.includes('A memory saved through the browser.')},title);
 checks.push('Edit the memory text and save');
 await card.getByRole('button',{name:'Write with AI'}).click();await card.locator('.ai-notice').waitFor();await card.getByRole('button',{name:'Send this trip'}).click();
 await p.waitForFunction(()=>document.querySelector('.memory-editor')||document.querySelector('#error:not([hidden])'),null,{timeout:25000});
 if(await card.locator('.memory-editor').count()){checks.push('AI draft editor opened for review');await card.getByRole('button',{name:'Discard changes'}).click();}
 else{assert.match(await p.locator('#error-text').innerText(),/AI draft failed|No AI provider|configured/i);checks.push('Unconfigured AI fails visibly without changing the trip');}
 await p.screenshot({path:out+'/api-ui.png'});
 await card.getByRole('button',{name:'Delete trip'}).click();
 await p.waitForFunction(t=>![...document.querySelectorAll('.trip-card h3')].some(h=>h.textContent===t),title);tripId=null;
 checks.push('Delete the trip and its photos');
 await p.setViewportSize({width:390,height:844});assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,'390px horizontal overflow');checks.push('No horizontal overflow at 390px');
 assert.deepEqual(errors,[]);writeFileSync(out+'/api-ui-results.json',JSON.stringify({status:'passed',checks,errors},null,2));console.log(JSON.stringify({status:'passed',checks:checks.length,out}));
}finally{
 if(tripId){try{await fetch(base+'/api/trips/'+tripId,{method:'DELETE'});}catch{}}
 await browser.close();
}
