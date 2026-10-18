"""Own measured geometric LODs with original higher-source UV/photo, avoiding supplied-LOD bake defects.
Builds and actually renders each pose sequentially; manual visual inspection stays separate.
"""
from pathlib import Path
import sys,os,json,subprocess,fcntl,hashlib
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/production'))
from intake_licensed_scan import intake
from prepare_scan_texture import prepare
B='/home/user/.cache/blender-4.3.2-linux-x64/blender';plan=json.loads((R/'design/scanned-people-intake-plan.json').read_text());E={k:os.environ[k]for k in ['PATH','HOME','LANG']if k in os.environ};E.update(OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='1',LD_LIBRARY_PATH='/home/user/.cache/blender-deps/usr/lib/x86_64-linux-gnu');logs=R/'.cache/own-scan-lod-logs';logs.mkdir(exist_ok=True)
def sha(p):
 with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def run(script,env,native,logname):
 with (R/'.cache/blender-job.lock').open('w')as lock,(logs/(logname+'.log')).open('w')as log:
  fcntl.flock(lock,fcntl.LOCK_EX);args=[B,'-b',str(native)]if native else[B,'--factory-startup','-b'];subprocess.run(args+['-t','2','--python-exit-code','1','--python',str(R/'tools/production'/script)],cwd=R,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
rows=[]
for row in plan['variants']:
 pose=row['pose'];reportname='R12-native-scan-asset-'+pose+'-own-lod-clean.json';p=R/'evidence/production'/reportname;valid=False
 if p.exists():
  d=json.loads(p.read_text());native=R/d['native'];valid=native.exists()and sha(native)==d['native_sha256']
 if not valid:
  intake(pose,'LOD0');tex=prepare(pose,'LOD0',4096);high_path=R/'evidence/production'/('R12-native-scan-asset-'+pose+'-LOD0.json');high=None
  if high_path.exists():
   high=json.loads(high_path.read_text());n=R/high['native']
   if not n.exists()or sha(n)!=high['native_sha256']:high=None
  if high is None:
   env=dict(E,SQUARE_SCAN_POSE=pose,SQUARE_SCAN_LOD='LOD0',SQUARE_SCAN_TEXTURE_OVERRIDE=tex['derivative']);run('import_licensed_scan_study.py',env,None,pose+'-import-original-high');high=json.loads(high_path.read_text())
  env=dict(E,SQUARE_SCAN_POSE=pose,SQUARE_SCAN_TEXTURE_OVERRIDE=tex['derivative']);run('derive_scan_lod_from_original.py',env,R/high['native'],pose+'-derive-own-lod');d=json.loads(p.read_text())
 rows.append({'variant':row['variant'],'pose':pose,'native':d['native'],'native_sha256':d['native_sha256'],'report':reportname,'vertices':d['mesh_vertices'],'polygons':d['mesh_polygons'],'actual_decimation':d['own_mesh_decimation'],'texture_dimensions':d['packed_diffuse_dimensions']});print('ACTUAL_ORIGINAL_UV_OWN_SCAN_LOD_READY',row['variant'],pose,d['native_sha256'],flush=True)
 image_meta=R/'evidence/quality-studies/licensed-scan-study'/(pose+'-own-lod-clean-full.json');valid=False
 if image_meta.exists():
  m=json.loads(image_meta.read_text());image=R/m['actual_native_render_image'];valid=m['actual_opened_native_sha256']==d['native_sha256']and image.exists()and sha(image)==m['image_sha256']
 if not valid:
  env=dict(E,SQUARE_SCAN_POSE=pose,SQUARE_SCAN_VIEW='full',SQUARE_SCAN_REPORT=reportname,SQUARE_SCAN_OUTPUT_SUFFIX='-own-lod-clean');run('render_licensed_scan_study.py',env,R/d['native'],pose+'-own-lod-render')
 print('ACTUAL_ORIGINAL_UV_OWN_SCAN_LOD_RENDER_READY',row['variant'],pose,flush=True)
 # Retain reproducible pinned receipts/upstream URLs; discard only redundant downloaded ZIP copies to bound disk.
 source_receipt=R/'evidence/production'/('R12-actual-scan-intake-'+pose+'-LOD0.json')
 if source_receipt.exists():
  source=json.loads(source_receipt.read_text());archive=R/source['source_archive']
  if archive.exists()and sha(archive)==source['source_archive_sha256']:archive.unlink();print('REDUNDANT_PINNED_DOWNLOAD_ZIP_COPY_RELEASED',pose,flush=True)
(R/'evidence/production/R12-twelve-own-lod-native-scans.json').write_text(json.dumps({'stage':'Actual own original-UV source-photo scan LODs and saved-source body renders; individual inspection/adoption pending','variants':rows},indent=2)+'\n');print('TWELVE_ORIGINAL_UV_OWN_SCAN_LODS_RENDERED_NOT_VISUALLY_APPROVED',flush=True)
