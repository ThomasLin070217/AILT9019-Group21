// Diagnostic audit: records observations, including known defects; not a passing regression suite.
const {chromium}=await import(process.env.PLAYWRIGHT_MODULE||'playwright');
import {writeFileSync,mkdirSync} from 'node:fs';
const dir=process.env.EVIDENCE_DIR||'/tmp/travel-map-audit';
const base=process.env.BASE_URL||'http://127.0.0.1:8019';mkdirSync(dir,{recursive:true});
const browser=await chromium.launch({headless:true,...(process.env.CHROMIUM_EXECUTABLE?{executablePath:process.env.CHROMIUM_EXECUTABLE}:{})});
const results={viewports:[],notes:[],gestures:{}};
try {
 for(const width of [320,390,540,541,768,851,1024,1440]){
 const ctx=await browser.newContext({viewport:{width,height:844},isMobile:width<541,hasTouch:width<541});const p=await ctx.newPage();await p.goto(base+'/app/');await p.waitForSelector('.city-button');
 results.viewports.push(await p.evaluate(()=>({width:innerWidth,documentWidth:document.documentElement.scrollWidth,cardTop:Math.round(document.querySelector('.memory-panel').getBoundingClientRect().top),smallTargets:[...document.querySelectorAll('button,input,select,summary')].filter(e=>e.getClientRects().length&&!e.disabled).map(e=>{const r=e.getBoundingClientRect();return {label:e.getAttribute('aria-label')||e.textContent||e.id,w:Math.round(r.width),h:Math.round(r.height)}}).filter(r=>r.w<44||r.h<44)})));
 if(width===390){
 await p.locator('.marker[data-city-id="jp-tokyo"] .pin').tap();results.gestures.tapSelect=await p.locator('#city-name').innerText();results.gestures.cardVisibleAfterTap=await p.locator('.memory-panel').evaluate(e=>{const r=e.getBoundingClientRect();return r.top<innerHeight&&r.bottom>0});
 await p.locator('#zoom-in').tap();const before=await p.locator('#map').getAttribute('viewBox'),r=await p.locator('#map').boundingBox(),cdp=await ctx.newCDPSession(p);
 const x=r.x+r.width*.3,y=r.y+r.height*.7;
 await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x,y}]});for(let i=1;i<=6;i++)await cdp.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:x+8*i,y:y-4*i}]});await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
 results.gestures.touchPanChangedView=before!==await p.locator('#map').getAttribute('viewBox');results.gestures.dragCleared=!await p.locator('#map').evaluate(e=>e.classList.contains('dragging'));
 }
 if(width===1440){
 await p.getByRole('button',{name:'Edit sample text'}).first().click();await p.locator('textarea').fill('UNSAVED_AUDIT_DRAFT');await p.locator('.city-button[data-city-id="jp-tokyo"]').click();await p.locator('.city-button[data-city-id="jp-osaka"]').click();results.notes.push({unsavedDraftSurvivesCitySwitch:(await p.locator('#trip-list').innerText()).includes('UNSAVED_AUDIT_DRAFT')});
 const trips=await p.evaluate(async()=>await (await fetch('../data/demo-trips.json')).json());trips[0].title='LongTitle'.repeat(22);await p.evaluate(t=>localStorage.setItem('travel-memory-map.demo.v1',JSON.stringify(t)),trips);await p.reload();await p.waitForSelector('.city-button');results.notes.push(await p.evaluate(()=>({longTitleDocumentOverflow:document.documentElement.scrollWidth>innerWidth,longTitlePanelOverflow:document.querySelector('.memory-panel').scrollWidth>document.querySelector('.memory-panel').clientWidth})));
 await p.screenshot({path:dir+'/long-title.png',fullPage:true});
 }
 await ctx.close();
 }
 writeFileSync(dir+'/audit-results.json',JSON.stringify(results,null,2));console.log(JSON.stringify(results));
}finally{await browser.close()}
