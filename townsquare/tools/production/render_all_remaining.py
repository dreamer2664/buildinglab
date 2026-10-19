"""Render the remaining evidence views one at a time with resumable, digest-checked state.

Priority order: street-level heroes, then per-floor interiors, then cutaways, then plans.
Every frame goes through the same saved-source / separate-OIDN pipeline as the other views.
"""
import json, subprocess, sys, os
from pathlib import Path

R = Path(__file__).resolve().parents[2]
design = json.loads((R / 'design/production-views.json').read_text())
OUT = R / 'evidence/current-production'
order = {'town': 0, 'aerial': 0, 'interior': 1, 'cutaway': 2, 'plan': 3, 'people': 4}
todo = [f for f in design['frames']
        if not (OUT / (f['id'] + '.png')).exists() and f['kind'] in order]
todo.sort(key=lambda f: (order[f['kind']], f['id']))
limit = int(os.environ.get('REMAINING_LIMIT', '1000'))
env = dict(os.environ, SQUARE_VIEW_PRESETS_FILE=str(R / 'design/production-views.json'))
for f in todo[:limit]:
    if f['kind'] == 'people':
        env['SQUARE_PRUNE_MODE'] = ''
    else:
        env['SQUARE_PRUNE_MODE'] = ''
    print('REMAINING_VIEW_START', f['id'], f['kind'], flush=True)
    r = subprocess.run([sys.executable, 'tools/production/render_current_evidence.py',
                        '--views', f['id'], '--samples', str(min(f.get('samples', 16), 24))],
                       cwd=R, env=env)
    print('REMAINING_VIEW_EXIT', f['id'], r.returncode, flush=True)
    if r.returncode != 0:
        print('REMAINING_VIEW_FAILED_CONTINUING', f['id'], flush=True)
