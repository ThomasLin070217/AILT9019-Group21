import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {countVisits,visitTier,updateTrip,cityTrips,filterCities,validateTrip,initialView,zoomView,clampView,project} from '../app/domain.mjs';
import {DemoRepository,ApiRepository,STORAGE_KEY,DraftStore,photoURL} from '../app/repository.mjs';
const cities=JSON.parse(readFileSync(new URL('../data/cities.json',import.meta.url)));
const seed=JSON.parse(readFileSync(new URL('../data/demo-trips.json',import.meta.url)));
const storage=()=>{const records=new Map();return {getItem:k=>records.get(k)??null,setItem:(k,v)=>records.set(k,v)};};
test('a saved trip ID, not photos or repeated snapshots, defines a visit',()=>{
 const original=seed[0];const updated={...original,photos:[{id:'a'},{id:'b'}],memory_text:'Regenerated text'};
 assert.equal(countVisits([original,updated]).get(original.city_id),1);
 const repeated={...original,id:'another-trip'};
 assert.equal(countVisits([original,updated,repeated]).get(original.city_id),2);
});
test('brightness changes only at 1, 2 and 4 visits',()=>{
 assert.deepEqual([0,1,2,3,4,5,100].map(visitTier),[0,1,2,2,3,3,3]);
 assert.throws(()=>visitTier(-1));assert.throws(()=>visitTier(1.5));
});
test('create, edit, reconstruct repository, and remove preserve the visit invariant',async()=>{
 const store=storage();const repo=new DemoRepository(cities,seed,store);
 const before=await repo.list();const after=await repo.add('jp-osaka');
 assert.equal(countVisits(after).get('jp-osaka'),3);
 const newest=after.at(-1);await repo.edit(newest.id,{memory_text:'New card text',photos:[{id:'p1'}]});
 const reloaded=await new DemoRepository(cities,seed,store).list();
 assert.equal(reloaded.length,before.length+1);assert.equal(countVisits(reloaded).get('jp-osaka'),3);
 assert.equal(reloaded.find(t=>t.id===newest.id).memory_text,'New card text');
 const removed=await repo.remove(newest.id);assert.equal(countVisits(removed).get('jp-osaka'),2);
});
test('card edits cannot change identity; invalid dates and cities do not persist',async()=>{
 const repo=new DemoRepository(cities,seed,storage());
 assert.throws(()=>updateTrip(seed,seed[0].id,{id:'new'},cities));
 assert.throws(()=>updateTrip(seed,seed[0].id,{city_id:'cn-beijing'},cities));
 await assert.rejects(repo.edit(seed[0].id,{trip_date:'2026-02-31'}));
 await assert.rejects(repo.add('unsupported-city'));
 assert.deepEqual(await repo.list(),seed);
});
test('corrupt and unavailable storage surface errors instead of overwriting or claiming a save',async()=>{
 const store=storage();store.setItem(STORAGE_KEY,'not json');const repo=new DemoRepository(cities,seed,store);
 await assert.rejects(repo.list());assert.equal(store.getItem(STORAGE_KEY),'not json');
 await repo.reset();assert.deepEqual(await repo.list(),seed);
 const unavailable={getItem:()=>null,setItem:()=>{throw new Error('quota exceeded');}};
 await assert.rejects(new DemoRepository(cities,seed,unavailable).add('jp-osaka'),/quota exceeded/);
});
test('city filtering supports native names, regions and visited-only without altering counts',()=>{
 assert.deepEqual(filterCities(cities,seed,{query:'大阪'}).map(c=>c.id),['jp-osaka']);
 assert.equal(filterCities(cities,seed,{region:'Japan',visitedOnly:true}).length,1);
 assert.equal(filterCities(cities,seed,{query:'no such city'}).length,0);
 assert.equal(countVisits(seed).get('hk-hong-kong'),4);
});
test('city cards are separate, newest-first and selected-city-only',()=>{
 const rows=cityTrips(seed,'jp-osaka');assert.equal(rows.length,2);
 assert.equal(rows[0].trip_date,'2026-05-16');assert.notEqual(rows[0].id,rows[1].id);
});
test('all city IDs are unique, licensed points fit initial view, and fixtures validate',()=>{
 assert.equal(cities.length,19);assert.equal(new Set(cities.map(c=>c.id)).size,19);
 const v=initialView();
 for(const city of cities){const [x,y]=project(city.longitude,city.latitude);assert.ok(x>=v.x&&x<=v.x+v.width&&y>=v.y&&y<=v.y+v.height);assert.ok(city.source_ne_id);}
 seed.forEach(t=>validateTrip(t,cities));
});
test('zoom/pan stays within catalogue bounds and zoom limits',()=>{
 const full=initialView();let v=full;
 for(let i=0;i<30;i++)v=zoomView(v,.65);
 assert.equal(v.width,full.width/8);
 v=clampView({...v,x:-10000,y:10000});assert.equal(v.x,full.x);assert.equal(v.y,full.y+full.height-v.height);
 for(let i=0;i<30;i++)v=zoomView(v,1/.65);
 assert.equal(v.width,full.width);
});
test('API adapter reads backend data and never silently substitutes demo trips',async()=>{
 const old=globalThis.fetch;
 try {
  globalThis.fetch=async url=>{assert.equal(url,'/api/trips');return {ok:true,json:async()=>[seed[0]]};};
  assert.deepEqual(await new ApiRepository(cities).list(),[seed[0]]);
  globalThis.fetch=async()=>({ok:false,status:503});await assert.rejects(new ApiRepository(cities).list(),/503/);
 }finally{globalThis.fetch=old;}
});


test('drafts survive reconstruction but never enter saved visit records',()=>{
 const store=storage(),drafts=new DraftStore(store);drafts.set('demo-01','A draft');
 const reloaded=new DraftStore(store);assert.equal(reloaded.get('demo-01'),'A draft');
 assert.equal(countVisits(seed).get('jp-osaka'),2);reloaded.remove('demo-01');assert.equal(new DraftStore(store).has('demo-01'),false);
 drafts.set('__proto__','Safe text');assert.equal(drafts.get('__proto__'),'Safe text');
});
test('draft storage failures retain in-tab text and warn',()=>{
 const warnings=[];const drafts=new DraftStore({getItem:()=>null,setItem:()=>{throw new Error('quota')}},m=>warnings.push(m));
 drafts.set('demo-01','Keep this');assert.equal(drafts.get('demo-01'),'Keep this');assert.match(warnings[0],/Keep this page open/);
});
test('photo previews accept only same-origin media paths',()=>{
 const origin='http://localhost:8019';assert.equal(photoURL({url:'/media/a.jpg'},origin),origin+'/media/a.jpg');
 for(const url of ['https://example.org/a.jpg','//example.org/a.jpg','data:image/png;base64,a','/media/../docs/a.jpg','/api/secret','javascript:alert(1)'])assert.equal(photoURL({url},origin),null);
 assert.equal(photoURL({id:'old-reference'},origin),null);
});
