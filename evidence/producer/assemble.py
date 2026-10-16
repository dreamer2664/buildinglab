"""Save the integrated native release CANDIDATE; acceptance is never implied by filename.
Run on the completed cache-stage blend (see HANDOFF), not directly on interiors. Native cameras and all furnished mesh components preserved.
"""
import bpy,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent));from view_modes import set_view
s=bpy.context.scene
# A fresh process avoids invalidating the batch builder's evaluated dependency graph.
for o in s.objects:
 if o.type=='MESH' and o.get('component_names'):assert [m.name if m else None for m in o.data.materials]==json.loads(o['source_material_names']),o.name+' saved material slots lost'
originals=[o for o in s.objects if o.type=='MESH' and not o.get('component_names')]
assert originals and any(o.get('component_names') for o in s.objects),'Load the completed batch-stage blend, not the unbatched source'
bpy.data.batch_remove(ids=originals);originals=None
bpy.ops.outliner.orphans_purge(do_recursive=True)
for o in s.objects:
 if o.get('desired_name'):o.name=o['desired_name'];del o['desired_name']
s['mesh_batching']='Lossless evaluated-mesh consolidation; original component names and Generated coordinates preserved; unbatched interiors also delivered.'
s['stage']='Integrated release candidate — requires visual-package gates and independent acceptance'
s['metric_scale']='1 Blender unit = 1 metre';s['overall_height_m']=21.12;s['furnished_home_count_claim']=14
s['copyright']='Original geometry/materials/stroke signs: CC0 1.0; scripts MIT; see rights record.'
s['not_engineered_or_code_approved']=True
s.cycles.use_denoising=False;s.cycles.samples=16;s.cycles.max_bounces=6;s.cycles.diffuse_bounces=2;s.cycles.glossy_bounces=2;s.cycles.transmission_bounces=4;s.cycles.transparent_max_bounces=4;s.cycles.volume_bounces=0;s.cycles.caustics_reflective=False;s.cycles.caustics_refractive=False;s.cycles.sample_clamp_indirect=3
s.render.resolution_x=3840;s.render.resolution_y=2160;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.color_depth='8';s.render.image_settings.compression=35
s.render.use_persistent_data=False;s.render.filepath='//../renders/final/exterior-day.png'
text=bpy.data.texts.get('VIEW_MODES.py') or bpy.data.texts.new('VIEW_MODES.py');text.clear();text.write((ROOT/'evidence/producer/view_modes.py').read_text())
readme=bpy.data.texts.get('START_HERE.txt') or bpy.data.texts.new('START_HERE.txt');readme.clear();readme.write('CASA DEI COLORI / six occupied levels L01–L06 / 14 furnished homes\n\nRelease CANDIDATE; do not infer independent acceptance.\nMetric units. Clear collections are nested under each occupied level.\nIn Text Editor open VIEW_MODES.py and Run Script to restore intact mode.\nPython Console: exec(bpy.data.texts["VIEW_MODES.py"].as_string()); set_view("floor","L03")\nOther modes: intact, interior, plan, section, structure.\nEvery floor can be isolated; high partitions, facade and ceiling are separate.\nOriginal mesh signage; no font dependency, linked images, libraries or add-ons.\nAll rooms and furnishings are actual editable geometry; no image-generated facades.\nFinal meshes are losslessly batched to bound RAM; source component names are custom properties.\nUse scene/interiors.blend for individual component/modifier editing, or Edit Mode in this file.\nSee HANDOFF.md and evidence/producer for tests, settings, rights and known defects.\nNot an engineered/code-approved design.\n')
# Final reception sightline includes both desk and the mail wall rather than just lockers.
from mathutils import Vector
cam=bpy.data.objects['CAM_L01_DETAIL'];cam.location=(15.38,4.4,1.62);cam.rotation_euler=(Vector((12.6,7.2,1.05))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=18
set_view('intact');s.camera=bpy.data.objects['CAM_EXTERIOR_DAY']
# Use material-preview viewport so a clean machine can inspect without automatic execution.
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.clip_end=500;area.spaces.active.shading.type='MATERIAL'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'scene/building-final.blend'),compress=True)
report={'blender':bpy.app.version_string,'build_hash':bpy.app.build_hash.decode(),'mesh_objects':sum(o.type=='MESH' for o in s.objects),'objects':len(s.objects),'materials':len(bpy.data.materials),'cameras':[o.name for o in s.objects if o.type=='CAMERA'],'engine':s.render.engine,'colour_management':'AgX / Medium High Contrast; exposure 0 exteriors/cutaways, +0.8 interiors','samples':16,'denoising':'integrated OFF to bound RAM; separate tiled OIDN display-referred sRGB colour-only','status':'candidate, not accepted'}
(ROOT/'evidence/producer/scene-report.json').write_text(json.dumps(report,indent=2)+'\n');print('ASSEMBLED_NATIVE_CANDIDATE',report['objects'],report['mesh_objects'])
