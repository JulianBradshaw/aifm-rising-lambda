"""Two-λ version of figures/lambda_sweep/sweep_anchors.py: forward λ 0.3..1.0, η linear rescale."""
import csv, logging, os, sys
from concurrent.futures import ProcessPoolExecutor
REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
sys.path.insert(0, REPO)
PRESETS = ['daniel-08-16-26','eli-08-16-26','brendan-08-16-26']
MODES = ['uplift-solved','time-horizon','revenue']
def job(a):
    logging.disable(logging.CRITICAL)
    from two_lambda.model import Variant, simulate
    name, mode, lam = a
    try:
        r = simulate(Variant(lambda_forward=lam), mode, end=2040.0, preset=name)
        ac, asi, err = r['milestones'].get('AC'), r['milestones'].get('ASI'), None
    except Exception as e:
        ac = asi = None; err = repr(e)[:200]
    return dict(preset=name, ac_anchor_mode=mode, lambda_forward=lam,
        ac_year=None if ac is None else round(ac,4), asi_year=None if asi is None else round(asi,4),
        months_ac_to_asi=None if (ac is None or asi is None) else round((asi-ac)*12,2), error=err)
if __name__ == '__main__':
    jobs = [(n, m, round(0.3+0.05*k,2)) for n in PRESETS for m in MODES for k in range(15)]
    with ProcessPoolExecutor(os.cpu_count()) as ex: rows = list(ex.map(job, jobs))
    w = csv.DictWriter(open('lambda_sweep_anchors_two_lambda.csv','w',newline=''), fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    for r in rows:
        if r['lambda_forward'] in (0.3,0.5,1.0) or r['error']: print(r)
