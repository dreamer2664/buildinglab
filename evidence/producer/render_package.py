"""Sequential fresh-process render/OIDN pipeline with source/dimension/digest guards.
Usage: python3 evidence/producer/render_package.py --blender /path/to/blender --oidn-lib /path/to/blender/lib [--views id,id] [--resume]
All render inputs are from the exact saved native candidate. No credentials are forwarded.
Mechanical rendering is NOT human inspection: all new records begin not-inspected.
"""
import argparse,subprocess,os,json,hashlib,sys,datetime,shutil
from pathlib import Path
from PIL import Image
from views import VIEWS
from annotate_plan import annotate
from caption_view import caption
R=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
p=argparse.ArgumentParser();p.add_argument('--blender',required=True);p.add_argument('--oidn-lib',required=True);p.add_argument('--views');p.add_argument('--resume',action='store_true');a=p.parse_args();wanted=a.views.split(',') if a.views else [v['id'] for v in VIEWS];assert all(x in [v['id'] for v in VIEWS] for x in wanted)
native=R/'scene/building-final.blend';digest=sha(native);cache=Path.home()/'.cache/buildinglab-render-diagnostics';cache.mkdir(parents=True,exist_ok=True)
# Deliberately small allowlist: no transport credentials, secrets or service keys.
E={'PATH':os.environ['PATH'],'HOME':str(Path.home()),'LANG':'C.UTF-8','OMP_NUM_THREADS':'4'}
manifest_path=R/'evidence/producer/screenshot-manifest.json';manifest=json.loads(manifest_path.read_text()) if manifest_path.exists() else {'source':'scene/building-final.blend','source_sha256':digest,'images':[],'independent_acceptance':'pending'}
for view in wanted:
 v=next(v for v in VIEWS if v['id']==view);png=R/'renders/final'/(view+'.png');mp=R/'evidence/producer'/('render-'+view+'.json');old=next((x for x in manifest['images'] if x['id']==view),None)
 if a.resume and old and png.exists() and old['source_sha256']==digest and old['sha256']==sha(png) and Image.open(png).size==(v['width'],v['height']):print('RESUME_VERIFIED',view,flush=True);continue
 if png.exists():
  history=R/'renders/revision-B';history.mkdir(parents=True,exist_ok=True);shutil.move(png,history/(view+'-'+sha(png)[:12]+'.png'))
 assert sha(native)==digest,'Native changed during rendering; regenerate package coherently'
 print('RENDER_START',view,now(),flush=True);E['RENDER_VIEW']=view
 with (cache/(view+'.log')).open('w') as log:subprocess.run([a.blender,'-b',str(native),'-t','6','--python-exit-code','1','--python',str(R/'evidence/producer/render_one.py')],cwd=R,env=E,stdout=log,stderr=subprocess.STDOUT,check=True)
 assert Image.open(png).size==(v['width'],v['height']);raw_sha=sha(png)
 subprocess.run([sys.executable,str(R/'assets/exterior/denoise_png.py'),str(png),a.oidn_lib],cwd=R,env=E,check=True)
 noisy=png.with_name(png.stem+'.noisy.png')
 if noisy.exists():shutil.move(noisy,cache/(view+'.noisy.png'))
 if v['mode']=='plan':annotate(view)
 else:caption(view)
 m=json.loads(mp.read_text());m.update({'source_sha256':digest,'raw_sha256':raw_sha,'render_completed_utc':now(),'postprocess':'Separate tiled OpenImageDenoise, display-referred sRGB colour-only; then disclosed technical labels/caption.'});mp.write_text(json.dumps(m,indent=2)+'\n')
 record={'id':view,'path':str(png.relative_to(R)),'camera':v['camera'],'width':v['width'],'height':v['height'],'sha256':sha(png),'bytes':png.stat().st_size,'time':now(),'source_sha256':digest,'metadata':str(mp.relative_to(R)),'review_result':'not inspected','producer_opened_individually':False}
 manifest['source_sha256']=digest;manifest['images']=[x for x in manifest['images'] if x['id']!=view]+[record];manifest_path.write_text(json.dumps(manifest,indent=2)+'\n');print('RENDER_READY_NOT_INSPECTED',view,record['bytes'],flush=True)
assert sha(native)==digest
print('RENDER_BATCH_FINISHED',len(wanted),'views. Human inspection and independent review are separate gates.',flush=True)
