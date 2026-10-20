"""Train-only rendering. Actual image metrics; no capped/clamped acceptance statistics."""
import bpy,sys,argparse,json,time,hashlib
from pathlib import Path
from PIL import Image
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from render_batch import configure_cycles,setup_demodulated_compositor
ROOT=Path(__file__).resolve().parents[1]
a=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
p=argparse.ArgumentParser();p.add_argument('--views',default='1,2,3,4,5,6');p.add_argument('--res',type=int,default=1024);p.add_argument('--samples',type=int,default=24);p.add_argument('--tiled',action='store_true');args=p.parse_args(a)
scene=bpy.context.scene
configure_cycles(args.samples);setup_demodulated_compositor()
scene.cycles.max_bounces=3;scene.cycles.glossy_bounces=2;scene.cycles.transmission_bounces=3;scene.cycles.seed=31
scene.render.resolution_x=args.res;scene.render.resolution_y=round(args.res*9/16);scene.render.resolution_percentage=100
scene.render.image_settings.file_format='JPEG';scene.render.image_settings.quality=96
# Train-only subjects; existing whole-station views remain untouched.
cams=sorted([o for o in bpy.data.objects if o.type=='CAMERA' and o.name.startswith('TRAINVIEW_')],key=lambda o:o.name)
out=ROOT/'renders/trains'/('native' if args.res>=2560 else 'proof');out.mkdir(parents=True,exist_ok=True)
reports=[]
for i in map(int,args.views.split(',')):
 cam=cams[i-1];scene.camera=cam;
 # Explicit inspection cutaway: omit the high platform deck only for bogie view.
 hidden=[]
 if i==5:
  for ob in bpy.data.objects:
   if ob.name.startswith(('PLT_07_', 'Platform stone joint','Platform longitudinal joint')) and not ob.hide_render:
    hidden.append(ob);ob.hide_render=True
 path=out/(cam.name+'.jpg');scene.render.filepath=str(path)
 start=time.time()
 if args.tiled:
  W=args.res;H=round(W*9/16);assembled=Image.new('RGB',(W,H));tiles=ROOT/'renders/trains/.cache';tiles.mkdir(parents=True,exist_ok=True)
  for row in range(2):
   for column in range(2):
    x0=column*(W//2);x1=(column+1)*(W//2);y0=row*(H//2);y1=(row+1)*(H//2)
    a0=max(0,x0-16);a1=min(W,x1+16);b0=max(0,y0-16);b1=min(H,y1+16)
    scene.render.use_border=True;scene.render.use_crop_to_border=True
    scene.render.border_min_x=a0/W;scene.render.border_max_x=a1/W;scene.render.border_min_y=b0/H;scene.render.border_max_y=b1/H
    tile=tiles/(cam.name+f'_{row}_{column}.jpg');scene.render.filepath=str(tile)
    bpy.ops.render.render(write_still=True)
    piece=Image.open(tile).convert('RGB')
    # Blender border is bottom-up; Pillow is top-down. No tile is resized.
    expected=(a1-a0,b1-b0)
    if piece.size!=expected:raise RuntimeError(f'Native tile size mismatch {piece.size} != {expected}')
    crop=piece.crop((x0-a0,b1-y1,x1-a0,b1-y0));assembled.paste(crop,(x0,H-y1))
  assembled.save(path,quality=96)
  scene.render.use_border=False;scene.render.use_crop_to_border=False
 else:bpy.ops.render.render(write_still=True)
 im=Image.open(path).convert('RGB');pixels=np.asarray(im,dtype=np.float32)/255;lum=pixels[:,:,0]*.2126+pixels[:,:,1]*.7152+pixels[:,:,2]*.0722
 report={'file':path.name,'camera':cam.name,'resolution':list(im.size),'samples':args.samples,'seconds':round(time.time()-start,2),'mean_luminance':float(lum.mean()),'blown_pct_actual':float((lum>.98).mean()*100),'crushed_pct_actual':float((lum<.012).mean()*100),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'visual_inspection':'PENDING'}
 report['native_render_method']='four native-pixel border tiles with 16px overlap, assembled without resizing' if args.tiled else 'full frame'
 report['cutaway_note']='High platform deck/furniture hidden to expose bogie' if i==5 else None
 for ob in hidden:ob.hide_render=False
 reports.append(report);print('RENDERED',json.dumps(report),flush=True)
(out/'RENDER_MANIFEST.json').write_text(json.dumps({'status':'renders generated, not acceptance','views':reports},indent=2))
