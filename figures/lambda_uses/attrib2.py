import itertools, json, sys
from concurrent.futures import ProcessPoolExecutor
from aifm_sites import *
S5 = ['anchor', 'dynamics', 'history', 'eta', 'cap']
def job(a):
    mode, target, subset = a
    p = dict(preset('daniel-08-16-26'), parallel_penalty=0.5, ac_anchor_mode=mode)
    try: r = model_run(p, {s: target for s in subset})
    except Exception as e: r = dict(err=str(e)[:200])
    return dict(mode=mode, target=target, subset=list(subset), **r)
if __name__ == '__main__':
    jobs = [(mode, tgt, sub) for mode in ['uplift-solved', 'time-horizon', 'revenue'] for tgt in [0.65, 0.8, 1.0]
            for k in range(6) for sub in itertools.combinations(S5, k)]
    with ProcessPoolExecutor(4) as ex: out = list(ex.map(job, jobs, chunksize=2))
    json.dump(out, open('attrib2_raw.json', 'w'), indent=0)
    print(len(out), sum('err' in r for r in out))
