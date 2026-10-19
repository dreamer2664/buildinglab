"""Actual segment/ray checks for lift floor plugs, flush cab floor and open ground portal.
Visual/concept checks only; not motion, swept clearance, safety or code certification.
Works on unbatched shell and on evaluated/batched native geometry.
"""
from mathutils import Vector

def lift_checks(scene,programme):
 def hits(objects,start,end):
  out=[]
  for o in objects:
   inv=o.matrix_world.inverted();a=inv@Vector(start);b=inv@Vector(end);v=b-a
   hit,p,n,face=o.ray_cast(a,v.normalized(),distance=v.length)
   if hit:out.append({'object':o.name,'point_m':list(o.matrix_world@p)})
  return out
 floors=[o for o in scene.objects if o.type=='MESH' and o.get('role') in ['slab','room_floor']]
 reports=[];errors=[]
 for level in programme['levels'][1:]:
  r=next(r for r in level['rooms'] if r['kind']=='elevator');x,y,xx,yy=r['rect'];z=level['elevation_m'];p=((x+xx)/2,(y+yy)/2)
  h=hits([o for o in floors if o.get('level')==level['id']],(*p,z+.08),(*p,z-.30));reports.append({'level':level['id'],'shaft_sample_xy_m':p,'horizontal_floor_hits':h})
  if h:errors.append(level['id']+' upper lift shaft blocked by horizontal floor geometry')
 ceiling_reports=[]
 for level in programme['levels']:
  r=next(r for r in level['rooms'] if r['kind']=='elevator');x,y,xx,yy=r['rect'];z=level['elevation_m']+level['storey_height_m']-.22;p=((x+xx)/2,(y+yy)/2)
  h=hits([o for o in scene.objects if o.type=='MESH' and o.get('role')=='ceiling' and o.get('level')==level['id']],(*p,z-.10),(*p,z+.10));ceiling_reports.append({'level':level['id'],'shaft_sample_xy_m':p,'ceiling_hits':h})
  if h:errors.append(level['id']+' lift shaft capped by common ceiling finish')
 lift=[o for o in scene.objects if o.type=='MESH' and o.get('role')=='lift' and o.get('level')=='L01']
 cab=hits(lift,(13,11.1,.20),(13,11.1,-.10));landing=hits([o for o in floors if o.get('level')=='L01'],(13,9.4,.20),(13,9.4,-.10))
 cab_z=max((h['point_m'][2] for h in cab),default=-99);landing_z=max((h['point_m'][2] for h in landing),default=-99)
 if cab_z<0 or landing_z<0 or abs(cab_z-landing_z)>.001:errors.append('ground cab floor is not flush with common landing')
 open_samples=[{'x_m':x,'hits':hits(lift,(x,9.3,1.1),(x,10.1,1.1))} for x in [12.51,12.76,13,13.24,13.49]]
 if any(p['hits'] for p in open_samples):errors.append('ground lift leaves obstruct sampled 0.98 m open portal')
 return {'scope':'actual geometric samples; not an engineering/code certificate','upper_shaft_samples':reports,'shaft_ceiling_samples':ceiling_reports,'cab_floor_top_m':cab_z,'landing_top_m':landing_z,'ground_portal_samples':open_samples,'errors':errors}
