"""Read-only actual recovered native rig inventory before any accessory adaptation."""
import bpy,os,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/production'))
from fingerprints import file_sha256
pid=os.environ['SQUARE_GROOM_PID'];r=json.loads((R/'evidence/production/R12-actual-editable-rig-recovery.json').read_text());row=next(x for x in r['recovered_editable_rigs']if x['rig']==pid);assert file_sha256(bpy.data.filepath)==row['sha256'];objects=[]
for o in bpy.context.scene.objects:
 d={'name':o.name,'type':o.type,'properties':dict(o.items()),'matrix_world':[list(r)for r in o.matrix_world]}
 if o.type=='MESH':d.update(vertices=len(o.data.vertices),polygons=len(o.data.polygons),uv_layers=[u.name for u in o.data.uv_layers],materials=[m.name if m else None for m in o.data.materials],modifiers=[{'type':m.type,'name':m.name,'target':m.object.name if m.type=='ARMATURE'and m.object else None}for m in o.modifiers],shape_keys=[k.name for k in o.data.shape_keys.key_blocks]if o.data.shape_keys else[])
 if o.type=='ARMATURE':d['pose_bones']=[{'name':p.name,'head':list(p.head),'tail':list(p.tail),'matrix':[list(r)for r in p.matrix]}for p in o.pose.bones]
 objects.append(d)
report={'rig':pid,'actual_recovered_native_sha256':row['sha256'],'objects':objects,'packed_images':sum(bool(i.packed_file)for i in bpy.data.images),'scope':'Actual read-only fresh Blender open of preserved rig; inventory for measured alignment, not new visual/highrealism approval.'};(R/'evidence/production'/('R12-recovered-rig-inventory-'+pid+'.json')).write_text(json.dumps(report,indent=2,default=str)+'\n');print('ACTUAL_RECOVERED_RIG_INVENTORY',pid,[(d['name'],d['type'],d.get('materials'))for d in objects if d['type']in['MESH','ARMATURE']],flush=True)
