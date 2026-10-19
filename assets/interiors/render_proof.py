"""Saved-scene inspection previews, never generated imagery. Run on interiors.blend.
PROOF_VIEWS optional comma list, defaults six interior heroes plus L02 axon and L03 bedroom.
"""
import bpy,os
from pathlib import Path
R=Path(__file__).resolve().parents[2];s=bpy.context.scene;s.cycles.use_denoising=False;s.cycles.samples=24;s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100
out=R/'assets/interiors/proof';out.mkdir(exist_ok=True)
views=os.environ.get('PROOF_VIEWS','L01_INTERIOR,L02_INTERIOR,L03_INTERIOR,L04_INTERIOR,L05_INTERIOR,L06_INTERIOR,L02_AXON,L03_DETAIL').split(',')
for view in views:
 lid=view.split('_')[0];axon='AXON' in view
 for c in bpy.data.collections:
  if c.get('occupied_level'):c.hide_render=c.name!=lid
  elif any(c.name.endswith('_'+x) for x in ['FACADE','PARTITIONS_HIGH','CEILING']):c.hide_render=axon
  elif c.name=='ROOF':c.hide_render=True
 s.camera=bpy.data.objects['CAM_'+view];s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=.8 if not axon else 0
 s.render.filepath=str(out/(view+'.png'));bpy.ops.render.render(write_still=True);print('PROOF_SAVED',view,flush=True)
