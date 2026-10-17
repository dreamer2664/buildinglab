"""Actually reopen exact anonymous current native, restore packed map bytes, render scoped smoke."""
import os,sys,json,subprocess,fcntl,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[2];B='/home/user/.cache/blender-4.3.2-linux-x64/blender';L='/home/user/.cache/blender-4.3.2-linux-x64/lib';C=R/'.cache/public-R11';source=C/'public-exact-Winterlichtplatz-R11.blend';expected=json.loads((R/'evidence/production/R11-native-build.json').read_text())['full_resolution_native_sha256']
with source.open('rb')as f:assert hashlib.file_digest(f,'sha256').hexdigest()==expected
env={k:os.environ[k]for k in ['PATH','HOME','LANG','LD_LIBRARY_PATH']if k in os.environ};env.update(OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='1')
def run(name,args,extra={}):
 e=env.copy();e.update(extra)
 with (R/'.cache/blender-job.lock').open('w')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  with (C/(name+'.log')).open('w')as log:subprocess.run(args,env=e,cwd=R,stdout=log,stderr=subprocess.STDOUT,check=True)
 print('EXACT_PUBLIC_NATIVE_STEP_EXECUTED',name,flush=True)
base=[B,'--factory-startup','-b',str(source),'-t','2','--python-exit-code','1','--python']
run('actual-native-reopen',base+[str(R/'tools/production/validate_native.py')],{'SQUARE_VALIDATION_REPORT':'R11-public-exact-native-reopen.json'})
run('actual-packed-map-recovery-test',[B,'--factory-startup','-b','-t','2','--python-exit-code','1','--python',str(R/'tools/production/restore_packed_source_maps.py')])
run('actual-native-smoke',base+[str(R/'tools/production/render_public_native_smoke.py')],{'SQUARE_VIEW':'B01_L01_interior'})
run('ordinary-oidn',[sys.executable,str(R/'tools/denoise_png.py'),str(C/'exact-public-native-B01_L01_interior.png'),L])
p=R/'evidence/production/R11-public-checkpoint.json';d=json.loads(p.read_text());d['exact_public_native_reopen']='ACTUAL_FRESH_REOPEN_PASS / R11-public-exact-native-reopen.json';d['exact_public_native_smoke']='Actual1152x648B01 image rendered/OIDN. Separate original opening still PENDING, not final photographic approval.';p.write_text(json.dumps(d,indent=2)+'\n');print('EXACT_PUBLIC_NATIVE_CHECKS_COMPLETE / actual image inspection remains separate',flush=True)
