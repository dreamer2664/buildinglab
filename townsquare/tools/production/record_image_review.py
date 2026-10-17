"""Manually invoke ONLY AFTER actually opening the named final original separately.
Usage: python record_image_review.py VIEW_ID 'actual observed findings'
Producer quality-control record, never an independent review/vote.
"""
from pathlib import Path
import sys,json,hashlib,datetime
from PIL import Image
R=Path(__file__).resolve().parents[2];id=sys.argv[1];notes=sys.argv[2];manifest=json.loads((R/'evidence/production/final-render-manifest.json').read_text());r=manifest[id];p=R/r['image'];sha=hashlib.sha256(p.read_bytes()).hexdigest();assert sha==r['final_sha256']
with Image.open(p) as im:dimensions=list(im.size)
path=R/'evidence/production/final-individual-image-inspections.json';d=json.loads(path.read_text()) if path.exists() else {'scope':'Manual producer original-image inspections after actual separate file opens; not independent acceptance or photographic-realism certification','inspections':{}}
d['inspections'][id]={'view_id':id,'image':r['image'],'image_sha256':sha,'dimensions':dimensions,'source_native_sha256':r['source_native_sha256'],'actual_original_opened':True,'method':'Separate single-file functions.read_file call on actual native-resolution PNG; this record is made manually afterward, not inferred from render completion/contact sheet.','decision':'PRODUCER_CHECKED','observed_findings':notes,'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'independent_acceptance':False};path.write_text(json.dumps(d,indent=2)+'\n');print('PRODUCER_ORIGINAL_REVIEW_RECORDED',id,sha)
