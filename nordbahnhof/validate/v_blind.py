#!/usr/bin/env python3
"""Verify recorded blind trials; never invent judge outcomes or generate passing results."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,default=ROOT/'evidence/BLIND/actual_trials.json');p.add_argument('--json',type=Path,default=ROOT/'evidence/v_blind.json');p.add_argument('--class',dest='kind',default='all');p.add_argument('--trials',type=int,default=20)
    a=p.parse_args();errors=[];summaries={}
    if not a.input.exists():
        errors.append('No actual recorded judge trials. Previous deterministic screening values were fabricated placeholders and are withdrawn.')
    else:
        d=json.loads(a.input.read_text());classes=['exterior','interior_volume','human','material_macro','iron','vehicle'] if a.kind=='all' else [a.kind]
        for c in classes:
            rows=[r for r in d.get('trials',[]) if r.get('class')==c]
            valid=[r for r in rows if r.get('judge') and r.get('artifact_sha256') and r.get('reference_sha256') and r.get('timestamp') and isinstance(r.get('correct'),bool)]
            correct=sum(r['correct'] for r in valid);summaries[c]={'recorded_trials':len(valid),'correct':correct}
            if len(valid)!=20:errors.append(f'{c}: requires 20 complete real trial records, found {len(valid)}')
            if correct>9:errors.append(f'{c}: {correct}/20 exceeds 9/20 threshold')
    report={'validator':'v_blind','status':'BLOCKED' if errors else 'PASS','classes':summaries,'errors':errors,'note':'Record validation is not proof of independent judge identity.'}
    a.json.parent.mkdir(parents=True,exist_ok=True);a.json.write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2));return 1 if errors else 0
if __name__=='__main__':sys.exit(main())
