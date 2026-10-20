"""Replace rejected prototypes with attributed HSRD-100 scans; six real identities only."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
col=bpy.data.collections.get('08_PEOPLE')
for o in list(bpy.data.objects):
 if o.name.startswith('HERO_'):bpy.data.objects.remove(o,do_unlink=True)
if not col:
 col=bpy.data.collections.new('08_PEOPLE');bpy.context.scene.collection.children.link(col)
entries=json.loads((ROOT/'assets/scans/PROVENANCE.json').read_text())
placements=[(12,96.5,.76),(16.5,96.8,.76),(19.2,96.8,.76),(14.2,98.0,.76),(22,99,.76),(26,99,.76)]
for index,(entry,loc) in enumerate(zip(entries,placements)):
 folder=ROOT/'assets/scans'/entry['pose_id'];before=set(bpy.data.objects)
 bpy.ops.wm.obj_import(filepath=str(next(folder.glob('*.obj'))),forward_axis='Y',up_axis='Z',use_split_objects=False,use_split_groups=False)
 new=[o for o in bpy.data.objects if o not in before and o.type=='MESH'];ob=new[0];ob.name=f'SCAN_HERO_{index+1:02}'
 for c in list(ob.users_collection):c.objects.unlink(ob)
 col.objects.link(ob)
 vs=ob.data.vertices;mins=[min(v.co[a] for v in vs) for a in range(3)];maxs=[max(v.co[a] for v in vs) for a in range(3)]
 scale=1.75/(maxs[2]-mins[2]);origin=Vector(((mins[0]+maxs[0])/2,(mins[1]+maxs[1])/2,mins[2]))
 for v in vs:v.co=(v.co-origin)*scale
 mat=bpy.data.materials.new(entry['pose_id']+'_photo');mat.use_nodes=True;bsdf=mat.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Roughness'].default_value=.7;bsdf.inputs['Specular IOR Level'].default_value=.2
 tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(folder/'diffuse.jpg'));tex.image.pack();mat.node_tree.links.new(tex.outputs['Color'],bsdf.inputs['Base Color'])
 ob.data.materials.clear();ob.data.materials.append(mat)
 for p in ob.data.polygons:p.use_smooth=True
 ob.location=loc;ob.rotation_euler.z=math.pi
 ob['subject_id']=entry['subject_id'];ob['pose_id']=entry['pose_id'];ob['license']='CC BY 4.0 Digital Reality Lab';ob['provenance']='nordbahnhof/assets/scans/PROVENANCE.json'
# Fresh human framing, avoid the locomotive envelope.
for idx in range(4):
 cam=next(o for o in bpy.data.objects if o.type=='CAMERA' and o.name.startswith(f'CAM_{17+idx:02}'))
 x,y,z=placements[idx];cam.location=(x+.55,y-1.5,z+1.4);target=Vector((x,y,z+1.35));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=34
# Better shed composition: frame away from a foreground column.
cam=next(o for o in bpy.data.objects if o.type=='CAMERA' and o.name.startswith('CAM_29'))
cam.location=(-68,97,2.6);cam.rotation_euler=(Vector((28,91,10))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=26
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'source/NORDBAHNHOF_REBUILD.blend'),compress=True)
print('Six scanned identities installed; not a completed 400-person population.')
