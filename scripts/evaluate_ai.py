#!/usr/bin/env python3
"""Freeze-check or run five real Responses API cases; never invent reviewer verdicts."""
import argparse,base64,csv,hashlib,json,subprocess,sys,tempfile
from datetime import datetime,timezone
from pathlib import Path
from uuid import uuid4
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from album_store import AlbumStore
from ai_memory import AIError,PROMPT_VERSION,generate,settings

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--live',action='store_true',help='Send the five public fixtures to the configured provider (billable). Default only verifies local inputs.')
 parser.add_argument('--case',action='append',choices=['T01','T02','T03','T04','T05'],help='Only rerun named cases; default all five.')
 parser.add_argument('--output',type=Path,default=ROOT/'.context/ai-evaluation')
 args=parser.parse_args()
 raw=(ROOT/'data/evaluation/cases.json').read_bytes();manifest=json.loads(raw)
 for case in manifest['cases']:
  for photo in case['photos']:
   if hashlib.sha256((ROOT/photo['path']).read_bytes()).hexdigest()!=photo['sha256']:raise SystemExit('Fixture hash mismatch: '+photo['path'])
 print('Verified five frozen fixture cases and image hashes.')
 if args.case:manifest['cases']=[case for case in manifest['cases'] if case['id'] in args.case]
 if not args.live:return
 config=settings(ROOT);stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');out=args.output/stamp;out.mkdir(parents=True)
 commit=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True).stdout.strip()
 dirty=bool(subprocess.run(['git','status','--porcelain'],cwd=ROOT,capture_output=True,text=True).stdout.strip())
 report={'source_commit':commit,'working_tree_dirty':dirty,'adapter_sha256':hashlib.sha256((ROOT/'ai_memory.py').read_bytes()).hexdigest(),'created_at':stamp,'status':'not_run','provider':config['provider'],'model':config['model'],'prompt_version':PROMPT_VERSION,'manifest_sha256':hashlib.sha256(raw).hexdigest(),'human_review':'pending; two independent reviewers required','runs':[]}
 if not config['key'] or not config['model']:
  report['reason']='Missing dedicated TRAVEL_AI_API_KEY or TRAVEL_AI_MODEL; zero provider requests made.'
 else:
  with tempfile.TemporaryDirectory(prefix='travel-eval-') as temp:
   store=AlbumStore(temp,json.loads((ROOT/'data/cities.json').read_text()))
   for case in manifest['cases']:
    trip=store.create({'request_id':str(uuid4()),'city_id':case['city_id'],'trip_date':case['date'],'title':case['id'],'notes':case['notes'],'photos':[{'data':base64.b64encode((ROOT/p['path']).read_bytes()).decode()} for p in case['photos']]})
    audit={};run={'case':case['id'],'expected_status':case['expected_status'],'human_verdict':'pending'}
    try:
     run['result']=generate(ROOT,store,trip,audit=audit)
     run['status_matches']=run['result']['status']==case['expected_status']
    except AIError as error:run['error']=str(error)
    run.update(audit);report['runs'].append(run)
    (out/(case['id']+'.json')).write_text(json.dumps(run,ensure_ascii=False,indent=2)+'\n')
    print(case['id']+': '+('error' if 'error' in run else 'received; human review pending'))
  report['status']='collected' if all('result' in r for r in report['runs']) else 'incomplete'
 with (out/'review.csv').open('w',newline='') as stream:
  writer=csv.writer(stream);writer.writerow(['case','reviewer','facts_retained','no_invention','uncertainty_handled','verdict','notes'])
  for case in manifest['cases']:
   for reviewer in ['reviewer_1','reviewer_2']:writer.writerow([case['id'],reviewer,'','','','pending',''])
 (out/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(report['status']+': '+str(out))
 if report['status'] in {'not_run','incomplete'}:return 2
if __name__=='__main__':sys.exit(main())
