"""Sequential, resumable native intake of twelve source poses. No visual acceptance automation."""
from pathlib import Path
import json,subprocess,os,hashlib,fcntl,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/production'))
from prepare_scan_texture import prepare
B='/home/user/.cache/blender-4.3.2-linux-x64/blender';plan=json.loads((R/'design/scanned-people-intake-plan.json').read_text());E={k:os.environ[k]for k in ['PATH','HOME','LANG']if k in os.environ};E.update(OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='1',LD_LIBRARY_PATH='/home/user/.cache/blender-deps/usr/lib/x86_64-linux-gnu');logs=R/'.cache/scan-native-logs';logs.mkdir(exist_ok=True);rows=[]
for row in plan['variants']:
 pose=row['pose'];texture=prepare(pose,'LOD1',4096);env=dict(E,SQUARE_SCAN_POSE=pose,SQUARE_SCAN_CLEAN='1',SQUARE_SCAN_TEXTURE_OVERRIDE=texture['derivative']);report=R/'evidence/production'/('R12-native-scan-asset-'+pose+'-clean.json');valid=False
 if report.exists():
  d=json.loads(report.read_text());p=R/d['native'];valid=p.exists()and hashlib.file_digest(p.open('rb'),'sha256').hexdigest()==d['native_sha256']
 if not valid:
  with (R/'.cache/blender-job.lock').open('w')as lock,(logs/(pose+'-import.log')).open('w')as log:
   fcntl.flock(lock,fcntl.LOCK_EX);subprocess.run([B,'--factory-startup','-b','-t','2','--python-exit-code','1','--python','tools/production/import_licensed_scan_study.py'],env=env,cwd=R,stdout=log,stderr=subprocess.STDOUT,check=True)
 d=json.loads(report.read_text());rows.append({'variant':row['variant'],'pose':pose,'native':d['native'],'native_sha256':d['native_sha256'],'vertices':d['mesh_vertices'],'polygons':d['mesh_polygons'],'actual_cleanup':d['cleanup'],'texture_dimensions':d['packed_diffuse_dimensions']});print('ACTUAL_CLEAN_NATIVE_SCAN_READY',row['variant'],pose,d['native_sha256'],flush=True)
(R/'evidence/production/R12-twelve-native-scans.json').write_text(json.dumps({'stage':'ACTUAL 12 packed native source-pose meshes imported, upper-body conservation and scoped sole cleanup checked; individual render/visual review and town adoption pending','variants':rows},indent=2)+'\n');print('TWELVE_ACTUAL_NATIVE_SCANS_BUILT_NOT_ADOPTED_OR_VISUALLY_ACCEPTED',flush=True)
