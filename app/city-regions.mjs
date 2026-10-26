import {project,initialView,clampView} from './domain.mjs';

/** Display geometry only; saved trips, not polygons, remain the visit source of truth. */
export function polygonsOf(geometry){
  if(geometry?.type==='Polygon')return [geometry.coordinates];
  if(geometry?.type==='MultiPolygon')return geometry.coordinates;
  throw new TypeError('City area must be a Polygon or MultiPolygon.');
}

export function regionPath(geometry){
  return polygonsOf(geometry).map(polygon=>polygon.map(ring=>{
    const points=ring.map(([longitude,latitude])=>project(longitude,latitude));
    return points.map(([x,y],i)=>`${i?'L':'M'}${x.toFixed(4)},${y.toFixed(4)}`).join(' ')+'Z';
  }).join(' ')).join(' ');
}

export function regionBounds(geometry){
  let west=Infinity,east=-Infinity,north=Infinity,south=-Infinity;
  for(const polygon of polygonsOf(geometry))for(const ring of polygon)for(const [lon,lat] of ring){
    const [x,y]=project(lon,lat);west=Math.min(west,x);east=Math.max(east,x);north=Math.min(north,y);south=Math.max(south,y);
  }
  if(!Number.isFinite(west))throw new Error('City area is empty.');
  return {west,east,north,south};
}

export function viewForRegion(geometry){
  const {west,east,north,south}=regionBounds(geometry),full=initialView();
  const width=Math.min(full.width,Math.max(full.width/32,(east-west)*1.45,(south-north)*1.45*900/680));
  const height=width*680/900;
  return clampView({x:(west+east-width)/2,y:(north+south-height)/2,width,height});
}
