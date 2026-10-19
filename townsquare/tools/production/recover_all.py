import os,sys,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2];B='/home/user/.cache/blender-4.3.2-linux-x64/blender';env={k:os.environ[k] for k in ['PATH','HOME','LANG','LD_LIBRARY_PATH'] if k in os.environ};env['OMP_NUM_THREADS']='2'
for key in [f'B{i:02}' for i in range(1,13)]+['PUBLIC']+[f'P{i:02}' for i in range(1,13)]:
 if (R/'.cache/render-chunks'/(key+'.blend')).exists() and (R/'evidence/production'/('recovered-'+key+'.json')).exists():continue
 env['SQUARE_CHUNK']=key;log=Path('/home/user/.cache')/('recover-'+key+'.log')
 with log.open('w') as f:subprocess.run([B,'--factory-startup','-b','-t','2','--python-exit-code','1','--python',str(R/'tools/production/recover_chunk.py')],cwd=R,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
 print('CHUNK_RECOVERED',key,flush=True)
print('ALL_RENDER_CHUNKS_RECOVERED_GEOMETRY_CONSERVED',flush=True)
