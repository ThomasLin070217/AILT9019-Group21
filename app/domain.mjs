/** Framework-independent map rules. A visit is one saved trip ID, never one photo. */
export function visitTier(count) {
  if (!Number.isInteger(count) || count < 0) throw new TypeError('Visit count must be a non-negative integer.');
  return count === 0 ? 0 : count === 1 ? 1 : count < 4 ? 2 : 3;
}
export function validateTrip(trip, cities) {
  if (!trip || typeof trip.id !== 'string' || !trip.id.trim()) throw new Error('Trip ID is missing.');
  if (!cities.some(city => city.id === trip.city_id)) throw new Error('Trip has an unsupported city.');
  for (const key of ['title', 'notes', 'memory_text']) {
    if (typeof trip[key] !== 'string') throw new Error(`Trip ${key} must be text.`);
    if (trip[key].length > (key === 'title' ? 200 : 5000)) throw new Error(`Trip ${key} is too long.`);
  }
  if (trip.trip_date !== null && (typeof trip.trip_date !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(trip.trip_date) || !Number.isFinite(Date.parse(trip.trip_date)) || new Date(trip.trip_date).toISOString().slice(0,10) !== trip.trip_date)) throw new Error('Trip date must be a valid YYYY-MM-DD or null.');
  if (!Array.isArray(trip.photos)) throw new Error('Trip photos must be an array.');
  return trip;
}
export function uniqueTrips(trips) {
  // A later occurrence represents the latest snapshot of that ID, not another visit.
  return [...new Map(trips.map(trip => [trip.id, trip])).values()];
}
export function countVisits(trips) {
  const counts = new Map();
  for (const trip of uniqueTrips(trips)) counts.set(trip.city_id, (counts.get(trip.city_id) || 0) + 1);
  return counts;
}
export function cityTrips(trips, cityId) {
  return uniqueTrips(trips).filter(trip => trip.city_id === cityId).sort((a,b) => (b.trip_date || '').localeCompare(a.trip_date || '') || a.id.localeCompare(b.id));
}
export function updateTrip(trips, id, patch, cities) {
  const current = trips.find(trip => trip.id === id);
  if (!current) throw new Error('Trip was not found.');
  if ('id' in patch || 'city_id' in patch) throw new Error('A card edit cannot change trip or city identity.');
  const updated = validateTrip({...current,...patch}, cities);
  return uniqueTrips(trips).map(trip => trip.id === id ? updated : trip);
}
export function filterCities(cities, trips, {query='', region='', visitedOnly=false}={}) {
  const search = query.trim().toLocaleLowerCase();
  const counts = countVisits(trips);
  return cities.filter(city => (!region || city.region === region) && (!visitedOnly || counts.has(city.id)) && `${city.name} ${city.local_name}`.toLocaleLowerCase().includes(search));
}
export function project(longitude, latitude) {
  const lat = Math.max(-80,Math.min(80,latitude))*Math.PI/180;
  return [longitude, -Math.log(Math.tan(Math.PI/4+lat/2))*180/Math.PI];
}
export function initialView() {
  const a=project(98,47), b=project(148,17);
  const height=b[1]-a[1], width=height*900/680;
  return {x:(98+148-width)/2,y:a[1],width,height};
}
export function zoomView(view, factor) {
  const full=initialView();
  const width=Math.max(full.width/32,Math.min(full.width,view.width*factor));
  const height=width*680/900;
  return clampView({x:view.x+(view.width-width)/2,y:view.y+(view.height-height)/2,width,height});
}
export function clampView(view) {
  const full=initialView();
  return {...view,x:Math.max(full.x,Math.min(full.x+full.width-view.width,view.x)),y:Math.max(full.y,Math.min(full.y+full.height-view.height,view.y))};
}
