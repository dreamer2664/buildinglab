import bpy,math
from mathutils import Vector
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for ob in list(bpy.data.objects):
 if ob.name.startswith('EMU_'):bpy.data.objects.remove(ob,do_unlink=True)
for i,(x,y) in enumerate([(12,96.5),(16.5,96.8),(19.2,96.8),(14.2,98)]):
 data=bpy.data.lights.new(f'Portrait bounce {i}','AREA');data.energy=170;data.shape='DISK';data.size=2.2;data.color=(.85,.90,1)
 ob=bpy.data.objects.new(data.name,data);bpy.context.scene.collection.objects.link(ob);ob.location=(x-.7,y-1.3,3.7);ob.rotation_euler=(Vector((x,y,2.15))-ob.location).to_track_quat('-Z','Y').to_euler()
# Give proof cameras honest names: these subjects are neither a guard, porter nor child.
for n in range(17,21):
 ob=next(o for o in bpy.data.objects if o.type=='CAMERA' and o.name.startswith(f'CAM_{n}'))
 ob.name=f'CAM_{n}_human_scan_subject_{n-16:02}'
# Aperture-limited photography without cinematic blur hiding faults.
for ob in bpy.data.objects:
 if ob.type=='CAMERA':ob.data.dof.use_dof=False
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'source/NORDBAHNHOF_REBUILD.blend'),compress=True)
