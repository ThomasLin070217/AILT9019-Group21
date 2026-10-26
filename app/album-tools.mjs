/** Download/import portable backups without overwriting current records. */
export function setupAlbumTools({onRestored,onMessage}){
 const $=id=>document.getElementById(id);let file=null,preview=null;
 async function upload(path){const response=await fetch(path,{method:'POST',headers:{'Content-Type':'application/zip'},body:file,signal:AbortSignal.timeout(60000)});const result=await response.json();if(!response.ok)throw new Error(result.error||'Could not read this backup.');return result;}
 function error(message){$('backup-error').textContent=message;$('backup-error').hidden=!message;}
 $('download-backup').addEventListener('click',async()=>{
  const button=$('download-backup');button.disabled=true;error('');
  try{const response=await fetch('/api/backup');if(!response.ok)throw new Error((await response.json()).error);const blob=await response.blob(),url=URL.createObjectURL(blob),link=document.createElement('a');link.href=url;link.download=`travel-memory-backup-${new Date().toISOString().slice(0,10)}.zip`;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);onMessage('Album backup downloaded. Keep it in a safe place; it contains your photos and notes.');}
  catch(e){error(e.message);}finally{button.disabled=false;}
 });
 $('restore-file').addEventListener('change',async()=>{
  file=$('restore-file').files[0]||null;preview=null;$('restore-preview').hidden=true;error('');if(!file)return;
  if(file.size>100*1024*1024){error('Choose a backup up to 100 MB.');return;}
  $('restore-file').disabled=true;
  try{preview=await upload('/api/backups/preview');$('restore-summary').textContent=`${preview.total} trips: ${preview.new} new, ${preview.unchanged} already saved, ${preview.conflicts} conflicts. Existing trips are never overwritten.`;$('restore-copy-label').hidden=!preview.conflicts;$('restore-copies').checked=false;$('restore-preview').hidden=false;}
  catch(e){error(e.message);}finally{$('restore-file').disabled=false;}
 });
 $('restore-backup').addEventListener('click',async()=>{
  if(!file||!preview)return;error('');
  if(preview.conflicts&&!$('restore-copies').checked){error('Choose “Import conflicts as new trips” to keep both versions.');return;}
  if(!confirm(`Import ${preview.new+($('restore-copies').checked?preview.conflicts:0)} trips from this backup? Existing trips will be kept. Conflicting copies count as new visits.`))return;
  const button=$('restore-backup');button.disabled=true;$('restore-file').disabled=true;
  try{const result=await upload('/api/backups/restore'+($('restore-copies').checked?'?copies=1':''));await onRestored();onMessage(`Restored ${result.imported} trips; skipped ${result.skipped} identical trips.`);$('restore-preview').hidden=true;$('restore-file').value='';file=null;preview=null;}
  catch(e){error(e.message);}finally{button.disabled=false;$('restore-file').disabled=false;}
 });
}
