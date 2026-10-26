/** Replace the photos of an existing trip without creating another visit. */
export function createPhotoEditor({repository,onSaved,onRender,onMessage}){
 const states=new Map(),el=(tag,text,classes)=>{const node=document.createElement(tag);if(text!==undefined)node.textContent=text;if(classes)node.className=classes;return node;};
 function discard(id){const state=states.get(id);state?.urls?.forEach(url=>URL.revokeObjectURL(url));states.delete(id);}
 function draw(card,trip){
  const button=el('button','Edit photos','text-button');button.type='button';card.querySelector('.card-actions').append(button);const s=states.get(trip.id);button.disabled=Boolean(s?.busy);
  button.addEventListener('click',()=>{if(!states.has(trip.id))states.set(trip.id,{files:[],urls:[],request_id:crypto.randomUUID(),revision:trip.revision??0,busy:false,error:''});onRender();});if(!s)return;
  const panel=el('section',undefined,'photo-editor ai-panel');panel.setAttribute('aria-label','Edit trip photos');panel.append(el('h4','Replace trip photos'),el('p','Choose the complete new set (1–5 JPEG, PNG or WebP; 5 MB each, 20 MB total). Your current photos stay until saving succeeds. The trip and visit count stay the same.'));
  const input=el('input');input.type='file';input.accept='image/jpeg,image/png,image/webp';input.multiple=true;input.disabled=s.busy;input.id=`replace-photos-${trip.id}`;const label=el('label','New photo set');label.htmlFor=input.id;panel.append(label,input);
  input.addEventListener('change',async()=>{
   const files=[...input.files];if(!files.length)return;
   if(files.length>5||files.some(f=>!['image/jpeg','image/png','image/webp'].includes(f.type)||f.size>5*1024*1024)||files.reduce((n,f)=>n+f.size,0)>20*1024*1024){s.error='Choose 1–5 supported photos, up to 5 MB each and 20 MB total.';onRender();return;}
   s.urls.forEach(url=>URL.revokeObjectURL(url));s.files=files;s.urls=files.map(file=>URL.createObjectURL(file));s.request_id=crypto.randomUUID();s.error='';onRender();
  });
  const previews=el('div',undefined,'photo-previews');s.files.forEach((file,i)=>{const figure=el('figure'),img=el('img');img.src=s.urls[i];img.alt=`New photo ${i+1}`;figure.append(img,el('figcaption',file.name));previews.append(figure);});panel.append(previews);
  const actions=el('div',undefined,'trip-form-actions'),save=el('button',s.busy?'Saving…':'Save new photos','primary-button'),cancel=el('button','Cancel photo edit');save.type='button';cancel.type='button';save.disabled=s.busy||!s.files.length;cancel.disabled=s.busy;actions.append(save,cancel);panel.append(actions);
  cancel.addEventListener('click',()=>{if(s.files.length&&!confirm('Discard the selected replacement photos? Your saved photos stay unchanged.'))return;discard(trip.id);onRender();});
  save.addEventListener('click',async()=>{if(s.busy||!s.files.length)return;s.busy=true;s.error='';onRender();try{const photos=await Promise.all(s.files.map(file=>new Promise((resolve,reject)=>{const reader=new FileReader();reader.onload=()=>resolve({data:reader.result.split(',')[1]});reader.onerror=()=>reject(new Error('A selected file could not be read.'));reader.readAsDataURL(file);})));const updated=await repository().replacePhotos(trip.id,{photos,request_id:s.request_id,expected_revision:s.revision});discard(trip.id);onSaved(updated);onMessage('Trip photos updated. Visit count unchanged.');}catch(e){s.error=e.message+' Your selected files are kept.';s.busy=false;onRender();}});
  if(s.error){const error=el('p',s.error,'form-error');error.setAttribute('role','alert');panel.append(error);}card.append(panel);
 }
 function reconcile(trips){const ids=new Set(trips.map(t=>t.id));for(const id of states.keys())if(!ids.has(id))discard(id);}
 window.addEventListener('beforeunload',event=>{if([...states.values()].some(s=>s.files.length||s.busy)){event.preventDefault();event.returnValue='';}});
 return {draw,reconcile};
}
