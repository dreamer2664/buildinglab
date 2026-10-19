import os,sys,json,hashlib,subprocess,fcntl
from pathlib import Path
R=Path(__file__).resolve().parents[2];B='/home/user/.cache/blender-4.3.2-linux-x64/blender';env={k:os.environ[k] for k in ['PATH','HOME','LANG','LD_LIBRARY_PATH'] if k in os.environ};env.update(OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='1');logs=R/'.cache/subasset-validation-logs';logs.mkdir(exist_ok=True)
keys=os.environ.get('SQUARE_ASSET_KEYS','').split(',') if os.environ.get('SQUARE_ASSET_KEYS') else None
exclusive_lock=(R/'.cache/blender-job.lock').open('w');fcntl.flock(exclusive_lock,fcntl.LOCK_EX);print('EXCLUSIVE_SAVED_NATIVE_REOPEN_BATCH_STARTED',flush=True)
for key in keys or [f'B{i:02}' for i in range(1,13)]+['PUBLIC']+[f'P{i:02}' for i in range(1,13)]:
 E=env.copy();E['SQUARE_ASSET']=key
 with (logs/(key+'.log')).open('w') as f:subprocess.run([B,'--factory-startup','-b','-t','2','--python-exit-code','1','--python',str(R/'tools/production/validate_subasset.py')],env=E,cwd=R,stdout=f,stderr=subprocess.STDOUT,check=True)
 print('ACTUAL_FULL_MAP_NATIVE_SUBASSET_REOPEN_PASS',key,flush=True)
print('SELECTED_EDITABLE_NATIVE_SUBASSETS_ACTUALLY_REOPENED_PASS',len(keys) if keys else 25,flush=True)
