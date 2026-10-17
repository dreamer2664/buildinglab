import os,subprocess,json,hashlib,fcntl,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2];B='/home/user/.cache/blender-4.3.2-linux-x64/blender';env={k:os.environ[k] for k in ['PATH','HOME','LANG','LD_LIBRARY_PATH'] if k in os.environ};env.update(OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='1');logs=R/'.cache/export-logs';logs.mkdir(parents=True,exist_ok=True)
def run(script,key):
 E=env.copy();E['SQUARE_COMPONENT']=key
 with (R/'.cache/blender-job.lock').open('w') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  with (logs/(script+'-'+key+'.log')).open('w') as f:subprocess.run([B,'--factory-startup','-b','-t','2','--python-exit-code','1','--python',str(R/'tools/production'/(script+'.py'))],env=E,cwd=R,stdout=f,stderr=subprocess.STDOUT,check=True)
for key in [f'B{i:02}' for i in range(1,13)]+['PUBLIC']+[f'P{i:02}' for i in range(1,13)]:
 report=R/'evidence/production'/('export-'+key+'.json');file=R/'.cache/final-components/GLB'/(key+'.glb')
 if not (report.exists() and file.exists() and json.loads(report.read_text()).get('source_native_sha256')==json.loads((R/'evidence/production/R6-native-build.json').read_text())['full_resolution_native_sha256']):run('export_component',key);old=R/'evidence/production'/('reimport-'+key+'.json');old.unlink(missing_ok=True)
 print('COMPONENT_EXPORT_COMPLETE',key,flush=True)
 report=R/'evidence/production'/('reimport-'+key+'.json')
 if not (report.exists() and json.loads(report.read_text())['status']=='PASS'):run('reimport_glb',key)
 print('COMPONENT_CLEAN_REIMPORT_PASS',key,flush=True)
with (R/'.cache/blender-job.lock').open('w') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);subprocess.run([sys.executable,str(R/'tools/production/merge_glb.py')],env=env,cwd=R,check=True)
run('reimport_glb','ALL');print('WHOLE_PORTABLE_MODEL_ACTUAL_CLEAN_REIMPORT_COMPLETED',flush=True)
