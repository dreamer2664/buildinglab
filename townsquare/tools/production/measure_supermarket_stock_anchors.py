"""Read-only shelf-top measurements from actual source supermarket furniture, not guessed rows."""
import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/production'))
from fingerprints import file_sha256
b=json.loads((R/'evidence/production/R13-crafted-exteriors.json').read_text());assert file_sha256(bpy.data.filepath)==b['native_sha256'];objects=[o for o in bpy.context.scene.objects if o.type=='MESH'and o.get('room_id')=='B01_L01_SALES'and o.get('layer')=='furniture'];tops=[];materials=[]
for o in objects:
 materials.extend(m.name for m in o.data.materials if m)
 for f in o.data.polygons:
  normal=o.matrix_world.to_3x3()@f.normal
  if normal.z<.99:continue
  ps=[o.matrix_world@o.data.vertices[i].co for i in f.vertices];lo=[min(p[k]for p in ps)for k in range(3)];hi=[max(p[k]for p in ps)for k in range(3)];a,c=hi[0]-lo[0],hi[1]-lo[1]
  if hi[2]-lo[2]>.002 or not .3<lo[2]<2.1:continue
  if 1.0<max(a,c)<8 and .18<min(a,c)<.72:tops.append({'source_object':o.name,'source_polygon':f.index,'world_bounds':[lo,hi],'surface_dimensions_m':[a,c],'surface_z_m':lo[2],'material':o.data.materials[f.material_index].name if f.material_index<len(o.data.materials)and o.data.materials[f.material_index]else None})
# Exact coincident face duplicates are not counted as separate shelves.
unique={tuple(round(x,4)for p in t['world_bounds']for x in p):t for t in tops};r={'source_native_sha256':b['native_sha256'],'actual_sales_room_furniture_objects':[o.name for o in objects],'actual_material_names':sorted(set(materials)),'actual_measured_shelf_top_faces':list(unique.values()),'stage':'Actual shelf surface candidates for original merchandising; not new geometry or clearance certification'};(R/'evidence/production/R13-supermarket-stock-anchors.json').write_text(json.dumps(r,indent=2)+'\n');print('ACTUAL_SUPERMARKET_SHELF_SURFACES_MEASURED',len(unique),flush=True)
for row in unique.values():print(row)
