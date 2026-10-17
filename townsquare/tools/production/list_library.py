import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[2]
with bpy.data.libraries.load(str(R/'.cache/recovery/master/Winterlichtplatz.blend'),link=False) as (src,dst):
 d={'objects':list(src.objects),'collections':list(src.collections),'scenes':list(src.scenes),'texts':list(src.texts)}
 (R/'evidence/production/library-index.json').write_text(json.dumps(d,indent=2)+'\n');print('LIBRARY_INDEX',len(d['objects']),d['collections'][:30],d['objects'][:40],flush=True)
