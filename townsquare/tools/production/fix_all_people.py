import os,subprocess,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[2];B='/home/user/.cache/blender-4.3.2-linux-x64/blender';env={k:os.environ[k] for k in ['PATH','HOME','LANG','LD_LIBRARY_PATH'] if k in os.environ};env['OMP_NUM_THREADS']='2'
with zipfile.ZipFile(R/'.cache/recovery/Winterlichtplatz-People-rigs-4bf44a021c3d.zip') as z:
 for n in range(1,13):
  pid=f'P{n:02}'
  if (R/'evidence/production'/('person-fit-'+pid+'.json')).exists():continue
  z.extract('People/'+pid+'.blend',R/'.cache/recovery');env['SQUARE_PERSON']=pid
  log=R/'.cache'/('fit-'+pid+'.log')
  with log.open('w') as f:subprocess.run([B,'--factory-startup','-b',str(R/'.cache/recovery/People'/(pid+'.blend')),'-t','2','--python-exit-code','1','--python',str(R/'tools/production/fix_person_accessories.py')],env=env,cwd=R,stdout=f,stderr=subprocess.STDOUT,check=True)
  print('CORRECTED_EDITABLE_RIG_AND_STATIC_INSTANCES',pid,flush=True)
