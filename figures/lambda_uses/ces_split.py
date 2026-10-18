# Split the compute-bottleneck drag on the after-today λ gain into (a) labor's weight in the experiment-capacity CES today
# and (b) saturation toward the infinite-labor ceiling between today and AC.
import csv, math, numpy as np
from aifm_sites import *
from progress_model.progress_rate import compute_research_effort
rows = []
for mode in ['uplift-solved','time-horizon','revenue']:
    p = dict(preset('daniel-08-16-26'), parallel_penalty=0.5, ac_anchor_mode=mode)
    a = model_run(p, {}, detail=True); m = a['model']; R = m.results; t = np.asarray(R['times']); PD = p['present_day']; ac = a['ac']; P = m.params
    f = lambda k, tt: float(np.interp(tt, t, np.asarray(R[k], float)))
    ec = lambda tt: float(np.exp(np.interp(tt, m.data.time, np.log(m.data.experiment_H100e))))
    RE = lambda C, S: compute_research_effort(C, S, P.alpha_experiment_capacity, P.rho_experiment_capacity, P.experiment_compute_exponent, 1.0)
    el = lambda C, S: math.log(RE(C, S*1.001)/RE(C, S))/math.log(1.001)
    G = f('coding_labors', ac)/f('coding_labors', PD); k = G**0.15
    S0, S1 = f('serial_coding_labors', PD), f('serial_coding_labors', ac)
    e0, e1 = el(ec(PD), S0), el(ec(ac), S1)
    gain = RE(ec(ac), S1*k)/RE(ec(ac), S1)
    lk = math.log(k)
    weight_drag = (1-e0)*lk; sat_drag = e0*lk - math.log(gain)
    rows.append(dict(anchor_mode=mode, serial_gain=round(k,4), labor_elasticity_today=round(e0,4), labor_elasticity_ac=round(e1,4),
        headroom_today=round(f('exp_cap_mult_with_infinite_labor', PD),2), headroom_ac=round(f('exp_cap_mult_with_infinite_labor', ac),2),
        throughput_gain=round(gain,4), share_lost_labor_weight=round(100*weight_drag/lk,1), share_lost_saturation=round(100*sat_drag/lk,1)))
    print(rows[-1])
    for asym in [1e4]:
        q = dict(p, inf_labor_asymptote=asym); b0 = model_run(q, {}); b1 = model_run(q, {'dynamics': 0.65})
        c1 = model_run(p, {'dynamics': 0.65})
        print(f"   benefit: ceiling 15 {12*(c1['ac']-a['ac']):+.2f} mo; ceiling 1e4 {12*(b1['ac']-b0['ac']):+.2f} mo")
w = csv.DictWriter(open('ces_split.csv','w',newline=''), fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

# Same throughput-gain calculation with the labor ceiling effectively removed (inf_labor_asymptote 1e4),
# using each anchor's default-run serial gain k so only the CES shape differs.
rows2 = []
for r0 in rows:
    mode = r0['anchor_mode']; k = r0['serial_gain']
    p = dict(preset('daniel-08-16-26'), parallel_penalty=0.5, ac_anchor_mode=mode, inf_labor_asymptote=1e4)
    a = model_run(p, {}, detail=True); m = a['model']; R = m.results; t = np.asarray(R['times']); PD = p['present_day']; ac = a['ac']; P = m.params
    f = lambda kk, tt: float(np.interp(tt, t, np.asarray(R[kk], float)))
    ec = lambda tt: float(np.exp(np.interp(tt, m.data.time, np.log(m.data.experiment_H100e))))
    RE = lambda C, S: compute_research_effort(C, S, P.alpha_experiment_capacity, P.rho_experiment_capacity, P.experiment_compute_exponent, 1.0)
    S1 = f('serial_coding_labors', ac); S0 = f('serial_coding_labors', PD)
    e0 = math.log(RE(ec(PD), S0*1.001)/RE(ec(PD), S0))/math.log(1.001)
    gain = RE(ec(ac), S1*k)/RE(ec(ac), S1)
    lost_noceil = 100*(1 - math.log(gain)/math.log(k)); lost_default = 100*(1 - math.log(r0['throughput_gain'])/math.log(k))
    rows2.append(dict(anchor_mode=mode, rho_no_ceiling=round(P.rho_experiment_capacity,4), labor_elasticity_today_no_ceiling=round(e0,4),
        throughput_gain_no_ceiling=round(gain,4), share_lost_default=round(lost_default,1), share_lost_without_ceiling=round(lost_noceil,1),
        share_lost_due_to_ceiling=round(lost_default-lost_noceil,1)))
    print(rows2[-1])
w = csv.DictWriter(open('ces_split_ceiling.csv','w',newline=''), fieldnames=list(rows2[0])); w.writeheader(); w.writerows(rows2)
