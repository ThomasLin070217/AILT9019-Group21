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
