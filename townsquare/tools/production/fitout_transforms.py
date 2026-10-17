"""Scoped, real vertex-region rigid edits to recovered merged furniture.
Never edits shells/body or stretches a partially-selected face. Original UVs/materials retained.
"""
import math
import numpy as np

def local_vertices(o,b,datum):
 a=np.empty(len(o.data.vertices)*3,dtype=np.float32);o.data.vertices.foreach_get('co',a);raw=a.reshape(-1,3).copy();m=np.asarray(o.matrix_world,dtype=np.float64);world=raw.astype(np.float64)@m[:3,:3].T+m[:3,3];ang=math.radians(b['rotation_deg']);c,s=math.cos(ang),math.sin(ang);rot=np.array([[c,-s,0],[s,c,0],[0,0,1]],dtype=float);origin=np.array([*b['centre_xy_m'],datum]);return raw,(world-origin)@rot,m,rot,origin

def material_bounds(o,b,datum,prefix):
 raw,a,m,rot,origin=local_vertices(o,b,datum);slots={i for i,x in enumerate(o.data.materials)if x and x.name.startswith(prefix)};ids=sorted({v for p in o.data.polygons if p.material_index in slots for v in p.vertices});assert ids,(o.name,prefix);v=a[ids];return v.min(axis=0),v.max(axis=0)

def edit_region(o,b,datum,minimum,maximum,angle=0,pivot=(0,0),delta=(0,0,0),tag='',material_prefixes=None):
 if o.data.users>1:o.data=o.data.copy()
 raw,a,m,rot,origin=local_vertices(o,b,datum);lo=np.asarray(minimum);hi=np.asarray(maximum);selected=np.all((a>=lo-1e-5)&(a<=hi+1e-5),axis=1);
 if material_prefixes:
  slots={i for i,mat in enumerate(o.data.materials) if mat and any(mat.name.startswith(prefix) for prefix in material_prefixes)};allowed=np.zeros(len(a),dtype=bool)
  for face in o.data.polygons:
   if face.material_index in slots:allowed[list(face.vertices)]=True
  selected &= allowed
 assert selected.any(),('No actual furniture selected',o.name,tag)
 partial=0
 for p in o.data.polygons:
  count=sum(bool(selected[v])for v in p.vertices)
  if count and count!=len(p.vertices):partial+=1
 assert partial==0,('Refusing to distort partially selected mesh faces',o.name,tag,partial)
 before=a[selected].copy();centre=np.array([*pivot,0]);c,s=math.cos(angle),math.sin(angle);turn=np.array([[c,-s,0],[s,c,0],[0,0,1]]);after=(before-centre)@turn.T+centre+np.asarray(delta);world=after@rot.T+origin;raw[selected]=(world-m[:3,3])@np.linalg.inv(m[:3,:3]).T;o.data.vertices.foreach_set('co',raw.ravel());o.data.update();o['R12_actual_scoped_edit']=tag
 return {'object':o.name,'tag':tag,'actual_vertices_rigidly_moved':int(selected.sum()),'partial_mesh_faces':partial,'before_local_bounds':[before.min(axis=0).tolist(),before.max(axis=0).tolist()],'after_local_bounds':[after.min(axis=0).tolist(),after.max(axis=0).tolist()],'angle_degrees':math.degrees(angle),'local_delta_m':list(delta),'scope':'Actual selected complete mesh faces; UV/material assignments retained, no whole-room turn or shell mutation. Clearance/visual reinspection still required.'}
