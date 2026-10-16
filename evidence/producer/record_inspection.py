"""Record an explicitly performed producer image inspection; never infer one from rendering.
Use only AFTER opening the named original PNG. --sync-manifest only restores existing
SHA-bound observations that a concurrently-running renderer may have overwritten.
"""
import argparse,datetime,hashlib,json
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--view');p.add_argument('--observations');p.add_argument('--known-major',type=int,default=0);p.add_argument('--sync-manifest',action='store_true');a=p.parse_args()
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
mp=R/'evidence/producer/screenshot-manifest.json';rp=R/'evidence/producer/visual-review.json';m=json.loads(mp.read_text())
r=json.loads(rp.read_text()) if rp.exists() else {'observer':'blender / producer agent; not independent reviewer','independent_acceptance':'pending','final_inspections':[],'defects':[]}
if a.view:
 assert a.observations and len(a.observations)>25,'Write the actual observation, not a render-success claim'
 row=next(x for x in m['images'] if x['id']==a.view);f=R/row['path'];digest=sha(f);assert digest==row['sha256'];assert row['source_sha256']==sha(R/'scene/building-final.blend')
 with Image.open(f) as im:dimensions=list(im.size)
 rec={'image':row['path'],'sha256':digest,'source_sha256':row['source_sha256'],'dimensions':dimensions,'opened_individually':True,'method':'original final PNG opened with workspace image reader; targeted native-pixel crops where needed','logged_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'observations':a.observations,'known_critical_major':a.known_major}
 r['final_inspections']=[x for x in r['final_inspections'] if x['image']!=rec['image']]+[rec];rp.write_text(json.dumps(r,indent=2)+'\n')
if a.view or a.sync_manifest:
 for row in m['images']:
  rec=next((x for x in r['final_inspections'] if x['image']==row['path'] and x['sha256']==row['sha256'] and x.get('source_sha256')==row['source_sha256']),None)
  if rec:
   row['producer_opened_individually']=True;row['review_result']='inspected: no known critical/major' if rec['known_critical_major']==0 else 'inspected: fixes required'
 mp.write_text(json.dumps(m,indent=2)+'\n')
print('Explicit SHA-bound producer inspections recorded:',len(r['final_inspections']))
