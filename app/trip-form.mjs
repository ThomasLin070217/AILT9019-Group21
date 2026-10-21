/** Real trip creation. Unsaved files stay in memory and never enter demo storage. */
export function setupTripForm({repository, onSaved}) {
  const $=id=>document.getElementById(id),form=$('trip-form');
  let selected=[],saving=false,reading=false,requestId=null,urls=[];
  function error(text){$('trip-error').textContent=text;$('trip-error').hidden=!text;}
  function release(){urls.forEach(url=>URL.revokeObjectURL(url));urls=[];}
  function renderPhotos(){
    release();$('photo-previews').replaceChildren();
    selected.forEach((file,index)=>{
      const item=document.createElement('figure'),img=document.createElement('img'),caption=document.createElement('figcaption'),remove=document.createElement('button');
      const url=URL.createObjectURL(file);urls.push(url);img.src=url;img.alt=`Selected photo ${index+1}`;
      caption.textContent=file.name;remove.type='button';remove.textContent='Remove';remove.disabled=saving;
      remove.setAttribute('aria-label',`Remove photo ${index+1}`);
      remove.addEventListener('click',()=>{selected.splice(index,1);renderPhotos();});
      item.append(img,caption,remove);$('photo-previews').append(item);
    });
    $('photo-selection-count').textContent=selected.length?`${selected.length} of 5 photos selected. The first photo will be the cover.`:'No photos selected.';
  }
  function changed(){return selected.length||$('trip-title').value||$('trip-date').value||$('trip-notes').value;}
  function close(){
    if(saving||reading)return;
    if(changed()&&!confirm('Discard this unsaved trip and its selected photos?'))return;
    reset();form.hidden=true;$('new-trip').hidden=false;$('new-trip').focus();
  }
  function reset(){form.reset();selected=[];requestId=null;release();renderPhotos();error('');}
  $('new-trip').addEventListener('click',()=>{
    const repo=repository();if(!repo)return;
    requestId=crypto.randomUUID();form.hidden=false;$('new-trip').hidden=true;
    $('trip-city').replaceChildren(...repo.cities.map(city=>{const option=document.createElement('option');option.value=city.id;option.textContent=`${city.name} / ${city.local_name}`;return option;}));
    $('trip-city').value=$('new-trip').dataset.cityId||repo.cities[0].id;
    form.scrollIntoView({block:'nearest'});$('trip-city').focus({preventScroll:true});
  });
  $('cancel-trip').addEventListener('click',close);
  $('trip-photos').addEventListener('change',async()=>{
    const files=[...$('trip-photos').files];$('trip-photos').value='';error('');
    if(!files.length)return;
    if(selected.length+files.length>5){error('Choose up to 5 photos. Remove a selected photo before adding another.');return;}
    if(files.some(file=>!['image/jpeg','image/png','image/webp'].includes(file.type)||file.size>5*1024*1024)){
      error('Choose JPEG, PNG or WebP photos, up to 5 MB each.');return;
    }
    if([...selected,...files].reduce((n,file)=>n+file.size,0)>20*1024*1024){error('The photos exceed 20 MB in total. Choose smaller files.');return;}
    reading=true;$('save-trip').disabled=true;$('trip-photos').disabled=true;
    try{
      for(const file of files){
        const bitmap=await createImageBitmap(file);
        const valid=bitmap.width*bitmap.height<=25_000_000;bitmap.close();
        if(!valid)throw new Error('Choose photos up to 25 megapixels.');
      }
      selected.push(...files);renderPhotos();
    }catch(e){error(e.message==='Choose photos up to 25 megapixels.'?e.message:'A photo could not be read. Choose a valid JPEG, PNG or WebP.');}
    finally{reading=false;$('save-trip').disabled=false;$('trip-photos').disabled=false;}
  });
  form.addEventListener('submit',async event=>{
    event.preventDefault();if(saving||reading)return;error('');
    if(!selected.length){error('Choose at least one photo before saving.');$('trip-photos').focus();return;}
    saving=true;$('trip-fields').disabled=true;$('save-trip').textContent='Saving trip…';form.setAttribute('aria-busy','true');renderPhotos();
    try{
      const photos=await Promise.all(selected.map(file=>new Promise((resolve,reject)=>{
        const reader=new FileReader();reader.onerror=()=>reject(new Error('Could not read a selected photo. Choose it again.'));
        reader.onload=()=>resolve({data:reader.result.split(',')[1]});reader.readAsDataURL(file);
      })));
      const data={request_id:requestId,city_id:$('trip-city').value,trip_date:$('trip-date').value||null,title:$('trip-title').value,notes:$('trip-notes').value,photos};
      const trip=await repository().create(data);
      reset();form.hidden=true;$('new-trip').hidden=false;onSaved(trip);
    }catch(e){error(`${e.message} Your form and photos are still here. If the connection was interrupted, retry the same save.`);}
    finally{saving=false;$('trip-fields').disabled=false;$('save-trip').textContent='Save trip';form.setAttribute('aria-busy','false');renderPhotos();}
  });
  window.addEventListener('beforeunload',event=>{if(!form.hidden&&changed()){event.preventDefault();event.returnValue='';}});
}
