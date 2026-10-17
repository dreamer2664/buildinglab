"""Bounded actual native-pixel guided-OIDN study,96px context; never infer quality from assembly."""
from pathlib import Path
import os,json,subprocess,hashlib,time
from PIL import Image
import numpy as np
R=Path(__file__).resolve().parents[2];id=os.environ.get('SQUARE_VIEW','D08');W,H=2560,1440;out=R/'.cache/guided-denoise-tiles-R11';out.mkdir(exist_ok=True);records=[];start=time.monotonic();env={k:os.environ[k]for k in ['PATH','HOME','LANG','LD_LIBRARY_PATH']if k in os.environ};env.update(OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='1',SQUARE_VIEW=id)
def sha(p):
 with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
for row in range(4):
 for col in range(4):
  i=row*4+col;core=[col*640,(col+1)*640,row*360,(row+1)*360];pixels=[max(0,core[0]-96),min(W,core[1]+96),max(0,core[2]-96),min(H,core[3]+96)];tile={'index':i,'pixels':pixels};p=out/(id+'-tile'+str(i).zfill(2)+'.png');meta=p.with_suffix('.json');valid=False
  if p.exists()and meta.exists():
   r=json.loads(meta.read_text());valid=r['native_pixel_crop']==tile and sha(p)==r['image_sha256']
  if not valid:
   e=env.copy();e['SQUARE_STUDY_TILE']=json.dumps(tile)
   with (out/(id+'-tile'+str(i).zfill(2)+'.log')).open('w')as log:subprocess.run(['/home/user/.cache/blender-4.3.2-linux-x64/blender','--factory-startup','-b',str(R/'.cache/master/Winterlichtplatz-render-R11.blend'),'-t','2','--python-exit-code','1','--python',str(R/'tools/production/study_guided_denoising.py')],env=e,cwd=R,stdout=log,stderr=subprocess.STDOUT,check=True)
  with Image.open(p)as im:assert im.size==(pixels[1]-pixels[0],pixels[3]-pixels[2]),(i,im.size,pixels)
  records.append({'index':i,'image':p.name,'sha256':sha(p),'report':meta.name,'core_pixels_bottom_origin':core,'context_window_pixels_bottom_origin':pixels});print('GUIDED_NATIVE_PIXEL_CROP_COMPLETE',id,i,flush=True)
canvases=[Image.new('RGB',(W,H)),Image.new('RGB',(W,H))]
for t in records:
 x0,x1,y0,y1=t['context_window_pixels_bottom_origin'];cx0,cx1,cy0,cy1=t['core_pixels_bottom_origin'];box=(cx0-x0,y1-cy1,cx1-x0,y1-cy0)
 for j,name in enumerate([t['image'],t['image'].replace('.png','-noisy-0001.png')]):
  with Image.open(out/name)as im:canvases[j].paste(im.crop(box),(cx0,H-cy1))
final=out/(id+'-assembled.png');raw=out/(id+'-assembled.noisy.png');canvases[0].save(final);canvases[1].save(raw);a=np.array(canvases[1]).astype(np.int16);baseline=R/'.cache/final-renders'/(id+'.noisy.png');comparison={}
if baseline.exists():
 b=np.array(Image.open(baseline).convert('RGB')).astype(np.int16);diff=np.abs(a-b);comparison={'existing_raw_pixels_exactly_equal':bool(np.array_equal(a,b)),'max_abs_difference_8bit':int(diff.max()),'mean_abs_difference_8bit':float(diff.mean()),'scope':'Checks camera/native pixel alignment and Monte Carlo/compositor differences, not quality acceptance.'}
r={'view':id,'dimensions':[W,H],'full_native_sha256':json.loads((R/'evidence/production/R11-native-build.json').read_text())['full_resolution_native_sha256'],'sha256':sha(final),'noisy_sha256':sha(raw),'method':'Actual Cycles24native2560x1440 camera-border4x4 with96px context, source-linear normal/albedo-guided standardOIDN/ACCURATE per crop before AgX, exact core pixel cropping/paste without scaling. Frozen native geometry/material/light/exposure unchanged.','tiles':records,'raw_comparison':comparison,'elapsed_seconds':time.monotonic()-start,'inspection':'PENDING / whole actual original must be separately opened; no asset realism acceptance inferred'};(out/(id+'-assembled.json')).write_text(json.dumps(r,indent=2)+'\n');print('GUIDED_NATIVE_2560_ASSEMBLED',id,json.dumps(comparison),flush=True)
