"""Restore public CC0 feasibility maps from exact recorded URLs/digests. No keys."""
from pathlib import Path
import hashlib,json,urllib.request
R=Path(__file__).resolve().parents[1]
for row in json.loads((R/'assets/materials/manifest.json').read_text()):
 p=R/row['file'];p.parent.mkdir(parents=True,exist_ok=True)
 if not p.exists():
  with urllib.request.urlopen(urllib.request.Request(row['source_url'],headers={'User-Agent':'Mozilla/5.0'}),timeout=90) as response:p.write_bytes(response.read())
 assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
 print('MAP_SHA_VERIFIED',row['file'])
