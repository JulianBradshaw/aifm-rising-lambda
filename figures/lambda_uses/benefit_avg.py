# Drag chain for the after-today λ 0.5 → 0.65 benefit, averaged over every order of switching the uses
# (Shapley weights, as in the per-use chart), with the 15× asymptote and with it raised to 10,000.
import itertools, math, csv, numpy as np
from concurrent.futures import ProcessPoolExecutor
from aifm_sites import *
from progress_model.progress_rate import compute_research_effort
OTHERS = ['anchor', 'history', 'eta', 'cap']; N = 5; TO = 0.65
def chain(a):
    mode, ctx, asym = a
    p = dict(preset('daniel-08-16-26'), parallel_penalty=0.5, ac_anchor_mode=mode, inf_labor_asymptote=asym)
    sites = {s: TO for s in ctx}
    b0 = model_run(p, sites, detail=True); b1 = model_run(p, dict(sites, dynamics=TO), detail=True)
    m = b0['model']; R = m.results; t = np.asarray(R['times']); PD = p['present_day']; ac = b0['ac']; P = m.params
    f = lambda k, tt: float(np.interp(tt, t, np.asarray(R[k], float)))
    G = f('coding_labors', ac)/f('coding_labors', PD); k = G**(TO-0.5)
    C = float(np.exp(np.interp(ac, m.data.time, np.log(m.data.experiment_H100e)))); S1 = f('serial_coding_labors', ac)
    RE = lambda S: compute_research_effort(C, S, P.alpha_experiment_capacity, P.rho_experiment_capacity, P.experiment_compute_exponent, 1.0)
    thr = RE(S1*k)/RE(S1)
    tb = np.asarray(b1['model'].results['times']); grid = np.linspace(PD, ac, 200)
    pa = np.interp(grid, t, R['progress']); pb = np.interp(grid, tb, b1['model'].results['progress'])
    rate = (np.gradient(pb, grid)/np.gradient(pa, grid))[-2]
    extra = (pb[-1]-pa[0])/(pa[-1]-pa[0])
    w = math.factorial(len(ctx))*math.factorial(N-len(ctx)-1)/math.factorial(N)
    return dict(mode=mode, ctx=list(ctx), asym=asym, w=w, G=G, lnk=math.log(k), lnthr=math.log(thr), lnrate=math.log(rate),
                lnextra=math.log(extra), shift=12*(b1['ac']-ac), T=(ac-PD)*12)
if __name__ == '__main__':
    jobs = [(mode, c, asym) for mode in ['uplift-solved','time-horizon','revenue'] for asym in [15.0, 1e4]
            for n in range(5) for c in itertools.combinations(OTHERS, n)]
    with ProcessPoolExecutor(4) as ex: out = list(ex.map(chain, jobs))
    rows = []
    for mode in ['uplift-solved','time-horizon','revenue']:
        A = {asym: [r for r in out if r['mode'] == mode and r['asym'] == asym] for asym in [15.0, 1e4]}
        avg = lambda L, key: sum(r['w']*r[key] for r in L)
        d, u = A[15.0], A[1e4]
        lnk = avg(d, 'lnk'); sh = lambda x: 100*x/lnk
        thr_noceil = avg(u, 'lnthr') * lnk/avg(u, 'lnk')   # same gain scale, CES with ceiling raised
        T0 = next(r['T'] for r in d if not r['ctx'])
        rows.append(dict(anchor_mode=mode, labor_growth_to_ac_lambda05=round(next(r['G'] for r in d if not r['ctx']),1),
            serial_labor_gain_at_ac=round(math.exp(lnk),4), months_today_to_ac=round(T0,2),
            share_lost_ces=round(100 - sh(thr_noceil),1), share_lost_asymptote=round(sh(thr_noceil) - sh(avg(d,'lnthr')),1),
            share_lost_stock_training=round(sh(avg(d,'lnthr')) - sh(avg(d,'lnrate')),1),
            share_lost_backloading=round(sh(avg(d,'lnrate')) - sh(avg(d,'lnextra')),1),
            share_left=round(sh(avg(d,'lnextra')),1), ac_shift_months_shapley=round(avg(d,'shift'),3)))
        print(rows[-1])
    w = csv.DictWriter(open('benefit_drag_avg.csv','w',newline=''), fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
