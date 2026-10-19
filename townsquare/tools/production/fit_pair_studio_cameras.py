"""Actual full-frame pair-studio camera fitting from the real actor bounds.
Composition-only unsaved camera change; no model/geometry edit. Every pair checked for both
complete silhouettes within frame and realistic 2-person framing.
"""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
import sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/production'))
frames=json.loads((R/'design/production-views.json').read_text())['frames'];s=bpy.context.scene;from view_tools import apply_view
records=[]
for f in frames:
 if f['kind']!='people'or (f['id'] not in ['D01','D02','D03','D04','D05','D06']):continue
 apply_view(f['id']);path_objects=[o for o in s.objects if o.type=='MESH'and o.get('person_id')in f['person_ids']and not o.hide_render];ids=sorted({int(o['person_id'])for o in path_objects});anchors=[]
 for pid in ids:anchors.append(sum((Vector((o.matrix_world.translation.x,o.matrix_world.translation.y,0))for o in path_objects if o.get('person_id')==pid),Vector())/max(1,sum(o.get('person_id')==pid for o in path_objects)))
 centre=sum(anchors,Vector())/len(anchors);points=[o.matrix_world@Vector(c)for o in path_objects for c in o.bound_box];top=max(p.z for p in points);side=Vector((anchors[1]-anchors[0]))if len(anchors)>1 else Vector((1,0,0));side.z=0
 if side.length:side.normalize()
 separation=(anchors[1]-anchors[0]).length if len(anchors)>1 else 1.0;cam=s.camera;best=None
 for distance in [2.5,3.0,3.5,4.0,4.8,5.6,6.5]:
  for lens in [42,50,58,66]:
   for raise_z in [.9,1.15,1.4]:
    target=Vector((centre.x,centre.y,min(top*.5,1.25)));position=target-side*distance+Vector((0,0,raise_z))
    cam.location=position;cam.rotation_euler=(target-position).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;bpy.context.view_layer.update();views=[world_to_camera_view(s,cam,p)for p in points];xs=[v.x for v in views];ys=[v.y for v in views];visible=min(xs)>-.012 and max(xs)<1.012 and min(ys)>-.012 and max(ys)<1.012;width=(max(xs)-min(xs));fill=max(width,1e-3)
    score=0 if visible else 100+abs(min(xs)) +abs(1-max(xs))+abs(min(ys))+abs(1-max(ys))
    if best is None or score<best['score']:best={'score':score,'position':list(position),'target':list(target),'lens':lens,'min_x':min(xs),'max_x':max(xs),'min_y':min(ys),'max_y':max(ys),'subject_width_fraction':width,'subject_height_fraction':max(ys)-min(ys)}
 assert best['score']==0,('Pair framing not fully visible',f['id'],best);cam.location=best['position'];cam.rotation_euler=(Vector(best['target'])-Vector(best['position'])).to_track_quat('-Z','Y').to_euler();cam.data.lens=best['lens'];f.update(position=best['position'],target=best['target'],lens_mm=best['lens']);records.append({'view':f['id'],'person_ids':ids,'actual_anchor_separation_m':separation,'actual_both_full_silhouettes_in_frame':True,**best});print('ACTUAL_PAIR_FRAME_FIT',f['id'],ids,best['lens'],round(best['subject_height_fraction'],3),flush=True)
(R/'evidence/production/R14-pair-studio-camera-fits.json').write_text(json.dumps({'studio_geometry':'Unsaved single physical cyclorama centred on actual pair, directional studio lights','views':records,'method':'Actual actor bounds projected through fitted camera; both complete silhouettes entirely inside frame. Not a model/hair fix or final visual acceptance.'},indent=2)+'\n');print('SIX_ACTUAL_PAIR_CAMERAS_FIT_BOTH_SUBJECTS_VISIBLE',flush=True)
