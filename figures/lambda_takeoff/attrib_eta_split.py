# Takeoff split by use of λ, as in attrib_eta_net.py, but with η in two rows. Six players, all 2^6 combinations:
#   anchor, history, cap - as before (patched sites)
#   benefit              - 'dynamics' site switched, with the serial rate of η-driven labor growth held fixed
#   etaboost             - that serial rate scaled by λ/0.5: what higher λ does to η-driven labor growth after today
#   etaadj               - η itself moved from 3 to the model's 3^(0.5/λ)
# Serial rate = 0.5 × 3 × (boost) × (adjustment); η fed in = rate / λ_dynamics. The 'eta' site stays at 0.5
# (exponent 1). All six on reproduces the plain run at the new λ. Runs on upstream with figures/lambda-sites.patch applied.
import itertools, json
from concurrent.futures import ProcessPoolExecutor
from aifm_sites import *
P6 = ['anchor', 'benefit', 'history', 'etaboost', 'etaadj', 'cap']
def job(a):
    mode, lam, subset = a
    ld = lam if 'benefit' in subset else 0.5
    rate = 0.5 * 3.0 * (lam / 0.5 if 'etaboost' in subset else 1.0) * (3.0 ** (0.5 / lam) / 3.0 if 'etaadj' in subset else 1.0)
    sites = {s: lam for s in subset if s in ('anchor', 'history', 'cap')}
    if 'benefit' in subset: sites['dynamics'] = lam
    p = dict(preset('daniel-08-16-26'), parallel_penalty=0.5, ac_anchor_mode=mode, coding_automation_efficiency_slope=rate / ld)
    try: r = model_run(p, sites)
    except Exception as e: r = dict(err=str(e)[:200])
    return dict(mode=mode, lam=lam, subset=list(subset), eta_used=rate / ld, **r)
if __name__ == '__main__':
    jobs = [(m, l, sub) for m in ['uplift-solved', 'time-horizon', 'revenue'] for l in [0.65, 1.0]
            for k in range(7) for sub in itertools.combinations(P6, k)]
    with ProcessPoolExecutor(4) as ex: out = list(ex.map(job, jobs, chunksize=2))
    json.dump(out, open('attrib_eta_split_raw.json', 'w'), indent=0)
    print(len(out), sum('err' in r for r in out))
