import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/production'))
from fix_ceiling_fixture_clearance import repair_clearance
r=repair_clearance(json.loads((R/'design/programme.json').read_text()));(R/'evidence/production/R11-ceiling-fixture-clearance.json').write_text(json.dumps(r,indent=2)+'\n');bpy.ops.wm.save_as_mainfile(filepath=str(R/'.cache/master/Winterlichtplatz-render-R11-prototype.blend'));print('CLEARANCE_PROTOTYPE_SAVED',len(r['changes']),len(r['actual_corrected_emitter_downward_ray_checks']),flush=True)
