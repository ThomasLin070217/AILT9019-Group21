/** Saved-trip text editor. Drafts survive city/view changes and tab reloads. */
export function createTripEditor({repository,onSaved,onRemoved,onRender,onReload,onWarning}){
 const key='travel-memory-map.local-edits.v1',drafts=new Map(),deletions=new Map();
 let storage;
 const values=trip=>({title:trip.title,trip_date:trip.trip_date||'',notes:trip.notes,...(trip.memory_text?{memory_text:trip.memory_text}:{})});
 const dirty=draft=>Object.keys(draft.values).some(key=>draft.values[key]!==draft.base[key]);
 const text=(tag,content,classes)=>{const element=document.createElement(tag);if(content!==undefined)element.textContent=content;if(classes)element.className=classes;return element;};
 function persist(){try{if(!storage)throw new Error();storage.setItem(key,JSON.stringify([...drafts].map(([id,d])=>[id,{base:d.base,values:d.values,revision:d.revision}])));}catch{onWarning('Your edit stays in this page only. Keep it open until you save.');}}
 try{
  storage=sessionStorage;const stored=JSON.parse(storage.getItem(key)||'[]');
  if(!Array.isArray(stored))throw new Error();
  for(const item of stored){
   if(!Array.isArray(item)||item.length!==2)throw new Error();
   const [id,draft]=item;
   if(typeof id!=='string'||!draft||!Number.isInteger(draft.revision)||draft.revision<0)throw new Error();
   for(const fields of [draft.base,draft.values])if(!fields||typeof fields.title!=='string'||fields.title.length>200||typeof fields.notes!=='string'||fields.notes.length>5000||typeof fields.trip_date!=='string'||fields.trip_date.length>10)throw new Error();
   drafts.set(id,{...draft,saving:false,error:''});
  }
 }catch{drafts.clear();onWarning('Saved edit drafts could not be read. Your saved trips are still available.');}
 function focusEdit(id){document.querySelector(`[data-trip-id="${CSS.escape(id)}"] .edit-trip`)?.focus({preventScroll:true});}
 function draw(card,trip){
  const deletion=deletions.get(trip.id);
  const actions=text('div',undefined,'card-actions'),edit=text('button','Edit trip','text-button edit-trip'),remove=text('button','Delete trip','text-button delete-trip');edit.type='button';remove.type='button';actions.append(edit,remove);card.append(actions);
  const draft=drafts.get(trip.id);
  edit.hidden=Boolean(draft);edit.disabled=Boolean(deletion);remove.hidden=Boolean(deletion);remove.disabled=Boolean(draft?.saving);
  edit.addEventListener('click',()=>{drafts.set(trip.id,{base:values(trip),values:values(trip),revision:trip.revision??0,saving:false,error:''});persist();onRender();document.getElementById(`edit-title-${trip.id}`)?.focus();});
  remove.addEventListener('click',()=>{
   if(drafts.get(trip.id)?.saving)return;
   deletions.set(trip.id,{deleting:false,error:''});onRender();document.querySelector(`[data-trip-id="${CSS.escape(trip.id)}"] .keep-trip`)?.focus({preventScroll:true});
  });
  if(deletion){
   const panel=text('section',undefined,'delete-trip-confirmation'),heading=text('h4','Delete this trip?');heading.id=`delete-heading-${trip.id}`;panel.setAttribute('aria-labelledby',heading.id);panel.setAttribute('aria-busy',String(deletion.deleting));
   panel.append(heading,text('p',`“${trip.title}” and its ${trip.photos.length} saved ${trip.photos.length===1?'photo':'photos'} will be removed from this computer's album. This removes one visit. Your original photo files are untouched.`));
   if(draft)panel.append(text('p','Any unsaved edits to this trip will also be discarded.'));
   panel.append(text('p','This cannot be undone.','small'));
   const controls=text('div',undefined,'trip-form-actions'),keep=text('button','Keep trip','keep-trip'),confirmDelete=text('button',deletion.deleting?'Deleting…':'Delete permanently','danger-button');keep.type='button';confirmDelete.type='button';keep.disabled=deletion.deleting;confirmDelete.disabled=deletion.deleting;controls.append(keep,confirmDelete);panel.append(controls);
   const failure=text('p',deletion.error,'form-error');failure.hidden=!deletion.error;failure.setAttribute('role','alert');failure.tabIndex=-1;panel.append(failure);card.append(panel);
   keep.addEventListener('click',()=>{deletions.delete(trip.id);onRender();document.querySelector(`[data-trip-id="${CSS.escape(trip.id)}"] .delete-trip`)?.focus({preventScroll:true});});
   confirmDelete.addEventListener('click',async()=>{
    if(deletion.deleting)return;deletion.deleting=true;deletion.error='';onRender();
    try{const result=await repository().remove(trip.id,trip.revision??0);drafts.delete(trip.id);deletions.delete(trip.id);persist();onRemoved(result);}
    catch(e){deletion.deleting=false;deletion.error=`${e.message} Refresh the album if the connection was interrupted; any edit draft is kept.`;onRender();document.querySelector(`[data-trip-id="${CSS.escape(trip.id)}"] .delete-trip-confirmation .form-error`)?.focus({preventScroll:true});}
   });
  }
  if(!draft)return;
  const form=text('form',undefined,'real-trip-editor'),heading=text('h4','Edit this trip'),fieldset=document.createElement('fieldset');
  heading.id=`edit-heading-${trip.id}`;form.setAttribute('aria-labelledby',heading.id);form.setAttribute('aria-busy',String(draft.saving));fieldset.disabled=draft.saving||Boolean(deletion);
  form.append(heading,text('p','Changes update this visit. The city, photos and visit count stay the same.','small'));
  for(const [name,label,type,limit] of [['title','Title','text',200],['trip_date','Trip date','date'],['notes','Your notes','textarea',5000],...(draft.values.memory_text!==undefined?[['memory_text','Saved memory','textarea',5000]]:[])]){
   const input=document.createElement(type==='textarea'?'textarea':'input'),caption=text('label',label);
   input.id=`edit-${name==='title'?'title':name}-${trip.id}`;caption.htmlFor=input.id;input.name=name;input.value=draft.values[name];
   if(type==='textarea')input.rows=5;else input.type=type;if(limit)input.maxLength=limit;
   input.addEventListener('input',()=>{draft.values[name]=input.value;draft.error='';persist();});fieldset.append(caption,input);
  }
  const controls=text('div',undefined,'trip-form-actions'),save=text('button',draft.saving?'Saving changes…':'Save changes','primary-button'),cancel=text('button','Cancel');
  save.type='submit';cancel.type='button';controls.append(save,cancel);fieldset.append(controls);
  const error=text('p',draft.error,'form-error');error.hidden=!draft.error;error.setAttribute('role','alert');error.tabIndex=-1;
  const reload=text('button','Reload saved version','text-button');reload.type='button';reload.disabled=draft.saving||Boolean(deletion);
  reload.addEventListener('click',async()=>{
   if(dirty(draft)&&!confirm('Discard your draft and load the latest saved version?'))return;
   reload.disabled=true;
   try{const rows=await repository().list();drafts.delete(trip.id);persist();onReload(rows);focusEdit(trip.id);}
   catch(e){draft.error=`${e.message} Your draft is still here.`;onRender();}
  });
  cancel.addEventListener('click',()=>{
   if(dirty(draft)&&!confirm('Discard your unsaved changes to this trip?'))return;
   drafts.delete(trip.id);persist();onRender();focusEdit(trip.id);
  });
  form.append(fieldset,error,reload);card.append(form);
  form.addEventListener('submit',async event=>{
   event.preventDefault();if(draft.saving)return;draft.saving=true;draft.error='';fieldset.disabled=true;reload.disabled=true;save.textContent='Saving changes…';form.setAttribute('aria-busy','true');
   const patch={...draft.values,trip_date:draft.values.trip_date||null,expected_revision:draft.revision};
   try{const updated=await repository().edit(trip.id,patch);drafts.delete(trip.id);persist();onSaved(updated);focusEdit(trip.id);}
   catch(e){draft.saving=false;draft.error=`${e.message} Your unsaved changes are kept.`;persist();onRender();document.querySelector(`[data-trip-id="${CSS.escape(trip.id)}"] .form-error`)?.focus({preventScroll:true});}
  });
 }
 function reconcile(trips){const ids=new Set(trips.map(trip=>trip.id));let changed=false;for(const id of drafts.keys())if(!ids.has(id)){drafts.delete(id);changed=true;}for(const id of deletions.keys())if(!ids.has(id))deletions.delete(id);if(changed)persist();}
 window.addEventListener('beforeunload',event=>{if([...drafts.values()].some(d=>dirty(d)||d.saving)||[...deletions.values()].some(d=>d.deleting)){event.preventDefault();event.returnValue='';}});
 return {draw,reconcile};
}
