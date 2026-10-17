"""Sequential, resumable CPU rendering, bounded native camera-border tiles and standard OIDN.
No production completion/visual acceptance is inferred by this renderer.
"""
import os,sys,subprocess,json,hashlib,time,argparse,fcntl
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parents[2];B='/home/user/.cache/blender-4.3.2-linux-x64/blender';LIB='/home/user/.cache/blender-4.3.2-linux-x64/lib'
p=argparse.ArgumentParser();p.add_argument('--pilot',action='store_true');p.add_argument('--views',default='');p.add_argument('--sample-limit',type=int,default=0);args=p.parse_args();all_frames=json.loads((R/'design/production-views.json').read_text())['frames']
ids=args.views.split(',') if args.views else (['B01_L01_interior','B01_L03_cutaway','B03_L01_interior','D01','H02'] if args.pilot else [f['id'] for f in all_frames if f['id'].startswith('D')]+[f['id'] for f in all_frames if f['kind'] in ['plan','cutaway','interior']]+[f['id'] for f in all_frames if f['id'].startswith('H')])
frames=[next(f for f in all_frames if f['id']==id) for id in ids];outrel='.cache/pilot-R10' if args.pilot else '.cache/final-renders';out=R/outrel;out.mkdir(parents=True,exist_ok=True);logs=R/'.cache/render-logs';logs.mkdir(parents=True,exist_ok=True)
meta_path=R/'evidence/production'/('pilot-render-manifest.json' if args.pilot else 'final-render-manifest.json');records=json.loads(meta_path.read_text()) if meta_path.exists() else {};current_source_sha256=json.loads((R/'evidence/production/R10-native-build.json').read_text())['full_resolution_native_sha256'];records={k:v for k,v in records.items() if v.get('source_native_sha256')==current_source_sha256}
env={k:os.environ[k] for k in ['PATH','HOME','LANG','LD_LIBRARY_PATH'] if k in os.environ};env.update(OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='1')
def digest(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  while b:=f.read(1024*1024):h.update(b)
 return h.hexdigest()
def run_frame(f,name,border=None):
 image=out/name;meta=image.with_suffix('.render.json')
 if image.exists() and meta.exists():
  old=json.loads(meta.read_text())
  if digest(image)==old['image_sha256_before_postprocess']:return old
 E=env.copy();E.update(SQUARE_VIEW=f['id'],SQUARE_OUT=outrel,SQUARE_IMAGE_NAME=name)
 if args.pilot:E.update(SQUARE_SCALE='.4' if f['resolution'][0]==2560 else '.3',SQUARE_SAMPLES='24' if f['kind']=='people' else '16')
 if args.sample_limit:E['SQUARE_SAMPLES']=str(min(f['samples'],args.sample_limit))
 if border:E['SQUARE_BORDER']=json.dumps(border)
 log=logs/(name+'.log')
 with (R/'.cache/blender-job.lock').open('w') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  with log.open('w') as logf:subprocess.run([B,'--factory-startup','-b',str(R/'.cache/master/Winterlichtplatz-render-R10.blend'),'-t','2','--python-exit-code','1','--python',str(R/'tools/production/render_frame.py')],env=E,cwd=R,stdout=logf,stderr=subprocess.STDOUT,check=True)
 return json.loads(meta.read_text())
for f in frames:
 id=f['id'];final=out/(id+'.png');noisy=final.with_suffix('.noisy.png')
 if id in records and final.exists() and digest(final)==records[id].get('final_sha256'):
  print('SKIP_ALREADY_RENDERED_AND_HASH_VERIFIED',id,flush=True);continue
 print('RENDER_VIEW',id,f['title'],flush=True);start=time.monotonic();reports=[]
 if not args.pilot and f['resolution'][0]>=3840:
  grid=4;borders=[(x/grid,(x+1)/grid,y/grid,(y+1)/grid) for y in range(grid) for x in range(grid)]
  for i,border in enumerate(borders):reports.append(run_frame(f,id+f'-tile{i}.png',border));print('TILE_COMPLETE',id,i,flush=True)
  canvas=Image.new('RGB',tuple(f['resolution']));w,h=f['resolution']
  for i,border in enumerate(borders):
   with Image.open(out/(id+f'-tile{i}.png')) as tile:
    assert tile.size==(w//grid,h//grid),tile.size;canvas.paste(tile,(round(border[0]*w),round((1-border[3])*h)))
  canvas.save(final);canvas.close()
 else:reports=[run_frame(f,id+'.png')]
 before=digest(final)
 if noisy.exists() and digest(noisy)!=before:raise RuntimeError('Existing noisy provenance differs: '+id)
 denoise_log=logs/(id+'.oidn.log')
 with (R/'.cache/blender-job.lock').open('w') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  with denoise_log.open('w') as logf:subprocess.run([sys.executable,str(R/'tools/denoise_png.py'),str(final),LIB],env=env,stdout=logf,stderr=subprocess.STDOUT,check=True)
 with Image.open(final) as im:dimensions=im.size
 if not args.pilot:assert list(dimensions)==f['resolution']
 record={'view_id':id,'title':f['title'],'kind':f['kind'],'source_native_sha256':reports[0]['original_source_native_sha256'],'geometry_uv_pose_material_signature':reports[0]['geometry_uv_pose_material_signature'],'image':str(final.relative_to(R)),'dimensions':dimensions,'final_sha256':digest(final),'noisy_original_sha256':digest(noisy),'noisy_original':str(noisy.relative_to(R)),'original_before_denoise_sha256':before,'postprocess':'Standard OIDN colour-only display-sRGB640px/48px-overlap tiles; no generative imagery','render_reports':[str((out/(id+f'-tile{i}.render.json')).relative_to(R)) for i in range(len(reports))] if len(reports)>1 else [str((out/(id+'.render.json')).relative_to(R))],'tile_assembly':'Exact native-pixel camera-border4x4, no scaling; common whole-frame frustum for every tile' if len(reports)>1 else None,'elapsed_seconds':round(time.monotonic()-start,2),'visual_inspection':'PENDING'}
 records[id]=record;meta_path.write_text(json.dumps(records,indent=2)+'\n');print('VIEW_RENDER_COMPLETE',id,sum(x['id'] in records for x in frames),'of',len(frames),'seconds',record['elapsed_seconds'],flush=True)
print('BATCH_RENDER_COMPLETE',len(frames),'visual inspection remains a separate gate',flush=True)
