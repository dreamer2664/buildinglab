"""Inventory and geometric spot checks, not structural/accessibility certification."""
import bpy,json,hashlib,re,time
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[1];s=bpy.context.scene
src=Path(bpy.data.filepath);info={'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'source_bytes':src.stat().st_size,'objects':len(bpy.data.objects),'mesh_datablock_polygons':sum(len(m.polygons) for m in bpy.data.meshes),'district_people':len([o for o in bpy.data.objects if o.name.startswith('DIST_PERSON_')]),'building_zones':len({m.group(1) for o in bpy.data.objects if (m:=re.match(r'DIST_(B[0-9]+)_',o.name))}),'packed_images':[{'name':i.name,'size':list(i.size),'packed':bool(i.packed_file)} for i in bpy.data.images if i.type=='IMAGE'],'cameras':[o.name for o in bpy.data.objects if o.type=='CAMERA' and o.name.startswith('DISTVIEW_')],'legacy_insert_replacement':'Obstructing RET_/WAIT_ inserts removed in district revision; original prior source retained separately. All original 34 rolling-stock vehicles retained.'}
vehicles=sorted({m.group(1) for o in bpy.data.objects if (m:=re.match(r'TRAIN_(TR[0-9]+_V[0-9]+)',o.name))});info['retained_vehicle_ids']=vehicles;info['retained_vehicle_count']=len(vehicles)
# Temporarily exclude movable photographic people to test the architectural route.
for o in bpy.data.objects:
 if o.name.startswith(('DIST_PERSON_','SCAN_HERO_')):o.hide_viewport=True
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();checks=[]
for label,a,b in [('threshold',(10.5,23,2.1),(10.5,37,2.1)),('concourse turn',(10.5,36,2.1),(34.0,36,2.1))]:
 a,b=Vector(a),Vector(b);v=b-a;hit,loc,no,idx,ob,mat=s.ray_cast(deps,a,v.normalized(),distance=v.length)
 checks.append({'label':label,'start':list(a),'end':list(b),'static_hit':ob.name if hit else None,'hit_location':list(loc) if hit else None,'clear_at_probe_height':not hit})
for z in(1.35,2.1,2.65):
 for x in(10.15,10.85):
  aa=Vector((x,23,z));bb=Vector((x,37,z));vv=bb-aa;hit,loc,no,idx,ob,mat=s.ray_cast(deps,aa,vv.normalized(),distance=vv.length);checks.append({'label':'threshold lateral probe','start':list(aa),'end':list(bb),'static_hit':ob.name if hit else None,'clear_at_probe_height':not hit})
 for y in(35.65,36.35):
  aa=Vector((10.5,y,z));bb=Vector((34,y,z));vv=bb-aa;hit,loc,no,idx,ob,mat=s.ray_cast(deps,aa,vv.normalized(),distance=vv.length);checks.append({'label':'concourse lateral probe','start':list(aa),'end':list(bb),'static_hit':ob.name if hit else None,'clear_at_probe_height':not hit})
info['walk_surface_spot_checks']=[]
for x,y in[(10.5,24),(10.5,27),(10.5,32),(10.5,36),(19.4,36),(26.4,36),(33.4,36),(35,36)]:
 hit,loc,no,idx,ob,mat=s.ray_cast(deps,Vector((x,y,2.5)),Vector((0,0,-1)),distance=4);info['walk_surface_spot_checks'].append({'xy':[x,y],'surface_object':ob.name if hit else None,'surface_z':float(loc.z) if hit else None})
info['architectural_route_head_height_spot_checks']=checks;info['not_certification']='These centerline and lateral rays do not certify full-body clearance, accessibility, railway operation, structural loads or all rooms. The side ramp stays south ofY38.5; existing first rake atY40 is preserved.'
(r/'evidence').mkdir(exist_ok=True);(r/'evidence/DISTRICT_SOURCE_AUDIT.json').write_text(json.dumps(info,indent=2));print(json.dumps({k:v for k,v in info.items() if k!='packed_images'},indent=2),flush=True)
