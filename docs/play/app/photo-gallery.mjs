// PhotoSwipe is lazy-loaded from a pinned, locally bundled MIT dependency.
// Captions are assigned with textContent: trip text is data, never HTML.
const dimensions = new Map();
let activeGallery;
function imageSize(src){
 if(dimensions.has(src))return Promise.resolve(dimensions.get(src));
 return new Promise((resolve,reject)=>{
  const image=new Image();
  const timer=setTimeout(()=>finish(new Error('Photo loading timed out')),8000);
  function finish(error){clearTimeout(timer);image.onload=null;image.onerror=null;
   if(error){reject(error);return;}
   const size={width:image.naturalWidth,height:image.naturalHeight};
   if(!size.width||!size.height){reject(new Error('Photo has no dimensions'));return;}
   dimensions.set(src,size);resolve(size);
  }
  image.onload=()=>finish();image.onerror=()=>finish(new Error('Photo unavailable'));image.src=src;
 });
}
export async function showPhotoGallery(items,index,trigger){
 if(activeGallery||!items.length)return;
 const [{default:PhotoSwipe},sizes]=await Promise.all([
  import('./vendor/photoswipe/photoswipe.esm.js'),
  Promise.all(items.map(item=>imageSize(item.src).catch(()=>({width:1600,height:1200}))))
 ]);
 // Another caller may have completed loading while this one was waiting.
 if(activeGallery)return;
 // Reserve the measured caption height, including wrapped long titles and alt text.
 const captionHeights=new Map();
 function captionPadding(viewport){
  const key=`${viewport.x}:${viewport.y}`;
  if(!captionHeights.has(key)){
   const probe=document.createElement('div');probe.className='pswp__memory-caption';
   Object.assign(probe.style,{position:'fixed',width:`${viewport.x}px`,visibility:'hidden',pointerEvents:'none'});
   probe.setAttribute('aria-hidden','true');document.body.append(probe);
   let height=0;
   try{for(const item of items){probe.textContent=item.caption||'';height=Math.max(height,probe.getBoundingClientRect().height);}}
   finally{probe.remove();}
   captionHeights.set(key,Math.ceil(height)+8);
  }
  return {top:64,bottom:captionHeights.get(key),left:16,right:16};
 }
 const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
 const gallery=new PhotoSwipe({
  dataSource:items.map((item,i)=>({...item,...sizes[i]})),index,loop:false,
  bgOpacity:1,showHideAnimationType:reduced?'none':'fade',
  showAnimationDuration:180,hideAnimationDuration:140,zoomAnimationDuration:reduced?0:180,
  paddingFn:captionPadding,
  closeTitle:'Close photos',zoomTitle:'Zoom photo',arrowPrevTitle:'Previous photo',arrowNextTitle:'Next photo',
  errorMsg:'Photo unavailable. Close the viewer to return to your saved memories.',
  trapFocus:true,returnFocus:true
 });
 activeGallery=gallery;
 const pageNodes=[document.querySelector('.topbar'),document.querySelector('main')].filter(Boolean);
 const priorInert=pageNodes.map(element=>element.inert);
 gallery.on('uiRegister',()=>gallery.ui.registerElement({
  name:'memory-caption',order:9,isButton:false,appendTo:'root',
  onInit:(element,instance)=>{element.setAttribute('aria-live','polite');
   instance.on('change',()=>{element.textContent=instance.currSlide?.data.caption||'';});
  }
 }));
 gallery.on('afterInit',()=>{gallery.element.setAttribute('aria-label','Trip photos');pageNodes.forEach(element=>{element.inert=true;});});
 gallery.on('destroy',()=>{
  activeGallery=null;pageNodes.forEach((element,i)=>{element.inert=priorInert[i];});
  if(trigger?.isConnected)trigger.focus({preventScroll:true});
 });
 try{gallery.init();}catch(error){activeGallery=null;gallery.destroy();throw error;}
}
