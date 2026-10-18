# Takeoff (AC -> ASI) against the Infinite Coding Labor Asymptote, with only λ's straightforward
# benefit (turning coding labor into progress after today) switched to the new λ. Every other use
# of λ stays at 0.5, so the calibration side effects drop out.
import json
from concurrent.futures import ProcessPoolExecutor
from aifm_sites import *
CAPS = [3, 5, 10, 15, 30, 100, 300, 1e3, 1e4, 1e5, 1e8]
def job(a):
    mode, cap, lam = a
    p = dict(preset('daniel-08-16-26'), parallel_penalty=0.5, ac_anchor_mode=mode, inf_labor_asymptote=cap)
    r = model_run(p, {} if lam == 0.5 else {'dynamics': lam})
    return dict(mode=mode, asymptote=cap, lam=lam, ac=r['ac'], asi=r['asi'], takeoff_months=12 * (r['asi'] - r['ac']))
if __name__ == '__main__':
    jobs = [(m, c, l) for m in ['uplift-solved', 'time-horizon', 'revenue'] for c in CAPS for l in [0.5, 0.65, 1.0]]
    with ProcessPoolExecutor(4) as ex: out = list(ex.map(job, jobs))
    json.dump(out, open('asym_benefit_raw.json', 'w'), indent=0)
    for r in out: print(r['mode'], r['asymptote'], r['lam'], round(r['ac'], 3), round(r['takeoff_months'], 2))
