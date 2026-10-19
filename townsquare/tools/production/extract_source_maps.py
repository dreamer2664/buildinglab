import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[2];out=R/'.cache/source-maps';out.mkdir(parents=True,exist_ok=True)
with bpy.data.libraries.load(str(R/'.cache/recovery/master/Winterlichtplatz.blend'),link=False) as (a,b):b.images=list(a.images)
records=[]
for i,im in enumerate(b.images):
 if not im or not im.packed_file:continue
 data=im.packed_file.data
 ext='.png' if data.startswith(b'\x89PNG') else '.jpg' if data.startswith(b'\xff\xd8') else '.exr' if data.startswith(b'v/1\x01') else '.hdr' if data.startswith(b'#?') else '.bin'
 p=out/(f'{i:03}'+ext);p.write_bytes(data)
 records.append({'name':im.name,'file':str(p.relative_to(R)),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'colorspace':im.colorspace_settings.name})
(R/'evidence/production/native-source-map-manifest.json').write_text(json.dumps(records,indent=2)+'\n');print('PACKED_SOURCE_MAPS_EXTRACTED',len(records),flush=True)
