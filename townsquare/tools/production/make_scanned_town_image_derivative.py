"""Save geometry-identical packed image-only derivative, then render in a FRESH process.
Avoid high-water full-image allocations in the same process as Cycles BVH construction.
"""
import bpy,sys,os,json,hashlib,re,gc
from pathlib import Path
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/production'))
from fingerprints import file_sha256,geometry_uv_pose_material_signature
b=json.loads((R/'evidence/production'/os.environ.get('SQUARE_SCAN_TOWN_BUILD_REPORT','R12-scanned-town.json')).read_text());assert file_sha256(bpy.data.filepath)==b['native_sha256'];before=geometry_uv_pose_material_signature();assert before==b['geometry_uv_pose_material_signature'];originals=[];changes=[];folder=R/'.cache/native-scan-photo-originals';folder.mkdir(exist_ok=True)
for image in list(bpy.data.images):
 if image.source!='FILE'or not image.users:continue
 assert image.packed_file,'Original photo must be packed';raw=image.packed_file.data;digest=hashlib.sha256(raw).hexdigest();name=image.name
 if name.startswith('HSRD100_'):
  p=folder/(digest+'.png')
  if not p.exists():p.write_bytes(raw)
  originals.append({'name':name,'source_packed_sha256':digest,'file':str(p.relative_to(R)),'original_dimensions':[int.from_bytes(raw[16:20],'big'),int.from_bytes(raw[20:24],'big')]})
 del raw
 source=tuple(image.size);cap=1024 if name.startswith('HSRD100_')else 2048 if re.match(r'^B\d\d\.png',name)else 1024 if name.startswith('MARKTGRUEN_PRODUCTS_')else 512
 factor=min(1,cap/max(source));dest=tuple(max(1,round(x*factor))for x in source)
 if dest!=source:image.scale(*dest);image.pack();changes.append({'image':name,'source_packed_sha256':digest,'source_dimensions':source,'render_derivative_dimensions':dest})
 image.buffers_free();gc.collect();print('IMAGE_ONLY_DERIVATIVE_PHOTO_READY',name,dest,flush=True)
after=geometry_uv_pose_material_signature();assert before==after;bpy.context.scene['source_authoritative_full_native_sha256']=b['native_sha256'];bpy.context.scene['derivative_notice']='Image-only packed preview source: all original geometry/UV/poses/material assignments conserved. Original full4k scan/photo maps and source pixels remain in authoritative native. Render-specific photographic resampling recorded, not a new architectural/people model.';path=R/'.cache/scanned-town'/('Winterlichtplatz-image-only-render-derivative-'+b['native_sha256'][:12]+'.blend');path.parent.mkdir(parents=True,exist_ok=True);bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);r=dict(b);r.update(native=str(path.relative_to(R)),native_sha256=file_sha256(path),native_bytes=path.stat().st_size,source_full_native_sha256=b['native_sha256'],source_full_native=b['native'],image_only_derivative_geometry_signature_before=before,image_only_derivative_geometry_signature_after=after,actual_image_resampling=changes,stage='GEOMETRY_IDENTICAL_IMAGE_ONLY_DERIVATIVE / actual source-bound render PENDING');(R/'evidence/production/R12-scanned-town-render-derivative.json').write_text(json.dumps(r,indent=2)+'\n');(R/'evidence/production/R12-render-scan-original-photos.json').write_text(json.dumps({'source_full_native_sha256':b['native_sha256'],'rows':originals},indent=2)+'\n');print('GEOMETRY_IDENTICAL_SCANNED_TOWN_IMAGE_DERIVATIVE_SAVED',r['native_bytes'],r['native_sha256'],before,flush=True)
