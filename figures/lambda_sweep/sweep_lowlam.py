# AC and ASI dates vs λ down to the low end, 3 presets x 3 AC anchors, under three η adjustments:
# the model's η^(0.5/λ), the proposed linear η·(0.5/λ), and none. The model always applies
# x -> x^(0.5/λ) to its input, so each variant feeds it the input that lands on the wanted η.
import csv, sys
from concurrent.futures import ProcessPoolExecutor
from aifm import preset, run
PRESETS = ['daniel-08-16-26','eli-08-16-26','brendan-08-16-26']
MODES = ['uplift-solved','time-horizon','revenue']
WANT = {'model': lambda e,l: e**(0.5/l), 'linear': lambda e,l: e*0.5/l, 'none': lambda e,l: e}
LAMS = [round(0.03+0.01*k,2) for k in range(28)] + [round(0.35+0.05*k,2) for k in range(14)]
def job(a):
    name, mode, form, lam = a
    p = preset(name); eta = p['coding_automation_efficiency_slope']
    want = WANT[form](eta, lam)
    q = dict(p, parallel_penalty=lam, ac_anchor_mode=mode, coding_automation_efficiency_slope=want**(lam/0.5))
    ac, asi, err = run(q)
    return dict(preset=name, ac_anchor_mode=mode, eta_form=form, parallel_penalty=lam, eta_effective=round(want,4),
        ac_year=None if ac is None else round(ac,4), asi_year=None if asi is None else round(asi,4),
        months_ac_to_asi=None if (ac is None or asi is None) else round((asi-ac)*12,2), error=None if err is None else str(err)[:200])
if __name__ == '__main__':
    jobs = [(n,m,f,l) for n in PRESETS for m in MODES for f in WANT for l in LAMS]
    with ProcessPoolExecutor(4) as ex: rows = list(ex.map(job, jobs, chunksize=4))
    w = csv.DictWriter(open('lambda_sweep_low.csv','w',newline=''), fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
