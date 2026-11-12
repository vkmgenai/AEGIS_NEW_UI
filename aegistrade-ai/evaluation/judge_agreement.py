"""Calibrate an actual different-family judge against independently supplied labels.

No labels or judge decisions are invented. Legacy suggested_machine_label is not used.
"""
from __future__ import annotations
import argparse,json,math
from pathlib import Path
from sklearn.metrics import cohen_kappa_score


def calibration(rows):
    labelled=[r for r in rows if isinstance(r.get('human_label'),bool) and isinstance(r.get('judge_label'),bool)]
    if len(labelled)<20:raise ValueError(f'Need 20+ human AND actual judge labels; found {len(labelled)}')
    for row in labelled:
        solver=row.get('solver_model','').split('/')[0]
        judge=row.get('judge_model','').split('/')[0]
        if not solver or not judge or solver==judge:raise ValueError('Record solver and different-family judge model IDs')
        if not row.get('human_reviewer'):raise ValueError('Record the human label reviewer')
    a=[r['human_label'] for r in labelled];b=[r['judge_label'] for r in labelled]
    kappa=float(cohen_kappa_score(a,b))
    return {'labelled':len(labelled),'agreement':sum(x==y for x,y in zip(a,b))/len(a),
            'cohen_kappa':kappa if math.isfinite(kappa) else None,
            'limitation':'Kappa is undefined if labels have no variation; agreement alone is not calibration.'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--labels',type=Path,default=Path(__file__).with_name('judge_calibration.json'))
    a=p.parse_args()
    try:print(json.dumps(calibration(json.loads(a.labels.read_text())),indent=2))
    except ValueError as exc:print('Not calibrated:',exc);return 2
    return 0

if __name__=='__main__':raise SystemExit(main())
