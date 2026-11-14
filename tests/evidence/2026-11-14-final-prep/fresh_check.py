from pathlib import Path
import subprocess,os,time,httpx,hashlib,shutil,json,platform,sys
root=Path('/private/tmp/ailt-final-fresh-20261114')
out=Path('/Users/thomaslin/Documents/HKU/Year2 Sem1 上海/AILT9019/AILT9019-final-prep/tests/evidence/2026-11-14-final-prep')
state=root/'var-final-check';restored=root/'var-restored-check';backup=root/'backup-final-check'
env={k:v for k,v in os.environ.items() if not k.startswith('AI_')}
env.update(AI_PROVIDER='',AI_API_KEY='',TMM_DB_PATH=str(state/'travel.db'),TMM_MEDIA_DIR=str(state/'media'),TMM_TMP_DIR=str(state/'tmp'))
client=httpx.Client(base_url='http://127.0.0.1:8052',timeout=10)
log=open(out/'server.txt','w');proc=None
checks=[]
def start(target):
 global proc
 env.update(TMM_DB_PATH=str(target/'travel.db'),TMM_MEDIA_DIR=str(target/'media'),TMM_TMP_DIR=str(target/'tmp'))
 proc=subprocess.Popen([str(root/'.venv/bin/python'),'-m','backend','--port','8052'],cwd=root,env=env,stdout=log,stderr=log)
 for _ in range(80):
  try:
   if client.get('/api/cities').status_code==200:return
  except httpx.TransportError:pass
  time.sleep(.1)
 raise RuntimeError('startup failed')
def stop():
 global proc
 if proc:proc.terminate();proc.wait(timeout=10);proc=None
try:
 start(state)
 r=client.get('/app/?mode=api&map=local');assert r.status_code==200
 trip=client.post('/api/trips',json={'city_id':'jp-osaka','title':'Fresh clone check','notes':'Fictional test, no AI call.'});assert trip.status_code==201,trip.text
 tid=trip.json()['id']
 with open(root/'data/fixtures/T02/park-bench.png','rb') as f:r=client.post(f'/api/trips/{tid}/photos',files={'file':('park.png',f,'image/png')})
 assert r.status_code==201,r.text
 photo=r.json();media=client.get(photo['url']).content;mh=hashlib.sha256(media).hexdigest()
 r=client.patch(f'/api/trips/{tid}',json={'title':'Edited and restored','memory_text':'Manually reviewed fictional text.'});assert r.status_code==200
 snapshot=client.get('/api/trips').json();assert len(snapshot)==1
 checks.append('Fresh clone install, real server, trip create/upload/edit: pass')
 r=client.post(f'/api/trips/{tid}/memory',json={'confirmed':True});assert r.status_code==503,r.text
 assert client.get('/api/trips').json()==snapshot
 checks.append('No-key AI returns 503; album unchanged: pass')
 r=client.post(f'/api/trips/{tid}/photos',files={'file':('invalid.png',b'not an image','image/png')});assert r.status_code in (415,422),r.text
 assert client.get('/api/trips').json()==snapshot
 checks.append('Invalid image rejected without changing saved trip: pass')
 stop();start(state)
 assert client.get('/api/trips').json()==snapshot
 assert hashlib.sha256(client.get(photo['url']).content).hexdigest()==mh
 checks.append('Restart preserves trip, text and photo hash: pass')
 stop();shutil.copytree(state,backup);shutil.copytree(backup,restored)
 start(restored)
 assert client.get('/api/trips').json()==snapshot
 assert hashlib.sha256(client.get(photo['url']).content).hexdigest()==mh
 checks.append('Stopped-server database plus media backup restored to a different directory: pass')
 result={'date_hkt':'2026-11-14','commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'python':sys.version.split()[0],'node':subprocess.check_output(['node','--version'],text=True).strip(),'os':platform.platform(),'environment':'new public HTTPS clone and new venv on same development Mac; not another computer or human acceptance','cloud_requests':0,'checks':checks,'trip_snapshot':snapshot,'photo_sha256':mh}
 (out/'fresh-clone.json').write_text(json.dumps(result,indent=2))
 print(json.dumps({k:v for k,v in result.items() if k!='trip_snapshot'},indent=2))
finally:stop();client.close();log.close()
