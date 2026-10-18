import csv
from concurrent.futures import ProcessPoolExecutor
from aifm import preset, run
PRESETS = ['daniel-08-16-26','eli-08-16-26','brendan-08-16-26']
MODES = ['uplift-solved','time-horizon','revenue','eci']
def job(a):
    name, mode, lam = a
    q = dict(preset(name), parallel_penalty=lam, ac_anchor_mode=mode)
    ac, asi, err = run(q)
    return dict(preset=name, ac_anchor_mode=mode, parallel_penalty=lam,
        ac_year=None if ac is None else round(ac,4), asi_year=None if asi is None else round(asi,4),
        months_ac_to_asi=None if (ac is None or asi is None) else round((asi-ac)*12,2), error=None if err is None else str(err)[:200])
if __name__ == '__main__':
    jobs = [(n, m, round(0.3+0.05*k,2)) for n in PRESETS for m in MODES for k in range(15)]
    with ProcessPoolExecutor(4) as ex: rows = list(ex.map(job, jobs))
    w = csv.DictWriter(open('lambda_sweep_anchors.csv','w',newline=''), fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    for r in rows:
        if r['parallel_penalty'] in (0.3,0.5,0.65,1.0) or r['error']: print(r)
