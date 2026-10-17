"""Actual clean-import glTF material/geometry smoke view with explicitly neutral proof lights."""
import bpy,sys,os,json,time,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/production'))
from view_tools import apply_view,prune_for_render,_area
from fingerprints import file_sha256
view=os.environ.get('SQUARE_VIEW','D01');source=Path(os.environ.get('SQUARE_PORTABLE_NATIVE',str(R/'.cache/final-components/Winterlichtplatz-GLB-clean-reimport.blend')))
assert Path(bpy.data.filepath)==source,'Must load actual clean-reimport saved native, not original model'
t=bpy.data.texts.new('VIEW_PRESETS.json');t.write((R/'design/production-views.json').read_text());t.use_fake_user=True
w=bpy.data.worlds.new('PORTABLE_PROOF / neutral ambient, not exported HDRI');w.use_nodes=True;w.node_tree.nodes.get('Background').inputs['Color'].default_value=(.72,.78,.88,1);w.node_tree.nodes.get('Background').inputs['Strength'].default_value=.35;bpy.context.scene.world=w
f=apply_view(view);s=bpy.context.scene
if f['kind']=='interior':
 p=f['target'];_area('Portable proof neutral softbox',(p[0],p[1],3.5),[p[0],p[1],0],1400,8)
cull=prune_for_render(f);s.render.resolution_x=1280;s.render.resolution_y=720;s.cycles.samples=24;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=2
out=R/'.cache/portable-proof';out.mkdir(exist_ok=True);s.render.filepath=str(out/(view+'.png'));started=time.monotonic();print('PORTABLE_PROOF_RENDER_START',view,flush=True);bpy.ops.render.render(write_still=True)
r={'view':view,'actual_clean_import_native':str(source.relative_to(R)),'clean_import_native_sha256':file_sha256(source),'glb_sha256':file_sha256(Path(os.environ.get('SQUARE_PORTABLE_GLB',str(R/'.cache/final-components/Winterlichtplatz-R10.glb')))),'raw_render_sha256':file_sha256(s.render.filepath),'dimensions':[1280,720],'samples':24,'seconds':round(time.monotonic()-started,3),'lighting':'Explicitly recreated neutral proof world/softbox; authored Blender HDRI/area-light match is NOT claimed. These test actual imported glTF materials and geometry, not original native scene.','render_only_visibility':cull,'inspection':'PENDING'};(out/(view+'.json')).write_text(json.dumps(r,indent=2)+'\n');print('PORTABLE_PROOF_RENDER_COMPLETE',view,flush=True)
