"""Actual anonymous published GLB fresh-import and neutral visual proof renders; no inferred inspections."""
import os,sys,json,subprocess,fcntl,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[2];B='/home/user/.cache/blender-4.3.2-linux-x64/blender';L='/home/user/.cache/blender-4.3.2-linux-x64/lib';C=R/'.cache/public-R10-additional';source=C/'public-exact-Winterlichtplatz-R10.glb';native=C/'public-exact-clean-reimport.blend';logs=C/'proof-logs';logs.mkdir(exist_ok=True)
env={k:os.environ[k] for k in ['PATH','HOME','LANG','LD_LIBRARY_PATH'] if k in os.environ};env.update(OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='1')
def run(name,args,extra={}):
 e=env.copy();e.update(extra)
 with (R/'.cache/blender-job.lock').open('w') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  with (logs/(name+'.log')).open('w') as log:subprocess.run(args,env=e,cwd=R,stdout=log,stderr=subprocess.STDOUT,check=True)
 print('PUBLIC_GLB_CHECK_EXECUTED',name,flush=True)
run('actual-anonymous-public-clean-reimport',[B,'--factory-startup','-b','-t','2','--python-exit-code','1','--python',str(R/'tools/production/reimport_glb.py')],{'SQUARE_COMPONENT':'ALL','SQUARE_REIMPORT_PATH':str(source),'SQUARE_REIMPORT_REPORT':'R10-public-glb-reimport.json','SQUARE_REIMPORT_SAVE':str(native)})
for view in ['D02','H02','B01_L01_interior']:
 run('proof-'+view,[B,'--factory-startup','-b',str(native),'-t','2','--python-exit-code','1','--python',str(R/'tools/production/render_portable_proof.py')],{'SQUARE_VIEW':view,'SQUARE_PORTABLE_NATIVE':str(native),'SQUARE_PORTABLE_GLB':str(source)})
 run('denoise-'+view,[sys.executable,str(R/'tools/denoise_png.py'),str(R/'.cache/portable-proof'/(view+'.png')),L])
 p=R/'.cache/portable-proof'/(view+'.json');d=json.loads(p.read_text());im=R/'.cache/portable-proof'/(view+'.png')
 with im.open('rb') as f:d['denoised_png_sha256']=hashlib.file_digest(f,'sha256').hexdigest()
 d['inspection']='PENDING / must separately open actual original';p.write_text(json.dumps(d,indent=2)+'\n')
 (R/'evidence/production'/('R10-public-glb-proof-'+view+'.json')).write_text(json.dumps(d,indent=2)+'\n')
print('THREE_PUBLIC_GLB_VISUAL_PROOFS_RENDERED_INSPECTION_PENDING',flush=True)
