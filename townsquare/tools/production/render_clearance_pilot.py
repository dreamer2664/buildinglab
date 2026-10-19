import bpy,sys,os,json,time
from pathlib import Path
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/production'))
from view_tools import apply_view,prune_for_render
from image_tools import upgrade_images
from fingerprints import file_sha256
id=os.environ['SQUARE_VIEW'];source=file_sha256(bpy.data.filepath);f=apply_view(id);culled=prune_for_render(f);maps=upgrade_images(R,f);s=bpy.context.scene;s.render.resolution_x=1024;s.render.resolution_y=576;s.cycles.samples=24;s.render.threads_mode='FIXED';s.render.threads=2;s.render.filepath=str(R/'.cache/pilot-R11-clearance'/(id+'.png'));Path(s.render.filepath).parent.mkdir(exist_ok=True);start=time.monotonic();bpy.ops.render.render(write_still=True);r={'view':id,'saved_prototype_derivative_sha256':source,'base_exposure_EV':s.view_settings.exposure,'additional_exposure_bias_EV':0,'samples':24,'dimensions':[1024,576],'seconds':time.monotonic()-start,'sha256_before_standard_denoise':file_sha256(s.render.filepath),'purpose':'Actual saved ceiling/fixture-clearance prototype camera image; NO high exposure compensation, NO native-final acceptance inferred','inspection':'PENDING'};Path(s.render.filepath).with_suffix('.json').write_text(json.dumps(r,indent=2)+'\n');print('CLEARANCE_PILOT_RENDERED',id,r['seconds'],flush=True)
