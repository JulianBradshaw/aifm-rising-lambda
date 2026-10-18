# Takeoff split by use of λ, as in attrib.py, but with η's share of the
# straightforward benefit folded into the η row. Five players, all 2^5 on/off combinations:
#   anchor, history, cap   - as before (patched sites)
#   benefit (excl. η)      - 'dynamics' site switched, with η rescaled so the serial rate of
#                            η-driven labor growth (λ_dynamics × η) is held where it was
#   η net                  - serial rate of η-driven labor growth moved from its λ 0.5 value
#                            (0.5 × 3 = 1.5) to what the model delivers at the new λ: λ × 3^(0.5/λ)
# The 'eta' site stays at 0.5 (exponent 1), so the η fed in is used as given.
# All five on reproduces the plain run at the new λ. Runs on upstream with figures/lambda-sites.patch applied.
import itertools, json
from concurrent.futures import ProcessPoolExecutor
from aifm_sites import *
P5 = ['anchor', 'benefit', 'history', 'etanet', 'cap']
def job(a):
    mode, lam, subset = a
    ld = lam if 'benefit' in subset else 0.5
    serial_eta = lam * 3.0 ** (0.5 / lam) if 'etanet' in subset else 0.5 * 3.0
    sites = {s: lam for s in subset if s in ('anchor', 'history', 'cap')}
    if 'benefit' in subset: sites['dynamics'] = lam
    p = dict(preset('daniel-08-16-26'), parallel_penalty=0.5, ac_anchor_mode=mode,
             coding_automation_efficiency_slope=serial_eta / ld)
    try: r = model_run(p, sites)
    except Exception as e: r = dict(err=str(e)[:200])
    return dict(mode=mode, lam=lam, subset=list(subset), eta_used=serial_eta / ld, **r)
if __name__ == '__main__':
    jobs = [(m, l, sub) for m in ['uplift-solved', 'time-horizon', 'revenue'] for l in [0.65, 1.0]
            for k in range(6) for sub in itertools.combinations(P5, k)]
    with ProcessPoolExecutor(4) as ex: out = list(ex.map(job, jobs, chunksize=2))
    json.dump(out, open('attrib_eta_net_raw.json', 'w'), indent=0)
    print(len(out), sum('err' in r for r in out))
