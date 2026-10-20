/** Optional Maps JavaScript API adapter. No city search, routing, or photo upload. */
export async function createGoogleMap({container,config,onSelect,onNearby,onFailure,onZoom}) {
  let failed=false, disposed=false, rejectLoad;
  const fail=()=>{if(!failed&&!disposed){failed=true;rejectLoad?.(new Error('Google Maps unavailable'));onFailure();}};
  // Google may reject authentication after the SDK callback has already run.
  window.gm_authFailure=fail;
  await new Promise((resolve,reject)=>{
    const timer=setTimeout(fail,15000);
    rejectLoad=error=>{clearTimeout(timer);reject(error);};
    window.travelMemoryMapsReady=()=>{clearTimeout(timer);if(!failed)resolve();};
    const script=document.createElement('script');script.async=true;script.onerror=fail;
    const url=new URL('https://maps.googleapis.com/maps/api/js');
    url.search=new URLSearchParams({key:config.apiKey,v:'weekly',loading:'async',callback:'travelMemoryMapsReady',libraries:'marker',language:'en'}).toString();
    script.src=url.href;document.head.append(script);
  });
  const [{Map:GoogleMap},{AdvancedMarkerElement}]=await Promise.all([google.maps.importLibrary('maps'),google.maps.importLibrary('marker')]);
  if(failed)throw new Error('Google Maps unavailable');
  const map=new GoogleMap(container,{center:{lat:33,lng:123},zoom:4,mapId:config.mapId||'DEMO_MAP_ID',renderingType:google.maps.RenderingType.RASTER,disableDefaultUI:true,clickableIcons:false,gestureHandling:'cooperative',minZoom:3,maxZoom:18,streetViewControl:false,tilt:0});
  const markers=new globalThis.Map();let current=[],selectedId=null,hasFitted=false;
  const notifyZoom=()=>onZoom(map.getZoom()||4);
  map.addListener('zoom_changed',notifyZoom);
  const fit=()=>{if(!current.length)return;const bounds=new google.maps.LatLngBounds();for(const item of current)bounds.extend({lat:item.latitude,lng:item.longitude});map.fitBounds(bounds,55);if(current.length===1)google.maps.event.addListenerOnce(map,'idle',()=>{if(map.getZoom()>10)map.setZoom(10);});};
  function nearby(city){
    const projection=map.getProjection();if(!projection)return [city];
    const a=projection.fromLatLngToPoint(new google.maps.LatLng(city.latitude,city.longitude)),scale=2**map.getZoom();
    return current.filter(other=>{const b=projection.fromLatLngToPoint(new google.maps.LatLng(other.latitude,other.longitude));return Math.hypot(a.x-b.x,a.y-b.y)*scale<38;});
  }
  const ready=new Promise((resolve,reject)=>{
    const timer=setTimeout(()=>{fail();reject(new Error('Map did not become ready'));},15000);
    google.maps.event.addListenerOnce(map,'tilesloaded',()=>{clearTimeout(timer);if(failed)reject(new Error('Google Maps unavailable'));else resolve();});
  });
  const adapter={
    ready,
    update(items,selected){
      if(failed||disposed)return;
      current=items;selectedId=selected;
      const ids=new Set(items.map(item=>item.id));
      for(const [id,entry] of markers)if(!ids.has(id)){entry.marker.map=null;markers.delete(id);}
      for(const item of items){
        let entry=markers.get(item.id);
        if(!entry){
          const content=document.createElement('div');content.className='google-city-pin';
          const number=document.createElement('span');number.className='google-visit-count';
          const label=document.createElement('span');label.className='google-city-label';label.textContent=item.name;
          content.append(number,label);
          const marker=new AdvancedMarkerElement({map,position:{lat:item.latitude,lng:item.longitude},gmpClickable:true});
          marker.append(content);marker.dataset.cityId=item.id;marker.classList.add('google-city-marker');
          let keyboardClick=false;
          marker.addEventListener('keydown',event=>{keyboardClick=['Enter',' '].includes(event.key);});
          marker.addEventListener('pointerdown',()=>{keyboardClick=false;});
          marker.addEventListener('gmp-click',event=>{
            const keyboard=keyboardClick||event.domEvent?.detail===0;keyboardClick=false;
            const choices=nearby(item);
            if(!keyboard&&choices.length>1){onNearby(choices);return;}
            onSelect(item.id,Boolean(keyboard));
          });
          entry={marker,content,number,photo:null,photoURL:null};markers.set(item.id,entry);
        }
        entry.marker.title=`${item.name}, ${item.count} ${item.count===1?'visit':'visits'}`;
        entry.marker.zIndex=item.id===selected?1000:10+item.count;
        entry.content.dataset.tier=String(item.tier);entry.content.classList.toggle('is-selected',item.id===selected);
        entry.number.textContent=item.count?String(item.count):'';
        const photo=item.id===selected?item.cover:null;
        if(entry.photoURL!==photo){
          entry.photo?.remove();entry.photo=null;entry.photoURL=photo;
          if(photo){const image=document.createElement('img');image.className='google-pin-photo';image.alt='';image.src=photo;image.addEventListener('error',()=>image.remove());entry.content.prepend(image);entry.photo=image;}
        }
      }
      if(!hasFitted&&items.length){hasFitted=true;fit();}
    },
    select(id){const item=current.find(c=>c.id===id);if(item&&!map.getBounds()?.contains({lat:item.latitude,lng:item.longitude}))map.panTo({lat:item.latitude,lng:item.longitude});},
    focus(id){markers.get(id)?.marker.focus();},
    zoom(delta){map.setZoom(Math.max(3,Math.min(18,(map.getZoom()||4)+delta)));},
    fit,
    refresh(){google.maps.event.trigger(map,'resize');notifyZoom();adapter.select(selectedId);},
    destroy(){disposed=true;for(const {marker} of markers.values())marker.map=null;google.maps.event.clearInstanceListeners(map);container.replaceChildren();}
  };
  notifyZoom();return adapter;
}
