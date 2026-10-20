"""A disclosed small test render of the exact downloaded native, NOT final evidence."""
import bpy,sys,os,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from view_modes import set_view
set_view('intact');s=bpy.context.scene;s.camera=bpy.data.objects['CAM_EXTERIOR_DAY'];s.cycles.samples=4;s.cycles.use_denoising=False
s.render.resolution_x=640;s.render.resolution_y=360;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
out=R/'.cache/published-native-smoke.png';out.parent.mkdir(parents=True,exist_ok=True);s.render.filepath=str(out)
bpy.ops.render.render(write_still=True)
report={'stage':'small published-native reopen/render smoke test, NOT one of the required 29 final originals','native_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'png_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'resolution':[640,360],'samples':4,'integrated_denoising':False,'blender':bpy.app.version_string,'no_native_resave':True}
(R/'evidence/producer/published-smoke-render.json').write_text(json.dumps(report,indent=2)+'\n')
print('PUBLISHED_NATIVE_SMOKE_RENDER_COMPLETED')
