/** Render only a saved card to a downloadable local PNG. */
export async function exportCard(trip,city){
 await document.fonts.ready;
 const canvas=document.createElement('canvas'),ctx=canvas.getContext('2d'),width=1080,pad=64;
 function lines(text,font,maxWidth){ctx.font=font;const output=[];for(const paragraph of text.split('\n')){let line='';for(const char of paragraph){if(ctx.measureText(line+char).width>maxWidth&&line){output.push(line);line=char;}else line+=char;}output.push(line);}return output;}
 const title=lines(trip.title||'Untitled memory','48px Fraunces, Georgia, serif',width-pad*2),body=lines(trip.memory_text||trip.notes||'No notes yet.','28px system-ui, sans-serif',width-pad*2);
 let image=null;
 if(trip.photos[0]?.url){image=new Image();image.src=trip.photos[0].url;await image.decode();}
 const coverHeight=image?640:0,height=coverHeight+240+title.length*60+body.length*43;
 if(height>12000)throw new Error('This card is too long to export. Shorten the saved text first.');
 canvas.width=width;canvas.height=height;ctx.fillStyle='#f6f5f1';ctx.fillRect(0,0,width,height);
 if(image){const ratio=Math.max(width/image.width,coverHeight/image.height),w=image.width*ratio,h=image.height*ratio;ctx.save();ctx.beginPath();ctx.rect(0,0,width,coverHeight);ctx.clip();ctx.drawImage(image,(width-w)/2,(coverHeight-h)/2,w,h);ctx.restore();}
 let y=coverHeight+64;ctx.fillStyle='#ad4a29';ctx.font='24px system-ui, sans-serif';ctx.fillText(`${city.name} / ${city.local_name} · ${trip.trip_date||'Date not recorded'}`,pad,y);y+=70;
 ctx.fillStyle='#292e30';ctx.font='48px Fraunces, Georgia, serif';for(const line of title){ctx.fillText(line,pad,y);y+=60;}y+=25;
 ctx.font='28px system-ui, sans-serif';ctx.fillStyle='#626767';for(const line of body){ctx.fillText(line,pad,y);y+=43;}
 ctx.font='20px system-ui, sans-serif';ctx.fillText('Travel Memory · saved memory',pad,height-40);
 const blob=await new Promise(resolve=>canvas.toBlob(resolve,'image/png'));if(!blob)throw new Error('Could not create this PNG. Try a shorter card.');
 const url=URL.createObjectURL(blob),link=document.createElement('a');link.href=url;link.download=`${city.name}-${trip.trip_date||'memory'}-${trip.id.slice(0,8)}.png`;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
