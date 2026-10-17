"""Recover exact canonical photographic bytes from current packed native; read-only, no network."""
import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[2];b=json.loads((R/'evidence/production/R11-native-build.json').read_text());source=R/b['full_resolution_native'];manifest=json.loads((R/'evidence/production/native-source-map-manifest.json').read_text());needed={r['sha256'] for r in manifest};data={}
if bpy.data.filepath and Path(bpy.data.filepath).resolve()==source.resolve():
 images=list(bpy.data.images) # Never recursively library-load the already open native.
else:
 with bpy.data.libraries.load(str(source),link=False) as (a,c):c.images=list(a.images)
 images=c.images
for im in images:
 if not im or not im.packed_file:continue
 raw=im.packed_file.data;h=hashlib.sha256(raw).hexdigest()
 if h in needed:data[h]=raw
missing=[]
for r in manifest:
 p=R/r['file']
 if r['sha256'] not in data:missing.append(r['name']);continue
 p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data[r['sha256']]);assert p.stat().st_size==r['bytes']
assert not missing,'Canonical maps absent from packed current native: '+str(missing)
print('ACTUAL_PACKED_PHOTOGRAPHIC_MAPS_RESTORED_EXACT_SHA',len(manifest))
