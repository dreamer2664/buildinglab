import bpy,json,hashlib,os
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];s=bpy.context.scene;kind=os.environ.get('SQUARE_PREVIEW','town');c=s.camera
if kind=='human':c.location=(-3.6,-12.8,1.65);target=(-3,-9,1.1);c.data.lens=64
else:c.location=(10,-12,2.2);target=(-8,24,4.6);c.data.lens=28
s.view_settings.exposure=1.2
if kind=='human':
 light=bpy.data.lights.new('Close-human / soft photographic key','AREA');light.energy=180;light.shape='DISK';light.size=4
 ob=bpy.data.objects.new(light.name,light);s.collection.objects.link(ob);ob.location=(-5,-12,3.5);ob.rotation_euler=(Vector((-3,-9,1.3))-ob.location).to_track_quat('-Z','Y').to_euler()
c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();s.render.resolution_x=1200;s.render.resolution_y=750;s.render.resolution_percentage=100;s.cycles.samples=16;s.cycles.use_denoising=False
s.render.filepath=str(R/'.cache'/(kind+'-study-R2.png'));s.render.image_settings.file_format='PNG'
from bpy_extras.object_utils import world_to_camera_view
bpy.context.view_layer.update();culled=[]
for o in list(s.objects):
 if o.type!='MESH':continue
 pts=[world_to_camera_view(s,c,o.matrix_world@Vector(p)) for p in o.bound_box]
 outside=all(p.z<0 for p in pts) or all(p.x<-.15 for p in pts) or all(p.x>1.15 for p in pts) or all(p.y<-.15 for p in pts) or all(p.y>1.15 for p in pts)
 if outside:culled.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
bpy.data.orphans_purge(do_recursive=True)
(R/'evidence/production'/(kind+'-study-culling.json')).write_text(json.dumps({'method':'Render-only camera frustum,15percent image margin; all light objects retained; original production geometry unchanged on disk. Offscreen reflections/shadows can differ.','removed_mesh_objects':culled},indent=2)+'\n')
print('RENDER_ONLY_FRUSTUM_CULL',len(culled),flush=True)
bpy.ops.render.render(write_still=True)
p=Path(s.render.filepath);(R/'evidence/production'/(kind+'-study-render.json')).write_text(json.dumps({'image':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source_native_sha256':s.get('source_native_sha256'),'render_derivative':bpy.data.filepath,'samples':16,'size':[1200,750],'camera':list(c.location),'target':target,'lens_mm':c.data.lens,'visual_review':'PENDING'},indent=2)+'\n')
