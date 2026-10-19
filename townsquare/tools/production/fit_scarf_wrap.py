"""Keep original editable scarf textile shape; fit against evaluated parka with real triangle-overlap tests."""
import bpy,bmesh,itertools,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_ray_tri

def fit_wrap_to_coat(wrap,coat,clearance=.003):
 bpy.context.view_layer.update();ev=coat.evaluated_get(bpy.context.evaluated_depsgraph_get());cm=ev.to_mesh();cv=[coat.matrix_world@v.co for v in cm.vertices];cm.calc_loop_triangles();cf=[tuple(p.vertices) for p in cm.loop_triangles];tree=BVHTree.FromPolygons(cv,cf,all_triangles=True,epsilon=clearance);ev.to_mesh_clear()
 original=wrap.data.copy();original.name=wrap.name+' / conserved original pre-fit mesh';original.use_fake_user=True
 mesh=wrap.data;points=[wrap.matrix_world@v.co for v in mesh.vertices];mesh.calc_loop_triangles();polys=[tuple(p.vertices) for p in mesh.loop_triangles];center=sum(points,Vector())/len(points);inv=wrap.matrix_world.inverted()
 def cross(a,b):
  for tri,other in ((a,b),(b,a)):
   for j in range(3):
    origin=tri[j];delta=tri[(j+1)%3]-origin
    if delta.length_squared<1e-16:continue
    hit=intersect_ray_tri(*other,delta,origin,True)
    if hit is not None:
     t=(hit-origin).dot(delta)/delta.length_squared
     if .000001<t<.999999:return True
  return False
 def count(ps):
  pairs=tree.overlap(BVHTree.FromPolygons(ps,polys,all_triangles=True,epsilon=clearance));total=0
  for i,j in pairs:
   if cross([cv[k] for k in cf[i]],[ps[k] for k in polys[j]]):total+=1
  return total
 before=count(points);candidates=[]
 for scale,dy,dz in itertools.product([1,1.04,1.08,1.12,1.16,1.20],[0,-.005,-.010,-.015,-.020,-.030],[0,.005,.010,.015,.020,.025,.030,.040,.050,.060,.065,.070,.075,.080,.085,.090]):
  cost=math.hypot(dy,dz)+.15*abs(scale-1);candidates.append((cost,scale,dy,dz))
 chosen=None;best=(999999,None)
 for cost,scale,dy,dz in sorted(candidates):
  ps=[Vector((center.x+(p.x-center.x)*scale,center.y+(p.y-center.y)*scale+dy,p.z+dz)) for p in points]
  n=count(ps)
  if n<best[0]:best=(n,(scale,dy,dz))
  if n==0:chosen=(ps,scale,dy,dz,cost);break
 assert chosen is not None,('No collision-free small scarf-wrap fit found',before,best,[(min(p[k] for p in points),max(p[k] for p in points)) for k in range(3)],[(min(p[k] for p in cv),max(p[k] for p in cv)) for k in range(3)])
 ps,scale,dy,dz,cost=chosen
 for v,p in zip(mesh.vertices,ps):v.co=inv@p
 mesh.update()
 for p in mesh.polygons:p.use_smooth=True
 assert count([wrap.matrix_world@v.co for v in mesh.vertices])==0
 return {'part':wrap.name,'fix':'Actual side macro exposed collar penetration. Original editable textile shape fitted by minimum-cost bounded affine search against evaluated parka; narrow-phase triangle-edge intersection regression0 (BVH broad-phase3mm margin). Original pre-fit mesh retained.','original_triangle_overlap_pairs':before,'corrected_triangle_overlap_pairs':0,'world_y_shift_m':dy,'world_z_shift_m':dz,'horizontal_scale':scale,'max_vertex_displacement_m':max((p-q).length for p,q in zip(ps,points)),'bvh_margin_m':clearance,'anatomy_or_pose_changes':False}
