import bpy,json,hashlib,os
from pathlib import Path
R=Path(__file__).resolve().parents[2];s=bpy.context.scene
out={'native_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'scene_properties':dict(s.items()),'collections':[{'name':c.name,'properties':dict(c.items()),'objects':len(c.objects)} for c in bpy.data.collections],'cameras':[{'name':o.name,'position':list(o.location),'lens':o.data.lens,'properties':dict(o.items())} for o in s.objects if o.type=='CAMERA'],'texts':[t.name for t in bpy.data.texts],'objects_sample':[{'name':o.name,'type':o.type,'position':list(o.location),'props':dict(o.items())} for o in s.objects if o.type=='MESH'],'images':[{'name':im.name,'dimensions':list(im.size),'packed':bool(im.packed_file)} for im in bpy.data.images]}
(R/'evidence/production/recovered-native-inventory.json').write_text(json.dumps(out,indent=2,default=str)+'\n')
print('RECOVERED_NATIVE_INSPECTION',len(s.objects),len(out['cameras']),out['texts'],flush=True)
for t in bpy.data.texts:
 (R/'evidence/production'/('embedded-'+t.name.replace('/','_'))).write_text(t.as_string())
