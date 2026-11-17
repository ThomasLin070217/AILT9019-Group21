/** Optional geographic basemap; trip records and city geometry stay in this app. */
const STYLE='https://tiles.openfreemap.org/styles/positron';
let sdkPromise;
function sdk(){
 if(window.maplibregl)return Promise.resolve(window.maplibregl);
 if(!sdkPromise)sdkPromise=new Promise((resolve,reject)=>{
  const script=document.createElement('script');script.src='./vendor/maplibre/maplibre-gl.js';script.async=true;
  script.onload=()=>window.maplibregl?resolve(window.maplibregl):reject(new Error('Renderer did not load'));
  script.onerror=()=>reject(new Error('Renderer did not load'));document.head.append(script);
 });
 return sdkPromise;
}
function geometryBounds(geometry){
 const bounds=[[Infinity,Infinity],[-Infinity,-Infinity]];
 const visit=value=>{if(typeof value[0]==='number'){
  bounds[0][0]=Math.min(bounds[0][0],value[0]);bounds[0][1]=Math.min(bounds[0][1],value[1]);
  bounds[1][0]=Math.max(bounds[1][0],value[0]);bounds[1][1]=Math.max(bounds[1][1],value[1]);
 }else for(const part of value)visit(part);};visit(geometry.coordinates);return bounds;
}
export async function createStreetsMap({container,regionData,onSelect,onNearby,onFailure,onZoom}){
 const lib=await sdk();
 const map=new lib.Map({container,style:STYLE,center:[119,34],zoom:3.4,minZoom:3,maxZoom:18,dragRotate:false,pitchWithRotate:false,renderWorldCopies:false});
 map.touchZoomRotate.disableRotation();
 let loaded=false,failed=false,disposed=false,current=[],selected=null,shown=new Set(),counts=new Map(),fitted=false;
 const markers=new Map();
 const fail=()=>{if(!failed&&!disposed){failed=true;onFailure();}};
 const areas=()=>({type:'FeatureCollection',features:regionData.features.map(feature=>({
  ...feature,properties:{...feature.properties,visible:Number(shown.has(feature.properties.city_id)),tier:Math.min(counts.get(feature.properties.city_id)||0,4),selected:Number(feature.properties.city_id===selected)}
 }))});
 const fit=()=>{if(!current.length)return;const bounds=new lib.LngLatBounds();for(const city of current)bounds.extend([city.longitude,city.latitude]);map.fitBounds(bounds,{padding:50,maxZoom:9,duration:0});};
 const near=city=>{const p=map.project([city.longitude,city.latitude]);return current.filter(other=>{const q=map.project([other.longitude,other.latitude]);return Math.hypot(p.x-q.x,p.y-q.y)<38;});};
 const ready=new Promise((resolve,reject)=>{
  const timer=setTimeout(()=>{fail();reject(new Error('Street map timed out'));},18000);
  map.once('load',()=>{
   clearTimeout(timer);if(failed||disposed){reject(new Error('Street map unavailable'));return;}
   loaded=true;map.addSource('city-areas',{type:'geojson',data:areas()});
   const before=map.getStyle().layers.find(layer=>layer.type==='symbol')?.id;
   map.addLayer({id:'city-visit-fill',type:'fill',source:'city-areas',filter:['==',['get','visible'],1],paint:{
    'fill-color':['match',['get','tier'],1,'#71946a',2,'#cb754d',3,'#eca33f',4,'#eca33f','#ad4a29'],
    'fill-opacity':['case',['==',['get','tier'],0],['case',['==',['get','selected'],1],.12,0],['interpolate',['linear'],['get','tier'],1,.3,4,.55]]
   }},before);
   map.addLayer({id:'city-outline',type:'line',source:'city-areas',filter:['==',['get','visible'],1],paint:{
    'line-color':['case',['==',['get','selected'],1],'#9b3d23',['>', ['get','tier'],0],'#4f7354','#7d9794'],
    'line-opacity':['case',['==',['get','selected'],1],1,['>', ['get','tier'],0],.9,.75],
    'line-width':['case',['==',['get','selected'],1],2.4,1.2]
   }},before);
   map.on('click','city-visit-fill',event=>{const id=event.features?.[0]?.properties?.city_id;if(id)onSelect(id,false);});
   map.on('mouseenter','city-visit-fill',()=>{map.getCanvas().style.cursor='pointer';});
   map.on('mouseleave','city-visit-fill',()=>{map.getCanvas().style.cursor='';});
   if(fitted)fit();resolve();
  });
  map.on('error',event=>{if(!loaded){clearTimeout(timer);fail();reject(event.error||new Error('Map style unavailable'));}});
 });
 map.on('zoom',()=>onZoom(map.getZoom()));
 return {
  ready,
  updateRegions(items,nextCounts,nextSelected){if(failed||disposed)return;shown=new Set(items.map(city=>city.id));counts=nextCounts;selected=nextSelected;if(loaded)map.getSource('city-areas')?.setData(areas());},
  update(items,nextSelected){
   if(failed||disposed)return;current=items;selected=nextSelected;
   const ids=new Set(items.map(city=>city.id));for(const [id,entry] of markers)if(!ids.has(id)){entry.marker.remove();markers.delete(id);}
   for(const city of items){
    let entry=markers.get(city.id);
    if(!entry){
     const button=document.createElement('button');button.type='button';button.className='street-city-marker online-city-marker';button.dataset.cityId=city.id;
     button.addEventListener('click',event=>{const nearby=near(city);if(event.detail!==0&&nearby.length>1){onNearby(nearby);return;}onSelect(city.id,event.detail===0);});
     entry={button,marker:new lib.Marker({element:button,anchor:'center'}).setLngLat([city.longitude,city.latitude]).addTo(map)};markers.set(city.id,entry);
    }
    entry.button.setAttribute('aria-label',`${city.name}, ${city.count} ${city.count===1?'visit':'visits'}`);
    entry.button.setAttribute('aria-pressed',String(city.id===nextSelected));entry.button.dataset.tier=String(city.tier);
    const count=document.createElement('span');count.className='street-pin-count';count.textContent=city.count?String(city.count):'';
    const label=document.createElement('span');label.className='street-pin-label';label.textContent=city.name;
    entry.button.replaceChildren(count,label);
    if(city.cover&&city.id===nextSelected){const photo=document.createElement('img');photo.className='street-pin-photo';photo.alt='';photo.src=city.cover;photo.addEventListener('error',()=>photo.remove());entry.button.prepend(photo);}
   }
   if(!fitted&&items.length){fitted=true;if(loaded)fit();}
  },
  select(id){const city=current.find(c=>c.id===id);if(city&&!map.getBounds().contains([city.longitude,city.latitude]))map.panTo([city.longitude,city.latitude]);},
  focusRegion(id){const feature=regionData.features.find(f=>f.properties.city_id===id);if(feature)map.fitBounds(geometryBounds(feature.geometry),{padding:58,maxZoom:10,duration:450});},
  focus(id){markers.get(id)?.button.focus({preventScroll:true});},
  zoom(delta){map.zoomTo(Math.max(3,Math.min(18,map.getZoom()+delta)));},fit,
  refresh(){map.resize();},
  destroy(){disposed=true;for(const {marker} of markers.values())marker.remove();map.remove();container.replaceChildren();}
 };
}
