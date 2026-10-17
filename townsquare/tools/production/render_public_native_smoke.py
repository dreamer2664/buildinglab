"""Directly open the exact anonymously downloaded full-map native; memory-only render budget."""
import bpy,os,json,sys,time
from pathlib import Path
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/production'));from fingerprints import file_sha256
from view_tools import apply_view,prune_for_render
from image_tools import upgrade_images
build=json.loads((R/'evidence/production/R6-native-build.json').read_text());actual=file_sha256(bpy.data.filepath);assert actual==build['full_resolution_native_sha256'],'Not exact full-map public source bytes'
view=os.environ.get('SQUARE_VIEW','H02');f=apply_view(view);cull=prune_for_render(f)
# No image dimension query before geometry pruning; avoid eagerly decoding unused full maps.
resampled=[]
for im in bpy.data.images:
 if im.source!='FILE' or not all(im.size):continue
 old=tuple(im.size);scale=min(1,512/max(old));new=[max(1,round(old[0]*scale)),max(1,round(old[1]*scale))]
 if list(old)!=new:im.scale(*new);resampled.append({'image':im.name,'old':old,'new':new})
 im.buffers_free()
upgrades=upgrade_images(R,f);s=bpy.context.scene;s.render.resolution_x=1152;s.render.resolution_y=648;s.cycles.samples=16;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=2;out=R/'.cache/public-R6';out.mkdir(exist_ok=True);s.render.filepath=str(out/('exact-public-native-'+view+'.png'));start=time.monotonic();print('EXACT_PUBLIC_FULL_NATIVE_RENDER_START',actual,view,flush=True);bpy.ops.render.render(write_still=True)
r={'status':'RENDERED_INSPECTION_PENDING','view':view,'actually_opened_full_resolution_native_sha256':actual,'source_file':bpy.data.filepath,'image':str(Path(s.render.filepath).relative_to(R)),'raw_sha256':file_sha256(s.render.filepath),'dimensions':[1152,648],'samples':16,'seconds':round(time.monotonic()-start,3),'memory_only_pruning':cull,'memory_only_photo_resampling':resampled,'close_map_upgrades':upgrades,'scope':'Actual exact anonymous public full-map native loaded directly; source geometry unchanged, memory-only pruning/photo resampling before render, no source resave. This is smoke/portability evidence, not final4K acceptance.'};(R/'evidence/production'/('R6-public-native-smoke-'+view+'.json')).write_text(json.dumps(r,indent=2)+'\n');print('EXACT_PUBLIC_FULL_NATIVE_ACTUAL_SMOKE_RENDER_COMPLETE',view,flush=True)
