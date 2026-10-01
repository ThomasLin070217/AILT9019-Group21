import {validateTrip, uniqueTrips, updateTrip} from './domain.mjs';
export const STORAGE_KEY='travel-memory-map.demo.v1';
export async function getJSON(url) {
  const controller=new AbortController();
  const timeout=setTimeout(()=>controller.abort(),10000);
  try {
    const response=await fetch(url,{signal:controller.signal});
    if (!response.ok) throw new Error(`${url}: HTTP ${response.status}`);
    return await response.json();
  } finally {clearTimeout(timeout);}
}
export class DemoRepository {
  constructor(cities, seed, storage=globalThis.localStorage) {this.cities=cities;this.seed=structuredClone(seed);this.storage=storage;}
  async list() {
    const raw=this.storage.getItem(STORAGE_KEY);
    const rows=raw===null ? structuredClone(this.seed) : JSON.parse(raw);
    if (!Array.isArray(rows)) throw new Error('Saved demo data is not a trip list.');
    return uniqueTrips(rows.map(row=>validateTrip(row,this.cities)));
  }
  save(rows) {
    rows.forEach(row=>validateTrip(row,this.cities));
    // Storage failures surface to the UI; never claim a save succeeded.
    this.storage.setItem(STORAGE_KEY,JSON.stringify(uniqueTrips(rows)));
    return structuredClone(uniqueTrips(rows));
  }
  async add(cityId) {
    const rows=await this.list();
    return this.save([...rows,{id:crypto.randomUUID(),city_id:cityId,trip_date:new Date().toISOString().slice(0,10),title:'Another small memory',notes:'A fictional sample visit for testing the map.',memory_text:'This is sample text, written for the map prototype. No AI was called.',photos:[],source:'demo'}]);
  }
  async edit(id, patch) {return this.save(updateTrip(await this.list(),id,patch,this.cities));}
  async remove(id) {return this.save((await this.list()).filter(trip=>trip.id!==id));}
  async reset() {return this.save(structuredClone(this.seed));}
}
export class ApiRepository {
  constructor(cities){this.cities=cities;}
  async list(){
    const rows=await getJSON('/api/trips');
    if (!Array.isArray(rows)) throw new Error('The backend must return a trip array.');
    return uniqueTrips(rows.map(row=>validateTrip(row,this.cities)));
  }
}

/** Per-tab drafts survive city changes and reloads without becoming saved trips. */
export class DraftStore {
  constructor(storage, onWarning=()=>{}) {
    this.storage=storage;this.onWarning=onWarning;this.key='travel-memory-map.demo-drafts.v1';this.rows={};
    try {const raw=storage?.getItem(this.key);if(raw){const parsed=JSON.parse(raw);if(!parsed||Array.isArray(parsed)||typeof parsed!=='object'||Object.values(parsed).some(v=>typeof v!=='string'||v.length>5000))throw new Error('Invalid drafts');this.rows=parsed;}}
    catch {onWarning('Saved drafts could not be read. New edits will be kept in this tab.');}
  }
  has(id){return Object.hasOwn(this.rows,id);}
  get(id){return this.rows[id];}
  set(id,text){Object.defineProperty(this.rows,id,{value:text,writable:true,configurable:true,enumerable:true});this.persist();}
  remove(id){delete this.rows[id];this.persist();}
  clear(){this.rows={};this.persist();}
  persist(){try{if(!this.storage)throw new Error('Unavailable');this.storage.setItem(this.key,JSON.stringify(this.rows));}catch{this.onWarning('Draft kept in this tab only. Keep this page open until you save.');}}
}

/** Only the backend's same-origin media paths may supply user-photo previews. */
export function photoURL(photo, origin) {
  if(!photo||typeof photo.url!=='string'||!photo.url.startsWith('/media/'))return null;
  try{const url=new URL(photo.url,origin);return url.origin===origin&&url.pathname.startsWith('/media/')?url.href:null;}catch{return null;}
}
