import bpy,os,json,hashlib,sys,time
from pathlib import Path
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/production'))
from view_tools import apply_view,prune_for_render
from image_tools import upgrade_images
from fingerprints import file_sha256
build=json.loads((R/'evidence/production/R6-native-build.json').read_text());validation=json.loads((R/'evidence/production/R6-render-derivative-reopen.json').read_text());opened_derivative_sha256=file_sha256(bpy.data.filepath);assert opened_derivative_sha256==validation['sha256'],'Working input bytes differ from separately reopened/signature-validated derivative';assert validation['full_resolution_native_sha256']==build['full_resolution_native_sha256'];opened_geometry_signature=validation['verified_geometry_uv_pose_material_signature']
view=os.environ['SQUARE_VIEW'];f=apply_view(view);s=bpy.context.scene;scale=float(os.environ.get('SQUARE_SCALE','1'));s.render.resolution_x=round(f['resolution'][0]*scale);s.render.resolution_y=round(f['resolution'][1]*scale);s.cycles.samples=int(os.environ.get('SQUARE_SAMPLES',str(f['samples'])))
border=json.loads(os.environ['SQUARE_BORDER']) if os.environ.get('SQUARE_BORDER') else None
culling=prune_for_render(f,None);upgrades=upgrade_images(R,f)
if border:
 s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x,s.render.border_max_x,s.render.border_min_y,s.render.border_max_y=border
s.render.threads_mode='FIXED';s.render.threads=2;s.render.image_settings.compression=45;s.cycles.use_denoising=False
out=R/os.environ.get('SQUARE_OUT','.cache/final-renders')/os.environ.get('SQUARE_IMAGE_NAME',view+'.png');out.parent.mkdir(parents=True,exist_ok=True);s.render.filepath=str(out)
start=time.monotonic();print('FRAME_RENDER_START',view,'dimensions',[s.render.resolution_x,s.render.resolution_y],'samples',s.cycles.samples,'objects',len(s.objects),'culled',len(culling['removed_objects']),flush=True);bpy.ops.render.render(write_still=True)
h=hashlib.sha256()
with out.open('rb') as image:
 while b:=image.read(1024*1024):h.update(b)
report={'view_id':view,'frame':f,'original_source_native_sha256':build['full_resolution_native_sha256'],'candidate_revision':'R6 / actual anatomical source with documented clothing-fitting corrections','geometry_uv_pose_material_signature':build['geometry_uv_pose_material_signature_full_resolution'],'working_render_derivative':bpy.data.filepath,'opened_derivative_sha256':opened_derivative_sha256,'separately_reopened_derivative_geometry_signature':opened_geometry_signature,'source_binding_method':'Actual separate derivative reopen/signature check plus exact frame input SHA verification before rendering; avoids forcing offscreen UV layers into RAM in every render.','native_pixel_dimensions':[s.render.resolution_x,s.render.resolution_y],'crop_border':border,'cycles_samples':s.cycles.samples,'integrated_denoise':False,'render_seconds':round(time.monotonic()-start,3),'original_noisy_image':str(out.relative_to(R)),'image_sha256_before_postprocess':h.hexdigest(),'render_only_visibility':culling,'photographic_map_upgrades':upgrades,'render_implementation_sha256':{n:file_sha256(R/'tools/production'/n) for n in ['render_frame.py','view_tools.py','image_tools.py','fingerprints.py']},'tile_visibility_scope':'Whole-frame common frustum for all borders; no tile-specific object visibility differences.','visual_inspection':'PENDING'}
meta=out.with_suffix('.render.json');meta.write_text(json.dumps(report,indent=2)+'\n');print('FRAME_RENDER_COMPLETE',view,str(out),'seconds',report['render_seconds'],flush=True)
