# Plain λ 1 runs (every use of λ switched) at several asymptotes, Coding Uplift anchor, for the bar chart.
import json
from concurrent.futures import ProcessPoolExecutor
from aifm_sites import *
S5 = ['anchor', 'dynamics', 'history', 'eta', 'cap']
CAPS = [15, 100, 1e3, 1e4, 1e8]
def job(cap):
    p = dict(preset('daniel-08-16-26'), parallel_penalty=0.5, ac_anchor_mode='uplift-solved', inf_labor_asymptote=cap)
    r = model_run(p, {s: 1.0 for s in S5})
    return dict(asymptote=cap, ac=r['ac'], asi=r['asi'], takeoff_months=12 * (r['asi'] - r['ac']))
if __name__ == '__main__':
    with ProcessPoolExecutor(4) as ex: out = list(ex.map(job, CAPS))
    json.dump(out, open('asym_full_raw.json', 'w'), indent=0)
    for r in out: print(r)
