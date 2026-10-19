"""UNSAVED fitting study: real original licensed hair vertices fitted just outside actual head/neck skin.
No scalp removal, photo repaint, camera trick, native save, topology/UV/material alteration or acceptance.
"""
import bpy,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree

def smooth(t):
 t=max(0,min(1,t));return t*t*(3-2*t)
def apply():
 rows=[]
 for o in list(bpy.context.scene.objects):
  if o.type!='MESH'or not o.get('person_id'):continue
  mesh=o.data;hair={i for i,m in enumerate(mesh.materials)if m and 'braid01'in m.name.lower()};skin={i for i,m in enumerate(mesh.materials)if m and(m.name.endswith('.body')or'.body.'in m.name)}
  if not hair:continue
  assert skin,('Cannot fit without actual body/skin triangles',o.name,[m.name for m in mesh.materials if m]);o.data=mesh=mesh.copy();mesh.calc_loop_triangles();coords=[v.co.copy()for v in mesh.vertices];tris=[tuple(t.vertices)for t in mesh.loop_triangles if t.material_index in skin];bvh=BVHTree.FromPolygons(coords,tris,all_triangles=True);verts={v for p in mesh.polygons if p.material_index in hair for v in p.vertices};changes=[];miss=0
  for i in sorted(verts):
   p=coords[i]
   if not(1.265<p.z<1.47 and p.y>.025):continue
   hit,n,face,d=bvh.ray_cast(Vector((p.x,1,p.z)),Vector((0,-1,0)),2)
   if hit is None:miss+=1;continue
   clearance=.004;limit=hit.y+clearance;strength=smooth((p.z-1.265)/.025)*smooth((1.47-p.z)/.035)
   if p.y>limit:
    y=p.y+(limit-p.y)*strength;mesh.vertices[i].co.y=y;changes.append({'vertex':i,'before':list(p),'after':[p.x,y,p.z],'actual_skin_hit':list(hit),'clearance_m':clearance,'strength':strength})
  mesh.update();rows.append({'object':o.name,'person_id':o['person_id'],'actual_modified_hair_vertices':len(changes),'skin_triangles':len(tris),'hair_vertex_count':len(verts),'missing_skin_rays':miss,'max_actual_displacement_m':max((c['before'][1]-c['after'][1]for c in changes),default=0),'changes':changes,'scope':'Only original braid01 rear/nape mesh vertices, actual same-object body skin ray hits,4mm target stand-off with smooth vertical boundary fade. Original topology/UV/alpha texture/material/body geometry retained. UNSAVED test, not adoption.'})
 bpy.context.view_layer.update();return rows
