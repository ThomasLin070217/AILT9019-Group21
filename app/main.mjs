import {visitTier,countVisits,cityTrips,filterCities,project,initialView,zoomView,clampView} from './domain.mjs';
import {DemoRepository,ApiRepository,getJSON,DraftStore,photoURL} from './repository.mjs';
import {createGoogleMap} from './google-map.mjs';
const $=id=>document.getElementById(id), NS='http://www.w3.org/2000/svg';
const mode=new URLSearchParams(location.search).get('mode')==='api'?'api':'demo';
let cities=[],trips=[],selected='jp-osaka',repository,view=initialView(),busy=false,ready=false;
let googleMap=null,mapStarted=false,mapFailed=false;
let draftStorage;try{draftStorage=sessionStorage;}catch{}
const drafts=new DraftStore(draftStorage,text=>message(text));
const demoCovers={'demo-01':{file:'osaka-castle-2.jpg',author:'Eleni Afiontzi',source:'https://unsplash.com/photos/JdIC1dJtO_U'},'demo-02':{file:'osaka-castle-1.jpg',author:'欣慧',source:'https://unsplash.com/photos/dEMBfH4nWY8'}};
let viewerTrigger;
const prominent=new Set(['cn-beijing','cn-shanghai','cn-chengdu','hk-hong-kong','tw-taipei','jp-osaka','jp-tokyo','jp-sapporo']);
function node(tag,text,classes){const el=document.createElement(tag);if(text!==undefined)el.textContent=text;if(classes)el.className=classes;return el;}
function svg(tag,attrs={}){const el=document.createElementNS(NS,tag);for(const [key,value]of Object.entries(attrs))el.setAttribute(key,value);return el;}
function message(text){$('status').textContent=text;}
function showError(error){$('error').hidden=false;$('error-text').textContent=mode==='api'?`Could not load backend records. ${error.message} Start the backend and retry. Demo data has not been substituted.`:`Could not read or save this browser's sample album. ${error.message} Retry, or restore samples if the saved demo is damaged.`;$('recover').hidden=mode!=='demo'||!repository;}
function clearError(){$('error').hidden=true;$('error-text').textContent='';}
function setBusy(value){busy=value;for(const id of ['add-sample','reset','refresh','retry','recover'])$(id).disabled=value;$('workspace').setAttribute('aria-busy',String(value));}
async function mutate(action,success,afterSave=()=>{}){if(busy)return;setBusy(true);clearError();try{trips=await action();afterSave();render();message(success);}catch(error){showError(error);}finally{setBusy(false);}}
function filters(){return {query:$('search').value,region:$('region').value,visitedOnly:$('visited').checked};}
function choose(id,keyboard=false){
 const origin=document.activeElement?.classList.contains('google-city-marker')?'google':document.activeElement?.classList.contains('marker')?'markers':'cities';$('nearby-cities').hidden=true;selected=id;render();
 $('memories').scrollTop=0;
 if(origin==='google')googleMap?.focus(id);else $(origin).querySelector(`[data-city-id="${CSS.escape(id)}"]`)?.focus({preventScroll:true});
 googleMap?.select(id);
 if(!keyboard&&matchMedia('(max-width:850px)').matches)$('memories').scrollIntoView({block:'start',behavior:'instant'});
 window.dispatchEvent(new CustomEvent('travel-map:city-selected',{detail:{city_id:id}}));
}
function visibleCities(){return filterCities(cities,trips,filters());}
function render(){
 const visible=visibleCities(),counts=countVisits(trips);
 if(!visible.some(c=>c.id===selected))selected=visible[0]?.id||null;
 $('progress').replaceChildren(node('strong',`${counts.size} cities visited`),document.createTextNode(` of ${cities.length} supported · ${trips.length} trips`));
 $('result-count').textContent=`${visible.length} of ${cities.length} cities`;
 $('cities').replaceChildren();
 if(!visible.length)$('cities').append(node('p','No matching cities. Change your search or turn off the visited filter.','empty'));
 const catalogue=[...visible].sort((a,b)=>Number(counts.has(b.id))-Number(counts.has(a.id))||a.name.localeCompare(b.name));
 for(const city of catalogue){
  const count=counts.get(city.id)||0,button=node('button',undefined,'city-button');button.type='button';button.dataset.cityId=city.id;button.setAttribute('aria-pressed',String(city.id===selected));button.setAttribute('aria-label',`${city.name}, ${count} ${count===1?'visit':'visits'}`);
  const label=node('span',city.name);label.append(node('small',city.local_name));button.append(label,node('span',count?String(count):'—',`visit-badge ${count?'visited':''}`));button.addEventListener('click',event=>choose(city.id,event.detail===0));$('cities').append(button);
 }
 renderMarkers(visible,counts);renderMemories();
}
function drawLand(data){
 const grid=[];
 for(let lon=90;lon<=160;lon+=10){const a=project(lon,60),b=project(lon,5);grid.push(svg('path',{d:`M${a}L${b}`,class:'graticule'}));}
 for(let lat=10;lat<=60;lat+=10){const a=project(88,lat),b=project(160,lat);grid.push(svg('path',{d:`M${a}L${b}`,class:'graticule'}));}
 $('grid').replaceChildren(...grid);
 const polygons=[];
 for(const feature of data.features){
  const geometry=feature.geometry;
  if(geometry.type==='Polygon')polygons.push(geometry.coordinates);
  if(geometry.type==='MultiPolygon')polygons.push(...geometry.coordinates);
 }
 const path=polygons.map(polygon=>polygon.map(ring=>ring.map((point,i)=>{const [x,y]=project(...point);return `${i?'L':'M'}${x.toFixed(4)},${y.toFixed(4)}`;}).join(' ')+'Z').join(' ')).join(' ');
 $('land').replaceChildren(svg('path',{d:path,class:'land','fill-rule':'evenodd'}));
 applyView();
}
function applyView(){
 $('map').setAttribute('viewBox',`${view.x} ${view.y} ${view.width} ${view.height}`);
 const zoomed=view.width<initialView().width-.01;$('map').classList.toggle('zoomed',zoomed);
 $('zoom-out').disabled=!zoomed;$('zoom-in').disabled=view.width<=initialView().width/8+.01;
 if(ready)renderMarkers(visibleCities(),countVisits(trips));
}
function renderMarkers(visible,counts){
 if(googleMap){googleMap.update(visible.map(city=>{
  const trip=cityTrips(trips,city.id).find(t=>(mode==='demo'&&demoCovers[t.id])||t.photos.some(p=>photoURL(p,location.origin)));
  const sample=trip&&mode==='demo'&&demoCovers[trip.id];
  return {...city,count:counts.get(city.id)||0,tier:visitTier(counts.get(city.id)||0),cover:sample?`../data/demo-covers/${sample.file}`:photoURL(trip?.photos.find(p=>photoURL(p,location.origin)),location.origin)};
 }),selected);return;}
 const rect=$('map').getBoundingClientRect();
 const pixelsPerUnit=Math.min(rect.width/view.width,rect.height/view.height);
 const scale=pixelsPerUnit>0?12/pixelsPerUnit:view.width/initialView().width;
 $('markers').replaceChildren();
 // Draw the selected marker last so its photo and hit area remain reachable.
 for(const city of [...visible].sort((a,b)=>Number(a.id===selected)-Number(b.id===selected))){
  const [x,y]=project(city.longitude,city.latitude),count=counts.get(city.id)||0;
  const g=svg('g',{class:'marker',transform:`translate(${x} ${y})`,role:'button',tabindex:'0','aria-label':`${city.name}, ${count} ${count===1?'visit':'visits'}`,'aria-pressed':String(city.id===selected),'data-city-id':city.id});
  const title=svg('title');title.textContent=`${city.name} · ${count} saved trips`;g.append(title,svg('circle',{r:1.85*scale,class:'hit'}),svg('circle',{r:1.05*scale,class:'selection'}),svg('circle',{r:(count?.78:.3)*scale,class:`pin tier-${visitTier(count)}`}));
  if(count){const number=svg('text',{class:`visit-number count-tier-${visitTier(count)}`,y:.3*scale,style:`font-size:${.9*scale}px`});number.textContent=String(count);g.append(number);}
  const selectedTrip=city.id===selected?cityTrips(trips,city.id).find(t=>(mode==='demo'&&demoCovers[t.id])||t.photos.some(p=>photoURL(p,location.origin))):null;
  if(selectedTrip){
   const sample=mode==='demo'&&demoCovers[selectedTrip.id],url=sample?`../data/demo-covers/${sample.file}`:photoURL(selectedTrip.photos.find(p=>photoURL(p,location.origin)),location.origin);
   g.append(svg('path',{d:`M0 ${-1.1*scale}V${-2*scale}`,class:'photo-stem'}),svg('rect',{x:-1.9*scale,y:-5.1*scale,width:3.8*scale,height:3.1*scale,rx:.35*scale,class:'photo-pin'}));
   const image=svg('image',{href:url,x:-1.7*scale,y:-4.9*scale,width:3.4*scale,height:2.7*scale,preserveAspectRatio:'xMidYMid slice','aria-hidden':'true'});
   image.addEventListener('error',()=>image.remove());g.append(image);
  }
  if(prominent.has(city.id)||city.id===selected){const rightEdge=x+(1.2+city.name.length*.6)*scale>view.x+view.width-.5;const text=svg('text',{x:(rightEdge?-1.2:1.2)*scale,'text-anchor':rightEdge?'end':'start',y:.3*scale,style:`font-size:${scale}px;stroke-width:${.2*scale}px`});text.textContent=city.name;g.append(text);}
  g.addEventListener('click',event=>{const nearby=visible.filter(other=>{const [ox,oy]=project(other.longitude,other.latitude);return Math.hypot(x-ox,y-oy)*pixelsPerUnit<38;});if(nearby.length>1&&event.detail!==0){showNearby(nearby);return;}choose(city.id,event.detail===0);});g.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();choose(city.id,true);}});$('markers').append(g);
 }
}
function renderMemories(){
 const city=cities.find(c=>c.id===selected);$('trip-list').replaceChildren();$('demo-tools').hidden=mode!=='demo'||!city;$('api-handoff').hidden=mode!=='api'||!city;
 if(!city){$('city-region').textContent='No city selected';$('city-name').textContent='Keep exploring';$('city-local').textContent='';$('city-count').textContent='Clear a filter to return to your cities.';return;}
 const rows=cityTrips(trips,city.id);$('city-region').textContent=city.region;$('city-name').textContent=city.name;$('city-local').textContent=city.local_name;$('city-count').textContent=`${rows.length} ${rows.length===1?'visit':'visits'} · ${rows.length?'Each trip, its own memory.':'A story still to come.'}`;
 if(!rows.length){const empty=node('div',undefined,'empty');empty.append(node('strong','Your first memory belongs here.'),node('p',mode==='demo'?'Open “Try visit counting” below to light up this city with a fictional visit.':'No saved trips for this city yet.'));$('trip-list').append(empty);}
 for(const trip of rows){
  const card=node('article',undefined,'trip-card');card.dataset.tripId=trip.id;
  const date=node('time',trip.trip_date?new Intl.DateTimeFormat('en',{day:'numeric',month:'short',year:'numeric',timeZone:'UTC'}).format(new Date(trip.trip_date)):'Date not recorded');if(trip.trip_date)date.dateTime=trip.trip_date;
  const cover=makeCover(trip);if(cover)card.append(cover);
  card.append(date,node('h3',trip.title||'Untitled memory'),node('p',trip.memory_text||trip.notes||'No notes yet.'),node('p',mode==='demo'?'Fictional trip · sample content':`${trip.photos.length} photo references`,'photo-count'));
  if(mode==='demo'){
   const actions=node('div',undefined,'card-actions'),edit=node('button','Edit sample text','text-button'),remove=node('button','Remove sample','text-button');
   edit.addEventListener('click',()=>editCard(card,trip,true));remove.addEventListener('click',()=>{if(confirm('Remove this sample visit and any draft for it?'))mutate(()=>repository.remove(trip.id),'Sample visit removed. Counts recalculated from saved trip IDs.',()=>drafts.remove(trip.id));});
   actions.append(edit,remove);card.append(actions);
  }
  $('trip-list').append(card);if(mode==='demo'&&drafts.has(trip.id))editCard(card,trip,false);
 }
}
function editCard(card,trip,focus=false){
 const existing=card.querySelector('form');if(existing){if(focus)existing.querySelector('textarea').focus();return;}
 const form=node('form'),label=node('label','Sample memory text'),textarea=node('textarea');textarea.value=drafts.has(trip.id)?drafts.get(trip.id):trip.memory_text;textarea.maxLength=5000;textarea.required=true;textarea.id=`edit-${trip.id}`;label.htmlFor=textarea.id;
 textarea.addEventListener('input',()=>drafts.set(trip.id,textarea.value));
 const help=node('p','Draft stays in this tab when you change cities or reload. Save to update the trip.','small');
 const save=node('button','Save sample text'),cancel=node('button','Discard draft');cancel.type='button';
 cancel.addEventListener('click',()=>{if(!drafts.has(trip.id)||confirm('Discard this unsaved draft?')){drafts.remove(trip.id);renderMemories();focusEdit(trip.id);}});
 form.append(label,textarea,help,save,cancel);card.append(form);if(focus)textarea.focus();
 form.addEventListener('submit',async event=>{event.preventDefault();await mutate(()=>repository.edit(trip.id,{memory_text:textarea.value}),'Sample text saved. Visit count unchanged.',()=>drafts.remove(trip.id));if(!drafts.has(trip.id))focusEdit(trip.id);});
}
function focusEdit(id){$('trip-list').querySelector(`[data-trip-id="${CSS.escape(id)}"] .card-actions button`)?.focus({preventScroll:true});}
function makeCover(trip){
 const sample=mode==='demo'&&demoCovers[trip.id];
 const photo=trip.photos.find(p=>photoURL(p,location.origin));
 const url=sample?`../data/demo-covers/${sample.file}`:photoURL(photo,location.origin);
 if(!url)return null;
 const figure=node('figure',undefined,'trip-cover'),button=node('button',undefined,'cover-button'),img=node('img');
 const alt=sample?'Osaka Castle — example photograph':(typeof photo.alt==='string'?photo.alt:'Trip photograph');
 button.setAttribute('aria-label',`Open photo for ${trip.title||'this memory'}`);img.alt=alt;img.src=url;img.loading='lazy';img.decoding='async';img.width=960;img.height=640;
 button.append(img);button.addEventListener('click',()=>{viewerTrigger=button;$('viewer-image').src=url;$('viewer-image').alt=alt;$('viewer-caption').textContent=sample?`Example photo by ${sample.author} / Unsplash · not a photo from this fictional trip`:alt;$('photo-viewer').showModal();});
 figure.append(button);if(sample){const caption=node('figcaption','Example photo · '),link=node('a',`${sample.author} / Unsplash`);link.href=sample.source;link.target='_blank';link.rel='noreferrer';caption.append(link);figure.append(caption);}
 img.addEventListener('error',()=>{button.replaceWith(node('p','Photo unavailable. Your memory text is still here.','photo-missing'));});return figure;
}
function showNearby(nearby){
 const panel=$('nearby-cities');panel.replaceChildren(node('p','These cities are close together. Choose one:'));
 for(const city of nearby){const button=node('button',city.name);button.addEventListener('click',event=>{panel.hidden=true;choose(city.id,event.detail===0);});panel.append(button);}
 const close=node('button','Close choices','text-button');close.addEventListener('click',()=>{panel.hidden=true;$('fit').focus();});panel.append(close);panel.hidden=false;panel.querySelector('button').focus({preventScroll:true});if(matchMedia('(max-width:850px)').matches)panel.scrollIntoView({block:'center',behavior:'instant'});
}
async function load(){
 setBusy(true);clearError();ready=false;message('');$('loading').hidden=false;$('mode-label').textContent=mode==='api'?'Backend mode · waiting for local API records':'Demo album · fictional trips · no AI calls';
 try{
  const [catalogue,land,seed]=await Promise.all([getJSON(mode==='api'?'/api/cities':'../data/cities.json'),getJSON('../data/map/land.geojson'),mode==='demo'?getJSON('../data/demo-trips.json'):Promise.resolve([])]);
  if(!Array.isArray(catalogue)||!catalogue.length||catalogue.some(c=>!c.id||!c.name||!Number.isFinite(c.longitude)||!Number.isFinite(c.latitude))||new Set(catalogue.map(c=>c.id)).size!==catalogue.length)throw new Error('Invalid city catalogue.');
  cities=catalogue;repository=mode==='demo'?new DemoRepository(cities,seed):new ApiRepository(cities);trips=await repository.list();ready=true;drawLand(land);render();
  $('mode-label').textContent=mode==='demo'?'Demo album · fictional trips saved in this browser · no AI calls':'Backend mode · showing records from the local API';$('reset').hidden=mode!=='demo';$('refresh').hidden=mode!=='api';
 }catch(error){showError(error);$('progress').textContent='Map unavailable';}
 finally{$('loading').hidden=true;setBusy(false);}
 if(ready)startGoogleMap();
}
async function startGoogleMap(){
 if(mapStarted||new URLSearchParams(location.search).get('map')==='local')return;
 // Defer billable/online loading while the user is only browsing the album.
 if(document.body.classList.contains('album-view'))return;
 mapStarted=true;
 try{
  const response=await fetch('/api/map-config');if(!response.ok)return;
  const config=await response.json();if(!config.apiKey)return;
  $('map-provider').textContent='Connecting to Google Maps…';
  const fallback=()=>{
   mapFailed=true;googleMap?.destroy();googleMap=null;
   document.body.classList.remove('google-active');$('google-map').setAttribute('aria-hidden','true');$('google-map').inert=true;
   $('map-provider').textContent='East Asia · local map';$('google-credit').hidden=true;$('local-credit').hidden=false;
   $('map-notice').hidden=false;$('map-notice').textContent='Google Maps is unavailable. Showing the local map. Check the connection, API access and website restrictions, then reload to retry.';
   if(ready){applyView();renderMarkers(visibleCities(),countVisits(trips));}
  };
  const candidate=await createGoogleMap({container:$('google-map'),config,onSelect:choose,onNearby:showNearby,onFailure:fallback,onZoom:zoom=>{$('zoom-in').disabled=zoom>=18;$('zoom-out').disabled=zoom<=3;}});
  if(mapFailed){candidate.destroy();return;}
  googleMap=candidate;renderMarkers(visibleCities(),countVisits(trips));await candidate.ready;
  if(mapFailed)return;
  document.body.classList.add('google-active');$('google-map').setAttribute('aria-hidden','false');$('google-map').inert=false;
  $('map-provider').textContent='Google Maps';$('google-credit').hidden=false;$('local-credit').hidden=true;
 }catch{if(!mapFailed){mapFailed=true;googleMap?.destroy();googleMap=null;document.body.classList.remove('google-active');$('map-provider').textContent='East Asia · local map';$('map-notice').hidden=false;$('map-notice').textContent='Google Maps could not start. The local map is still available. Reload to retry.';if(ready)applyView();}}
}
for(const id of ['search','region','visited'])$(id).addEventListener(id==='search'?'input':'change',()=>{if(ready)render();});
$('zoom-in').addEventListener('click',()=>{if(googleMap){googleMap.zoom(1);return;}view=zoomView(view,.65);applyView();});$('zoom-out').addEventListener('click',()=>{if(googleMap){googleMap.zoom(-1);return;}view=zoomView(view,1/.65);applyView();});$('fit').addEventListener('click',()=>{if(googleMap){googleMap.fit();return;}view=initialView();applyView();});
$('add-sample').addEventListener('click',()=>{if(selected)mutate(()=>repository.add(selected),'Sample visit saved in this browser. City brightness updated.');});
$('reset').addEventListener('click',()=>{if(confirm('Replace your sample edits with the original fictional trips?'))mutate(()=>repository.reset(),'Original sample album restored.',()=>drafts.clear());});
$('recover').addEventListener('click',async()=>{if(confirm('Replace damaged demo records with the original samples?')){try{await repository.reset();drafts.clear();await load();}catch(error){showError(error);}}});
$('retry').addEventListener('click',load);$('refresh').addEventListener('click',load);
window.addEventListener('travel-map:trips-changed',()=>{if(ready)mutate(()=>repository.list(),'Trip records refreshed.');});
// Touch scroll stays native at fit level. Pan only after zoom, outside markers.
let drag=null;
$('map').addEventListener('pointerdown',event=>{
 if(!ready||view.width>=initialView().width-.01||event.target.closest('.marker'))return;
 drag={id:event.pointerId,x:event.clientX,y:event.clientY,view:{...view}};$('map').setPointerCapture(event.pointerId);$('map').classList.add('dragging');
});
$('map').addEventListener('pointermove',event=>{
 if(!drag||drag.id!==event.pointerId)return;
 const rect=$('map').getBoundingClientRect(),ratio=Math.min(rect.width/drag.view.width,rect.height/drag.view.height);
 view=clampView({...drag.view,x:drag.view.x-(event.clientX-drag.x)/ratio,y:drag.view.y-(event.clientY-drag.y)/ratio});applyView();
});
for(const type of ['pointerup','pointercancel','lostpointercapture'])$('map').addEventListener(type,()=>{drag=null;$('map').classList.remove('dragging');});
function setAlbumView(album){
 document.body.classList.toggle('album-view',album);
 $('view-map').setAttribute('aria-pressed',String(!album));$('view-album').setAttribute('aria-pressed',String(album));
 const url=new URL(location.href);if(album)url.searchParams.set('view','album');else url.searchParams.delete('view');history.replaceState(null,'',url);
 if(!album&&ready){renderMarkers(visibleCities(),countVisits(trips));googleMap?.refresh();startGoogleMap();}
}
$('view-map').addEventListener('click',()=>setAlbumView(false));$('view-album').addEventListener('click',()=>setAlbumView(true));
setAlbumView(new URLSearchParams(location.search).get('view')==='album');
new ResizeObserver(()=>{if(ready&&!document.body.classList.contains('album-view'))renderMarkers(visibleCities(),countVisits(trips));}).observe($('map'));
load();

$('back-map').addEventListener('click',()=>{$('map-wrap').scrollIntoView({block:'start',behavior:'instant'});$('fit').focus({preventScroll:true});});
$('close-viewer').addEventListener('click',()=>$('photo-viewer').close());
$('photo-viewer').addEventListener('close',()=>{viewerTrigger?.focus({preventScroll:true});$('viewer-image').removeAttribute('src');});
