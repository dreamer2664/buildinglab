"""Current-source production views, sequential sterile Blender processes and separate OIDN.
Resumable source/image digest checks. Individual visual inspection is deliberately NOT automated.
"""
from pathlib import Path
import os,json,subprocess,hashlib,fcntl,argparse,time,sys
R=Path(__file__).resolve().parents[2];B='/home/user/.cache/blender-4.3.2-linux-x64/blender';p=argparse.ArgumentParser();p.add_argument('--views',required=True);p.add_argument('--scale',type=float,default=1);p.add_argument('--samples',type=int,default=32);a=p.parse_args();source=json.loads((R/'evidence/production/R14-frozen-render-source.json').read_text());out='evidence/current-production';(R/out).mkdir(exist_ok=True);logs=R/'.cache/current-production-logs';logs.mkdir(exist_ok=True);env={k:os.environ[k]for k in ['PATH','HOME','LANG']if k in os.environ};env.update(OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='1',LD_LIBRARY_PATH='/home/user/.cache/blender-deps/usr/lib/x86_64-linux-gnu');manifest=R/'evidence/production/R14-current-render-manifest.json';records=json.loads(manifest.read_text())if manifest.exists()else{}
def sha(p):
 with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def run(args,E,name):
 with (R/'.cache/blender-job.lock').open('a')as lock,(logs/(name+'.log')).open('w')as log:
  fcntl.flock(lock,fcntl.LOCK_EX);subprocess.run(args,env=E,cwd=R,stdout=log,stderr=subprocess.STDOUT,check=True)
for view in a.views.split(','):
 meta=R/out/(view+'.json');ready=False
 if meta.exists():
  r=json.loads(meta.read_text());image=R/r['image'];ready=r['exact_saved_native_sha256']==source['native_sha256']and not r.get('separate_compositor_pending')and image.exists()and sha(image)==r['image_sha256']
 if not ready:
  E=dict(env,SQUARE_PEOPLE_BUILD_REPORT='R14-frozen-render-source.json',SQUARE_VIEW=view,SQUARE_STUDY_TILE=os.environ.get('SQUARE_STUDY_TILE',''),SQUARE_STUDY_SCALE=str(a.scale),SQUARE_PRUNE_MODE=os.environ.get('SQUARE_PRUNE_MODE',''),SQUARE_VIEW_PRESETS_FILE=os.environ.get('SQUARE_VIEW_PRESETS_FILE',''),SQUARE_STUDY_SAMPLES=str(a.samples),SQUARE_RENDER_SCAN_LOD=os.environ.get('SQUARE_RENDER_SCAN_LOD','1'),SQUARE_STUDY_SEPARATE_COMPOSITOR='1',SQUARE_PEOPLE_STUDY_OUT=out)
  if not meta.exists()or json.loads(meta.read_text()).get('exact_saved_native_sha256')!=source['native_sha256']:
   print('ACTUAL_CURRENT_SOURCE_FRAME_START',view,flush=True);run([B,'-b',str(R/source['native']),'-t','2','--python-exit-code','1','--python','tools/production/render_saved_people_study.py'],E,view+'-render')
  r=json.loads(meta.read_text())
  if r.get('separate_compositor_pending'):
   E=dict(env,SQUARE_STUDY_META=str(meta.relative_to(R)))
   if r['dimensions'][0]*r['dimensions'][1]>1500000:run([sys.executable,'tools/production/denoise_study_tiled.py',str(meta.relative_to(R))],E,view+'-tiled-colour-denoise')
   else:run([B,'--factory-startup','-b','-t','2','--python-exit-code','1','--python','tools/production/denoise_saved_study_exr.py'],E,view+'-guided-denoise')
 r=json.loads(meta.read_text());assert not r.get('separate_compositor_pending');assert sha(R/r['image'])==r['image_sha256'];records[view]={'image':r['image'],'image_sha256':r['image_sha256'],'dimensions':r['dimensions'],'actual_derivative_sha256':r['exact_saved_native_sha256'],'authoritative_source_native_sha256':r['authoritative_full_native_sha256'],'report':str(meta.relative_to(R)),'inspection':'PENDING / must actually open original'};manifest.write_text(json.dumps(records,indent=2)+'\n');print('ACTUAL_CURRENT_SOURCE_FRAME_COMPLETE',view,r['dimensions'],r['image_sha256'],'NOT_VISUALLY_ACCEPTED',flush=True)
