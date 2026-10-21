/** Explicit disclosure → cloud request → editable unsaved draft → explicit save. */
export function createAIControls({repository,onSaved,onRender,onMessage}){
 const states=new Map(),key='travel-memory-map.ai-drafts.v1';
 const el=(tag,text,classes)=>{const node=document.createElement(tag);if(text!==undefined)node.textContent=text;if(classes)node.className=classes;return node;};
 function persist(){try{sessionStorage.setItem(key,JSON.stringify([...states].filter(([,s])=>s.result).map(([id,s])=>[id,{result:s.result,title:s.title,memory_text:s.memory_text}])));}catch{onMessage('AI draft stays in this page only. Keep it open until you save or discard it.');}}
 try{const rows=JSON.parse(sessionStorage.getItem(key)||'[]');if(Array.isArray(rows))for(const [id,s]of rows)if(typeof id==='string'&&s?.result&&['draft','clarification'].includes(s.result.status)&&Number.isInteger(s.result.expected_revision)&&['warnings','questions'].every(k=>Array.isArray(s.result[k])&&s.result[k].length<=10&&s.result[k].every(v=>typeof v==='string'&&v.length<=1000))&&typeof s.title==='string'&&s.title.length<=200&&typeof s.memory_text==='string'&&s.memory_text.length<=5000)states.set(id,{...s,busy:false,error:'',disclosure:false});}catch{}
 async function configuration(id){let s=states.get(id)||{};states.set(id,{...s,busy:true,disclosure:true,error:''});onRender();try{const response=await fetch('/api/ai-config');const config=await response.json();if(!response.ok)throw new Error(config.error);s=states.get(id);states.set(id,{...s,config,busy:false});}catch(e){states.set(id,{...states.get(id),busy:false,error:e.message});}onRender();}
 function draw(card,trip){
  const actions=card.querySelector('.card-actions'),button=el('button','Generate AI memory','text-button');button.type='button';actions.append(button);let s=states.get(trip.id);button.disabled=Boolean(s?.busy);
  button.addEventListener('click',()=>configuration(trip.id));if(!s)return;
  const panel=el('section',undefined,'ai-panel');panel.setAttribute('aria-label','AI memory draft');panel.setAttribute('aria-busy',String(Boolean(s.busy)));
  if(s.disclosure){
   panel.append(el('h4','Review before sending'));
   if(s.config){
    panel.append(el('p',`${s.config.provider} · ${s.config.model||'model not configured'}`,'ai-provider'),el('p',`Only this trip: ${trip.photos.length} metadata-free photo copies (up to 1024 px), the selected city, trip date and your notes. No other trips, previous AI memories or original file metadata are included.`));
    const details=el('details');details.append(el('summary','See the text being sent'),el('p',`${trip.city_id} · ${trip.trip_date||'No date'}`),el('p',trip.notes||'No notes.'));panel.append(details);
    panel.append(el('p',`Endpoint: ${s.config.endpoint}`,'small'),el('p','The provider may charge for this request and retain data under its own policy. Local deletion cannot delete provider-held data.','small'));
    if(s.config.privacy_url){const link=el('a','Provider data policy');link.href=s.config.privacy_url;link.target='_blank';link.rel='noreferrer';panel.append(link);}
    if(!s.config.configured)panel.append(el('p','AI is not configured. Set TRAVEL_AI_API_KEY and TRAVEL_AI_MODEL in .env.ai.local on this computer, then check setup again. Your album works without AI.','form-error'));
   }else panel.append(el('p',s.busy?'Checking AI setup…':'AI setup could not be loaded.'));
   const controls=el('div',undefined,'trip-form-actions'),send=el('button',s.busy?'Working…':'Send & generate','primary-button'),close=el('button','Cancel'),check=el('button','Check AI setup','text-button');
   for(const b of [send,close,check])b.type='button';send.disabled=s.busy||!s.config?.configured;close.disabled=Boolean(s.busy);check.disabled=Boolean(s.busy);controls.append(send,close,check);panel.append(controls);
   check.addEventListener('click',()=>configuration(trip.id));close.addEventListener('click',()=>{s.disclosure=false;if(!s.result)states.delete(trip.id);onRender();});
   send.addEventListener('click',async()=>{
    if(s.busy)return;if(s.result&&!confirm('Replace your current unsaved AI draft with a new generated draft?'))return;
    s.busy=true;s.error='';onRender();
    try{const response=await fetch(`/api/trips/${encodeURIComponent(trip.id)}/generate`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({expected_revision:trip.revision??0,consent:true}),signal:AbortSignal.timeout(70000)});const result=await response.json();if(!response.ok)throw new Error(result.error||'Generation failed.');Object.assign(s,{result,title:result.title,memory_text:result.memory_text,disclosure:false});persist();onMessage('AI result received as an unsaved draft. Review it against your photos and notes.');}
    catch(e){s.error=e.message+' Your saved trip is unchanged. Retry only when you choose to.';}finally{s.busy=false;onRender();}
   });
  }
  if(s.result){
   const result=s.result;panel.append(el('h4',result.status==='clarification'?'More information needed':'AI draft · not saved'),el('p',`${result.provider} · ${result.model} · ${result.prompt_version}`,'small'));
   for(const text of [...result.warnings,...result.questions])panel.append(el('p',text,'ai-warning'));
   if(result.status==='clarification')panel.append(el('p','Update this trip’s notes or photos, then request a new draft. Nothing has been saved.'));
   else{
    const form=el('form'),fields=el('fieldset');fields.disabled=Boolean(s.busy);
    for(const [name,label,type,limit]of [['title','Draft title','input',200],['memory_text','Draft memory','textarea',5000]]){const caption=el('label',label),input=document.createElement(type);input.id=`ai-${name}-${trip.id}`;caption.htmlFor=input.id;input.value=s[name];input.maxLength=limit;input.required=true;if(type==='textarea')input.rows=6;input.addEventListener('input',()=>{s[name]=input.value;persist();});fields.append(caption,input);}
    fields.append(el('p','Check every factual detail. Saving updates this same trip; it never creates another visit.','small'));const save=el('button',s.busy?'Saving…':'Save reviewed memory','primary-button');save.type='submit';fields.append(save);form.append(fields);panel.append(form);
    form.addEventListener('submit',async event=>{event.preventDefault();if(s.busy)return;s.busy=true;s.error='';onRender();try{const updated=await repository().edit(trip.id,{title:s.title,memory_text:s.memory_text,expected_revision:result.expected_revision});states.delete(trip.id);persist();onSaved(updated);onMessage('Reviewed memory saved to this trip. Visit count unchanged.');}catch(e){s.error=e.message+' Your AI draft is kept.';s.busy=false;onRender();}});
   }
   const discard=el('button','Discard AI draft','text-button');discard.type='button';discard.disabled=Boolean(s.busy);discard.addEventListener('click',()=>{if(!confirm('Discard this unsaved AI result? Your saved trip will stay as it is.'))return;states.delete(trip.id);persist();onRender();});panel.append(discard);
  }
  if(s.error){const error=el('p',s.error,'form-error');error.setAttribute('role','alert');panel.append(error);}card.append(panel);
 }
 function reconcile(trips){const ids=new Set(trips.map(t=>t.id));let changed=false;for(const id of states.keys())if(!ids.has(id)){states.delete(id);changed=true;}if(changed)persist();}
 window.addEventListener('beforeunload',event=>{if([...states.values()].some(s=>s.busy||s.result?.status==='draft')){event.preventDefault();event.returnValue='';}});
 return {draw,reconcile};
}
