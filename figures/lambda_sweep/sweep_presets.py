import csv
from concurrent.futures import ProcessPoolExecutor
from aifm import preset, run
NAMES = {'daniel-08-16-26':'Daniel','eli-08-16-26':'Eli','brendan-08-16-26':'Brendan'}
def job(a):
    name, lam = a
    p = preset(name); q = dict(p, parallel_penalty=lam)
    ac, asi, err = run(q)
    return dict(preset=name, parallel_penalty=lam, present_day=round(p['present_day'],4),
        ac_year=None if ac is None else round(ac,4), asi_year=None if asi is None else round(asi,4),
        months_ac_to_asi=None if (ac is None or asi is None) else round((asi-ac)*12,2), error=None if err is None else str(err)[:200])
if __name__ == '__main__':
    jobs = [(n, round(0.3+0.05*k,2)) for n in NAMES for k in range(15)]
    with ProcessPoolExecutor(4) as ex: rows = list(ex.map(job, jobs))
    for r in rows: print(r)
    w = csv.DictWriter(open('lambda_sweep_presets.csv','w',newline=''), fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
