"""Actual separate saved-source studio renders; manual individual inspection is separate."""
from pathlib import Path
import subprocess,os,json,fcntl,hashlib
R=Path(__file__).resolve().parents[2];B='/home/user/.cache/blender-4.3.2-linux-x64/blender';rows=json.loads((R/'evidence/production/R12-twelve-native-scans.json').read_text())['variants'];env={k:os.environ[k]for k in ['PATH','HOME','LANG']if k in os.environ};env.update(OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='1',LD_LIBRARY_PATH='/home/user/.cache/blender-deps/usr/lib/x86_64-linux-gnu');out=R/'evidence/quality-studies/licensed-scan-study';logs=R/'.cache/scan-native-logs'
for row in rows:
 pose=row['pose'];report=out/(pose+'-clean-full.json');p=R/row['native']
 with p.open('rb')as f:assert hashlib.file_digest(f,'sha256').hexdigest()==row['native_sha256']
 E=dict(env,SQUARE_SCAN_POSE=pose,SQUARE_SCAN_CLEAN='1',SQUARE_SCAN_VIEW='full')
 with (R/'.cache/blender-job.lock').open('w')as lock,(logs/(pose+'-full-render.log')).open('w')as log:
  fcntl.flock(lock,fcntl.LOCK_EX);subprocess.run([B,'-b',str(p),'-t','2','--python-exit-code','1','--python','tools/production/render_licensed_scan_study.py'],env=E,cwd=R,stdout=log,stderr=subprocess.STDOUT,check=True)
 d=json.loads(report.read_text());assert d['actual_opened_native_sha256']==row['native_sha256'];print('ACTUAL_SEPARATE_CLEAN_SCAN_RENDER_READY',row['variant'],pose,d['image_sha256'],flush=True)
print('TWELVE_ACTUAL_NATIVE_BODY_RENDERS_COMPLETE_NOT_VISUAL_ACCEPTANCE',flush=True)
