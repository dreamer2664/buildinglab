"""Actual saved-native rendering study: standard linear-HDR normal/albedo-guided OIDN, no generative imagery."""
import bpy,sys,json,time,os
from pathlib import Path
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/production'))
from view_tools import apply_view,prune_for_render
from image_tools import upgrade_images
from fingerprints import file_sha256
b=json.loads((R/'evidence/production/R11-native-build.json').read_text());assert file_sha256(bpy.data.filepath)==b['render_derivative_sha256'];id=os.environ.get('SQUARE_VIEW','D08');tile=json.loads(os.environ['SQUARE_STUDY_TILE']) if os.environ.get('SQUARE_STUDY_TILE') else None;name=id+('-tile'+str(tile['index']).zfill(2) if tile else '');f=apply_view(id);prune_for_render(f);upgrade_images(R,f);s=bpy.context.scene
prototype=None;prototype_impl='prototype_hair_fibres.py'
if os.environ.get('SQUARE_HAIR_PROTOTYPE')=='1':
 from prototype_hair_fibres import apply
 prototype=apply();name+='-hair-prototype'
elif os.environ.get('SQUARE_HAIR_PROTOTYPE')=='2':
 from prototype_hair_curves import apply
 prototype=apply();prototype_impl='prototype_hair_curves.py';name+='-physical-hair-prototype'
if tile:
 w,h=f['resolution'];x0,x1,y0,y1=tile['pixels'];s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=(x0+.25)/w if x0 else 0;s.render.border_max_x=(x1+.25)/w if x1<w else 1;s.render.border_min_y=(y0+.25)/h if y0 else 0;s.render.border_max_y=(y1+.25)/h if y1<h else 1
s.cycles.samples=24;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=2;bpy.context.view_layer.cycles.denoising_store_passes=True;s.use_nodes=True;tree=s.node_tree;tree.nodes.clear();rl=tree.nodes.new('CompositorNodeRLayers');dn=tree.nodes.new('CompositorNodeDenoise');dn.prefilter='ACCURATE';tree.links.new(rl.outputs['Image'],dn.inputs['Image']);tree.links.new(rl.outputs['Denoising Normal'],dn.inputs['Normal']);tree.links.new(rl.outputs['Denoising Albedo'],dn.inputs['Albedo']);comp=tree.nodes.new('CompositorNodeComposite');tree.links.new(dn.outputs['Image'],comp.inputs['Image']);out=R/('.cache/guided-denoise-tiles-R11' if tile else '.cache/guided-denoise-study-R11');out.mkdir(exist_ok=True);raw=tree.nodes.new('CompositorNodeOutputFile');raw.base_path=str(out);raw.format.file_format='PNG';raw.format.color_mode='RGB';raw.format.color_depth='8';raw.format.compression=45;raw.file_slots[0].path=name+'-noisy-';tree.links.new(rl.outputs['Image'],raw.inputs[0]);s.render.image_settings.compression=45;s.render.filepath=str(out/(name+'.png'));start=time.monotonic();bpy.ops.render.render(write_still=True);r={'view':id,'native_pixel_crop':tile,'full_native_sha256':b['full_resolution_native_sha256'],'actual_opened_derivative_sha256':file_sha256(bpy.data.filepath),'dimensions':[s.render.resolution_x,s.render.resolution_y],'samples':24,'method':'Actual Cycles render of frozenR11 with recorded camera/lighting; standard non-generative compositor OIDN with actual source-linear colour, denoising normal and albedo passes; accurate auxiliary prefilter. Geometry/materials/lights/exposure untouched; no native resave.','camera_exposure_EV':s.view_settings.exposure,'seconds':time.monotonic()-start,'image_sha256':file_sha256(s.render.filepath),'raw_paths':[p.name for p in out.glob(name+'-noisy-*.png')],'inspection':'PENDING / do not infer improved realism from renderer success'}
if prototype is not None:
 r['method']='UNSAVED actual3Dhair-fibre/cap-surface/skin-microbump study applied after frozen derivative load; source file never saved/changed. Actual native-pixel normal/albedo-guided OIDN crop, not final production adoption.';r['unsaved_hair_skin_prototype']=prototype;r['prototype_implementation_sha256']=file_sha256(R/'tools/production'/prototype_impl)
(out/(name+'.json')).write_text(json.dumps(r,indent=2)+'\n');print('ACTUAL_GUIDED_DENOISE_STUDY_RENDER_COMPLETE',id,flush=True)
