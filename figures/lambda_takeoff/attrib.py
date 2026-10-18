# All 2^5 on/off combinations of λ's use sites, for AC, ASI and takeoff, at three
# Infinite Coding Labor Asymptote settings. Needs the patched scratch copy from
# figures/lambda-sites.patch applied.
import itertools, json
from concurrent.futures import ProcessPoolExecutor
from aifm_sites import *
S5 = ['anchor', 'dynamics', 'history', 'eta', 'cap']
CAPS = {'15': 15.0, '100': 100.0, '1e8': 1e8}
def job(a):
    mode, target, cap, subset = a
    p = dict(preset('daniel-08-16-26'), parallel_penalty=0.5, ac_anchor_mode=mode, inf_labor_asymptote=CAPS[cap])
    try: r = model_run(p, {s: target for s in subset})
    except Exception as e: r = dict(err=str(e)[:200])
    return dict(mode=mode, target=target, asymptote=cap, subset=list(subset), **r)
if __name__ == '__main__':
    jobs = [(mode, tgt, cap, sub) for cap in CAPS for mode in ['uplift-solved', 'time-horizon', 'revenue'] for tgt in [0.65, 1.0]
            for k in range(6) for sub in itertools.combinations(S5, k)]
    with ProcessPoolExecutor(4) as ex: out = list(ex.map(job, jobs, chunksize=2))
    json.dump(out, open('attrib_raw.json', 'w'), indent=0)
    print(len(out), sum('err' in r for r in out))
