# AC, ASI and takeoff vs λ under three ways of adjusting η (Coding Automation Efficiency
# Improvement Factor) for λ: the model's η^(0.5/λ), the linear η·(0.5/λ), and no adjustment.
# The model always applies x -> x^(0.5/λ) to its input, so each variant feeds it the input
# that lands on the wanted value.
import json, numpy as np
from concurrent.futures import ProcessPoolExecutor
from aifm_sites import *
ETA = 3.0
WANT = {'power': lambda l: ETA ** (0.5 / l), 'linear': lambda l: ETA * 0.5 / l, 'none': lambda l: ETA}
def job(a):
    mode, form, lam = a
    want = WANT[form](lam)
    p = dict(preset('daniel-08-16-26'), ac_anchor_mode=mode, parallel_penalty=lam,
             coding_automation_efficiency_slope=want ** (lam / 0.5))
    r = model_run(p, None, detail=True); m = r.pop('model')
    return dict(mode=mode, form=form, lam=lam, eta_used=float(m._original_automation_efficiency_slope), eta_want=want,
                ac=r['ac'], asi=r['asi'], takeoff_months=12 * (r['asi'] - r['ac']), f_now=r['f_now'])
if __name__ == '__main__':
    lams = [round(x, 2) for x in np.arange(0.3, 1.001, 0.05)]
    jobs = [(m, f, l) for m in ['uplift-solved', 'time-horizon', 'revenue'] for f in WANT for l in lams]
    with ProcessPoolExecutor(4) as ex: out = list(ex.map(job, jobs))
    json.dump(out, open('eta_sweep_raw.json', 'w'), indent=0)
    for r in out: print(r['mode'], r['form'], r['lam'], round(r['eta_used'], 3), round(r['eta_want'], 3), round(r['ac'], 3), round(r['asi'], 3), round(r['takeoff_months'], 1))
