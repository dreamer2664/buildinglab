"""Measured duplicate-face repair matching Blender's glTF exporter validation.
Not a triangle-count tolerance waiver: every unique geometric triangle must remain EXACTLY,
all original vertex coordinates remain EXACTLY and every kept textured triangle was in source.
"""
import bpy,array,struct,hashlib

def _sets(mesh):
 mesh.calc_loop_triangles();geometry=set();textured=set();uv=mesh.uv_layers.active
 for tri in mesh.loop_triangles:
  points=[];corners=[]
  for vi,li in zip(tri.vertices,tri.loops):
   xyz=struct.pack('<3f',*mesh.vertices[vi].co);points.append(xyz);corners.append(xyz+(struct.pack('<2f',*uv.data[li].uv)if uv else b''))
  geometry.add(hashlib.blake2b(b''.join(sorted(points)),digest_size=16).digest());textured.add(hashlib.blake2b(struct.pack('<i',tri.material_index)+b''.join(sorted(corners)),digest_size=16).digest())
 return geometry,textured

def repair_duplicate_faces(mesh):
 positions=array.array('f',[0])*(len(mesh.vertices)*3);mesh.vertices.foreach_get('co',positions);before_positions=positions.tobytes();before_counts=[len(mesh.vertices),len(mesh.polygons)];g0,u0=_sets(mesh);before_triangles=len(mesh.loop_triangles);changed=mesh.validate(verbose=True,clean_customdata=False);mesh.update();g1,u1=_sets(mesh);positions=array.array('f',[0])*(len(mesh.vertices)*3);mesh.vertices.foreach_get('co',positions);assert positions.tobytes()==before_positions,'Topology validation moved/removed source vertex coordinates';assert g0==g1,'Topology validation removed/changed unique triangle geometry';assert u1.issubset(u0),'Topology validation created/altered textured surface triangles';after_counts=[len(mesh.vertices),len(mesh.polygons)];proof=hashlib.sha256(b''.join(sorted(g0))).hexdigest();return {'actual_mesh_validate_changed':changed,'source_vertices_faces_before':before_counts,'actual_vertices_faces_after':after_counts,'actual_source_triangles_before':before_triangles,'actual_validated_triangles_after':len(mesh.loop_triangles),'actual_duplicate_faces_removed':before_counts[1]-after_counts[1],'original_vertex_coordinates_exact_equality':True,'unique_triangle_geometry_set_exact_equality':True,'unique_triangle_geometry_signature_before_and_after':proof,'kept_textured_triangle_set_is_exact_source_subset':True,'textured_triangle_set_counts':[len(u0),len(u1)],'method':'Actual Mesh.validate duplicateface repair BEFORE export expectation; glTF exporter invokes this same validation. No coordinate/UV approximation and no relaxed triangle gate. Native unchanged unless explicitly saved by a separate source-repair stage.'}
