"""Non-destructive full-map building components + static portable study + actual clean imports.
Dedicated output/report namespace, never overwrites frozen R11 components or gates.
"""
import os,sys,json,subprocess,fcntl,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[2];b=json.loads((R/'evidence/production'/os.environ.get('SQUARE_EXPORT_BUILD_REPORT','R12-placement-corrected-interiors.json')).read_text());source=R/b['native'];assert hashlib.file_digest(source.open('rb'),'sha256').hexdigest()==b['native_sha256'];base=R/os.environ.get('SQUARE_EXPORT_OUT','.cache/placement-portable-components');reports=R/os.environ.get('SQUARE_EXPORT_REPORTS','evidence/production/placement-portable');reports.mkdir(exist_ok=True);logs=R/os.environ.get('SQUARE_EXPORT_LOGS','.cache/placement-portable-logs');logs.mkdir(exist_ok=True);B='/home/user/.cache/blender-4.3.2-linux-x64/blender';env={k:os.environ[k]for k in ['PATH','HOME','LANG','LD_LIBRARY_PATH']if k in os.environ};env.update(OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='1',SQUARE_SOURCE_NATIVE=b['native'],SQUARE_SOURCE_SHA256=b['native_sha256'],SQUARE_COMPONENT_OUT=str(base.relative_to(R)),SQUARE_COMPONENT_REPORTS=str(reports.relative_to(R)),SQUARE_WHOLE_GLB_NAME='Winterlichtplatz-interior-study.glb',SQUARE_REVISION='UNPROMOTED inspected-interior study '+b['native_sha256'][:12])
def run(script,key):
 E=env.copy();E['SQUARE_COMPONENT']=key
 with (R/'.cache/blender-job.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  with (logs/(script+'-'+key+'.log')).open('w')as output:subprocess.run([B,'--factory-startup','-b','-t','2','--python-exit-code','1','--python',str(R/'tools/production'/(script+'.py'))],cwd=R,env=E,stdout=output,stderr=subprocess.STDOUT,check=True)
for key in [f'B{i:02}'for i in range(1,13)]+['PUBLIC']+[f'P{i:02}'for i in range(1,13)]:
 p=base/'GLB'/(key+'.glb');report=reports/('export-'+key+'.json');valid=False
 if p.exists()and report.exists():
  row=json.loads(report.read_text());valid=row['source_native_sha256']==b['native_sha256']and row['glb_sha256']==hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
 if not valid:run('export_component',key)
 print('STUDY_COMPONENT_EXPORTED',key,flush=True);run('reimport_glb',key);print('STUDY_COMPONENT_CLEAN_REIMPORT_PASS',key,flush=True)
with (R/'.cache/blender-job.lock').open('a')as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);subprocess.run([sys.executable,str(R/'tools/production/merge_glb.py')],cwd=R,env=env,check=True)
run('reimport_glb','ALL');r={'stage':'ACTUAL_PORTABLE_STUDY_EXPORT_AND_CLEAN_REIMPORT_NOT_FINAL_VISUAL_ACCEPTANCE','source_native_sha256':b['native_sha256'],'component_count':25,'native_building_public_components':13,'people':('36static anatomical instances/12variants. P06/P12original anatomy/clothes conserved, new100k native physical curves per variant and explicit6k tube portableLOD/PBR approximation; matching rig adaptation must be read separately, not inferred from staticGLB.'if b.get('actual_groom_variant_adaptations')else'36static anatomical instances/12variants; editable human rigs are unchanged existing licensed sources, not newly modified'),'whole_glb':str((base/'Winterlichtplatz-interior-study.glb').relative_to(R)),'whole_glb_sha256':hashlib.file_digest((base/'Winterlichtplatz-interior-study.glb').open('rb'),'sha256').hexdigest(),'clean_reimport':json.loads((reports/'reimport-ALL.json').read_text()),'lighting_limitations':'Core glTF does not reproduce Blender HDRI/area lights/procedural shaders/AgX;512px portable images, full packed originals in natives.'};(R/'evidence/production'/os.environ.get('SQUARE_EXPORT_SUMMARY','R12-placement-portable-summary.json')).write_text(json.dumps(r,indent=2)+'\n');print('STUDY_WHOLE_PORTABLE_CLEAN_REIMPORT_PASS',r['whole_glb_sha256'],flush=True)
