"""Reopen and test exact publicly downloaded native/GLB, without credentials.
Usage: python3 evidence/producer/verify_published_assets.py --blender /path/to/blender
Uses actual checkpoint receipt URLs/digests, not an invented remote asset ID.
The small smoke render does not count toward final-resolution image evidence.
"""
from pathlib import Path
import argparse,json,hashlib,urllib.request,os,subprocess,datetime
R=Path(__file__).resolve().parents[2];p=argparse.ArgumentParser();p.add_argument('--blender',required=True);a=p.parse_args();receipt=json.loads((R/'exports/checkpoint-receipt.json').read_text());cache=R/'.cache/published-asset-tests';cache.mkdir(parents=True,exist_ok=True)
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
rows={}
for name in ['scene/building-final.blend','exports/building-final.glb']:
 row=receipt['assets'][name];url=row['url'];assert url.startswith('https://github.com/dreamer2664/storagecode/releases/download/');dest=cache/Path(name).name
 if not dest.exists():
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'buildinglab-public-open-test'}),timeout=180) as src,dest.open('wb') as dst:
   while b:=src.read(1024*1024):dst.write(b)
 assert sha(dest)==row['sha256'] and dest.stat().st_size==row['bytes'];rows[name]={'url':url,'bytes':dest.stat().st_size,'sha256':sha(dest)}
E={k:os.environ[k] for k in ['PATH','HOME','LANG'] if k in os.environ};E['OMP_NUM_THREADS']='2'
base=[a.blender,'-b',str(cache/'building-final.blend'),'-t','2','--python-exit-code','1','--python']
for label,script,tail in [('native-check','tools/validate_scene.py',[]),('glb-clean-reimport','tools/test_export.py',['--','--import-only',str(cache/'building-final.glb'),'--report','export-redownload-test.json']),('test-render','evidence/producer/smoke_published_native.py',[])]:
 print('PUBLIC_REOPEN_TEST',label,flush=True)
 with (cache/(label+'.log')).open('w') as log:subprocess.run(base+[str(R/script)]+tail,cwd=R,env=E,stdout=log,stderr=subprocess.STDOUT,check=True)
n=json.loads((R/'evidence/producer/scene-validation.json').read_text());g=json.loads((R/'evidence/producer/export-redownload-test.json').read_text());s=json.loads((R/'evidence/producer/published-smoke-render.json').read_text());assert n['status']==g['status']=='PASS';assert n['native_sha256']==g['native_sha256']==s['native_sha256']==rows['scene/building-final.blend']['sha256'];assert g['glb_sha256']==rows['exports/building-final.glb']['sha256'];assert s['native_sha256']==sha(R/'scene/building-final.blend');assert g['glb_sha256']==sha(R/'exports/building-final.glb')
report={'status':'PASS','verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stage':'actual public unauthenticated redownload, exact native opened/validated/smoke-rendered, GLB clean imported without re-export','public_assets':rows,'native_sha256':s['native_sha256'],'glb_sha256':g['glb_sha256'],'test_render_dimensions':s['resolution'],'final_evidence_count_contribution':0,'independent_acceptance':'pending'}
(R/'evidence/producer/published-asset-open-test.json').write_text(json.dumps(report,indent=2)+'\n');print('PUBLIC_NATIVE_OPEN_RENDER_AND_GLB_REIMPORT_PASS',flush=True)
