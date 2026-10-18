"""Actual exact saved native people regression, separate process/image, standard guided OIDN.
No geometry modification except explicitly render-only pruning. Not final-resolution acceptance.
"""
import bpy,os,sys,json,time,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/production'))
from fingerprints import file_sha256,geometry_uv_pose_material_signature
from view_tools import apply_view,prune_for_render
from image_tools import upgrade_images
b=json.loads((R/'evidence/production'/os.environ.get('SQUARE_PEOPLE_BUILD_REPORT','R12-groomed-town.json')).read_text());actual=file_sha256(bpy.data.filepath);assert actual==b['native_sha256'];assert geometry_uv_pose_material_signature()==b['geometry_uv_pose_material_signature'],'Opened source geometry/UV/pose mismatch';id=os.environ.get('SQUARE_VIEW','D03');f=apply_view(id);cull=prune_for_render(f);distance_lod=None
if os.environ.get('SQUARE_RENDER_SCAN_LOD')=='1':
 from render_scan_distance_lod import apply_scan_distance_lod
 distance_lod=apply_scan_distance_lod(f)
upgrades=upgrade_images(R,f);s=bpy.context.scene;tile=json.loads(os.environ['SQUARE_STUDY_TILE'])if os.environ.get('SQUARE_STUDY_TILE')else None;name=id
if tile:
 w,h=f['resolution'];x0,x1,y0,y1=tile['pixels'];s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=(x0+.25)/w if x0 else 0;s.render.border_max_x=(x1+.25)/w if x1<w else 1;s.render.border_min_y=(y0+.25)/h if y0 else 0;s.render.border_max_y=(y1+.25)/h if y1<h else 1;name+='-crop'+str(tile['index'])
else:
 scale=float(os.environ.get('SQUARE_STUDY_SCALE','.5'));s.render.resolution_x=round(f['resolution'][0]*scale);s.render.resolution_y=round(f['resolution'][1]*scale)
s.cycles.samples=int(os.environ.get('SQUARE_STUDY_SAMPLES','16'));
if hasattr(s.cycles,'use_light_tree'):s.cycles.use_light_tree=False
s.render.threads_mode='FIXED';s.render.threads=2;s.cycles.use_denoising=False;bpy.context.view_layer.cycles.denoising_store_passes=True;s.use_nodes=True;tree=s.node_tree;tree.nodes.clear();rl=tree.nodes.new('CompositorNodeRLayers');dn=tree.nodes.new('CompositorNodeDenoise');dn.prefilter='ACCURATE'
for a,bn in [('Image','Image'),('Denoising Normal','Normal'),('Denoising Albedo','Albedo')]:tree.links.new(rl.outputs[a],dn.inputs[bn])
comp=tree.nodes.new('CompositorNodeComposite');tree.links.new(dn.outputs['Image'],comp.inputs['Image']);out=R/os.environ.get('SQUARE_PEOPLE_STUDY_OUT','evidence/quality-studies/saved-groom-people');out.mkdir(parents=True,exist_ok=True);raw=tree.nodes.new('CompositorNodeOutputFile');raw.base_path=str(out);raw.format.file_format='PNG';raw.format.color_mode='RGB';raw.format.color_depth='8';raw.file_slots[0].path=name+'-noisy-';tree.links.new(rl.outputs['Image'],raw.inputs[0]);s.render.image_settings.compression=45;s.render.filepath=str(out/(name+'.png'));import gc,ctypes
gc.collect()
try:ctypes.CDLL(None).malloc_trim(0)
except (AttributeError,OSError):pass
start=time.monotonic();bpy.ops.render.render(write_still=True)
with open(s.render.filepath,'rb')as image:header=image.read(24)
r={'view_id':id,'exact_saved_native_sha256':actual,'authoritative_full_native_sha256':b.get('source_full_native_sha256',actual),'actual_opened_native':bpy.data.filepath,'native_hair_geometry_signature':b.get('hair_curve_and_root_fade_signature'),'actual_camera_frame':f,'native_pixel_crop':tile,'dimensions':[int.from_bytes(header[16:20],'big'),int.from_bytes(header[20:24],'big')],'samples':s.cycles.samples,'cycles_light_tree':False,'light_sampling_note':'Light-tree acceleration disabled to bound memory; physical light/material geometry retained, no relighting or emissive-plane substitution.','seconds':time.monotonic()-start,'image':str(Path(s.render.filepath).relative_to(R)),'image_sha256':file_sha256(s.render.filepath),'raw_images':[{'path':str(p.relative_to(R)),'sha256':file_sha256(p)}for p in out.glob(name+'-noisy-*.png')],'render_only_visibility':cull,'render_only_distance_scan_geometry_lod':distance_lod,'photographic_map_upgrades':upgrades,'actual_visible_native_hair_curve_objects':[o.name for o in s.objects if o.type=='CURVES'and not o.hide_render],'actual_visible_portable_lod_objects':[o.name for o in s.objects if o.get('portable_hair_lod')and not o.hide_render],'method':'Actual saved candidate rendering, unchanged source geometry/UV/material assignments/light/camera presets, photo-map resampling explicitly recorded; normal/albedo-guided source-linear standard OIDN, no generative image or model change. Low-resolution/native crop study, not final92/highrealism/independent acceptance.','inspection':'PENDING'};assert not r['actual_visible_portable_lod_objects'];(out/(name+'.json')).write_text(json.dumps(r,indent=2)+'\n');print('EXACT_SAVED_NATIVE_PEOPLE_RENDER_COMPLETE',id,r['dimensions'],actual,flush=True)
