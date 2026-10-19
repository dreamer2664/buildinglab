"""Negative regression tests for design validator; mutates isolated fixtures, never the real design."""
from pathlib import Path
import tempfile,shutil,json,subprocess,sys,unittest
R=Path(__file__).resolve().parents[1]
class DesignTests(unittest.TestCase):
 def run_fixture(self,mutate=None):
  with tempfile.TemporaryDirectory() as td:
   r=Path(td);(r/'design').mkdir();(r/'tools').mkdir()
   shutil.copy(R/'tools/validate_design.py',r/'tools/validate_design.py')
   for p in (R/'design').glob('plan-*.svg'):shutil.copy(p,r/'design'/p.name)
   d=json.loads((R/'design/programme.json').read_text())
   if mutate:mutate(d,r)
   (r/'design/programme.json').write_text(json.dumps(d))
   return subprocess.run([sys.executable,str(r/'tools/validate_design.py')],capture_output=True,text=True)
 def test_valid(self):self.assertEqual(self.run_fixture().returncode,0)
 def test_missing_home(self):self.assertNotEqual(self.run_fixture(lambda d,r:d['levels'][1]['homes'].pop()).returncode,0)
 def test_seventh_level(self):self.assertNotEqual(self.run_fixture(lambda d,r:d['levels'].append(d['levels'][-1])).returncode,0)
 def test_bad_scale(self):self.assertNotEqual(self.run_fixture(lambda d,r:d.update(footprint_m=[20,20])).returncode,0)
 def test_missing_plan(self):self.assertNotEqual(self.run_fixture(lambda d,r:(r/'design/plan-L06.svg').unlink()).returncode,0)
 def test_blocked_access(self):self.assertNotEqual(self.run_fixture(lambda d,r:d['levels'][1].update(doors=[])).returncode,0)
 def test_door_outside_wall(self):self.assertNotEqual(self.run_fixture(lambda d,r:d['levels'][1]['doors'][0].update(x=100)).returncode,0)
if __name__=='__main__':unittest.main()
