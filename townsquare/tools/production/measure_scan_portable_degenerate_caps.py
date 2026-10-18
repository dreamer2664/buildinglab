"""Read-only source diagnosis for exact portable triangle mismatch, not a gate waiver."""
import bpy,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/production'))
from fingerprints import file_sha256
b=json.loads((R/'evidence/production/R13-crafted-exteriors.json').read_text());source=R/b['native'];assert file_sha256(source)==b['native_sha256'];bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(source),link=False)as(a,c):c.objects=['CROWD_01_P01']
o=c.objects[0];m=o.data;m.calc_loop_triangles();tiny=[{'triangle':t.index,'polygon':t.polygon_index,'area_m2':t.area,'vertices':list(t.vertices),'positions':[list(m.vertices[i].co)for i in t.vertices]}for t in m.loop_triangles if t.area<=1e-16];r={'source_native_sha256':b['native_sha256'],'source_actor':o.name,'actual_loop_triangles':len(m.loop_triangles),'actual_triangles_at_or_below_1e_minus16_m2':tiny,'actual_zero_area_count':sum(t.area==0 for t in m.loop_triangles),'measured_area_threshold_m2':1e-16,'stage':'DIAGNOSIS_ONLY_NOT_ACCEPTANCE'};(R/'evidence/production/R13-source-scan-degenerate-cap-diagnosis.json').write_text(json.dumps(r,indent=2)+'\n');print('ACTUAL_SOURCE_SCAN_DEGENERATE_CAPS',len(tiny),r['actual_zero_area_count'],tiny[:5],flush=True)
