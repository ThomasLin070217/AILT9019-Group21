"""Original geometric test cards, not travel photographs or model-generated evidence.
Requires Pillow only to rebuild; committed PNGs need no dependency at runtime.
"""
from pathlib import Path
import json,hashlib
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/fixtures/T01';OUT.mkdir(parents=True,exist_ok=True)
font=ImageFont.load_default(size=36)
small=ImageFont.load_default(size=24)
for name,title,subtitle,colors in [
 ('01-blue-red.png','SYNTHETIC VISUAL FIXTURE','Two squares: blue and red',[(45,90,170),(180,60,45)]),
 ('02-green-circle.png','SYNTHETIC VISUAL FIXTURE','One green circle',[(45,125,85)])]:
 im=Image.new('RGB',(900,600),'#f7f6ef');d=ImageDraw.Draw(im)
 d.text((45,45),title,fill='#20372e',font=font);d.text((45,110),subtitle,fill='#20372e',font=small)
 if len(colors)==2:
  d.rectangle((90,225,330,465),fill=colors[0]);d.rectangle((460,225,700,465),fill=colors[1])
 else:d.ellipse((300,205,590,495),fill=colors[0])
 d.text((45,550),'Not a real photograph or proof of travel.',fill='#20372e',font=small)
 im.save(OUT/name)
fixture={
 'id':'T01','owner':'Thomas','status':'prepared_not_run','kind':'synthetic_visual_smoke_test',
 'input':{'city_id':'jp-osaka','city':'Osaka','photos':['01-blue-red.png','02-green-circle.png'],'notes':'Fictional test record: I visited Osaka for two days. It rained on the first day. I made these colour cards during the trip.'},
 'known_facts':['The user-specified city is Osaka.','The fictional visit lasted two days.','The user says it rained on the first day.','Image 1 contains one blue square and one red square.','Image 2 contains one green circle.'],
 'required_memory_facts':['Osaka','two-day visit','rain on first day'],
 'permitted_optional_details':['The blue/red squares and green circle, if mentioned accurately.'],
 'forbidden_inferences':['Identifying the synthetic cards as photographs of Osaka.','Any companion, specific landmark, restaurant, meal, feeling or date not supplied.','Claiming the coloured shapes prove the city or weather.'],
 'pass_rule':'An editable title and short text preserve the three required memory facts, introduce no unsupported experiences, and do not describe these synthetic graphics as real travel photos.',
 'source':{'creator':'Original task-authored geometric fixtures','licence':'CC0-1.0','permission':'Prepared for inclusion in the team course repository; no people or personal data.','sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.glob('*.png')}},
 'limitations':['Tests note grounding and simple visible details only.','Does not establish quality on real travel photos.','No cloud model has been called; reviewers and results remain blank.'],
 'results':[]}
(OUT/'case.json').write_text(json.dumps(fixture,indent=2)+'\n')
print('T01 prepared; no model run claimed.')
