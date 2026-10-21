"""One-shot, restart-safe native-pixel render orchestrator. Run with system Python.
Blender and OIDN never run concurrently, to fit the workstation RAM budget.
"""
from pathlib import Path
import subprocess,sys,json,time,hashlib
import numpy as np,OpenEXR
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];BUILD=ROOT/'build';CACHE=ROOT/'renders/district/raw_tiles';OUT=ROOT/'renders/district/native';OUT.mkdir(parents=True,exist_ok=True)
start=time.time();events=[]
views=list(map(int,sys.argv[1].split(','))) if len(sys.argv)>1 else [1,2,3,4,5,6,7,8]
def run(cmd,log):
 with log.open('w') as o:
  subprocess.run(cmd,stdout=o,stderr=subprocess.STDOUT,check=True)
 if 'Traceback' in log.read_text():raise RuntimeError(str(log))
for view in views:
 full=np.zeros((1440,2560,3),np.float16);records=[];view_start=time.time()
 for row in range(2):
  for col in range(4):
   tile=f'{row},{col}';raws=list(CACHE.glob(f'DISTVIEW_0{view}*_2560_{row}-{col}.exr'))
   raws=[p for p in raws if not p.name.endswith('.denoised.exr')]
   if not raws:
    log=OUT/f'view{view}_tile{row}{col}_cycles.log'
    run(['blender','-b','-t','2',str(ROOT/'source/NORDBAHNHOF_DISTRICT.blend'),'--python',str(BUILD/'render_district_raw.py'),'--','--view',str(view),'--res','2560','--samples','320','--tile',tile],log)
    raws=[p for p in CACHE.glob(f'DISTVIEW_0{view}*_2560_{row}-{col}.exr') if not p.name.endswith('.denoised.exr')]
   assert len(raws)==1,raws
   p=raws[0];q=p.with_suffix('.denoised.exr');meta=json.loads(p.with_suffix('.json').read_text());records.append(meta)
   if not q.exists():run([sys.executable,str(BUILD/'finish_realism.py'),str(p)],OUT/f'view{view}_tile{row}{col}_oidn.log')
   f=OpenEXR.File(str(q),separate_channels=True);c=f.channels();a=np.stack([c[k].pixels for k in 'RGB'],axis=-1)
   A,B,C,D=meta['raw_region'];x0,x1,y0,y1=meta['destination']
   assert a.shape[:2]==(D-C,B-A),(a.shape,meta)
   full[1440-y1:1440-y0,x0:x1]=a[D-y1:D-y0,x0-A:x1-A]
   print(f'TILE_DONE view={view} tile={row},{col} samples=320 seconds={meta["seconds"]:.1f}',flush=True)
   del f,c,a
 name=records[0]['camera'];linear=OUT/(name+'.denoised.exr')
 OpenEXR.File({'compression':OpenEXR.ZIP_COMPRESSION},{k:full[:,:,i].copy() for i,k in enumerate('RGB')}).write(str(linear))
 run(['blender','-b','-t','2','--python',str(BUILD/'district_agx.py'),'--',str(linear)],OUT/(name+'_agx.log'))
 jpg=OUT/(name+'.jpg');im=Image.open(jpg).convert('RGB');assert im.size==(2560,1440)
 rgb=np.asarray(im,dtype=np.float32)/255;lum=rgb@np.array([.2126,.7152,.0722],dtype=np.float32)
 report={'file':jpg.name,'camera':name,'resolution':[2560,1440],'samples':320,'native_method':'8 raw HDR border tiles, 32px overlap; external Intel OIDN 2.5.1 high quality; assembled in linear light without resizing; Blender AgX Medium High Contrast, exposure +0.3','render_only_lod':'Render-only frustum/typographic/curtain/scan LOD; original rolling stock and closed interior fittings omitted. Full packed scene retained.','tiles':records,'cycles_render_seconds':sum(t['seconds'] for t in records),'invocation_wall_seconds':time.time()-view_start,'sha256':hashlib.sha256(jpg.read_bytes()).hexdigest(),'mean_luminance_actual':float(lum.mean()),'white_over_98pct_actual':float((lum>.98).mean()*100),'black_under_1_2pct_actual':float((lum<.012).mean()*100),'visual_inspection':'PENDING'}
 (OUT/(name+'.json')).write_text(json.dumps(report,indent=2));events.append(report)
 print(f'VIEW_DONE view={view} file={jpg.name} seconds={report["invocation_wall_seconds"]:.1f}',flush=True)
 del full,rgb,lum
(OUT/'RENDER_MANIFEST.json').write_text(json.dumps({'status':'rendered; not acceptance','duration_seconds':time.time()-start,'views':events},indent=2))
print('ALL_RENDERS_READY',flush=True)
