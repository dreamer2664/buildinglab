"""Reopen saved blockout and render individual level views. No synthetic images.
BLDG_RENDER_PASS=A|B optional; outputs are blockout evidence, not 29-view final package.
"""
from pathlib import Path
import bpy,os,json,hashlib,datetime,time
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene
PASS=os.environ.get('BLDG_RENDER_PASS','A');out=ROOT/'design/evidence'/('pass-'+PASS);out.mkdir(parents=True,exist_ok=True)
manifest=[]
source_sha=hashlib.sha256((ROOT/'scene/blockout.blend').read_bytes()).hexdigest()
for lid in ['L01','L02','L03','L04','L05','L06','FULL_STACK']:
 for c in bpy.data.collections:
  if c.get('occupied_level'):c.hide_render=(lid!='FULL_STACK' and c.name!=lid)
 scene.camera=bpy.data.objects['CAM_'+lid+'_AXON' if lid!='FULL_STACK' else 'CAM_FULL_STACK']
 scene.render.filepath=str(out/(lid+'.png'));t=time.time();bpy.ops.render.render(write_still=True)
 p=Path(scene.render.filepath)
 manifest.append({'image':str(p.relative_to(ROOT)),'camera':scene.camera.name,'width':scene.render.resolution_x,'height':scene.render.resolution_y,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'render_seconds':round(time.time()-t,2),'review_result':'not inspected','source_blend_sha256':source_sha})
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
